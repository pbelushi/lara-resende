"""Credibilidade da meta medida pelo Focus, com a mesma fórmula usada no experimento argentino (REM).

c = (inflação passada − inflação esperada) / (inflação passada − meta)

c = 1: a expectativa segue a meta; c = 0: a expectativa repete a inflação passada (pura inércia).
É a mesma decomposição da equação de expectativas do modelo, π_e = λ_π·meta + (1 − λ_π)·π_ant
(sem o termo de inconsistência κ·incons), de modo que c é o λ_π "de pesquisa".

Por período, c é agregado por mínimos quadrados, c = Σ(a·b) / Σ(a²), com a = π_ant − meta e
b = π_ant − π_e, só nos meses em que |a| ≥ 1 p.p. (quando passado e meta quase coincidem, a
razão não informa nada).

Duas âncoras:
- meta oficial do CMN para os 12 meses seguintes (média ponderada pelos meses de cada ano);
- 3,0%, a meta fixa usada pelo modelo na validação histórica (comparação na mesma unidade do λ_π).

Também calcula o índice de credibilidade de de Mendonça (2007): 1 com a expectativa na meta, cai
linearmente até 0 no limite do intervalo de tolerância e é 0 fora dele.

Uso: python -m src.credibilidade_focus
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
SAIDA = RAIZ / "outputs" / "v2_2" / "credibilidade_focus"

# Metas do CMN (centro e tolerância, % a.a.). Desde 2025, meta contínua de 3,0%.
METAS = {2005: (4.5, 2.5), 2006: (4.5, 2.0), **{a: (4.5, 2.0) for a in range(2007, 2017)},
         2017: (4.5, 1.5), 2018: (4.5, 1.5), 2019: (4.25, 1.5), 2020: (4.0, 1.5), 2021: (3.75, 1.5),
         2022: (3.5, 1.5), 2023: (3.25, 1.5), **{a: (3.0, 1.5) for a in range(2024, 2029)}}
META_MODELO = 3.0
LIMIAR = 1.0  # p.p.: só meses em que inflação passada e âncora diferem ao menos isso

# Mesmas janelas da validação 2D (credibilidades_separadas.EPIS); o t0 fica de fora.
EPISODIOS = {"2015–16": ("2014-12-31", "2016-12-31"),
             "2016–19": ("2016-06-30", "2019-12-31"),
             "2020–22": ("2020-06-30", "2022-12-31")}
LAMBDA_MODELO = {"2015–16": 0.50, "2016–19": 1.00, "2020–22": 0.35}  # validação 2D, P2


def meta_12m(data: pd.Timestamp, idx: int = 0) -> float:
    """Meta (idx=0) ou tolerância (idx=1) média dos 12 meses seguintes ao mês de `data`."""
    meses = pd.period_range(data.to_period("M") + 1, periods=12, freq="M")
    return float(np.mean([METAS[m.year][idx] for m in meses]))


def painel_mensal() -> pd.DataFrame:
    ipca = pd.read_csv(RAW / "sgs_433.csv", parse_dates=["data"]).set_index("data")["433"].astype(float)
    ipca12 = ((1 + ipca / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
    focus = pd.read_csv(RAW / "focus_ipca12m.csv", parse_dates=["Data"]).set_index("Data")["Mediana"]
    # expectativa no fim do mês (média dos últimos 5 dias úteis), comparada à inflação 12m divulgada até então
    pie = focus.resample("MS").apply(lambda s: s.iloc[-5:].mean() if len(s) else np.nan)
    d = pd.DataFrame({"pi_e": pie})
    # no fim do mês t, o último IPCA conhecido é o de t−1 (divulgado por volta do dia 10 de t)
    d["pi_ant"] = ipca12.shift(1).reindex(d.index)
    d = d.dropna()
    d = d[d.index.year >= 2005]
    d["meta"] = [meta_12m(t) for t in d.index]
    d["tol"] = [meta_12m(t, 1) for t in d.index]
    for nome, ancora in (("oficial", d["meta"]), ("modelo", META_MODELO)):
        a = d["pi_ant"] - ancora
        b = d["pi_ant"] - d["pi_e"]
        d[f"a_{nome}"], d[f"b_{nome}"] = a, b
        d[f"c_{nome}"] = np.where(a.abs() >= LIMIAR, b / a, np.nan)
    gap = (d["pi_e"] - d["meta"]).abs()
    d["icbc"] = np.clip(1 - gap / d["tol"], 0, 1)  # de Mendonça (2007)
    return d


def mq(d: pd.DataFrame, nome: str) -> tuple[float, int]:
    m = d[f"a_{nome}"].abs() >= LIMIAR
    a, b = d.loc[m, f"a_{nome}"], d.loc[m, f"b_{nome}"]
    return (float((a * b).sum() / (a * a).sum()) if m.sum() else np.nan), int(m.sum())


def por_episodio(d: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for nome, (ini, fim) in EPISODIOS.items():
        j = d.loc[(d.index > pd.Timestamp(ini)) & (d.index <= pd.Timestamp(fim))]
        c_of, n_of = mq(j, "oficial")
        c_mo, n_mo = mq(j, "modelo")
        linhas.append({"episodio": nome, "lambda_pi_modelo": LAMBDA_MODELO[nome],
                       "c_focus_meta_oficial": c_of, "meses_oficial": n_of,
                       "c_focus_meta_3": c_mo, "meses_meta_3": n_mo,
                       "icbc_medio": j["icbc"].mean(),
                       "pi_ant_medio": j["pi_ant"].mean(), "pi_e_medio": j["pi_e"].mean(),
                       "meta_media": j["meta"].mean()})
    return pd.DataFrame(linhas)


def por_ano(d: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for ano, j in d.groupby(d.index.year):
        c, n = mq(j, "oficial")
        linhas.append({"ano": ano, "c_focus": c, "meses": n, "icbc": j["icbc"].mean(),
                       "pi_ant_dez": j["pi_ant"].iloc[-1], "pi_e_dez": j["pi_e"].iloc[-1], "meta": j["meta"].iloc[-1]})
    return pd.DataFrame(linhas)


def antecedencia(d: pd.DataFrame) -> pd.DataFrame:
    """A expectativa se aproxima da meta antes ou depois da inflação? Correlação entre a variação em 6 meses
    da distância da expectativa à meta e a variação da distância da inflação à meta, com defasagens."""
    ge = (d["pi_e"] - d["meta"]).diff(6)
    gp = (d["pi_ant"] - d["meta"]).diff(6)
    return pd.DataFrame([{"defasagem_meses": k, "corr": ge.corr(gp.shift(-k))} for k in range(-12, 13, 3)])


def marcos_desinflacao(d: pd.DataFrame) -> list[dict]:
    """Nas duas desinflações (2016–17 e 2022–23): quando a expectativa voltou para perto da meta e quando a
    inflação 12m voltou ao intervalo de tolerância."""
    out = []
    for nome, ini, fim in (("2016–17", "2016-01-01", "2018-06-30"), ("2022–23", "2022-01-01", "2024-06-30")):
        j = d.loc[ini:fim]
        e = j.index[(j["pi_e"] - j["meta"]).abs() <= 0.5]
        p = j.index[j["pi_ant"] <= j["meta"] + j["tol"]]
        out.append({"desinflacao": nome,
                    "expectativa_a_0,5pp_da_meta": e[0].strftime("%Y-%m") if len(e) else None,
                    "inflacao_12m_dentro_do_teto": p[0].strftime("%Y-%m") if len(p) else None})
    return out


def grafico(d: pd.DataFrame, anual: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.plot(d.index, d["pi_ant"], color="#555", lw=1.4, label="IPCA 12 meses (último divulgado)")
    ax1.plot(d.index, d["pi_e"], color="#1f6fb2", lw=1.6, label="Focus: IPCA 12 meses à frente")
    ax1.plot(d.index, d["meta"], color="#c0392b", lw=1.2, ls="--", label="Meta (12 meses à frente)")
    ax1.fill_between(d.index, d["meta"] - d["tol"], d["meta"] + d["tol"], color="#c0392b", alpha=0.07)
    ax1.set_ylabel("% a.a.")
    ax1.legend(frameon=False, fontsize=8, loc="upper left")
    for nome, (ini, fim) in EPISODIOS.items():
        for ax in (ax1, ax2):
            ax.axvspan(pd.Timestamp(ini), pd.Timestamp(fim), color="#999", alpha=0.08)
        ax1.text(pd.Timestamp(ini), ax1.get_ylim()[1] * 0.93, nome, fontsize=8, color="#444")
    t = pd.to_datetime(anual["ano"].astype(str) + "-07-01")
    ax2.plot(t, anual["c_focus"].clip(-0.2, 1.4), "-", color="#1f6fb2")
    ok = anual["meses"] >= 6
    ax2.plot(t[ok], anual.loc[ok, "c_focus"], "o", color="#1f6fb2", label="c do Focus (MQ por ano)")
    ax2.plot(t[~ok], anual.loc[~ok, "c_focus"].clip(-0.2, 1.4), "o", mfc="white", color="#1f6fb2",
             label="c do Focus, ano com menos de 6 meses informativos")
    ax2.plot(t, anual["icbc"], "s-", color="#888", ms=4, label="Índice de de Mendonça (média do ano)")
    for nome, (ini, fim) in EPISODIOS.items():
        ax2.hlines(LAMBDA_MODELO[nome], pd.Timestamp(ini), pd.Timestamp(fim), color="#e67e22", lw=3)
    ax2.plot([], [], color="#e67e22", lw=3, label="λ_π efetivo (validação do modelo)")
    ax2.axhline(1, color="#ccc", lw=0.8)
    ax2.axhline(0, color="#ccc", lw=0.8)
    ax2.set_ylabel("credibilidade")
    ax2.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(SAIDA / "fig_credibilidade_focus.png", dpi=160)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    d = painel_mensal()
    ep, anual, ant = por_episodio(d), por_ano(d), antecedencia(d)
    marcos = marcos_desinflacao(d)
    d.to_csv(SAIDA / "credibilidade_focus_mensal.csv")
    ep.to_csv(SAIDA / "credibilidade_focus_episodios.csv", index=False)
    anual.to_csv(SAIDA / "credibilidade_focus_anual.csv", index=False)
    ant.to_csv(SAIDA / "credibilidade_focus_antecedencia.csv", index=False)
    (SAIDA / "marcos_desinflacao.json").write_text(json.dumps(marcos, ensure_ascii=False, indent=1))
    grafico(d, anual)
    pd.set_option("display.width", 200)
    print(ep.round(2).to_string(index=False))
    print(anual.round(2).to_string(index=False))
    print(ant.round(2).to_string(index=False))
    print(marcos)


if __name__ == "__main__":
    main()
