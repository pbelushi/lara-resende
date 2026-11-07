"""Credibilidades separadas: λ_fiscal baixo travado, λ_π livre acima de 0,5.

Hipótese (contexto brasileiro desde o Real): o regime de metas sustenta a credibilidade da meta de inflação (λ_π)
mesmo quando a credibilidade fiscal (λ_fiscal) é baixa.

1. Validação em duas dimensões: λ_π e λ_fiscal de melhor ajuste em 2015–16, 2016–19 e 2020–22 (P2, mesma medida de
   erro de src/validacao.py: inflação 12 meses e NTN-B 10 anos).
2. Estratégias do paper com λ_fiscal ∈ {0,1; 0,2; 0,3} e λ_π ∈ {0,5; …; 1,0}.
3. Busca aleatória repetida: λ_fiscal travado e λ_π sorteado por trajetória em U(0,5; 1,0).

Uso: python -m src.credibilidades_separadas [--n1 4000] [--n2 1500] [--N1 200] [--jobs 2]
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from . import busca_aleatoria as B, metricas, modelo, recessivo as R, validacao, varredura

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "outputs" / "v2_2" / "credibilidades_separadas"
LF = [0.1, 0.2, 0.3]
LP_GRADE = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
EPIS = {"2015–16: recessão e crise fiscal": ("2014-12-31", "2016-12-31"),
        **validacao.EPISODIOS}
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------- 1. validação 2D

def validar_2d(p: dict, espec: str = "P2") -> pd.DataFrame:
    painel = pd.read_csv(validacao.PROC / "trimestral.csv", index_col=0, parse_dates=True)
    arq = validacao.RAW / "focus_anuais_historico.csv"
    anuais = pd.read_csv(arq, parse_dates=["Data"]) if arq.exists() else None
    g = validacao.GRADE_LAMBDA
    LP, LFm = np.meshgrid(g, g, indexing="ij")
    linhas = []
    for nome, (ini, fim) in EPIS.items():
        ini, fim = pd.Timestamp(ini), pd.Timestamp(fim)
        jan = painel.loc[ini:fim]
        T = len(jan) - 1
        q = copy.deepcopy(p)
        q["especificacao"] = espec
        q["ini"] = validacao._ini_historico(painel, ini, p["ini"])
        q.pop("g_potencial", None)
        q = modelo.preparar(q)
        i_h, s_h = jan["meta_selic"].values, jan["s_spc"].values
        z = np.zeros(T + 1)
        cen = {"chave": "hist", "nome": "h", "cor": "#333", "regra": "exogena", "delta": z, "i_exog": i_h,
               "medidas_receita": z, "medidas_despesa": z, "venda_reservas": z, "capex_ppp": z, "T": T}
        s_est = modelo.s_estabilizador(jan["selic"].iloc[-4:].mean(), jan["gamma"].iloc[-1], jan["dbgg"].iloc[-1])
        F = q["p1"] * (jan["dbgg"].iloc[-1] - q["d_ref"]) + modelo.p2_efetivo(q) * (s_est - s_h[-1])
        plano = {"F": float(F), "i": np.concatenate([i_h, np.full(8, i_h[-1])]),
                 "s_mat": validacao.plano_s_focus(anuais, jan.index, s_h, int(q["H_vp"]))}
        tr = modelo.simular(q, cen, LP.ravel(), LFm.ravel(), plano=plano,
                            override={"i": i_h, "s": s_h, "de": jan["de"].values}, guardar=("pi", "r_long"))
        dados = {"pi": jan["ipca12"].values, "r_long": jan["ntnb10"].values}
        erro = validacao._erro(tr, dados).reshape(LP.shape)
        k = np.unravel_index(np.nanargmin(erro), erro.shape)
        diag = np.nanargmin(np.diag(erro))
        # região de quase-indiferença: erro até 5% acima do mínimo
        quase = erro <= np.nanmin(erro) * 1.05
        linhas.append({"episodio": nome, "especificacao": espec, "lambda_pi": float(g[k[0]]),
                       "lambda_fiscal": float(g[k[1]]), "erro_min": float(np.nanmin(erro)),
                       "lambda_diagonal": float(g[diag]), "erro_diagonal": float(np.diag(erro)[diag]),
                       "faixa_lambda_pi_5pct": f"{g[np.where(quase.any(axis=1))[0]].min():.2f}–"
                                              f"{g[np.where(quase.any(axis=1))[0]].max():.2f}",
                       "faixa_lambda_fiscal_5pct": f"{g[np.where(quase.any(axis=0))[0]].min():.2f}–"
                                                   f"{g[np.where(quase.any(axis=0))[0]].max():.2f}"})
        pd.DataFrame(erro, index=g, columns=g).to_csv(SAIDA / f"erro_2d_{ini.year}.csv")
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------------------------- 2 e 3. simulação

def simular_combo(c: dict, p_base: dict, cfg: dict, espec: str, choques: np.ndarray, lam_pi, lam_f):
    """Trajetórias de uma combinação para vetores (P,) de λ_π e λ_fiscal; choques (P, T, 4)."""
    pac, aloc = B.pacote_de(c, cfg["horizonte"])
    extra = {"alongamento": True, "w_lft_alvo": c["w_lft"], "T_along": c["T_along"], "s_ipca": 0.7} if c["along"] else {}
    q = R.preparar_espec(p_base, espec, extra)
    k = c["T_res"]
    aj = {"politica_monetaria": c["regra"], "pacote_fiscal": c["total"] > 0,
          "venda_reservas": [c["reservas"] / k] * k if c["reservas"] > 0 else []}
    chave = "A"
    if c["regra"] == "exogena":
        chave = "B"
        aj.update({"i_alvo": 7.5, "T_corte": 6})
    elif c["regra"] != "taylor":
        chave = "C"
        aj.update({"i_alvo": c["i_alvo"], "T_corte": c["T_corte"], "delta0": c["delta0"], "T_delta": c["T_delta"],
                   "piso_final": c.get("piso_final")})
    cc = copy.deepcopy(cfg)
    cc["pacote_fiscal"] = pac
    cen = varredura.preparar_cenarios(q, cc, [chave], aj)[chave]
    tr = modelo.simular(q, cen["cen"], lam_pi, lam_f, choques=choques, plano=cen["plano"], guardar=R.GUARDAR)
    return tr, q, aloc


def avaliar_livre(c, p_base, cfg, espec, choques, lp_draw, trS_cache, lf_grade=None):
    """λ_fiscal travado em cada valor de lf_grade (padrão LF); λ_π sorteado por trajetória (lp_draw, (N,))."""
    LF_ = list(lf_grade or LF)
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    N = choques.shape[0]
    lam_pi = np.tile(lp_draw, len(LF_))
    lam_f = np.repeat(LF_, N)
    ch = np.tile(choques, (len(LF_), 1, 1))
    tr, q, aloc = simular_combo(c, p_base, cfg, espec, ch, lam_pi, lam_f)
    key = (espec, N)
    if key not in trS_cache:
        trS_cache[key] = simular_combo(REF["S"], p_base, cfg, espec, ch, lam_pi, lam_f)[0]
    trS = trS_cache[key]
    rs = lambda t: {k: (v.reshape(len(LF_), N, -1) if v.ndim > 1 else v.reshape(len(LF_), N))  # noqa: E731
                    for k, v in t.items()}
    a, s = rs(tr), rs(trS)
    m = R.atividade(a, s, q)
    out = []
    mult = sum(R.CONF["itens"][k]["m"] * v for k, v in aloc.items()) / max(sum(aloc.values()), 1e-9)
    for i, lf in enumerate(LF_):
        sub = {k: v[i] for k, v in a.items()}
        ok = {suf: metricas.sucesso(sub, q, bilateral=b, divida=d)[0] for suf, (b, d) in metricas.METRICAS.items()}
        v = m["valida"][i]
        out.append({"especificacao": espec, "lambda_fiscal": lf, **{f"p{suf}": float(o.mean()) for suf, o in ok.items()},
                    "dif_1-16": float(np.nanmean(np.where(v, m["dif_1-16"][i], np.nan))) if v.any() else np.nan,
                    "dif_1-8": float(np.nanmean(np.where(v, m["dif_1-8"][i], np.nan))) if v.any() else np.nan,
                    "p_recessao_1-16": float(m["recessao_1-16"][i].mean()),
                    "total_efetivo": float(sum(aloc.values())), "mult_medio": float(mult),
                    **{f"x_{k}": float(aloc.get(k, 0.0)) for k in B.ITENS}})
    return out


def _lote(lote, p_base, cfg, espec, choques, lp_draw, lf_grade=None):
    cache: dict = {}
    res = []
    for cid, c in lote:
        try:
            for l in avaliar_livre(c, p_base, cfg, espec, choques, lp_draw, cache, lf_grade):
                res.append({"id": cid, **l, **{f"c_{k}": v for k, v in c.items() if k != "pesos"}})
        except Exception as e:  # noqa: BLE001
            log.warning("combinação %s falhou: %s", cid, e)
    return res


def rodar(combos, p_base, cfg, espec, choques, lp_draw, jobs, lote=50, lf_grade=None) -> pd.DataFrame:
    it = list(combos.items())
    res = Parallel(n_jobs=jobs)(delayed(_lote)(it[i:i + lote], p_base, cfg, espec, choques, lp_draw, lf_grade)
                                for i in range(0, len(it), lote))
    return pd.DataFrame([x for r in res for x in r])


BASE_PESOS = [1.2, 0, 0.4, 0, 0, 0.3, 0, 0.8, 0, 0]  # pacote base do paper (renúncias, subsídios, emendas, pisos)
_C = {"inicio": 2, "rampa": 8, "i_alvo": 7.5, "T_corte": 6, "delta0": 1.0, "T_delta": 8, "T_res": 4,
      "along": False, "w_lft": 0.4, "T_along": 20}
REF = {
    "S": {**_C, "total": 0.0, "pesos": BASE_PESOS, "regra": "taylor", "reservas": 0.0},
    "A": {**_C, "total": 2.7, "pesos": BASE_PESOS, "regra": "taylor", "reservas": 0.0},
    "A_reservas": {**_C, "total": 2.7, "pesos": BASE_PESOS, "regra": "taylor", "reservas": 100.0},
    "B": {**_C, "total": 0.0, "pesos": BASE_PESOS, "regra": "exogena", "reservas": 100.0},
    "C": {**_C, "total": 2.7, "pesos": BASE_PESOS, "regra": "condicionada", "reservas": 100.0, "piso_final": None},
    "C_sem_piso": {**_C, "total": 2.7, "pesos": BASE_PESOS, "regra": "condicionada_sem_piso", "reservas": 100.0},
}


def estrategias_grade(p, cfg, choques, lp_grade=None, lf_grade=None) -> pd.DataFrame:
    """Estratégias de referência em toda a grade λ_π × λ_fiscal (N = 1000)."""
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    N = choques.shape[0]
    pares = [(lp, lf) for lp in (lp_grade or LP_GRADE) for lf in (lf_grade or LF)]
    lp = np.repeat([a for a, _ in pares], N)
    lf = np.repeat([b for _, b in pares], N)
    ch = np.tile(choques, (len(pares), 1, 1))
    linhas = []
    for espec in ("P1", "P2", "P3_theta05"):
        trS, qS, _ = simular_combo(REF["S"], p, cfg, espec, ch, lp, lf)
        for nome, c in REF.items():
            tr, q, _ = simular_combo(c, p, cfg, espec, ch, lp, lf)
            rs = lambda t: {k: (v.reshape(len(pares), N, -1) if v.ndim > 1 else v.reshape(len(pares), N))  # noqa: E731
                            for k, v in t.items()}
            a, s = rs(tr), rs(trS)
            m = R.atividade(a, s, q)
            for i, (x, y) in enumerate(pares):
                sub = {k: v[i] for k, v in a.items()}
                v = m["valida"][i]
                linhas.append({"especificacao": espec.replace("_theta05", ""), "estrategia": nome, "lambda_pi": x,
                               "lambda_fiscal": y,
                               "p_teto": float(metricas.sucesso(sub, q)[0].mean()),
                               "p_banda": float(metricas.sucesso(sub, q, bilateral=True)[0].mean()),
                               "p_liq_banda": float(metricas.sucesso(sub, q, bilateral=True, divida="liquida")[0].mean()),
                               "dif_1-16": float(np.nanmean(np.where(v, m["dif_1-16"][i], np.nan))) if v.any() else np.nan})
    return pd.DataFrame(linhas)


def main():
    global SAIDA
    ap = argparse.ArgumentParser()
    ap.add_argument("--n1", type=int, default=4000)
    ap.add_argument("--n2", type=int, default=1500)
    ap.add_argument("--N1", type=int, default=200)
    ap.add_argument("--final", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--lf", default=",".join(str(x) for x in LF), help="grade de λ_fiscal travado")
    ap.add_argument("--lp", default="0.5,1.0", help="intervalo do sorteio uniforme de λ_π")
    ap.add_argument("--lp-grade", default=",".join(str(x) for x in LP_GRADE))
    ap.add_argument("--tag", default="", help="subpasta de saída (vazio = rodada original)")
    ap.add_argument("--pular-validacao", action="store_true")
    a = ap.parse_args()
    lf_grade = [float(x) for x in a.lf.split(",")]
    lp_lo, lp_hi = (float(x) for x in a.lp.split(","))
    lp_grade = [float(x) for x in a.lp_grade.split(",")]
    lf_ref = lf_grade[len(lf_grade) // 2]
    if a.tag:
        SAIDA = SAIDA / a.tag
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    SAIDA.mkdir(parents=True, exist_ok=True)
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    if not a.pular_validacao:
        log.info("1. validação 2D")
        v = validar_2d(p)
        v.to_csv(SAIDA / "validacao_2d.csv", index=False)
        print(v.to_string(index=False))
    log.info("2. estratégias na grade λ_π × λ_fiscal")
    estrategias_grade(p, cfg, choques, lp_grade, lf_grade).to_csv(SAIDA / "estrategias_grade.csv", index=False)
    log.info("3. busca aleatória com λ_fiscal travado em %s e λ_π ~ U(%s; %s)", lf_grade, lp_lo, lp_hi)
    rng = np.random.default_rng(a.seed)
    lp_draw = np.random.default_rng(2027).uniform(lp_lo, lp_hi, 1000)
    combos = {f"r{i:05d}": B.sortear(rng) for i in range(a.n1)}
    combos.update({f"ref_{k}": c for k, c in REF.items() if k not in ("S", "B")})
    d1 = rodar(combos, p, cfg, "P2", choques[:a.N1], lp_draw[:a.N1], a.jobs, lf_grade=lf_grade)
    d1.to_csv(SAIDA / "fase1.csv", index=False)
    piv = d1.pivot_table(index="id", columns="lambda_fiscal", values=["p_bil", "dif_1-16"])
    score = piv["p_bil"].mean(axis=1)
    top = list(score.sort_values(ascending=False).head(60).index)
    lim0 = float(piv[("p_bil", lf_ref)].quantile(0.9))
    top += list(piv[piv[("p_bil", lf_ref)] >= lim0]["dif_1-16"][lf_ref].sort_values(ascending=False).head(30).index)
    top = [t for t in dict.fromkeys(top) if t.startswith("r")]
    filhos = {f"m{j:05d}": B.mutar(combos[top[j % len(top)]], rng, 0.15 if j < a.n2 // 2 else 0.3) for j in range(a.n2)}
    combos.update(filhos)
    d2 = rodar(filhos, p, cfg, "P2", choques[:a.N1], lp_draw[:a.N1], a.jobs, lf_grade=lf_grade)
    d2.to_csv(SAIDA / "fase2.csv", index=False)
    d12 = pd.concat([d1, d2])
    piv = d12.pivot_table(index="id", columns="lambda_fiscal", values=["p_bil", "dif_1-16"])
    piv.columns = [f"{x}_{y}" for x, y in piv.columns]
    piv["p_med"] = piv[[f"p_bil_{x}" for x in lf_grade]].mean(axis=1)
    fin = list(piv.sort_values("p_med", ascending=False).head(a.final // 2).index)
    teto = float(piv[f"p_bil_{lf_ref}"].max())
    for frac in (0.6, 0.7, 0.8, 0.9):   # fronteira sucesso × atividade, relativa ao melhor sucesso encontrado
        sub = piv[piv[f"p_bil_{lf_ref}"] >= frac * teto].sort_values(f"dif_1-16_{lf_ref}", ascending=False)
        fin += list(sub.head(5).index)
    fin += [k for k in combos if k.startswith("ref_")]
    fin = list(dict.fromkeys(fin))
    log.info("fase 3: %d finalistas", len(fin))
    d3 = pd.concat([rodar({i: combos[i] for i in fin}, p, cfg, e, choques, lp_draw, a.jobs, lote=4, lf_grade=lf_grade)
                    for e in ("P1", "P2", "P3_theta05")])
    d3["especificacao"] = d3["especificacao"].str.replace("_theta05", "")
    d3.to_csv(SAIDA / "fase3_finalistas.csv", index=False)
    (SAIDA / "combinacoes.json").write_text(json.dumps(combos), encoding="utf-8")
    (SAIDA / "execucao.json").write_text(json.dumps({"lambda_fiscal": lf_grade,
                                                     "lambda_pi": f"U({lp_lo}; {lp_hi}) por trajetória",
                                                     "seed_lambda_pi": 2027, "n1": a.n1, "n2": a.n2, "N1": a.N1,
                                                     "seed": a.seed, "tetos": B.TETO}), encoding="utf-8")
    log.info("pronto: %s", SAIDA)


if __name__ == "__main__":
    main()
