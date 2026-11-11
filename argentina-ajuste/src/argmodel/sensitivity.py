"""
Sensibilidade: as conclusões sobrevivem quando mudamos as hipóteses frágeis?

Para cada hipótese alternativa, roda as mudanças de uma alavanca por vez
(e as combinações de destaque) contra a referência, com números aleatórios
comuns, e reporta a diferença mediana por simulação. Não recalibra — o
objetivo é ver se SINAL e ORDEM dos efeitos mudam.

Uso:  python -m argmodel.sensitivity
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from .experiment import REFERENCE, load_calibrated
from .model import ROOT, Scenario, metrics, simulate

OUTS = ["infl_2025", "pobreza_2024S1", "pobreza_2025S2", "renda_media_2025", "pib_2025",
        "embi_dez25", "reservas_dez25"]

ALTERNATIVES = {
    "base calibrada": {},
    "canal monetário forte (phi=0.20)": {"inflation.phi_money": 0.20},
    "sem canal monetário (phi=0)": {"inflation.phi_money": 0.0},
    "pobreza menos sensível (sigma=0.60)": {"poverty.sigma": 0.60},
    "multiplicadores ×1.5": {"__mult": 1.5},
    "multiplicadores ×0.5": {"__mult": 0.5},
    "câmbio real pesa menos no salário (0.2)": {"income.rw_rer": 0.20},
    "câmbio real pesa mais no salário (0.6)": {"income.rw_rer": 0.60},
    "mercado ignora risco da dívida em pesos": {"country_risk.e_debt_peso": 0.0},
    "mercado teme dívida em pesos (1.2)": {"country_risk.e_debt_peso": 1.2},
    "Congresso mais favorável (coalizão 0.45)": {"legislative.coalition_share": 0.45},
    "cesta básica não reage ao câmbio (zeta=0)": {"poverty.zeta_rer": 0.0},
    "cesta básica reage mais ao câmbio (zeta=0.25)": {"poverty.zeta_rer": 0.25},
    "salário real recupera devagar (catchup=0.02)": {"income.catchup": 0.02},
    "salário real recupera rápido (catchup=0.12)": {"income.catchup": 0.12},
    "sem rebote da safra (agri=0)": {"activity.agri_rebound": 0.0},
    "rebote da safra forte (agri=0.03)": {"activity.agri_rebound": 0.03},
    "tarifas entram toda na linha (eta=0)": {"poverty.eta_reg": 0.0},
    "tarifas fora da linha (eta=1)": {"poverty.eta_reg": 1.0},
    "repasse do salto médio (beta_fx=0.30)": {"inflation.beta_fx": 0.30},
    "repasse do salto alto (beta_fx=0.45)": {"inflation.beta_fx": 0.45},
    "repasse simétrico (0,16, versão anterior)": {"inflation.beta_fx": 0.16, "inflation.beta_fx_down": 0.16},
}

COMPARISONS = {
    "câmbio competitivo (DEV+)": dict(dev=True),
    "juros reais positivos (JUROS+)": dict(rate=True),
    "DEV+ e JUROS+": dict(dev=True, rate=True),
    "ajuste de baixo multiplicador": dict(fiscal="baixo_multiplicador"),
    "ajuste gradual": dict(fiscal="gradual"),
    "sem privatizações (PRIV−)": dict(priv=False),
    "troca de dívida (SWAP+)": dict(swap=True),
    "BMULT + SWAP+": dict(fiscal="baixo_multiplicador", swap=True),
    "BMULT + SWAP+ + JUROS+": dict(fiscal="baixo_multiplicador", swap=True, rate=True),
}


def _apply(p: dict, changes: dict) -> dict:
    q = copy.deepcopy(p)
    for k, v in changes.items():
        if k == "__mult":
            q["fiscal"]["multipliers"] = {c: m * v for c, m in q["fiscal"]["multipliers"].items()}
            continue
        a, b = k.split(".")
        q[a][b] = v
    return q


def run(n: int = 300, seed: int = 11) -> pd.DataFrame:
    base = load_calibrated()
    ref_kw = dict(dev=REFERENCE.dev, rate=REFERENCE.rate, fiscal=REFERENCE.fiscal,
                  priv=REFERENCE.priv, swap=REFERENCE.swap)
    rows = []
    for alt, changes in ALTERNATIVES.items():
        p = _apply(base, changes)
        mref = metrics(simulate(p, REFERENCE, n=n, seed=seed))
        for comp, kw in COMPARISONS.items():
            sc = Scenario(**{**ref_kw, **kw})
            m = metrics(simulate(p, sc, n=n, seed=seed))
            row = {"hipotese": alt, "mudanca": comp}
            for o in OUTS:
                row[o] = float(np.nanmedian(m[o] - mref[o]))
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    df = run()
    df.to_csv(ROOT / "outputs" / "sensibilidade.csv", index=False)
    pd.set_option("display.width", 220)
    for o in ["pobreza_2025S2", "infl_2025", "renda_media_2025"]:
        print(f"\nΔ {o} vs referência")
        print(df.pivot(index="mudanca", columns="hipotese", values=o).round(1).to_string())


if __name__ == "__main__":
    main()
