"""
Troca de dívida sob diferentes graus de adesão do mercado (λ).

Para cada par (λ_fiscal, λ_π) em [0, 1], compara a referência com e sem troca de
dívida, com números aleatórios comuns. Reporta a diferença mediana e a chance de
a troca melhorar cada métrica, e a adesão mínima λ* em que ela ainda compensa.
Também decompõe o efeito em λ = 0 ligando um canal por vez.

Uso:  python -m argmodel.lambda_swap
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from .experiment import REFERENCE, load_calibrated
from .model import ROOT, Scenario, metrics, simulate

GRID = np.round(np.arange(0, 1.0001, 0.1), 2)
OUTS = {"embi_dez25": -1, "reservas_dez25": +1, "pobreza_2025S2": -1, "infl_2025": -1,
        "renda_media_2025": +1, "pib_2025": +1}   # sinal = direção "melhor"


def _base_kw():
    r = REFERENCE
    return dict(dev=r.dev, rate=r.rate, fiscal=r.fiscal, priv=r.priv, swap=False)


def compare(p: dict, lf: float, lp: float, ref_m: pd.DataFrame, n: int, seed: int) -> dict:
    q = copy.deepcopy(p)
    q["debt_swap"]["lambda_fiscal"] = float(lf)
    q["debt_swap"]["lambda_pi"] = float(lp)
    m = metrics(simulate(q, Scenario(**{**_base_kw(), "swap": True}), n=n, seed=seed))
    row = {"lambda_fiscal": lf, "lambda_pi": lp}
    for o, sgn in OUTS.items():
        d = (m[o] - ref_m[o]).to_numpy()
        row[f"d_{o}"] = float(np.nanmedian(d))
        row[f"P_melhor_{o}"] = float(np.mean(sgn * d > 0))
    row["divida_peso_pib_dez25"] = float(np.nanmedian(m["divida_peso_pib_dez25"]))
    return row


def run(n: int = 300, seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = load_calibrated()
    ref_m = metrics(simulate(p, Scenario(**_base_kw()), n=n, seed=seed))
    grid = pd.DataFrame([compare(p, lf, lp, ref_m, n, seed) for lf in GRID for lp in GRID])

    # decomposição em λ = 0: cada canal sozinho (os demais no valor de referência)
    l0 = p["debt_swap"]["lambda_ref"]
    chans = {"adesão": ("adh_floor",), "prêmio": ("prem_slope",), "risco de rolagem (EMBI)": ("e_slope",),
             "dolarização na rolagem": ("roll_max",), "expectativas (λ_π)": ("c_slope",)}
    dec = []
    for name, keys in chans.items():
        q = copy.deepcopy(p)
        # neutraliza todos os canais, depois religa só o escolhido, com λ = 0
        q["debt_swap"].update({"prem_slope": 0.0, "e_slope": 0.0, "roll_max": 0.0, "c_slope": 0.0,
                               "adh_floor": 1.0})
        for k in keys:
            q["debt_swap"][k] = p["debt_swap"][k]
        r = compare(q, 0.0, 0.0, ref_m, n, seed)
        r["canal"] = name
        dec.append(r)
    r = compare(p, l0, l0, ref_m, n, seed); r["canal"] = f"todos em λ = {l0} (referência)"; dec.append(r)
    r = compare(p, 0.0, 0.0, ref_m, n, seed); r["canal"] = "todos em λ = 0"; dec.append(r)
    return grid, pd.DataFrame(dec)


def lambda_star(grid: pd.DataFrame) -> pd.DataFrame:
    """Menor λ (diagonal λ_fiscal = λ_π) em que a mediana da troca é melhor que não trocar."""
    diag = grid[np.isclose(grid.lambda_fiscal, grid.lambda_pi)].sort_values("lambda_fiscal")
    rows = []
    for o, sgn in OUTS.items():
        ok = diag[sgn * diag[f"d_{o}"] > 0]
        rows.append({"metrica": o, "lambda_star": ok.lambda_fiscal.min() if len(ok) else np.nan,
                     "efeito_lambda0": diag[f"d_{o}"].iloc[0], "efeito_lambda1": diag[f"d_{o}"].iloc[-1]})
    return pd.DataFrame(rows)


def main():
    grid, dec = run()
    out = ROOT / "outputs"
    grid.to_csv(out / "lambda_troca_grade.csv", index=False)
    dec.to_csv(out / "lambda_troca_canais.csv", index=False)
    ls = lambda_star(grid)
    ls.to_csv(out / "lambda_troca_lambda_star.csv", index=False)
    pd.set_option("display.width", 220)
    print(ls.round(2).to_string(index=False))
    cols = ["canal", "d_embi_dez25", "d_reservas_dez25", "d_pobreza_2025S2", "d_infl_2025", "d_pib_2025"]
    print(dec[cols].round(2).to_string(index=False))



# --- combinações selecionadas sob adesão baixa ----------------------------------------
COMBOS = {
    "BMULT + JUROS+ (sem troca)": dict(fiscal="baixo_multiplicador", rate=True, swap=False),
    "BMULT + SWAP+": dict(fiscal="baixo_multiplicador", swap=True),
    "BMULT + SWAP+ + JUROS+": dict(fiscal="baixo_multiplicador", rate=True, swap=True),
}
SETTINGS = [("λ = 0,75 (calibração)", 0.75, 1), ("λ = 0,5", 0.5, 1), ("λ = 0,25", 0.25, 1),
            ("λ = 0", 0.0, 1), ("λ = 0, medo ×3", 0.0, 3), ("λ = 0,25, medo ×6", 0.25, 6)]
FEAR = ["prem_slope", "e_slope", "roll_max", "c_slope"]


def _with_lambda(p, lam, k):
    q = copy.deepcopy(p)
    q["debt_swap"]["lambda_fiscal"] = q["debt_swap"]["lambda_pi"] = float(lam)
    for s in FEAR:
        q["debt_swap"][s] *= k
    return q


def _vs_ref(m, ref_m):
    out = {}
    for o, sgn in OUTS.items():
        d = (m[o] - ref_m[o]).to_numpy()
        out[f"d_{o}"] = float(np.nanmedian(d))
        out[f"P_melhor_{o}"] = float(np.mean(sgn * d > 0))
    out["P_melhor_3"] = float(np.mean((m["infl_2025"] < ref_m["infl_2025"]).to_numpy()
                                      & (m["pobreza_2025S2"] < ref_m["pobreza_2025S2"]).to_numpy()
                                      & (m["renda_media_2025"] > ref_m["renda_media_2025"]).to_numpy()))
    for o in OUTS:
        out[o] = float(np.nanmedian(m[o]))
    return out


def combos(n: int = 400, seed: int = 7):
    """Combinações selecionadas e o grid de 48 cenários sob adesão baixa."""
    from .experiment import grid as full_grid
    p = load_calibrated()
    ref_m = metrics(simulate(p, REFERENCE, n=n, seed=seed))   # referência não troca: não depende de λ
    rows, dom = [], []
    for label, lam, k in SETTINGS:
        q = _with_lambda(p, lam, k)
        for name, kw in COMBOS.items():
            sc = Scenario(**{**_base_kw(), **kw})
            r = _vs_ref(metrics(simulate(q, sc, n=n, seed=seed)), ref_m)
            rows.append({"ajuste": label, "combinacao": name, **r})
        # quantos dos 48 cenários vencem a referência nas três frentes (medianas)
        res = []
        for sc in full_grid():
            if sc == REFERENCE:
                continue
            r = _vs_ref(metrics(simulate(q, sc, n=n, seed=seed)), ref_m)
            ok = r["d_infl_2025"] < 0 and r["d_pobreza_2025S2"] < 0 and r["d_renda_media_2025"] > 0
            res.append((sc, ok, r["d_pobreza_2025S2"], r["d_infl_2025"]))
        best = min(res, key=lambda x: x[2])
        dom.append({"ajuste": label, "n_vencem_3_frentes": sum(x[1] for x in res),
                    "n_com_troca": sum(x[1] and x[0].swap for x in res),
                    "menor_pobreza": str(best[0]), "d_pobreza_melhor": best[2], "d_infl_melhor": best[3]})
    return pd.DataFrame(rows), pd.DataFrame(dom)


def main_combos():
    c, d = combos()
    out = ROOT / "outputs"
    c.to_csv(out / "lambda_troca_combinacoes.csv", index=False)
    d.to_csv(out / "lambda_troca_dominancia.csv", index=False)
    pd.set_option("display.width", 250)
    cols = ["ajuste", "combinacao", "d_infl_2025", "d_pobreza_2025S2", "d_renda_media_2025", "d_embi_dez25",
            "d_reservas_dez25", "d_pib_2025", "P_melhor_pobreza_2025S2", "P_melhor_infl_2025", "P_melhor_3"]
    print(c[cols].round(2).to_string(index=False))
    print(d.round(2).to_string(index=False))


if __name__ == "__main__":
    import sys
    main_combos() if "--combos" in sys.argv else main()
