"""Estimação da regra de atualização do λ: quanto a credibilidade cai quando o resultado de um ano fica
desalinhado das metas e quanto sobe quando as cumpre ou supera.

Regra (revisão anual, assimétrica):

  Δλ_π = β⁺_π · max(g_π, 0) + β⁻_π · min(g_π, 0)       g_π = tol − |π_ano − meta|   (p.p.)
  Δλ_f = β⁺_f · max(g_f, 0) + β⁻_f · min(g_f, 0)       g_f = primário_ano − meta    (p.p. do PIB)

g_π > 0: inflação dentro do intervalo de tolerância (quanto mais perto do centro, maior); g_π < 0: fora dele.
g_f > 0: primário acima da meta; g_f < 0: abaixo. Testa-se também o efeito cruzado do fiscal sobre λ_π.

Dados (Brasil, 2005–2025): credibilidades medidas pelo Focus (credibilidade_focus.py e
credibilidade_fiscal_focus.py) e resultados observados (IPCA de dezembro, primário de dezembro em 12 meses,
metas do CMN e da LDO).

- Anual: Δ da credibilidade média do 1º trimestre de y+1 contra a do 1º trimestre de y, sobre o resultado do
  ano y (≈ 20 observações).
- Trimestral sobreposto (robustez): Δ em 4 trimestres sobre o resultado dos 4 trimestres anteriores, com erros
  HAC (Newey-West, 4 defasagens).

Medidas de credibilidade: λ_π = índice de de Mendonça (limitado a [0, 1]) e c do Focus (truncado em [0, 1]);
λ_f = índice de cumprimento esperado da meta de primário e c_f contra a meta original.
As medidas de pesquisa divergem do λ efetivo em nível (seções 2.6 e 2.7 da aba de credibilidade); aqui só se
usa a sensibilidade das variações, aplicada na mesma escala ao λ do modelo.

Uso: python -m src.lambda_dinamico_estimacao
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .credibilidade_focus import METAS, RAW, SAIDA as S_PI
from .credibilidade_fiscal_focus import SAIDA as S_F

SAIDA = S_PI.parent / "lambda_dinamico"


def resultados_anuais() -> pd.DataFrame:
    ipca = pd.read_csv(RAW / "sgs_433.csv", parse_dates=["data"]).set_index("data")["433"].astype(float)
    ipca12 = ((1 + ipca / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
    prim = -pd.read_csv(RAW / "sgs_5793.csv", parse_dates=["data"]).set_index("data")["5793"].astype(float)
    metas = pd.read_csv(RAW / "metas_primario.csv", parse_dates=["data_efeito"])
    linhas = []
    for y in range(2005, 2026):
        dez = pd.Timestamp(f"{y}-12-01")
        m = metas[metas["ano_meta"] == y]
        orig = m.loc[m["tipo"] == "original", "meta_pct_pib"]
        vig = m[m["data_efeito"] <= pd.Timestamp(f"{y}-12-31")]
        vig = vig.iloc[-1] if len(vig) else None
        linhas.append({"ano": y, "ipca": ipca12.get(dez, np.nan), "meta_pi": METAS[y][0], "tol_pi": METAS[y][1],
                       "primario": prim.get(dez, np.nan),
                       "meta_s_original": float(orig.iloc[0]) if len(orig) else np.nan,
                       "meta_s_vigor": (np.nan if vig is None or vig["tipo"] == "suspensao"
                                        else float(vig["meta_efetiva_pct_pib"]))})
    d = pd.DataFrame(linhas).set_index("ano")
    d["g_pi"] = d["tol_pi"] - (d["ipca"] - d["meta_pi"]).abs()
    d["g_f_original"] = d["primario"] - d["meta_s_original"]
    d["g_f_vigor"] = d["primario"] - d["meta_s_vigor"]
    return d


def credibilidades_mensais() -> pd.DataFrame:
    pi = pd.read_csv(S_PI / "credibilidade_focus_mensal.csv", index_col=0, parse_dates=True)
    f = pd.read_csv(S_F / "credibilidade_fiscal_mensal.csv", index_col=0, parse_dates=True)
    return pd.DataFrame({"icbc": pi["icbc"], "c_pi": pi["c_oficial"].clip(0, 1),
                         "icf": f["icf"], "c_f": f["c_original"].clip(0, 1)})


def painel_anual(res: pd.DataFrame, cred: pd.DataFrame) -> pd.DataFrame:
    q1 = cred[cred.index.month <= 3].groupby(cred[cred.index.month <= 3].index.year).mean()
    d = res.copy()
    for k in cred.columns:
        d[f"d_{k}"] = q1[k].shift(-1).reindex(d.index) - q1[k].reindex(d.index)
        d[f"nivel_{k}"] = q1[k].reindex(d.index)
    return d


def painel_trimestral(cred: pd.DataFrame) -> pd.DataFrame:
    ipca = pd.read_csv(RAW / "sgs_433.csv", parse_dates=["data"]).set_index("data")["433"].astype(float)
    ipca12 = ((1 + ipca / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
    prim = -pd.read_csv(RAW / "sgs_5793.csv", parse_dates=["data"]).set_index("data")["5793"].astype(float)
    fm = pd.read_csv(S_F / "credibilidade_fiscal_mensal.csv", index_col=0, parse_dates=True)
    q = cred.resample("QS").mean()
    meta = pd.Series({t: METAS[t.year][0] for t in q.index if t.year in METAS})
    tol = pd.Series({t: METAS[t.year][1] for t in q.index if t.year in METAS})
    # resultado dos 4 trimestres que terminam no trimestre anterior (último mês do trimestre anterior)
    fim_ant = q.index - pd.DateOffset(months=1)
    pi12 = ipca12.reindex(fim_ant).values
    s12 = prim.reindex(fim_ant).values
    meta_s = fm["meta_ano"].reindex(fim_ant).values      # meta em vigor do ano corrente naquele mês
    d = pd.DataFrame({"g_pi": tol.reindex(q.index).values - np.abs(pi12 - meta.reindex(q.index).values),
                      "g_f": s12 - meta_s}, index=q.index)
    for k in cred.columns:
        d[f"d_{k}"] = q[k] - q[k].shift(4)
    # o resultado é o dos 4 trimestres anteriores ao início da janela de variação
    d["g_pi"] = d["g_pi"].shift(0)
    return d.loc["2006":"2025"]


def ajustar(y: pd.Series, sinais: dict, hac: int | None = None) -> dict:
    X = pd.DataFrame({k: v for k, v in sinais.items()})
    m = pd.concat([y.rename("y"), X], axis=1).dropna()
    if len(m) < 8:
        return {"n": len(m)}
    Xc = sm.add_constant(m[list(sinais)])
    fit = sm.OLS(m["y"], Xc).fit(cov_type="HAC", cov_kwds={"maxlags": hac}) if hac else sm.OLS(m["y"], Xc).fit(
        cov_type="HC1")
    return {"n": int(len(m)), "r2": round(float(fit.rsquared), 3),
            **{f"b_{k}": round(float(fit.params[k]), 4) for k in Xc.columns},
            **{f"se_{k}": round(float(fit.bse[k]), 4) for k in Xc.columns},
            **{f"p_{k}": round(float(fit.pvalues[k]), 3) for k in Xc.columns}}


def assim(g: pd.Series, nome: str) -> dict:
    return {f"{nome}_pos": g.clip(lower=0), f"{nome}_neg": g.clip(upper=0)}


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    res, cred = resultados_anuais(), credibilidades_mensais()
    a = painel_anual(res, cred)
    tq = painel_trimestral(cred)
    a.to_csv(SAIDA / "painel_anual.csv")
    tq.to_csv(SAIDA / "painel_trimestral.csv")
    est = []
    for med in ("icbc", "c_pi"):
        est.append({"alvo": "lambda_pi", "medida": med, "painel": "anual",
                    **ajustar(a[f"d_{med}"], assim(a["g_pi"], "g_pi"))})
        est.append({"alvo": "lambda_pi", "medida": med, "painel": "anual + cruzado fiscal",
                    **ajustar(a[f"d_{med}"], {**assim(a["g_pi"], "g_pi"), "g_f_neg": a["g_f_original"].clip(upper=0)})})
        est.append({"alvo": "lambda_pi", "medida": med, "painel": "trimestral HAC",
                    **ajustar(tq[f"d_{med}"], assim(tq["g_pi"], "g_pi"), hac=4)})
    for med in ("icf", "c_f"):
        for ref in ("original", "vigor"):
            est.append({"alvo": "lambda_fiscal", "medida": med, "painel": f"anual, meta {ref}",
                        **ajustar(a[f"d_{med}"], assim(a[f"g_f_{ref}"], "g_f"))})
        est.append({"alvo": "lambda_fiscal", "medida": med, "painel": "trimestral HAC, meta em vigor",
                    **ajustar(tq[f"d_{med}"], assim(tq["g_f"], "g_f"), hac=4)})
    e = pd.DataFrame(est)
    e.to_csv(SAIDA / "estimativas.csv", index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(a[["ipca", "meta_pi", "g_pi", "primario", "meta_s_original", "meta_s_vigor", "g_f_original", "g_f_vigor",
             "nivel_icbc", "d_icbc", "nivel_c_pi", "d_c_pi", "nivel_icf", "d_icf", "d_c_f"]].round(2).to_string())
    cols = [c for c in e.columns if not c.startswith("se_")]
    print(e[cols].to_string(index=False))
    (SAIDA / "estimativas.json").write_text(json.dumps(est, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
