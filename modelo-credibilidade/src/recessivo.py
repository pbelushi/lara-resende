"""Efeito recessivo das estratégias: PIB, composição do pacote fiscal, setores e emprego.

Módulo sobre o modelo v2.2 calibrado (R_min = US$ 300 bi; choques com seed 42; bootstrap com seed 2026). Não altera a
lógica de sucesso já reportada: os multiplicadores por item do pacote (config/recessivo.yaml) substituem a3 só aqui.

Efeito fiscal em nível: cada item do pacote entra como m · (medida_t − ρ_f · medida_{t−1}), com ρ_f = a1, de modo
que o efeito direto sobre o hiato é m × medida em vigor e o multiplicador acumulado direto é m em qualquer horizonte
(--impulso restaura a forma anterior, m · (−Δmedida)).

1. Atividade agregada: crescimento anual, diferença de produto acumulada contra a referência sem ajuste (S), hiato
   mínimo, probabilidade de recessão técnica, anos com crescimento negativo e taxa de sacrifício, nas janelas 1–8,
   1–16 (eleição de 2030) e 1–40; bootstrap pareado entre estratégias.
2. Composição do pacote (base, qualidade, linear) com multiplicadores centrais, baixos, altos e dependentes do ciclo.
3. Bloco setorial: a variação do hiato contra S é decomposta pelos componentes da demanda, distribuída pela MIP 2015
   (67 atividades → 12 grupos da TRU) e reconciliada com o PIB do modelo macro; emprego pelos coeficientes de 2025.

Uso: python -m src.recessivo [--N 1000] [--R 1000] [--jobs -1] [--sem-fronteira]
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

from . import bootstrap, extrair_mip, modelo, politicas, validacao, varredura

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "outputs" / "v2_2" / "recessivo"
MIPD = RAIZ / "data" / "processed" / "mip"
CONF = yaml.safe_load((RAIZ / "config" / "recessivo.yaml").read_text(encoding="utf-8"))
GUARDAR = ("h", "g", "pi", "d_net", "d_gross") + modelo.DEMANDA
ANO0 = 2026  # t0 = 2026T3: o trimestre 1 é 2026T4; o ano civil 2027 vai de t = 2 a t = 5
ANOS = list(range(2027, 2036))
PI_ALTA = 20.0  # trajetórias com inflação acima de 20% em algum trimestre saem das métricas de produto
FISCAL_NIVEL = {"fiscal_nivel": True, "rho_f": None}  # --impulso troca por {"fiscal_nivel": False}
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------- pacote

def pacote(composicao: str, T: int, multiplicadores: str = "central") -> list[dict]:
    """Itens do pacote (formato de cenarios.yaml + trilha, canal e multiplicador) com o mesmo total do pacote_base."""
    itens = CONF["itens"]
    base = CONF["composicoes"]["pacote_base"]
    rampas = {k: politicas.rampa(v["inicio"], v["rampa"], v["impacto_final"], T) for k, v in base.items()}
    comp = CONF["composicoes"][composicao]
    if composicao == "pacote_base":
        trilhas = rampas
    else:
        total = sum(rampas.values())
        soma = sum(comp.values())
        trilhas = {k: total * v / soma for k, v in comp.items()}
    pos = {"central": None, "baixo": 0, "alto": 1}[multiplicadores]
    return [{"nome": itens[k]["nome"], "chave": k, "tipo": itens[k]["tipo"], "canal": itens[k]["canal"],
             "multiplicador": itens[k]["m"] if pos is None else itens[k]["faixa"][pos], "trilha": tr,
             "impacto_final": float(tr[-1])} for k, tr in trilhas.items()]


def multiplicador_efetivo(pac: list[dict]) -> np.ndarray:
    """Média dos multiplicadores ponderada pelo valor de cada item em vigor em cada trimestre."""
    v = np.array([it["trilha"] for it in pac])
    m = np.array([it["multiplicador"] for it in pac])
    with np.errstate(invalid="ignore"):
        return (m[:, None] * v).sum(axis=0) / v.sum(axis=0)


# ---------------------------------------------------------------------------------------------- simulação

def preparar_espec(p_base: dict, espec: str, extra: dict | None = None) -> dict:
    return modelo.preparar({**copy.deepcopy(p_base), **CONF["especificacoes"][espec], **FISCAL_NIVEL,
                            **(extra or {})})


def simular(p: dict, cfg: dict, est: str, lams, choques: np.ndarray, pac: list[dict] | None) -> dict:
    """Trajetórias (n_λ, N, T + 1) de uma estratégia; o pacote (se houver) entra com os multiplicadores por item."""
    e = CONF["estrategias"][est]
    c = copy.deepcopy(cfg)
    if pac is not None:
        c["pacote_fiscal"] = pac
    cen = varredura.preparar_cenarios(p, c, [e["cenario"]], e["ajustes"])[e["cenario"]]
    lams = np.asarray(lams, dtype=float)
    N = choques.shape[0]
    tr = modelo.simular(p, cen["cen"], np.repeat(lams, N), choques=np.tile(choques, (len(lams), 1, 1)),
                        plano=cen["plano"], guardar=GUARDAR)
    out = {k: v.reshape(len(lams), N, -1) for k, v in tr.items() if k != "ruptura"}
    out["ruptura"] = tr["ruptura"].reshape(len(lams), N)
    out["itens"] = cen["cen"].get("itens", [])
    return out


# ---------------------------------------------------------------------------------------------- atividade

def _log_nivel(g: np.ndarray, g0: float) -> np.ndarray:
    """log do PIB real (t = 0 → 0) e três trimestres anteriores ao t0 pela taxa g0 (para o ano civil de 2026)."""
    lv = np.concatenate([np.zeros(g.shape[:-1] + (1,)), np.cumsum(np.log1p(g[..., 1:] / 400), axis=-1)], axis=-1)
    antes = np.stack([-k * np.log1p(g0 / 400) * np.ones(g.shape[:-1]) for k in (3, 2, 1)], axis=-1)
    return np.concatenate([antes, lv], axis=-1)  # índice 0 = 2026T1, 3 = t0 (2026T3)... posição t + 3


def atividade(tr: dict, trS: dict, p: dict) -> dict:
    """Métricas por trajetória (n_λ, N). Diferença de produto acumulada contra S: Σ (PIB − PIB de S)/PIB de S, em %
    do PIB de um ano (positivo = produto acima de S). O modelo não tem custo de produto da inflação alta: as
    trajetórias com inflação acima de 20% em algum trimestre (da estratégia ou de S) saem das métricas de produto."""
    g0 = p["ini"]["g0"]
    lx, ls = _log_nivel(tr["g"], g0), _log_nivel(trS["g"], g0)
    razao = np.exp(lx - ls)[..., 3:] - 1  # t = 0..T
    explosiva = tr["ruptura"] >= 0
    inf_alta = explosiva_ou_alta(tr)
    valida = ~inf_alta & ~explosiva_ou_alta(trS)
    m = {"explosiva": explosiva, "inflacao_alta": inf_alta, "valida": valida}
    g = tr["g"]
    for jan, (a, b) in CONF["janelas"].items():
        m[f"dif_{jan}"] = 100 * razao[..., a:b + 1].sum(axis=-1) / 4
        neg = g < 0
        dois = neg[..., a:b + 1] & neg[..., a - 1:b]
        # trajetória explosiva conta como recessão na janela em que rompe
        rompe = explosiva & (tr["ruptura"] <= b)
        m[f"recessao_{jan}"] = np.where(rompe, True, np.nan_to_num(dois, nan=0).astype(bool).any(axis=-1))
        h = tr["h"][..., a:b + 1]
        m[f"hiato_min_{jan}"] = np.nanmin(h, axis=-1)
        m[f"trim_hiato_min_{jan}"] = np.nanargmin(np.where(np.isnan(h), np.inf, h), axis=-1) + a
    # crescimento por ano civil: média dos níveis trimestrais do ano sobre a do ano anterior
    anual = []
    for ano in [ANO0] + ANOS:
        ini = 4 * (ano - ANO0)  # 2026 → posições 0..3 (2026T1..T4); 2027 → 4..7
        anual.append(np.exp(lx[..., ini:ini + 4]).mean(axis=-1))
    anual = np.stack(anual, axis=-1)
    cresc = 100 * (anual[..., 1:] / anual[..., :-1] - 1)
    m["cresc_anual"] = cresc  # (n_λ, N, 9)
    m["anos_negativos"] = (cresc < 0).sum(axis=-1).astype(float)
    queda = np.nanmean(tr["pi"][..., 1:5], axis=-1) - np.nanmean(tr["pi"][..., 9:17], axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        m["sacrificio"] = np.where(queda > 0.05, -m["dif_1-16"] / queda, np.nan)
    return m


def explosiva_ou_alta(tr: dict) -> np.ndarray:
    """Ruptura (π > 50%) ou inflação acima de PI_ALTA em algum trimestre."""
    pi = np.where(np.isnan(tr["pi"]), np.inf, tr["pi"])[..., 1:]
    return (tr["ruptura"] >= 0) | (pi.max(axis=-1) > PI_ALTA)


def resumo(m: dict, est: str, espec: str, lams) -> list[dict]:
    """Mediana, faixa 10–90% e média por λ; métricas de atividade só sobre trajetórias não explosivas."""
    linhas = []
    for i, lam in enumerate(lams):
        v = m["valida"][i]
        base = {"estrategia": est, "especificacao": espec, "lambda": lam,
                "fracao_explosiva": float(m["explosiva"][i].mean()),
                "fracao_inflacao_alta": float(m["inflacao_alta"][i].mean())}
        for jan in CONF["janelas"]:
            r = {**base, "janela": jan}
            for k in ("dif", "hiato_min", "trim_hiato_min"):
                x = m[f"{k}_{jan}"][i][v]
                r.update({f"{k}_mediana": np.nanmedian(x) if x.size else np.nan,
                          f"{k}_p10": np.nanpercentile(x, 10) if x.size else np.nan,
                          f"{k}_p90": np.nanpercentile(x, 90) if x.size else np.nan,
                          f"{k}_media": np.nanmean(x) if x.size else np.nan})
            r["p_recessao_todas"] = float(m[f"recessao_{jan}"][i].mean())
            r["p_recessao_nao_explosivas"] = float(m[f"recessao_{jan}"][i][v].mean()) if v.any() else np.nan
            if jan == "1-40":
                x = m["anos_negativos"][i][v]
                r.update({"anos_negativos_media": np.nanmean(x), "anos_negativos_mediana": np.nanmedian(x)})
                s = m["sacrificio"][i][v]
                r.update({"sacrificio_mediana": np.nanmedian(s) if np.isfinite(s).any() else np.nan,
                          "sacrificio_validas": float(np.isfinite(s).mean())})
            linhas.append(r)
    return linhas


def crescimento(m: dict, est: str, espec: str, lams) -> list[dict]:
    linhas = []
    for i, lam in enumerate(lams):
        x = m["cresc_anual"][i][m["valida"][i]]
        for j, ano in enumerate(ANOS):
            c = x[:, j]
            linhas.append({"estrategia": est, "especificacao": espec, "lambda": lam, "ano": ano,
                           "mediana": np.nanmedian(c), "p10": np.nanpercentile(c, 10), "p90": np.nanpercentile(c, 90),
                           "media": np.nanmean(c)})
    return linhas


def _media_rep(x: np.ndarray, idx: np.ndarray) -> np.ndarray:
    return np.nanmean(x[idx], axis=1)


def comparar(ms: dict, espec: str, lams, idx: np.ndarray) -> list[dict]:
    """Diferenças pareadas (x − ref) da diferença de produto acumulada e de P(recessão), IC de 95% pelos mesmos
    índices."""
    pares = [tuple(x) for x in CONF["pares"]] + [(e, "S") for e in ms if e != "S"]
    linhas = []
    for x, ref in pares:
        for i, lam in enumerate(lams):
            v = ms[x]["valida"][i] & ms[ref]["valida"][i]
            for jan in CONF["janelas"]:
                for k in ("dif", "recessao"):
                    a = ms[x][f"{k}_{jan}"][i].astype(float)
                    b = np.zeros_like(a) if (ref == "S" and k == "dif") else ms[ref][f"{k}_{jan}"][i].astype(float)
                    d = np.where(v, a - b, np.nan) if k == "dif" else a - b
                    if k == "recessao":
                        d = 100 * d
                    rep = _media_rep(d, idx)
                    linhas.append({"especificacao": espec, "lambda": lam, "janela": jan, "metrica": k,
                                   "par": f"{x} − {ref}", "estimativa": float(np.nanmean(d)),
                                   "ic_lo": float(np.nanpercentile(rep, 2.5)),
                                   "ic_hi": float(np.nanpercentile(rep, 97.5))})
    return linhas


# ---------------------------------------------------------------------------------------------- setorial

class Matriz:
    """MIP 2015 (67 atividades), vetores dos canais e coeficientes de emprego de 2025."""

    def __init__(self):
        self.ativ = pd.read_csv(MIPD / "atividades_67.csv", dtype={"codigo": str}).set_index("codigo")
        self.L = np.load(MIPD / "L_tipo1.npy")
        self.L2 = np.load(MIPD / "L_tipo2.npy")
        f = pd.read_csv(MIPD / "demanda_final_2015.csv", dtype={"codigo": str}).set_index("codigo")
        pn = pd.read_csv(MIPD / "pnad_67.csv", dtype={"codigo": str}).set_index("codigo").loc[self.ativ.index]
        pc = pd.read_csv(MIPD / "pnad_coeficientes.csv").set_index("grupo")
        er = pd.read_csv(MIPD / "emprego_renda_setores.csv").set_index("grupo")
        self.grupo = self.ativ["grupo"].to_numpy()
        self.vbp = self.ativ["vbp_2015"].to_numpy()
        self.va_coef = (self.ativ["va_2015"] / self.ativ["vbp_2015"]).to_numpy()
        self.va_total = float(self.ativ["va_2015"].sum())
        self.ocup25 = pn["ocupados_2025_mil"].to_numpy()
        self.formal = pn["fracao_formal"].to_numpy()
        self.rend = pn["rendimento_medio_mensal"].to_numpy()
        self.ir = pc["ir_efetivo"].reindex(self.grupo).to_numpy()
        self.prev_sal = (er["prev_2015"] / er["sal_2015"]).reindex(self.grupo).to_numpy()
        self.m_int = pd.read_csv(MIPD / "importacoes_insumos_2015.csv", dtype={"codigo": str}).set_index(
            "codigo").loc[self.ativ.index, "insumos_importados_por_vbp"].to_numpy()
        self.m_final = pd.read_csv(MIPD / "importacoes_demanda_final_2015.csv").set_index("componente")[
            "parcela_importada"].to_dict()
        unit = lambda cod: (self.ativ.index == cod).astype(float)  # noqa: E731
        norm = lambda x: x / x.sum()  # noqa: E731
        self.vetores = {k: norm(f[k].clip(lower=0).to_numpy()) for k in ("familias", "fbcf", "governo", "exportacao")}
        self.vetores["absorcao"] = norm(f[["familias", "fbcf", "governo", "isflsf"]].sum(axis=1).clip(lower=0).to_numpy())
        self.vetores["construcao"] = unit("4180")
        self.vetores["maquinas"] = norm(unit("2800") + unit("2700") + 0.5 * unit("2991"))
        # parcela importada da demanda final de cada vetor (para o efeito sobre a balança comercial)
        self.imp_vetor = {"familias": self.m_final["familias"], "fbcf": self.m_final["fbcf"],
                          "governo": self.m_final["governo"], "exportacao": 0.0,
                          "absorcao": self.m_final["familias"], "construcao": 0.0, "maquinas": self.m_final["fbcf"]}

    def vetor(self, mix: dict) -> np.ndarray:
        return sum(w * self.vetores[k] for k, w in mix.items())


def _mix_canal(canal: str) -> dict:
    return CONF["canais"][canal]


def componentes_hiato(tr: dict, p: dict, itens: list[dict]) -> dict:
    """Contribuição acumulada de cada componente ao hiato: C_t = a1 C_{t−1} + termo_t, por canal de demanda.
    O resto (condição inicial, guardas numéricas) fica em 'outros'."""
    a1 = p["a1"]
    T1 = tr["h"].shape[-1]
    termos = {k: tr[k] for k in ("dem_juro", "dem_capex", "dem_cambio", "dem_choque", "dem_fiscal_resto")}
    for k, it in enumerate(itens):
        nome = f"item:{it['canal']}"
        termos[nome] = termos.get(nome, 0) + tr[f"dem_item{k}"]
    C = {}
    for k, x in termos.items():
        x = np.nan_to_num(x)
        c = np.zeros_like(x)
        for t in range(1, T1):
            c[..., t] = a1 * c[..., t - 1] + x[..., t]
        C[k] = c
    return C


def setorial(dC: dict, dh: np.ndarray, mat: Matriz) -> dict:
    """Distribui a variação média dos componentes (n_T,) pela matriz e reconcilia o VA com o PIB do modelo macro.

    dC: {componente: Δ contribuição ao hiato (% do PIB) por trimestre}; dh: Δ hiato total por trimestre.
    Devolve, por trimestre, ΔVBP e ΔVA por atividade (R$ milhões de 2015, reconciliados), o fator de escala e os
    empregos (mil) pelos tipos I reconciliado, I e II sem reconciliação."""
    pib = CONF["pib_2015"]
    nT = dh.shape[0]
    n = mat.L.shape[0]
    dF = np.zeros((nT, n))
    dF_exp = np.zeros((nT, n))
    imp_final = np.zeros(nT)
    soma_comp = np.zeros(nT)
    macro_abs = np.zeros(nT)   # Σ |contribuição de cada componente| (VA do modelo macro)
    matriz_abs = np.zeros(nT)  # Σ |VA da matriz de cada componente|
    for k, x in dC.items():
        mix = _mix_canal(k.split(":", 1)[1]) if k.startswith("item:") else CONF["componentes_macro"][k]
        v = mat.vetor(mix)
        dFk = np.outer(x / 100 * pib, v)
        dF += dFk
        macro_abs += np.abs(x / 100 * mat.va_total)
        matriz_abs += np.abs((dFk @ mat.L.T * mat.va_coef).sum(axis=1))
        if k == "dem_cambio":
            dF_exp += np.outer(x / 100 * pib, v)
        imp_final += x / 100 * pib * sum(w * mat.imp_vetor[c] / (1 - mat.imp_vetor[c]) for c, w in mix.items())
        soma_comp += x
    outros = dh - soma_comp
    v = mat.vetor(CONF["componentes_macro"]["outros"])
    dF += np.outer(outros / 100 * pib, v)
    dX1 = dF @ mat.L.T
    dX2 = dF @ mat.L2.T
    dVA = dX1 * mat.va_coef
    alvo = dh / 100 * mat.va_total
    soma = dVA.sum(axis=1)
    # reconciliação aditiva: o resíduo entre o PIB do modelo macro e o VA da matriz entra como demanda de absorção
    # doméstica. A escala proporcional falha quando componentes de sinais opostos (pacote × juro) se cancelam e a soma
    # da matriz fica perto de zero; a razão macro/matriz continua reportada como diagnóstico (soma(alvo)/soma(VA)).
    u = mat.L @ mat.vetores["absorcao"]
    va_u = float((u * mat.va_coef).sum())
    dX1c = dX1 + np.outer((alvo - soma) / va_u, u)
    emp = lambda dX: dX / mat.vbp * mat.ocup25  # noqa: E731
    return {"dVA": dX1c * mat.va_coef, "dX": dX1c, "alvo": alvo, "va_matriz": soma, "macro_abs": macro_abs,
            "matriz_abs": matriz_abs,
            "emp1": emp(dX1c), "emp1_bruto": emp(dX1), "emp2_bruto": emp(dX2),
            "dVA_exp": (dF_exp @ mat.L.T) * mat.va_coef,
            "imp": dX1c @ mat.m_int + imp_final, "exp": dF_exp.sum(axis=1)}


def tabelas_setoriais(st: dict, mat: Matriz, dh: np.ndarray, p: dict, okun: dict, est: str, espec: str,
                      lam: float) -> tuple[list[dict], list[dict], dict]:
    """Médias por janela: VA e emprego por grupo, retorno fiscal e desocupação."""
    va_g = pd.Series(mat.ativ["va_2015"].to_numpy()).groupby(mat.grupo).sum()
    l_va, l_emp = [], []
    diag = {}
    for jan, (a, b) in CONF["janelas"].items():
        sl = slice(a, b + 1)
        dva = pd.Series(st["dVA"][sl].mean(axis=0)).groupby(mat.grupo).sum()
        dva_exp = pd.Series(st["dVA_exp"][sl].mean(axis=0)).groupby(mat.grupo).sum()
        e1 = st["emp1"][sl].mean(axis=0)
        e1b, e2b = st["emp1_bruto"][sl].mean(axis=0), st["emp2_bruto"][sl].mean(axis=0)
        form = e1 * mat.formal
        massa = e1 * 1000 * mat.rend * 12 / 1e9          # R$ bi por ano (rendimento habitual de 2025)
        massa_f = form * 1000 * mat.rend * 12 / 1e9
        contrib = massa_f * mat.prev_sal
        ir = massa_f * mat.ir
        G = lambda x: pd.Series(x).groupby(mat.grupo).sum()  # noqa: E731
        for g in sorted(set(mat.grupo)):
            l_va.append({"estrategia": est, "especificacao": espec, "lambda": lam, "janela": jan, "grupo": g,
                         "grupo_nome": extrair_mip.GRUPOS[g], "dVA_rs_mi_2015": dva[g],
                         "dVA_pct_do_setor": 100 * dva[g] / va_g[g], "dVA_exportacoes_rs_mi_2015": dva_exp[g]})
            l_emp.append({"estrategia": est, "especificacao": espec, "lambda": lam, "janela": jan, "grupo": g,
                          "grupo_nome": extrair_mip.GRUPOS[g], "ocupacoes_mil": G(e1)[g],
                          "formais_mil": G(form)[g], "informais_mil": G(e1 - form)[g],
                          "massa_salarial_rs_bi_ano": G(massa)[g], "tipo1_sem_reconciliar_mil": G(e1b)[g],
                          "tipo2_sem_reconciliar_mil": G(e2b)[g], "induzido_tipo2_mil": G(e2b - e1b)[g]})
        dhm = float(np.mean(dh[sl]))
        # receita cíclica do modelo macro: rec_base (% do PIB) × ε_rec × Δhiato, em R$ bi do PIB anual de t0
        rec_ciclica = p["rec_base"] / 100 * p["eps_rec"] * dhm / 100 * p["ini"]["Y0"]
        # fator de escala por componente (VA do modelo macro ÷ VA da matriz, somando os componentes em módulo): mede a
        # coerência entre os multiplicadores do bloco fiscal e os da matriz sem a instabilidade de quando componentes
        # de sinais opostos se cancelam; o fator total (soma com sinal) fica ao lado
        soma_va = float(st["va_matriz"][sl].sum())
        diag[jan] = {"fator_escala": float(st["macro_abs"][sl].sum() / st["matriz_abs"][sl].sum()),
                     "fator_escala_total": float(st["alvo"][sl].sum() / soma_va) if abs(soma_va) > 1e-9 else np.nan,
                     "dh_medio": dhm, "desocupacao_pp": okun["beta"] * dhm,
                     "desocupacao_ic_lo": min(okun["ic_lo"] * dhm, okun["ic_hi"] * dhm),
                     "desocupacao_ic_hi": max(okun["ic_lo"] * dhm, okun["ic_hi"] * dhm),
                     "contrib_prev_rs_bi": float(contrib.sum()), "ir_rs_bi": float(ir.sum()),
                     "receita_ciclica_macro_rs_bi": rec_ciclica,
                     "exportacoes_pct_pib": float(st["exp"][sl].mean() / CONF["pib_2015"] * 100),
                     "importacoes_pct_pib": float(st["imp"][sl].mean() / CONF["pib_2015"] * 100)}
    return l_va, l_emp, diag


def rodar_espec(p_base: dict, cfg: dict, espec: str, choques: np.ndarray, idx: np.ndarray, fronteira: bool,
                okun: dict) -> dict:
    """Estratégias com pacote_base central, composições e fronteira de uma especificação."""
    lams = CONF["lambdas"]
    T = cfg["horizonte"]
    p = preparar_espec(p_base, espec)
    mat = Matriz()
    base = pacote("pacote_base", T)
    trs, ms = {}, {}
    for est in CONF["estrategias"]:
        trs[est] = simular(p, cfg, est, lams, choques, base)
    for est in trs:
        ms[est] = atividade(trs[est], trs["S"], p)
    out = {"resumo": [], "cresc": [], "boot": comparar(ms, espec, lams, idx), "va": [], "emp": [], "diag": [],
           "comp": [], "boot_comp": [], "fronteira": [], "decomp": [],
           "cred": sensibilidade_credibilidade(p_base, cfg, espec, choques, idx)}
    for est in ms:
        out["resumo"] += resumo(ms[est], est, espec, lams)
        out["cresc"] += crescimento(ms[est], est, espec, lams)
    # setorial: média das trajetórias válidas (o mapeamento é linear) da diferença contra S
    CS = componentes_hiato(trs["S"], p, trs["S"]["itens"])
    for est in ms:
        if est == "S":
            continue
        C = componentes_hiato(trs[est], p, trs[est]["itens"])
        for i, lam in enumerate(lams):
            v = ms[est]["valida"][i]
            if not v.any():
                continue
            dC = {}
            for k in set(C) | set(CS):
                a = C.get(k, np.zeros_like(trs[est]["h"]))[i][v]
                b = CS.get(k, np.zeros_like(trs["S"]["h"]))[i][v]
                dC[k] = (a - b).mean(axis=0)
            dh = (trs[est]["h"][i][v] - trs["S"]["h"][i][v]).mean(axis=0)
            for jan, (a, b) in CONF["janelas"].items():
                linha = {"estrategia": est, "especificacao": espec, "lambda": lam, "janela": jan,
                         "dh_total": float(dh[a:b + 1].mean())}
                for k, x in dC.items():
                    linha[k] = float(x[a:b + 1].mean())
                linha["pacote_direto"] = sum(v for k, v in linha.items() if k.startswith("item:"))
                linha["outros"] = linha["dh_total"] - sum(float(x[a:b + 1].mean()) for x in dC.values())
                out["decomp"].append(linha)
            st = setorial(dC, dh, mat)
            lv, le, dg = tabelas_setoriais(st, mat, dh, p, okun, est, espec, lam)
            out["va"] += lv
            out["emp"] += le
            out["diag"] += [{"estrategia": est, "especificacao": espec, "lambda": lam, "janela": j, **d}
                            for j, d in dg.items()]
    # composição do pacote
    for comp in CONF["composicoes"]:
        for mult, ciclo in (("central", False), ("central", True), ("baixo", False), ("alto", False)):
            pac = pacote(comp, T, mult)
            q = preparar_espec(p_base, espec, {"gamma_ciclo": CONF["gamma_ciclo"] if ciclo else 0.0})
            m_ef = multiplicador_efetivo(pac)
            mc = {}
            trS = trs["S"]  # S não tem pacote: γ não o afeta
            for est in ("A", "C", "C_sem_piso"):
                tr = trs[est] if (comp == "pacote_base" and mult == "central" and not ciclo) else simular(
                    q, cfg, est, lams, choques, pac)
                mc[est] = atividade(tr, trS, q)
                for r in resumo(mc[est], est, espec, lams):
                    out["comp"].append({"composicao": comp, "multiplicadores": mult, "ciclo": ciclo,
                                        "mult_efetivo_medio": float(np.nanmean(m_ef[1:])), **r})
            out.setdefault("_mc", {})[(comp, mult, ciclo)] = mc
    for mult, ciclo in (("central", False), ("central", True), ("baixo", False), ("alto", False)):
        q_, l_ = out["_mc"][("pacote_qualidade", mult, ciclo)], out["_mc"][("pacote_linear", mult, ciclo)]
        for est in q_:
            for i, lam in enumerate(lams):
                v = q_[est]["valida"][i] & l_[est]["valida"][i]
                for jan in CONF["janelas"]:
                    d = np.where(v, q_[est][f"dif_{jan}"][i] - l_[est][f"dif_{jan}"][i], np.nan)
                    rep = _media_rep(d, idx)
                    out["boot_comp"].append({"especificacao": espec, "estrategia": est, "lambda": lam,
                                             "janela": jan, "multiplicadores": mult, "ciclo": ciclo,
                                             "qualidade_menos_linear": float(np.nanmean(d)),
                                             "ic_lo": float(np.nanpercentile(rep, 2.5)),
                                             "ic_hi": float(np.nanpercentile(rep, 97.5))})
    del out["_mc"]
    # fronteira: λ*₇₀ pela dívida líquida (banda e teto) com o pacote_base central
    if fronteira:
        grade = varredura.grade_lambda(0.01)
        c = copy.deepcopy(cfg)
        c["pacote_fiscal"] = base
        for est, e in CONF["estrategias"].items():
            cens = varredura.preparar_cenarios(p, c if est != "S" else cfg, [e["cenario"]], e["ajustes"])
            _, oks, _ = varredura.diagonal(p, cens, grade, choques, trajetorias=True)
            linha = {"estrategia": est, "especificacao": espec}
            for suf, nome in (("_liq_bil", "banda"), ("_liq", "teto")):
                P = oks[suf][e["cenario"]].mean(axis=1)
                ls = bootstrap._lambda_star(P[None, :], grade, 0.7)[0]
                linha[f"lambda70_liq_{nome}"] = float(ls)
                linha[f"pmax_liq_{nome}"] = float(P.max())
            out["fronteira"].append(linha)
    return out


def multiplicadores_efetivos(p_base: dict, cfg: dict, lam: float = 0.7) -> pd.DataFrame:
    """Multiplicador acumulado de cada item: −Σ Δhiato ÷ Σ medida, para uma medida permanente de 1% do PIB desde o
    trimestre 1 (estratégia A só com esse item, determinística, contra S), em 4, 8 e 16 trimestres. "Direto" acumula
    só o termo do item com a persistência a1 (= m pela calibração de ρ_f); "modelo" inclui a resposta da Selic, do
    prêmio, do juro longo e do câmbio."""
    T = cfg["horizonte"]
    linhas = []
    degrau = np.where(np.arange(T + 1) >= 1, 1.0, 0.0)
    for espec in CONF["especificacoes"]:
        p = preparar_espec(p_base, espec)
        ref = simular(p, cfg, "S", [lam], np.zeros((1, T, 4)), None)
        for k, it in CONF["itens"].items():
            pac = [{"nome": it["nome"], "chave": k, "tipo": it["tipo"], "canal": it["canal"],
                    "multiplicador": it["m"], "trilha": degrau, "impacto_final": 1.0}]
            tr = simular(p, cfg, "A", [lam], np.zeros((1, T, 4)), pac)
            dh = (tr["h"] - ref["h"])[0, 0]
            direto = componentes_hiato(tr, p, tr["itens"])[f"item:{it['canal']}"][0, 0]
            linha = {"especificacao": espec, "item": k, "nome": it["nome"], "m": it["m"], "lambda": lam,
                     "rho_f": p["a1"] if p["rho_f"] is None else p["rho_f"]}
            for H in (4, 8, 16):
                linha[f"direto_{H}"] = float(-direto[1:H + 1].sum() / degrau[1:H + 1].sum())
                linha[f"modelo_{H}"] = float(-dh[1:H + 1].sum() / degrau[1:H + 1].sum())
            linhas.append(linha)
    return pd.DataFrame(linhas)


COMBOS_CRED = {"base": {}, "p1_p2_metade": {"_metade": True}, "a2_005": {"a2": 0.05}, "a2_030": {"a2": 0.30},
               "p_metade_a2_005": {"_metade": True, "a2": 0.05}, "p_metade_a2_030": {"_metade": True, "a2": 0.30}}


def sensibilidade_credibilidade(p_base: dict, cfg: dict, espec: str, choques: np.ndarray, idx: np.ndarray) -> list[dict]:
    """S e A com a sensibilidade do prêmio à dívida (p1, p2 e p2 de P3) pela metade e a2 nos limites da faixa."""
    lams = CONF["lambdas"]
    base = pacote("pacote_base", cfg["horizonte"])
    linhas = []
    for nome, c in COMBOS_CRED.items():
        extra = {k: v for k, v in c.items() if not k.startswith("_")}
        if c.get("_metade"):
            extra.update({k: p_base[k] / 2 for k in ("p1", "p2", "p2_p3")})
        p = preparar_espec(p_base, espec, extra)
        trS = simular(p, cfg, "S", lams, choques, None)
        trA = simular(p, cfg, "A", lams, choques, base)
        m = atividade(trA, trS, p)
        for i, lam in enumerate(lams):
            v = m["valida"][i]
            for jan in CONF["janelas"]:
                x = m[f"dif_{jan}"][i]
                rp = _media_rep(np.where(v, x, np.nan), idx)
                linhas.append({"especificacao": espec, "combinacao": nome, "a2": p["a2"], "p1": p["p1"],
                               "p2": p["p2"], "lambda": lam, "janela": jan,
                               "dif_mediana": float(np.nanmedian(x[v])) if v.any() else np.nan,
                               "dif_media": float(np.nanmean(x[v])) if v.any() else np.nan,
                               "ic_lo": float(np.nanpercentile(rp, 2.5)), "ic_hi": float(np.nanpercentile(rp, 97.5)),
                               "fracao_A_abaixo_de_S": float((x[v] < 0).mean()) if v.any() else np.nan,
                               "fracao_inflacao_alta": float(m["inflacao_alta"][i].mean())})
    return linhas


# ---------------------------------------------------------------------------------------------- relatório

def fm(x, nd=1) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def ic(r, nd=1, est="estimativa") -> str:
    s = f"{fm(r[est], nd)} [{fm(r['ic_lo'], nd)}; {fm(r['ic_hi'], nd)}]"
    return s + (" *" if (r["ic_lo"] > 0 or r["ic_hi"] < 0) else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=1000)
    ap.add_argument("--R", type=int, default=1000)
    ap.add_argument("--jobs", type=int, default=-1)
    ap.add_argument("--sem-fronteira", action="store_true")
    ap.add_argument("--impulso", action="store_true", help="efeito fiscal pelo impulso (forma anterior)")
    a = ap.parse_args()
    if a.impulso:
        FISCAL_NIVEL.clear()
        FISCAL_NIVEL["fiscal_nivel"] = False
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)[:a.N]  # mesmos choques da rodada principal
    idx = bootstrap.indices(a.N, a.R, 2026)
    okun = pd.read_csv(MIPD / "okun.csv").iloc[0].to_dict()
    res = Parallel(n_jobs=a.jobs)(delayed(rodar_espec)(p, cfg, e, choques, idx, not a.sem_fronteira, okun)
                                  for e in CONF["especificacoes"])
    junta = lambda k: pd.DataFrame([x for r in res for x in r[k]])  # noqa: E731
    tabs = {"atividade_agregada": junta("resumo"), "crescimento_anual": junta("cresc"),
            "bootstrap_atividade": junta("boot"), "composicao_pacote": junta("comp"),
            "bootstrap_composicao": junta("boot_comp"), "setorial_va": junta("va"), "setorial_emprego": junta("emp"),
            "setorial_diagnostico": junta("diag"), "fronteira": junta("fronteira"),
            "decomposicao_hiato": junta("decomp"), "sensibilidade_credibilidade": junta("cred")}
    for k, df in tabs.items():
        df.to_csv(SAIDA / f"{k}.csv", index=False)
    multiplicadores_efetivos(p, cfg).to_csv(SAIDA / "multiplicadores_efetivos.csv", index=False)
    val, dec = validacao.validar_recessao_2015(p)
    val.to_csv(SAIDA / "validacao_2015_2016.csv", index=False)
    dec.to_csv(SAIDA / "validacao_2015_2016_decomposicao.csv", index=False)
    pc = pd.read_csv(MIPD / "pnad_coeficientes.csv")
    sid = pd.read_csv(MIPD / "sidra_tabelas.csv")
    pc.to_csv(SAIDA / "pnad_coeficientes.csv", index=False)
    sid.to_csv(SAIDA / "pnad_coeficientes_tabelas_sidra.csv", index=False)
    (SAIDA / "execucao.json").write_text(json.dumps({"N": a.N, "R": a.R, "seed_choques": 42, "seed_bootstrap": 2026,
                                                     "fiscal_nivel": bool(FISCAL_NIVEL.get("fiscal_nivel"))},
                                                    indent=1), encoding="utf-8")
    log.info("pronto: %s", SAIDA)


if __name__ == "__main__":
    main()
