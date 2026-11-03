"""Varredura em λ (diagonal e superfície λ_π × λ_fiscal), matriz de experimentos, leques e sensibilidade.

Todos os experimentos usam os mesmos choques (common random numbers): as diferenças entre cenários,
especificações e variantes refletem a política, não o sorteio.
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from . import metricas, modelo, politicas

VARS_METRICAS = ("d_gross", "d_net", "pi", "R")
CHAVES_CENARIO = {"T_corte", "delta0", "T_delta", "i_alvo", "venda_reservas", "pacote_fiscal", "politica_monetaria",
                  "piso_final", "choque_t", "choque_de", "choque_prem", "choque_decai", "defesa_reservas"}
# chaves de controle das variantes (não são parâmetros do modelo)
CHAVES_CONTROLE = {"especificacoes", "cenario", "ref"}


def grade_lambda(passo: float = 0.01) -> np.ndarray:
    return np.round(np.arange(0, 1 + passo / 2, passo), 4)


def sortear_choques(p: dict, N: int, T: int, seed: int) -> np.ndarray:
    """Choques (N, T, 4) ~ Normal multivariada com a covariância dos resíduos históricos."""
    cov = np.array(p["choques"]["matriz"])
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(np.zeros(4), cov, size=(N, T))


# ---------------------------------------------------------------- experimentos

def aplicar_variante(p_base: dict, espec: str, variante: dict, chaves: list[str]):
    """Parâmetros e ajustes de cenário de uma variante; None se ela não se aplica à especificação."""
    variante = dict(variante)
    variante.pop("ref", None)
    especs = variante.pop("especificacoes", None)
    if especs and espec not in especs:
        return None
    alvo = variante.pop("cenario", None)
    chaves = [alvo] if alvo else list(chaves)
    ajustes = {k: variante.pop(k) for k in list(variante) if k in CHAVES_CENARIO}
    # parâmetros calibrados por especificação (ex.: b3 da Tarefa 3) vêm como {P1: x, P2: y, P3: z}
    variante = {k: (v[espec] if isinstance(v, dict) else v) for k, v in variante.items()}
    p = copy.deepcopy(p_base)
    p["especificacao"] = espec
    p.update(variante)
    return modelo.preparar(p), chaves, ajustes


def preparar_cenarios(p: dict, cfg: dict, chaves=None, ajustes: dict | None = None) -> dict:
    """Trilhas exógenas e plano anunciado de cada cenário (ajustes valem para todos os cenários listados)."""
    saida = {}
    for chave in chaves or cfg["cenarios"]:
        cen = politicas.montar_cenario(chave, cfg, p["ini"]["i0"], ajustes=ajustes)
        saida[chave] = {"cen": cen, "plano": modelo.plano_anunciado(p, cen)}
    return saida


def _metricas_bloco(p: dict, tr: dict, grupos: int, N: int) -> list[dict]:
    """Agrega P(sucesso) e percentis por grupo de N trajetórias consecutivas."""
    n = p["criterios"]["janela_final"]
    ok, det = metricas.sucesso(tr, p)
    ok5, _ = metricas.sucesso(tr, p, p["criterios"].get("tolerancia_inflacao_alt", 2.0))
    okb, detb = metricas.sucesso(tr, p, bilateral=True)
    okl = metricas.sucesso(tr, p, divida="liquida")[0]
    oklb = metricas.sucesso(tr, p, bilateral=True, divida="liquida")[0]
    piso_meta = p["pi_meta"] - p["criterios"]["tolerancia_inflacao"]
    d_fim = tr["d_gross"][:, -1]
    pi_fim = tr["pi"][:, -n:].mean(axis=1)
    rompeu = tr["ruptura"] >= 0
    linhas = []
    for j in range(grupos):
        s = slice(j * N, (j + 1) * N)
        sub = {k: v[s] for k, v in det.items()}
        subb = {k: v[s] for k, v in detb.items()}
        vivos = ~rompeu[s]
        abaixo = sub["inflacao_explosiva"] & (pi_fim[s] < piso_meta)
        q_d = np.nanpercentile(d_fim[s][vivos], [10, 50, 90]) if vivos.any() else [np.nan] * 3
        q_pi = np.nanpercentile(pi_fim[s][vivos], [10, 50, 90]) if vivos.any() else [np.nan] * 3
        linhas.append({
            "p_sucesso": ok[s].mean(), "p_sucesso_teto5": ok5[s].mean(), "p_sucesso_bil": okb[s].mean(),
            "p_sucesso_liq": okl[s].mean(), "p_sucesso_liq_bil": oklb[s].mean(),
            "p_inflacao_ok_bil": subb["inflacao"].mean(), "falha_abaixo_banda": abaixo.mean(),
            "frac_sucesso_abaixo_banda": float((ok[s] & (pi_fim[s] < piso_meta)).sum() / max(ok[s].sum(), 1)),
            "p_divida_ok": metricas.divida_ok(sub).mean(), "p_inflacao_ok": sub["inflacao"].mean(),
            "frac_explosiva": 1 - sub["inflacao_explosiva"].mean(), "frac_ruptura50": rompeu[s].mean(),
            **{f"falha_{k}": v for k, v in metricas.falhas(sub).items()},
            "d_final_p10": q_d[0], "d_final_p50": q_d[1], "d_final_p90": q_d[2],
            "pi_final_p10": q_pi[0], "pi_final_p50": q_pi[1], "pi_final_p90": q_pi[2],
        })
    return linhas


def diagonal(p: dict, cens: dict, grade: np.ndarray, choques: np.ndarray | None, bloco: int = 10,
             trajetorias: bool = False):
    """Varredura na diagonal λ_π = λ_fiscal; choques=None dá a versão determinística (N = 1).

    Com trajetorias=True devolve também, por cenário, o sucesso e o código de falha de cada trajetória:
    arrays (n_λ, N) usados no bootstrap.
    """
    N = 1 if choques is None else choques.shape[0]
    linhas, cods = [], {}
    oks_m = {suf: {} for suf in metricas.METRICAS}
    for chave, c in cens.items():
        cod_c = []
        okm_c = {suf: [] for suf in metricas.METRICAS}
        for k in range(0, len(grade), bloco):
            sub = grade[k:k + bloco]
            lam = np.repeat(sub, N)
            ch = None if choques is None else np.tile(choques, (len(sub), 1, 1))
            tr = modelo.simular(p, c["cen"], lam, choques=ch, plano=c["plano"], guardar=VARS_METRICAS)
            for l, m in zip(sub, _metricas_bloco(p, tr, len(sub), N)):
                linhas.append({"cenario": chave, "lambda": float(l), **m})
            if trajetorias:
                _, det = metricas.sucesso(tr, p)
                cod_c.append(metricas.codigo_falha(det).reshape(len(sub), N))
                for suf, ok in metricas.sucesso_todas(tr, p).items():
                    okm_c[suf].append(ok.reshape(len(sub), N))
        if trajetorias:
            cods[chave] = np.concatenate(cod_c)
            for suf in metricas.METRICAS:
                oks_m[suf][chave] = np.concatenate(okm_c[suf])
    df = pd.DataFrame(linhas)
    # (tabela, sucesso por trajetória em cada métrica {sufixo: {cenário: (n_λ, N)}}, códigos de falha)
    return (df, oks_m, cods) if trajetorias else df


def rodar_combinacao(p_base: dict, cfg: dict, espec: str, nome: str, variante: dict, grade: np.ndarray,
                     choques: np.ndarray, pasta: Path | None = None, retomar: bool = False) -> pd.DataFrame | None:
    """Diagonal determinística + Monte Carlo de uma (especificação, variante); grava parquet parcial."""
    arq = pasta / f"diagonal_{espec}_{nome}.parquet" if pasta else None
    arq_traj = pasta / f"trajetorias_{espec}_{nome}.npz" if pasta else None
    if retomar and arq is not None and arq.exists() and arq_traj.exists():
        df = pd.read_parquet(arq)
        if "p_sucesso_liq_bil" in df and "sucesso_det_liq_bil" in df:
            return df
    aplicada = aplicar_variante(p_base, espec, variante, list(cfg["cenarios"]))
    if aplicada is None:
        return None
    p, chaves, ajustes = aplicada
    cens = preparar_cenarios(p, cfg, chaves, ajustes)
    det = diagonal(p, cens, grade, None)[["cenario", "lambda", "frac_explosiva"]
                                         + [f"p_sucesso{s}" for s in metricas.METRICAS]]
    det = det.rename(columns={**{f"p_sucesso{s}": f"sucesso_det{s}" for s in metricas.METRICAS},
                              "frac_explosiva": "explosiva_det"})
    mc, oks_m, cods = diagonal(p, cens, grade, choques, trajetorias=True)
    oks = oks_m[""]
    df = det.merge(mc, on=["cenario", "lambda"]).assign(especificacao=espec, variante=nome)
    if arq is not None:
        arq.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(arq, index=False)
        np.savez_compressed(arq_traj, cenarios=np.array(list(oks)), grade=grade,
                            **{metricas.CHAVE_OK[s]: np.stack([np.packbits(oks_m[s][c], axis=-1) for c in oks])
                               for s in metricas.METRICAS},
                            codigo=np.stack([cods[c] for c in oks]), N=choques.shape[0])
    return df


def rodar_matriz(p_base: dict, cfg: dict, exp: dict, especs: list[str], grade: np.ndarray, choques: np.ndarray,
                 pasta: Path, retomar: bool = False, n_jobs: int = -1) -> pd.DataFrame:
    tarefas = [(e, n, v) for e in especs for n, v in exp["variantes"].items()]
    res = Parallel(n_jobs=n_jobs)(delayed(rodar_combinacao)(p_base, cfg, e, n, v, grade, choques, pasta, retomar)
                                  for e, n, v in tarefas)
    return pd.concat([r for r in res if r is not None], ignore_index=True)


def tabela_lambda_star(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (espec, var, chave), g in df.groupby(["especificacao", "variante", "cenario"], sort=False):
        g = g.sort_values("lambda")
        lam = g["lambda"].values
        ls = metricas.lambda_star_det(lam, g["sucesso_det"].values > 0.5)
        linhas.append({
            "especificacao": espec, "variante": var, "cenario": chave,
            "lambda_star_det": ls["lambda_star"], "det_monotonico": ls["monotonico"],
            "det_intervalos": "; ".join(f"[{a:.2f}, {b:.2f}]" for a, b in ls["intervalos"]) or "nenhum",
            "lambda_star_50": metricas.lambda_star_prob(lam, g["p_sucesso"].values, 0.5),
            "lambda_star_80": metricas.lambda_star_prob(lam, g["p_sucesso"].values, 0.8),
            "lambda_star_70": metricas.lambda_star_prob(lam, g["p_sucesso"].values, 0.7),
            "lambda_star_80_teto5": metricas.lambda_star_prob(lam, g["p_sucesso_teto5"].values, 0.8),
            "p_sucesso_max": g["p_sucesso"].max(),
            "quedas_p_sucesso": metricas.violacoes_monotonia(g["p_sucesso"].values, tolerancia=0.02),
            # demais métricas: banda simétrica (_bil), dívida líquida (_liq) e ambas (_liq_bil)
            **{k: v for s in ("_bil", "_liq", "_liq_bil") for k, v in {
                f"lambda_star_det{s}": metricas.lambda_star_det(lam, g[f"sucesso_det{s}"].values > 0.5)["lambda_star"],
                f"lambda_star_50{s}": metricas.lambda_star_prob(lam, g[f"p_sucesso{s}"].values, 0.5),
                f"lambda_star_70{s}": metricas.lambda_star_prob(lam, g[f"p_sucesso{s}"].values, 0.7),
                f"lambda_star_80{s}": metricas.lambda_star_prob(lam, g[f"p_sucesso{s}"].values, 0.8),
                f"p_sucesso_max{s}": g[f"p_sucesso{s}"].max()}.items()},
        })
    return pd.DataFrame(linhas)


def ordenar(ls: pd.DataFrame, col80: str = "lambda_star_80", refs: dict | None = None, sufixo: str = "") -> pd.DataFrame:
    """Posição de cada cenário: menor λ*₈₀, desempate por λ*₅₀, λ* determinístico e P(sucesso) máx.

    refs: {variante restrita a um cenário: variante de referência para os demais cenários} (padrão: base).
    """
    refs = refs or {}
    linhas = []
    for (espec, var), g in ls.groupby(["especificacao", "variante"], sort=False):
        if g["cenario"].nunique() < 2:
            ref = refs.get(var, "base")
            base = ls[(ls["especificacao"] == espec) & (ls["variante"] == ref) & ~ls["cenario"].isin(g["cenario"])]
            if base.empty:
                base = ls[(ls["especificacao"] == espec) & (ls["variante"] == "base") & ~ls["cenario"].isin(g["cenario"])]
            g = pd.concat([g, base])
        col80s = col80 if col80 != "lambda_star_80" else f"lambda_star_80{sufixo}"
        g = g.assign(_a=g[col80s].fillna(9), _b=g[f"lambda_star_50{sufixo}"].fillna(9),
                     _c=g[f"lambda_star_det{sufixo}"].fillna(9),
                     _d=-g[f"p_sucesso_max{sufixo}"]).sort_values(["_a", "_b", "_c", "_d"])
        for pos, c in enumerate(g["cenario"], start=1):
            linhas.append({"especificacao": espec, "variante": var, "cenario": c, "posicao": pos})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- superfície

def _superficie_cenario(p, c, chave, grade, choques, linhas_por_bloco=3):
    N = choques.shape[0]
    n = len(grade)
    saida, oks, cods, oksb = [], [], [], []
    for k in range(0, n, linhas_por_bloco):
        lp = grade[k:k + linhas_por_bloco]
        lam_pi = np.repeat(np.repeat(lp, n), N)
        lam_f = np.repeat(np.tile(grade, len(lp)), N)
        ch = np.tile(choques, (len(lp) * n, 1, 1))
        tr = modelo.simular(p, c["cen"], lam_pi, lam_f, choques=ch, plano=c["plano"], guardar=VARS_METRICAS)
        ok, det = metricas.sucesso(tr, p)
        okb, _ = metricas.sucesso(tr, p, bilateral=True)
        P = ok.reshape(-1, N).mean(axis=1)
        Pb = okb.reshape(-1, N).mean(axis=1)
        dok = metricas.divida_ok(det).reshape(-1, N).mean(axis=1)
        iok = det["inflacao"].reshape(-1, N).mean(axis=1)
        oks.append(ok.reshape(len(lp), n, N))
        oksb.append(okb.reshape(len(lp), n, N))
        cods.append(metricas.codigo_falha(det).reshape(len(lp), n, N))
        for j, (a, b) in enumerate(zip(np.repeat(lp, n), np.tile(grade, len(lp)))):
            saida.append({"cenario": chave, "lambda_pi": float(a), "lambda_fiscal": float(b), "p_sucesso": P[j],
                          "p_sucesso_bil": Pb[j], "p_divida_ok": dok[j], "p_inflacao_ok": iok[j]})
    return saida, np.concatenate(oks), np.concatenate(cods), np.concatenate(oksb)


def superficie(p_base: dict, cfg: dict, exp: dict, especs: list[str], choques: np.ndarray,
               n_jobs: int = -1):
    """P(sucesso) na grade λ_π × λ_fiscal; devolve (tabela, {(espec, variante, cenário): (ok, código)})."""
    sup = exp["superficie"]
    grade = grade_lambda(sup["passo"])
    tarefas = []
    for espec in especs:
        for nome in sup["variantes"]:
            p, chaves, ajustes = aplicar_variante(p_base, espec, exp["variantes"][nome], list(cfg["cenarios"]))
            cens = preparar_cenarios(p, cfg, chaves, ajustes)
            for chave, c in cens.items():
                tarefas.append((espec, nome, p, chave, c))
    res = Parallel(n_jobs=n_jobs)(delayed(_superficie_cenario)(p, c, ch, grade, choques[:sup["N"]])
                                  for _, _, p, ch, c in tarefas)
    linhas = [{"especificacao": e, "variante": n, **l} for (e, n, *_), r in zip(tarefas, res) for l in r[0]]
    trajs = {(e, n, ch): (r[1], r[2], r[3]) for (e, n, _, ch, _), r in zip(tarefas, res)}
    return pd.DataFrame(linhas), trajs


def areas(sup: pd.DataFrame, limiar: float = 0.8, col: str = "p_sucesso") -> pd.DataFrame:
    return (sup.groupby(["especificacao", "variante", "cenario"], sort=False)[col]
            .apply(lambda x: metricas.area_sucesso(x.values, limiar)).rename("area_sucesso").reset_index())


# ---------------------------------------------------------------- leques e decomposições

def leques(p: dict, cens: dict, choques: np.ndarray, lams=(0.3, 0.6, 0.9),
           variaveis=("d_gross", "i", "pi", "E")) -> dict:
    """Percentis 10/50/90 ao longo do tempo (só trajetórias não rompidas) e fração explosiva."""
    N = choques.shape[0]
    saida = {}
    for chave, c in cens.items():
        for lam in lams:
            tr = modelo.simular(p, c["cen"], np.full(N, lam), choques=choques, plano=c["plano"],
                                guardar=tuple(set(variaveis) | set(VARS_METRICAS)))
            vivos = tr["ruptura"] < 0
            _, det = metricas.sucesso(tr, p)
            q = {v: np.nanpercentile(tr[v][vivos], [10, 50, 90], axis=0) if vivos.any()
                 else np.full((3, tr[v].shape[1]), np.nan) for v in variaveis}
            q["frac_explosiva"] = 1 - det["inflacao_explosiva"].mean()
            saida[(chave, lam)] = q
    return saida


def decomposicao_divida(p: dict, cens: dict, lam: float = 0.5) -> pd.DataFrame:
    """Contribuições anuais para a variação da dívida bruta (trajetória determinística)."""
    linhas = []
    for chave, c in cens.items():
        tr = modelo.simular(p, c["cen"], lam, plano=c["plano"])
        for t in range(1, tr["d_gross"].shape[1]):
            linhas.append({"cenario": chave, "t": t, "ano": (t - 1) // 4 + 1,
                           "juros": tr["c_juros"][0, t], "crescimento": tr["c_cresc"][0, t],
                           "primario": tr["c_prim"][0, t], "reservas": tr["c_res"][0, t],
                           "variacao": tr["d_gross"][0, t] - tr["d_gross"][0, t - 1]})
    return pd.DataFrame(linhas)


def decomposicao_inflacao(p: dict, cens: dict, lam: float = 0.5) -> pd.DataFrame:
    """Componentes da inflação (média anual) na trajetória determinística."""
    linhas = []
    for chave, c in cens.items():
        tr = modelo.simular(p, c["cen"], lam, plano=c["plano"])
        for t in range(1, tr["pi"].shape[1]):
            linhas.append({"cenario": chave, "t": t, "ano": (t - 1) // 4 + 1, "pi": tr["pi"][0, t],
                           **{k.removeprefix("comp_"): tr[k][0, t] for k in modelo.COMP_PI}})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- sensibilidade

def _sens_ponto(p_base, cfg, espec, nome, valor, grade, choques):
    q = copy.deepcopy(p_base)
    q["especificacao"] = espec
    q[nome] = valor
    q = modelo.preparar(q)
    cens = preparar_cenarios(q, cfg)
    N = choques.shape[0]
    saida = {}
    for chave, c in cens.items():
        tr = modelo.simular(q, c["cen"], np.repeat(grade, N), choques=np.tile(choques, (len(grade), 1, 1)),
                            plano=c["plano"], guardar=VARS_METRICAS)
        ok, _ = metricas.sucesso(tr, q)
        saida[chave] = ok.reshape(len(grade), N).mean(axis=1)
    return espec, nome, valor, saida


def sensibilidade(p_base: dict, cfg: dict, exp: dict, especs: list[str], choques: np.ndarray,
                  n_jobs: int = -1) -> dict:
    """{espec: {param: {'valores', 'grade', cenário: P(sucesso) (n_valores, n_λ)}}}."""
    s = exp["sensibilidade"]
    grade = grade_lambda(s["passo_lambda"])
    tarefas = []
    for espec in especs:
        for nome, (lo, hi) in s["parametros"][espec].items():
            valores = ([0.0, 0.025, 0.05, 0.10, 0.15] if nome == "b2_p2"
                       else np.linspace(lo, hi, s["n_valores"]))
            tarefas += [(espec, nome, float(v)) for v in valores]
    res = Parallel(n_jobs=n_jobs)(delayed(_sens_ponto)(p_base, cfg, e, n, v, grade, choques[:s["N"]])
                                  for e, n, v in tarefas)
    saida: dict = {}
    for espec, nome, valor, r in res:
        d = saida.setdefault(espec, {}).setdefault(nome, {"valores": [], "grade": grade})
        d["valores"].append(valor)
        for ch, v in r.items():
            d.setdefault(ch, []).append(v)
    for espec in saida.values():
        for d in espec.values():
            d["valores"] = np.array(d["valores"])
            for ch in cfg["cenarios"]:
                d[ch] = np.array(d[ch])
    return saida
