"""Credibilidade fiscal medida pelo Focus, com a mesma fórmula da credibilidade da meta (credibilidade_focus.py).

c_f = (primário passado − primário esperado) / (primário passado − meta de primário)

c_f = 1: o mercado espera o primário anunciado; c_f = 0: espera a repetição do primário corrente.

- Primário passado: resultado primário do setor público consolidado em 12 meses (% do PIB, BCB/SGS 5793,
  sinal trocado), último dado divulgado no fim do mês (o do mês anterior).
- Primário esperado: mediana do Focus para o resultado primário (% do PIB) do ano corrente e do seguinte,
  ponderada pelos meses de cada ano nos 12 meses à frente.
- Meta: a meta em vigor (ou já anunciada) para cada ano, na mesma ponderação, a partir de
  data/raw/metas_primario.csv (setor público consolidado até 2020; governo central desde 2021, quando o
  consolidado deixou de ter meta). Levantamento completo, com fontes por linha:
  data/raw/metas_primario_levantamento.csv. Duas versões:
  * efetiva: a última meta anunciada ou aprovada, no piso legal (após o abatimento máximo; desde 2024, o
    limite inferior da banda); vale a data do anúncio, se anterior à lei. Meta suspensa ou sem limite
    (fim de 2014, 2020, 2021) = sem âncora, mês fora;
  * original: a meta cheia da primeira LDO do ano, sem abatimento nem revisões ("credibilidade do plano
    original").
  Antes de a LDO do ano seguinte ser aprovada, a meta do ano corrente vale também para ele.

Agregação por mínimos quadrados, como na meta de inflação, só nos meses em que primário passado e meta
diferem em pelo menos LIMIAR p.p. do PIB. Meses com meta suspensa (2020) ficam de fora.

Uso: python -m src.credibilidade_fiscal_focus
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .credibilidade_focus import EPISODIOS, RAW, SAIDA as SAIDA_PI

SAIDA = SAIDA_PI.parent / "credibilidade_fiscal_focus"
LIMIAR = 0.5
TOL_ICF = 1.0   # p.p. do PIB
LAMBDA_F_MODELO = {"2015–16": 0.00, "2016–19": 0.75, "2020–22": 0.00}   # validação 2D, P2
LAMBDA_PI_MODELO = {"2015–16": 0.50, "2016–19": 1.00, "2020–22": 0.35}


def carregar_metas() -> pd.DataFrame:
    m = pd.read_csv(RAW / "metas_primario.csv", parse_dates=["data_efeito"])
    return m.sort_values(["ano_meta", "data_efeito"])


def meta_em(metas: pd.DataFrame, ano: int, data: pd.Timestamp, versao: str) -> float:
    """Meta para `ano` conhecida em `data`. versao='efetiva' (última revisão, após abatimento máximo) ou
    'original' (primeira meta anunciada para o ano). NaN se não havia meta ou se estava suspensa."""
    m = metas[(metas["ano_meta"] == ano) & (metas["data_efeito"] <= data)]
    if m.empty:
        # meta do ano seguinte ainda não fixada: o mercado só conhece a do ano corrente
        anteriores = metas[(metas["ano_meta"] == ano - 1) & (metas["data_efeito"] <= data)]
        return meta_em(metas, ano - 1, data, versao) if len(anteriores) else np.nan
    if versao == "original":
        m = m[m["tipo"] == "original"]
        return float(m["meta_pct_pib"].iloc[0]) if len(m) else np.nan
    ult = m.iloc[-1]
    return np.nan if ult["tipo"] == "suspensao" else float(ult["meta_efetiva_pct_pib"])


def esperado_focus(anuais: pd.DataFrame, data: pd.Timestamp) -> dict:
    d = anuais[anuais["Data"] <= data]
    d = d[d["Data"] >= d["Data"].max() - pd.Timedelta(days=7)]   # última semana de pesquisas
    return d.groupby("DataReferencia")["Mediana"].mean().to_dict()


def pondera(data: pd.Timestamp, f) -> float:
    """Média de f(ano) nos 12 meses seguintes ao mês de `data`."""
    meses = pd.period_range(data.to_period("M") + 1, periods=12, freq="M")
    v = [f(m.year) for m in meses]
    return float(np.mean(v)) if not np.any(np.isnan(v)) else np.nan


def painel_mensal() -> pd.DataFrame:
    metas = carregar_metas()
    prim = -pd.read_csv(RAW / "sgs_5793.csv", parse_dates=["data"]).set_index("data")["5793"].astype(float)
    anuais = pd.read_csv(RAW / "focus_anuais_historico.csv", parse_dates=["Data"])
    anuais = anuais[anuais["Indicador"] == "Resultado primário"]
    anuais = anuais.assign(DataReferencia=anuais["DataReferencia"].astype(int))
    linhas = []
    for t in pd.date_range("2005-01-01", anuais["Data"].max(), freq="MS"):
        fim = t + pd.offsets.MonthEnd(0)
        esp = esperado_focus(anuais, fim)
        s_e = pondera(t, lambda a: esp.get(a, np.nan))
        linhas.append({"mes": t, "s_ant": prim.get(t - pd.DateOffset(months=1), np.nan), "s_e": s_e,
                       "meta_efetiva": pondera(t, lambda a: meta_em(metas, a, fim, "efetiva")),
                       "meta_original": pondera(t, lambda a: meta_em(metas, a, fim, "original")),
                       "s_e_ano": esp.get(t.year, np.nan),
                       "meta_ano": meta_em(metas, t.year, fim, "efetiva")})
    d = pd.DataFrame(linhas).set_index("mes")
    for v in ("efetiva", "original"):
        a = d["s_ant"] - d[f"meta_{v}"]
        b = d["s_ant"] - d["s_e"]
        d[f"a_{v}"], d[f"b_{v}"] = a, b
        d[f"c_{v}"] = np.where(a.abs() >= LIMIAR, b / a, np.nan)
    d["gap_esperado_meta"] = d["s_e"] - d["meta_efetiva"]
    # índice no espírito de de Mendonça: 1 se o mercado espera cumprir a meta (ou superá-la), cai linearmente
    # até 0 quando espera um primário TOL_ICF p.p. do PIB abaixo dela
    d["icf"] = np.clip(1 + d["gap_esperado_meta"] / TOL_ICF, 0, 1)
    d["icf_05"] = np.clip(1 + d["gap_esperado_meta"] / 0.5, 0, 1)
    return d


def mq(j: pd.DataFrame, v: str, limiar: float = LIMIAR) -> tuple[float, int]:
    m = (j[f"a_{v}"].abs() >= limiar) & j[f"b_{v}"].notna()
    a, b = j.loc[m, f"a_{v}"], j.loc[m, f"b_{v}"]
    return (float((a * b).sum() / (a * a).sum()) if m.sum() else np.nan), int(m.sum())


def por_episodio(d: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for nome, (ini, fim) in EPISODIOS.items():
        j = d.loc[(d.index > pd.Timestamp(ini)) & (d.index <= pd.Timestamp(fim))]
        ce, ne = mq(j, "efetiva")
        co, no = mq(j, "original")
        ce1, ne1 = mq(j, "efetiva", 1.0)
        linhas.append({"episodio": nome, "lambda_fiscal_modelo": LAMBDA_F_MODELO[nome],
                       "lambda_pi_modelo": LAMBDA_PI_MODELO[nome],
                       "c_f_meta_efetiva": ce, "meses_efetiva": ne, "c_f_meta_original": co, "meses_original": no,
                       "c_f_efetiva_limiar_1pp": ce1, "meses_limiar_1pp": ne1,
                       "s_ant_medio": j["s_ant"].mean(), "s_e_medio": j["s_e"].mean(),
                       "meta_efetiva_media": j["meta_efetiva"].mean(), "meta_original_media": j["meta_original"].mean(),
                       "gap_esperado_meta_medio": j["gap_esperado_meta"].mean(),
                       "icf_medio": j["icf"].mean(), "icf_05_medio": j["icf_05"].mean()})
    return pd.DataFrame(linhas)


def por_ano(d: pd.DataFrame) -> pd.DataFrame:
    pi = pd.read_csv(SAIDA_PI / "credibilidade_focus_anual.csv").set_index("ano")
    linhas = []
    for ano, j in d.groupby(d.index.year):
        ce, ne = mq(j, "efetiva")
        co, no = mq(j, "original")
        linhas.append({"ano": ano, "c_f_efetiva": ce, "meses": ne, "c_f_original": co, "meses_original": no,
                       "gap_esperado_meta": j["gap_esperado_meta"].mean(), "icf": j["icf"].mean(),
                       "c_pi_focus": pi["c_focus"].get(ano, np.nan), "meses_pi": pi["meses"].get(ano, np.nan)})
    return pd.DataFrame(linhas)


def granger(d: pd.DataFrame, max_lag: int = 6) -> list[dict]:
    """A credibilidade fiscal antecede a da meta (Montes, Oliveira e Nicolay, 2019)? Usa a distância entre
    expectativa e meta (sinal de credibilidade sem a divisão, que explode perto do limiar), em variações
    mensais, nos dois sentidos."""
    from statsmodels.tsa.stattools import grangercausalitytests
    pi = pd.read_csv(SAIDA_PI / "credibilidade_focus_mensal.csv", index_col=0, parse_dates=True)
    x = pd.DataFrame({"fiscal": -d["gap_esperado_meta"],                 # + = mercado espera primário ≥ meta
                      "meta": -(pi["pi_e"] - pi["meta"]).abs()}).dropna().diff().dropna()
    x = x[(x.index < "2020-01-01") | (x.index >= "2021-01-01")]
    out = []
    for causa, efeito in (("fiscal", "meta"), ("meta", "fiscal")):
        r = grangercausalitytests(x[[efeito, causa]], maxlag=max_lag)
        for k in (1, 3, 6):
            out.append({"hipotese": f"{causa} -> {efeito}", "defasagens": k,
                        "p_valor_F": round(float(r[k][0]["ssr_ftest"][1]), 4)})
    return out


def grafico(d: pd.DataFrame, anual: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.plot(d.index, d["s_ant"], color="#555", lw=1.4, label="Primário 12 meses (último divulgado)")
    ax1.plot(d.index, d["s_e"], color="#1f6fb2", lw=1.6, label="Focus: primário 12 meses à frente")
    ax1.plot(d.index, d["meta_efetiva"], color="#c0392b", lw=1.2, ls="--", label="Meta em vigor (12 meses à frente)")
    ax1.plot(d.index, d["meta_original"], color="#c0392b", lw=0.9, ls=":", label="Meta original da LDO")
    ax1.set_ylim(-4, 5)
    ax1.set_ylabel("% do PIB")
    ax1.axhline(0, color="#ccc", lw=0.8)
    ax1.legend(frameon=False, fontsize=8, loc="lower left")
    t = pd.to_datetime(anual["ano"].astype(str) + "-07-01")
    for nome, (ini, fim) in EPISODIOS.items():
        for ax in (ax1, ax2):
            ax.axvspan(pd.Timestamp(ini), pd.Timestamp(fim), color="#999", alpha=0.08)
        ax2.hlines(LAMBDA_F_MODELO[nome], pd.Timestamp(ini), pd.Timestamp(fim), color="#e67e22", lw=3)
    ok = anual["meses"] >= 6
    ax2.plot(t, anual["c_f_efetiva"].clip(-0.5, 1.5), "-", color="#1f6fb2")
    ax2.plot(t[ok], anual.loc[ok, "c_f_efetiva"].clip(-0.5, 1.5), "o", color="#1f6fb2",
             label="c fiscal do Focus (meta em vigor)")
    ax2.plot(t[~ok], anual.loc[~ok, "c_f_efetiva"].clip(-0.5, 1.5), "o", mfc="white", color="#1f6fb2",
             label="idem, ano com menos de 6 meses informativos")
    ax2.plot(t, anual["icf"], "^-", color="#2e8b57", ms=4, lw=1, label="Índice fiscal: espera cumprir a meta? (1 = sim)")
    ax2.plot(t, anual["c_pi_focus"].clip(-0.5, 1.5), "s--", color="#888", ms=4, lw=1, label="c da meta de inflação (Focus)")
    ax2.plot([], [], color="#e67e22", lw=3, label="λ_fiscal efetivo (validação do modelo)")
    ax2.axhline(1, color="#ccc", lw=0.8)
    ax2.axhline(0, color="#ccc", lw=0.8)
    ax2.set_ylabel("credibilidade")
    ax2.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(SAIDA / "fig_credibilidade_fiscal_focus.png", dpi=160)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    d = painel_mensal()
    ep, anual = por_episodio(d), por_ano(d)
    g = granger(d)
    d.to_csv(SAIDA / "credibilidade_fiscal_mensal.csv")
    ep.to_csv(SAIDA / "credibilidade_fiscal_episodios.csv", index=False)
    anual.to_csv(SAIDA / "credibilidade_fiscal_anual.csv", index=False)
    (SAIDA / "granger.json").write_text(json.dumps(g, ensure_ascii=False, indent=1))
    grafico(d, anual)
    pd.set_option("display.width", 220)
    print(ep.round(2).to_string(index=False))
    print(anual.round(2).to_string(index=False))
    print(pd.DataFrame(g).to_string(index=False))


if __name__ == "__main__":
    main()
