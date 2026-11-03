"""Estimação de b3 (repasse cambial) e ω (fração do prêmio que passa pela Selic) — Tarefa 3 da v2.2.

b3: projeções locais (Jordà) mensais do repasse acumulado ERPT_h = β_h/δ_h, em OLS e 2SLS (instrumentos:
variação do dólar amplo e do VIX), com IC por bootstrap em blocos; b3 do modelo é calibrado por especificação
casando o repasse acumulado simulado em 4 trimestres com ERPT_12.
ω: regra de Taylor com prêmio estimada por mínimos quadrados não lineares (HAC) e, como robustez, 2SLS
linear com instrumentos defasados; verificação cruzada pelo canal do juro longo.
"""
from __future__ import annotations

import copy
import io
import logging

import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
from scipy.optimize import brentq, least_squares

from . import dados, modelo, politicas
from .dados import PROC, RAW

log = logging.getLogger(__name__)

SERIES_EST = {
    "ipca_m": (433, ["ipca"], "mensal"),
    "ipca_comerc_m": (4447, ["ipca", "comercializaveis"], "mensal"),
    "ipca_livres_m": (11428, ["ipca", "itens livres"], "mensal"),
    "cambio_m": (3698, ["cambio", "venda", "media de periodo"], "mensal"),
    # IC-Br em US$: a versão em reais (27574) contém o próprio câmbio e absorveria o repasse
    "icbr": (29042, ["indice de commodities - brasil", "dolares"], "mensal"),
    "meta_inflacao": (13521, ["meta para a inflacao"], "anual"),
    "meta_selic": (432, ["meta selic"], "diaria"),
}
FONTES_EXTERNAS = {
    "dolar_amplo": "FRED DTWEXBGS (Nominal Broad U.S. Dollar Index, 2006–), encadeado com DTWEXB (1995–2019) "
                   "antes de 2006; proxy do DXY, que não é publicado em fonte aberta",
    "vix": "FRED VIXCLS (CBOE VIX)",
    "embi": "Ipeadata JPM366_EMBI366 (EMBI+ Brasil, J.P. Morgan; série inativa, termina em jul/2024)",
}
INICIO = "2004-01-01"
HORIZONTES = list(range(0, 25))


# ---------------------------------------------------------------- dados

def _fred(serie: str, offline: bool) -> pd.Series:
    arq = RAW / f"fred_{serie}.csv"
    if not (offline and arq.exists()):
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}", timeout=120)
        r.raise_for_status()
        arq.write_bytes(r.content)
    df = pd.read_csv(arq)
    return pd.Series(pd.to_numeric(df.iloc[:, 1], errors="coerce").values,
                     index=pd.to_datetime(df.iloc[:, 0]), name=serie).dropna()


def _ipea(codigo: str, offline: bool) -> pd.Series:
    arq = RAW / f"ipea_{codigo}.csv"
    if not (offline and arq.exists()):
        r = requests.get(f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{codigo}')", timeout=120)
        r.raise_for_status()
        v = r.json()["value"]
        pd.DataFrame({"data": [x["VALDATA"][:10] for x in v], "valor": [x["VALVALOR"] for x in v]}).to_csv(arq, index=False)
    df = pd.read_csv(arq, parse_dates=["data"])
    return df.set_index("data")["valor"].astype(float).dropna()


def validar(offline: bool = False) -> pd.DataFrame:
    """Valida os códigos SGS; falha explícita (RuntimeError) se algum não existir ou não conferir."""
    if offline:
        return pd.DataFrame()
    v = dados.validar_codigos(SERIES_EST)
    ruins = v[~v["ok"]]
    if len(ruins):
        raise RuntimeError("séries SGS inválidas para a estimação: "
                           + "; ".join(f"{r.codigo} ({r.serie}): {r.erro}" for r in ruins.itertuples()))
    return v


def painel_mensal(offline: bool = False) -> pd.DataFrame:
    """Painel mensal 2004– com preços, câmbio, controles, instrumentos, juros e prêmio."""
    s = {nome: dados.baixar_sgs(cod, INICIO, offline=offline) for nome, (cod, _, _) in SERIES_EST.items()}
    m = pd.DataFrame(index=pd.date_range(INICIO, s["ipca_m"].index.max(), freq="MS"))
    for k in ("ipca_m", "ipca_comerc_m", "ipca_livres_m", "cambio_m", "icbr"):
        m[k] = s[k].resample("MS").last()
    for k in ("ipca", "ipca_comerc", "ipca_livres"):
        m[f"p_{k}"] = 100 * np.log((1 + m[f"{k}_m"] / 100).cumprod())   # log do nível × 100
    m["pi_m"] = m["ipca_m"]
    m["e"] = 100 * np.log(m["cambio_m"])
    m["de"] = m["e"].diff()
    m["dicbr"] = 100 * np.log(m["icbr"]).diff()
    m["selic"] = s["meta_selic"].resample("MS").last()
    # meta de inflação 12 meses à frente: interpolação entre a meta do ano e a do ano seguinte
    meta = s["meta_inflacao"].groupby(s["meta_inflacao"].index.year).last()
    anos = m.index.year
    frac = (m.index.month - 1) / 12
    m["meta_12m"] = [(1 - f) * meta.get(a, np.nan) + f * meta.get(a + 1, meta.get(a, np.nan)) for a, f in zip(anos, frac)]
    focus = pd.read_csv(RAW / "focus_ipca12m.csv", index_col=0, parse_dates=True).iloc[:, 0]
    m["pi_e"] = focus.resample("MS").mean()
    m["desvio_focus"] = m["pi_e"] - m["meta_12m"]
    tri = pd.read_csv(PROC / "trimestral.csv", index_col=0, parse_dates=True)
    h = tri["h"].dropna()
    h.index = h.index.to_period("Q").to_timestamp(how="start") + pd.DateOffset(months=1)  # meio do trimestre
    m["hiato"] = h.reindex(m.index.union(h.index)).interpolate("time").reindex(m.index)
    # instrumentos externos
    novo, velho = _fred("DTWEXBGS", offline), _fred("DTWEXB", offline)
    novo_m, velho_m = novo.resample("MS").mean(), velho.resample("MS").mean()
    base = novo_m.index.min()
    encad = pd.concat([velho_m[velho_m.index < base] * novo_m.iloc[0] / velho_m.loc[base], novo_m])
    m["dolar"] = 100 * np.log(encad).reindex(m.index)
    m["ddolar"] = m["dolar"].diff()
    m["vix"] = _fred("VIXCLS", offline).resample("MS").mean().reindex(m.index)
    m["dvix"] = 100 * np.log(m["vix"]).diff()
    m["embi"] = _ipea("JPM366_EMBI366", offline).resample("MS").mean().reindex(m.index) / 100  # p.p.
    ntnb = pd.read_csv(RAW / "tesouro_direto_taxas.csv", parse_dates=["base", "venc"])
    ntnb = ntnb[ntnb["classe"] == "ntnb"].assign(anos=lambda d: (d["venc"] - d["base"]).dt.days / 365.25)
    idx = ntnb.assign(dist=(ntnb["anos"] - 10).abs()).groupby("base")["dist"].idxmin()
    m["ntnb10"] = ntnb.loc[idx].set_index("base")["taxa"].resample("MS").mean().reindex(m.index)
    anuais = pd.read_csv(RAW / "focus_anuais_historico.csv", parse_dates=["Data"])
    sel = anuais[anuais["Indicador"] == "Selic"]
    sel = sel.assign(alvo=sel["DataReferencia"].astype(int) == sel["Data"].dt.year + 1)
    m["selic_esperada"] = sel[sel["alvo"]].set_index("Data")["Mediana"].resample("MS").mean().reindex(m.index)
    m["d2020"] = (m.index.year == 2020).astype(float)
    return m


# ---------------------------------------------------------------- projeções locais

def _controles(m: pd.DataFrame, lags: int = 12) -> pd.DataFrame:
    """12 defasagens da inflação mensal; hiato e desvio do Focus defasados (o Focus reage ao câmbio no próprio
    mês e absorveria o repasse); variação do IC-Br em US$ (exógena ao câmbio doméstico)."""
    X = pd.DataFrame({f"pi_l{k}": m["pi_m"].shift(k) for k in range(1, lags + 1)}, index=m.index)
    X["hiato"] = m["hiato"].shift(1)
    X["desvio_focus"] = m["desvio_focus"].shift(1)
    X["dicbr"] = m["dicbr"]
    X["d2020"] = m["d2020"]
    return X


def _iv2sls(y, x_endog, Z_excl, W, hac_lags):
    """2SLS com um regressor endógeno. Devolve (beta_endog, se_HAC, F do primeiro estágio)."""
    Zfull = np.column_stack([Z_excl, W])
    pi_hat, *_ = np.linalg.lstsq(Zfull, x_endog, rcond=None)
    xhat = Zfull @ pi_hat
    rW, *_ = np.linalg.lstsq(W, x_endog, rcond=None)
    ssr_r = ((x_endog - W @ rW) ** 2).sum()
    ssr_u = ((x_endog - xhat) ** 2).sum()
    q, n, k = Z_excl.shape[1], len(y), Zfull.shape[1]
    F = ((ssr_r - ssr_u) / q) / (ssr_u / (n - k))
    X2 = np.column_stack([xhat, W])
    b, *_ = np.linalg.lstsq(X2, y, rcond=None)
    u = y - np.column_stack([x_endog, W]) @ b
    A = np.linalg.inv(X2.T @ X2)
    V = A @ _hac(X2 * u[:, None], hac_lags) @ A
    return float(b[0]), float(np.sqrt(V[0, 0])), float(F)


def dados_lp(m: pd.DataFrame, h: int, preco: str = "p_ipca", excluir_2020: bool = False) -> pd.DataFrame:
    """Base da projeção local no horizonte h (uma linha por mês, sem NaN)."""
    X = _controles(m)
    d = pd.DataFrame({"yp": m[preco].shift(-h) - m[preco].shift(1),
                      "ye": m["e"].shift(-h) - m["e"].shift(1), "de": m["de"],
                      "ddolar": m["ddolar"], "dvix": m["dvix"]}).join(X)
    if excluir_2020:
        d = d[d.index.year != 2020].drop(columns="d2020")
    return d.dropna()


def estimar_lp(d: pd.DataFrame, h: int, iv: bool = False) -> dict:
    """β_h (preço) e δ_h (câmbio) na base `d`; ERPT_h = β_h/δ_h."""
    ctrl = [c for c in d.columns if c not in ("yp", "ye", "de", "ddolar", "dvix")]
    W = sm.add_constant(d[ctrl].values, has_constant="add")
    out = {"h": h, "n": len(d)}
    for alvo, nome in (("yp", "beta"), ("ye", "delta")):
        y = d[alvo].values
        if iv:
            b, se, F = _iv2sls(y, d["de"].values, d[["ddolar", "dvix"]].values, W, h + 1)
            out["F1"] = F
        else:
            res = sm.OLS(y, np.column_stack([d["de"].values, W])).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
            b, se = float(res.params[0]), float(res.bse[0])
        out[nome], out[f"se_{nome}"] = b, se
    out["erpt"] = out["beta"] / out["delta"] if out["delta"] else np.nan
    return out


def lp(m: pd.DataFrame, h: int, preco: str = "p_ipca", iv: bool = False, excluir_2020: bool = False) -> dict:
    return estimar_lp(dados_lp(m, h, preco, excluir_2020), h, iv)


def erpt_bootstrap(m: pd.DataFrame, horizontes, preco="p_ipca", iv=False, B=300, bloco=12, seed=7,
                   excluir_2020=False) -> pd.DataFrame:
    """IC de ERPT_h por bootstrap em blocos móveis de linhas da base de cada horizonte."""
    saida = {}
    for h in horizontes:
        rng = np.random.default_rng(seed + h)
        d = dados_lp(m, h, preco, excluir_2020)
        n = len(d)
        reps = []
        for _ in range(B):
            inicios = rng.integers(0, n - bloco, size=n // bloco + 1)
            idx = np.concatenate([np.arange(s, s + bloco) for s in inicios])[:n]
            try:
                reps.append(estimar_lp(d.iloc[idx], h, iv)["erpt"])
            except Exception:  # noqa: BLE001
                reps.append(np.nan)
        saida[h] = np.nanpercentile(reps, [2.5, 97.5])
    return pd.DataFrame(saida, index=["lo", "hi"]).T


def estimar_b3(m: pd.DataFrame, B: int = 300) -> pd.DataFrame:
    linhas = []
    amostras = {"completa (dummy 2020)": (m, False), "sem 2020": (m, True),
                "2004–2015": (m.loc[:"2015-12-01"], False), "2016–2026": (m.loc["2016-01-01":], False)}
    casos = [("LP OLS", "p_ipca", False, a) for a in amostras] + \
            [("LP IV", "p_ipca", True, "completa (dummy 2020)"), ("LP IV", "p_ipca", True, "sem 2020")] + \
            [("LP OLS", "p_ipca_comerc", False, "completa (dummy 2020)"),
             ("LP OLS", "p_ipca_livres", False, "completa (dummy 2020)")]
    for metodo, preco, iv, amostra in casos:
        df, excl = amostras[amostra]
        base = m if amostra.startswith("completa") or amostra == "sem 2020" else df
        hs = HORIZONTES
        pts = [lp(base, h, preco, iv, excl) for h in hs]
        principais = [3, 6, 12, 24]
        ic = erpt_bootstrap(base, principais, preco, iv, B=B if amostra.startswith("completa") else B // 3,
                            excluir_2020=excl)
        for r in pts:
            linhas.append({"metodo": metodo, "indice": preco.removeprefix("p_"), "amostra": amostra, **r,
                           "ic_lo": ic.loc[r["h"], "lo"] if r["h"] in ic.index else np.nan,
                           "ic_hi": ic.loc[r["h"], "hi"] if r["h"] in ic.index else np.nan})
    return pd.DataFrame(linhas)


def escolher_principal(est: pd.DataFrame) -> dict:
    """OLS completo é o principal, salvo se o IV tiver primeiro estágio forte (F ≥ 10) em h = 12."""
    iv = est[(est["metodo"] == "LP IV") & (est["indice"] == "ipca") & (est["amostra"] == "completa (dummy 2020)")
             & (est["h"] == 12)]
    F = float(iv["F1"].iloc[0]) if len(iv) else np.nan
    metodo = "LP IV" if np.isfinite(F) and F >= 10 else "LP OLS"
    r = est[(est["metodo"] == metodo) & (est["indice"] == "ipca") & (est["amostra"] == "completa (dummy 2020)")]
    r = r.set_index("h")
    return {"metodo": metodo, "F1_iv_h12": F, "instrumentos_fracos": not (np.isfinite(F) and F >= 10),
            "erpt_12": float(r.loc[12, "erpt"]), "erpt_12_lo": float(r.loc[12, "ic_lo"]),
            "erpt_12_hi": float(r.loc[12, "ic_hi"]), "erpt_6": float(r.loc[6, "erpt"]),
            "erpt_24": float(r.loc[24, "erpt"]), "erpt_3": float(r.loc[3, "erpt"])}


# ---------------------------------------------------------------- calibração de b3 por impulso-resposta

def erpt_modelo(p: dict, espec: str, b3: float, cfg: dict, trimestres=(2, 4, 8), choque: float = 10.0) -> dict:
    """Repasse acumulado simulado: choque de `choque`% de depreciação no 1º trimestre, Selic fixa, λ = 0,5."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": espec, "b3": b3})
    cen = politicas.montar_cenario("A", cfg, q["ini"]["i0"])
    T = cen["T"]
    plano = modelo.plano_anunciado(q, cen)
    i_fixa = np.full(T + 1, q["ini"]["i0"])
    de0 = np.zeros(T + 1)
    de1 = de0.copy()
    de1[1] = choque
    base = modelo.simular(q, cen, 0.5, plano=plano, override={"i": i_fixa, "de": de0}, guardar=("pi",))
    chq = modelo.simular(q, cen, 0.5, plano=plano, override={"i": i_fixa, "de": de1}, guardar=("pi",))
    dif = (chq["pi"][0, 1:] - base["pi"][0, 1:]) / 4  # variação trimestral do nível de preços (p.p.)
    acum = np.cumsum(dif) / choque
    return {k: float(acum[k - 1]) for k in trimestres}


def calibrar_b3(p: dict, espec: str, alvo: float, cfg: dict, b_max: float = 1.0) -> tuple[float, str]:
    """b3 tal que o repasse acumulado em 4 trimestres = alvo (ERPT_12). Devolve (b3, observação)."""
    f = lambda b: erpt_modelo(p, espec, b, cfg)[4] - alvo  # noqa: E731
    f0 = f(0.0)
    if f0 >= 0:
        return 0.0, "alvo abaixo do repasse gerado com b3 = 0"
    if f(b_max) < 0:
        return b_max, f"alvo acima do repasse com b3 = {b_max}; b3 limitado"
    return float(brentq(f, 0.0, b_max, xtol=1e-6)), ""


# ---------------------------------------------------------------- ω: Taylor com prêmio

def _hac(g: np.ndarray, lags: int) -> np.ndarray:
    S = g.T @ g
    for L in range(1, lags + 1):
        G = g[L:].T @ g[:-L]
        S += (1 - L / (lags + 1)) * (G + G.T)
    return S


def fieller(b: float, d: float, Vbb: float, Vdd: float, Vbd: float, z: float = 1.959964) -> dict:
    """IC de Fieller para a razão ψ = b/d (b: coeficiente de curto prazo do prêmio; d = 1 − ρ).

    Conjunto {ψ : (b − ψd)² ≤ z² Var(b − ψd)}. É limitado quando d é significativamente diferente de zero;
    caso contrário é a união de dois raios ilimitados ou a reta inteira (ψ pode ser qualquer valor).
    """
    a = d ** 2 - z ** 2 * Vdd
    bq = -2 * (b * d - z ** 2 * Vbd)
    c = b ** 2 - z ** 2 * Vbb
    disc = bq ** 2 - 4 * a * c
    if a > 0 and disc >= 0:
        r = sorted([(-bq - np.sqrt(disc)) / (2 * a), (-bq + np.sqrt(disc)) / (2 * a)])
        tipo, lo, hi = "limitado", r[0], r[1]
    elif a < 0 and disc > 0:
        r = sorted([(-bq - np.sqrt(disc)) / (2 * a), (-bq + np.sqrt(disc)) / (2 * a)])
        tipo, lo, hi = "ilimitado (dois raios)", r[0], r[1]  # (−∞, lo] ∪ [hi, ∞)
    else:
        tipo, lo, hi = "reta inteira", -np.inf, np.inf
    contem = lambda x: bool(a * x * x + bq * x + c <= 0)  # noqa: E731
    return {"ic_tipo": tipo, "ic_lo": float(lo), "ic_hi": float(hi), "ic_contem_0": contem(0.0),
            "ic_contem_1": contem(1.0)}


def ic_texto(r) -> str:
    if r["ic_tipo"] == "limitado":
        return f"[{r['ic_lo']:.2f}; {r['ic_hi']:.2f}]".replace(".", ",")
    if r["ic_tipo"] == "reta inteira":
        return "(−∞; ∞)"
    return f"(−∞; {r['ic_lo']:.2f}] ∪ [{r['ic_hi']:.2f}; ∞)".replace(".", ",")


CLASSES_OMEGA = {
    "nao_identificado": "não identificado (IC ilimitado: 1 − ρ não é significativamente diferente de zero)",
    "nao_informativo": "não informativo para o modelo (IC limitado, mas contém 0 e 1)",
    "erro_especificacao": "possível erro de especificação (IC limitado e inteiramente fora de [0, 1])",
    "fora_do_dominio": "identificado, mas com estimativa pontual fora de [0, 1]",
    "identificado": "identificado",
}


def classificar_omega(r) -> str:
    """Classificação de ψ para uso no modelo, que exige ω ∈ [0, 1] por construção. Nunca corta a estimativa."""
    if r["ic_tipo"] != "limitado":
        return "nao_identificado"
    if r["ic_contem_0"] and r["ic_contem_1"]:
        return "nao_informativo"
    if r["ic_hi"] < 0 or r["ic_lo"] > 1:
        return "erro_especificacao"
    if not 0 <= r["psi"] <= 1:
        return "fora_do_dominio"
    return "identificado"


def _resumo_razao(rho, b_cp, V_rho, V_b, C_rho_b) -> dict:
    """ψ = b/(1 − ρ) com IC de Fieller. Cov(b, 1 − ρ) = −Cov(b, ρ)."""
    out = {"rho": float(rho), "se_rho": float(np.sqrt(V_rho)), "b_curto": float(b_cp),
           "se_b_curto": float(np.sqrt(V_b)), "psi": float(b_cp / (1 - rho))}
    out.update(fieller(b_cp, 1 - rho, V_b, V_rho, -C_rho_b))
    out["ic_texto"] = ic_texto(out)
    out["classe"] = classificar_omega(out)
    return out


def taylor_nls(df: pd.DataFrame, hac_lags: int = 12) -> dict:
    """i = ρ i(−1) + (1−ρ)(c + φπ gap + φh h(−1) + ψ (prem(−1) − média)) + u.

    O ponto é estimado por MQ não lineares. Como a reparametrização é exatamente identificada, o modelo equivale à
    forma linear i = ρ i(−1) + b0 + b1 gap + b2 h(−1) + b_curto·prem(−1); dela vêm ρ, o coeficiente de curto prazo
    do prêmio e a covariância HAC usada no IC de Fieller de ψ = b_curto/(1 − ρ).
    """
    d = df.dropna(subset=["i", "i_l1", "gap", "h_l1", "prem_l1"])
    i, il, gap, h, pr = (d[c].values for c in ("i", "i_l1", "gap", "h_l1", "prem_l1"))
    pr = pr - pr.mean()

    def res(th):
        rho, c, fp, fh, psi = th
        return i - (rho * il + (1 - rho) * (c + fp * gap + fh * h + psi * pr))

    sol = least_squares(res, x0=[0.9, 10.0, 1.5, 0.5, 0.5],
                        bounds=([0, -50, -20, -20, -50], [0.9999, 50, 20, 20, 50]))
    X = np.column_stack([il, np.ones(len(d)), gap, h, pr])
    lin = sm.OLS(i, X).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    V = np.asarray(lin.cov_params())
    out = _resumo_razao(lin.params[0], lin.params[4], V[0, 0], V[4, 4], V[0, 4])
    out.update({"n": len(d), "inicio": d.index[0].strftime("%Y-%m"), "fim": d.index[-1].strftime("%Y-%m"),
                "psi_nls": float(sol.x[4]), "rho_nls": float(sol.x[0])})
    return out


def taylor_gmm(df: pd.DataFrame, hac_lags: int = 12) -> dict:
    """Forma linear por 2SLS (instrumentos: defasagens 2–3 de gap, hiato e prêmio), covariância HAC e Fieller."""
    d = df.copy()
    for c in ("gap", "h_l1", "prem_l1"):
        for L in (2, 3):
            d[f"{c}_z{L}"] = d[c].shift(L)
    d = d.dropna(subset=["i", "i_l1", "gap", "h_l1", "prem_l1"] + [c for c in d if "_z" in c])
    X = np.column_stack([d["i_l1"], np.ones(len(d)), d["gap"], d["h_l1"], d["prem_l1"] - d["prem_l1"].mean()])
    Z = np.column_stack([d["i_l1"], np.ones(len(d))] + [d[c] for c in d if "_z" in c])
    y = d["i"].values
    PZ = Z @ np.linalg.pinv(Z.T @ Z) @ Z.T
    Xh = PZ @ X
    b = np.linalg.solve(Xh.T @ X, Xh.T @ y)
    u = y - X @ b
    A = np.linalg.inv(Xh.T @ Xh)
    V = A @ _hac(Xh * u[:, None], hac_lags) @ A
    out = _resumo_razao(b[0], b[4], V[0, 0], V[4, 4], V[0, 4])
    out.update({"n": len(d), "inicio": d.index[0].strftime("%Y-%m"), "fim": d.index[-1].strftime("%Y-%m")})
    return out


def canal_juro_longo(m: pd.DataFrame) -> dict:
    """Δ NTN-B10 = a + b Δprem + c Δ Selic esperada; o modelo implica b ≈ 1 − ω."""
    d = pd.DataFrame({"dy": m["ntnb10"].diff(), "dprem": m["embi"].diff(),
                      "dsel": m["selic_esperada"].diff()}).dropna()
    res = sm.OLS(d["dy"], sm.add_constant(d[["dprem", "dsel"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    b, se = float(res.params["dprem"]), float(res.bse["dprem"])
    return {"n": len(d), "inicio": d.index[0].strftime("%Y-%m"), "fim": d.index[-1].strftime("%Y-%m"),
            "b": b, "se_b": se, "b_lo": b - 1.96 * se, "b_hi": b + 1.96 * se,
            "c": float(res.params["dsel"]), "se_c": float(res.bse["dsel"])}


def base_taylor(m: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"i": m["selic"], "i_l1": m["selic"].shift(1), "gap": m["pi_e"] - m["meta_12m"],
                         "h_l1": m["hiato"].shift(1), "prem_l1": m["embi"].shift(1)}, index=m.index)


def estimar_omega(m: pd.DataFrame) -> pd.DataFrame:
    df = base_taylor(m).loc["2005-01-01":]
    amostras = {"completa": df, "2005–2015": df.loc[:"2015-12-01"], "2016–2024": df.loc["2016-01-01":],
                "pré-autonomia (até fev/2021)": df.loc[:"2021-02-01"],
                "pós-autonomia (mar/2021–)": df.loc["2021-03-01":]}
    linhas = []
    for nome, d in amostras.items():
        for metodo, f in (("NLS", taylor_nls), ("2SLS/GMM", taylor_gmm)):
            try:
                r = f(d)
            except Exception as e:  # noqa: BLE001
                r = {"erro": str(e)}
            linhas.append({"amostra": nome, "metodo": metodo, **r})
    return pd.DataFrame(linhas)


def unidade_embi(m: pd.DataFrame) -> dict:
    """Conferência de unidade: o Ipeadata publica o EMBI+ em pontos-base; o painel usa p.p. (100 bp = 1 p.p.)."""
    bruto = pd.read_csv(RAW / "ipea_JPM366_EMBI366.csv", parse_dates=["data"]).set_index("data")["valor"].dropna()
    bruto = bruto.loc["2005":]
    return {"bruto_media_bp": float(bruto.mean()), "bruto_min_bp": float(bruto.min()),
            "bruto_max_bp": float(bruto.max()), "painel_media_pp": float(m["embi"].loc["2005":].mean()),
            "fim": bruto.index.max().strftime("%Y-%m")}


def omega_principal(est: pd.DataFrame) -> dict:
    """ψ (NLS, amostra completa), sem corte em [0, 1]. Só vira ω do modelo se for 'identificado'; nos demais
    casos a variante estimada usa ω = 0 (base) e não há variantes estimada_omega_*."""
    r = est[(est["amostra"] == "completa") & (est["metodo"] == "NLS")].iloc[0]
    classe = r["classe"]
    usa = classe == "identificado"
    return {"psi": float(r["psi"]), "b_curto": float(r["b_curto"]), "se_b_curto": float(r["se_b_curto"]),
            "rho": float(r["rho"]), "se_rho": float(r["se_rho"]), "ic_texto": r["ic_texto"], "ic_tipo": r["ic_tipo"],
            "ic_lo": float(r["ic_lo"]), "ic_hi": float(r["ic_hi"]), "classe": classe,
            "classe_texto": CLASSES_OMEGA[classe], "usado_no_modelo": usa,
            "omega": float(r["psi"]) if usa else 0.0,
            # limites do IC para as variantes, restritos ao domínio do modelo (o IC reportado não é cortado)
            "omega_lo": float(max(r["ic_lo"], 0.0)) if usa else np.nan,
            "omega_hi": float(min(r["ic_hi"], 1.0)) if usa else np.nan,
            "n": int(r["n"]), "inicio": r["inicio"], "fim": r["fim"]}


def leitura_canal_longo(om: dict, cj: dict) -> dict:
    """A soma ψ + b só é informativa com ψ identificado; b isolado implica 1 − ω = b se o modelo valer."""
    b_preciso = (cj["b_hi"] - cj["b_lo"]) < 0.5
    informativa = om["classe"] == "identificado" and b_preciso
    return {"soma": om["psi"] + cj["b"], "informativa": informativa, "b_preciso": b_preciso,
            "omega_implicito": 1 - cj["b"], "omega_implicito_lo": 1 - cj["b_hi"],
            "omega_implicito_hi": 1 - cj["b_lo"]}


# ---------------------------------------------------------------- orquestração

def rodar(p: dict, cfg: dict, offline: bool = False, B: int = 300) -> dict:
    """Executa a Tarefa 3 e devolve tabelas, escolhas e variantes estimadas para a matriz de experimentos."""
    validacao = validar(offline)
    m = painel_mensal(offline)
    est_b3 = estimar_b3(m, B=B)
    princ = escolher_principal(est_b3)
    est_om = estimar_omega(m)
    om = omega_principal(est_om)
    cj = canal_juro_longo(m)
    calib = []
    for espec in ("P1", "P2", "P3"):
        linha = {"especificacao": espec}
        for rotulo, alvo in (("pontual", princ["erpt_12"]), ("baixo", princ["erpt_12_lo"]),
                             ("alto", princ["erpt_12_hi"])):
            b3, obs = calibrar_b3(p, espec, alvo, cfg)
            linha[f"b3_{rotulo}"], linha[f"obs_{rotulo}"] = b3, obs
            if rotulo == "pontual":
                ajuste = erpt_modelo(p, espec, b3, cfg)
                linha.update({"erpt_modelo_2t": ajuste[2], "erpt_modelo_4t": ajuste[4], "erpt_modelo_8t": ajuste[8],
                              "erpt_lp_6m": princ["erpt_6"], "erpt_lp_12m": princ["erpt_12"],
                              "erpt_lp_24m": princ["erpt_24"]})
        calib.append(linha)
    calib = pd.DataFrame(calib)
    b3 = {r.especificacao: {"pontual": r.b3_pontual, "baixo": r.b3_baixo, "alto": r.b3_alto}
          for r in calib.itertuples()}
    variantes = {
        "estimada": {"b3": {e: v["pontual"] for e, v in b3.items()}, "omega": om["omega"]},
        "estimada_b3_baixo": {"b3": {e: v["baixo"] for e, v in b3.items()}, "omega": om["omega"]},
        "estimada_b3_alto": {"b3": {e: v["alto"] for e, v in b3.items()}, "omega": om["omega"]},
    }
    if om["usado_no_modelo"]:
        variantes["estimada_omega_baixo"] = {"b3": {e: v["pontual"] for e, v in b3.items()}, "omega": om["omega_lo"]}
        variantes["estimada_omega_alto"] = {"b3": {e: v["pontual"] for e, v in b3.items()}, "omega": om["omega_hi"]}
    return {"validacao": validacao, "painel": m, "b3": est_b3, "b3_principal": princ, "omega": est_om,
            "omega_principal": om, "canal_longo": cj, "leitura_canal": leitura_canal_longo(om, cj),
            "unidade_embi": unidade_embi(m), "calibracao_b3": calib, "variantes": variantes}
