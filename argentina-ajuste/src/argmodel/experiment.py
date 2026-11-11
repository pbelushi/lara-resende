"""
Experimento fatorial: 2 (câmbio) × 2 (juros) × 3 (fiscal) × 2 (privatização)
× 2 (troca de dívida) = 48 combinações, cada uma com N simulações Monte Carlo
(choques macro + incerteza legislativa). Usa números aleatórios comuns
(mesma semente) para que as diferenças entre cenários reflitam as políticas,
não o sorteio.

Uso:  python -m argmodel.experiment            (usa params_calibrated.yaml)
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import yaml

from .model import ACTUAL, ROOT, Scenario, metrics, simulate

KEY = ["infl_2024", "infl_2025", "pobreza_2024S1", "pobreza_2025S2", "renda_media_2024",
       "renda_media_2025", "renda_pobres_2025", "pib_2024", "pib_2025", "embi_dez25",
       "embi_max", "reservas_dez25", "divida_fx_pib_dez25", "divida_peso_pib_dez25",
       "priv_aprovada", "priv_receita_usd"]

REFERENCE = Scenario(dev=False, rate=False, fiscal="motosserra", priv=True, swap=False)


def grid() -> list[Scenario]:
    return [Scenario(dev=d, rate=r, fiscal=f, priv=pr, swap=s)
            for d, r, f, pr, s in itertools.product(
                [False, True], [False, True], ["motosserra", "baixo_multiplicador", "gradual"],
                [False, True], [False, True])]


def load_calibrated() -> dict:
    with open(ROOT / "config" / "params_calibrated.yaml") as f:
        return yaml.safe_load(f)


def run(p: dict | None = None, n: int | None = None, seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = p or load_calibrated()
    n = n or p["n_sims"]
    rows, draws = [], []
    for sc in grid():
        m = metrics(simulate(p, sc, n=n, seed=seed))
        flags = dict(cenario=sc.label(), dev=int(sc.dev), juros=int(sc.rate), fiscal=sc.fiscal,
                     priv=int(sc.priv), swap=int(sc.swap))
        row = dict(flags)
        for k in KEY:
            v = m[k].to_numpy()
            row[f"{k}_p50"] = np.nanmedian(v)
            row[f"{k}_p10"] = np.nanpercentile(v, 10)
            row[f"{k}_p90"] = np.nanpercentile(v, 90)
        rows.append(row)
        d = m[KEY].copy()
        for k, v in flags.items():
            d[k] = v
        d["sim"] = np.arange(len(d))
        draws.append(d)
    summary = pd.DataFrame(rows)
    allsims = pd.concat(draws, ignore_index=True)

    # diferença contra a referência (combinação equivalente à política efetiva)
    ref = summary[summary.cenario == REFERENCE.label()].iloc[0]
    for k in ["infl_2025", "pobreza_2025S2", "renda_media_2025", "pib_2025", "embi_dez25"]:
        summary[f"d_{k}"] = summary[f"{k}_p50"] - ref[f"{k}_p50"]
    return summary, allsims


def main_effects(allsims: pd.DataFrame) -> pd.DataFrame:
    """Efeito médio de cada alavanca (regressão nas dummies, média sobre as demais)."""
    out = []
    for y in ["infl_2025", "pobreza_2024S1", "pobreza_2025S2", "renda_media_2025",
              "pib_2024", "pib_2025", "embi_dez25", "reservas_dez25"]:
        fit = smf.ols(f"{y} ~ dev + juros + C(fiscal, Treatment('motosserra')) + priv + swap",
                      data=allsims).fit()
        for name, coef in fit.params.items():
            if name == "Intercept":
                continue
            lab = (name.replace("C(fiscal, Treatment('motosserra'))[T.", "fiscal: ")
                   .replace("]", "") + " (vs motosserra)" if "fiscal" in name else name)
            out.append(dict(resultado=y, alavanca=lab, efeito=coef,
                            ic95_lo=fit.conf_int().loc[name, 0], ic95_hi=fit.conf_int().loc[name, 1]))
    return pd.DataFrame(out)


def interactions(allsims: pd.DataFrame) -> pd.DataFrame:
    """Interações de 2ª ordem relevantes para a pergunta (ex.: câmbio × juros)."""
    out = []
    for y in ["infl_2025", "pobreza_2025S2", "renda_media_2025", "embi_dez25"]:
        fit = smf.ols(f"{y} ~ (dev + juros + priv + swap)**2 + C(fiscal)", data=allsims).fit()
        for name, coef in fit.params.items():
            if ":" in name:
                out.append(dict(resultado=y, interacao=name, efeito=coef, p_valor=fit.pvalues[name]))
    return pd.DataFrame(out)


def main():
    p = load_calibrated()
    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)
    summary, allsims = run(p)
    summary.to_csv(outdir / "cenarios_resumo.csv", index=False)
    allsims.to_parquet(outdir / "cenarios_simulacoes.parquet", index=False)
    me = main_effects(allsims)
    me.to_csv(outdir / "efeitos_principais.csv", index=False)
    ia = interactions(allsims)
    ia.to_csv(outdir / "interacoes.csv", index=False)
    act = metrics(simulate(p, ACTUAL, n=1, stochastic=False)).iloc[0]
    act.to_frame("milei_efetivo_deterministico").to_csv(outdir / "validacao_metricas.csv")
    cols = ["cenario", "infl_2025_p50", "pobreza_2025S2_p50", "renda_media_2025_p50",
            "pib_2025_p50", "embi_dez25_p50", "priv_aprovada_p50"]
    pd.set_option("display.width", 200)
    print(summary.sort_values("pobreza_2025S2_p50")[cols].round(1).to_string(index=False))
    print(me.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
