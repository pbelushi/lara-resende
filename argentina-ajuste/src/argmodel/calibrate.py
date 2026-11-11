"""
Calibração por mínimos quadrados com prior.

O cenário ACTUAL (políticas efetivamente executadas, desfecho legislativo
observado) é simulado sem choques e comparado com os alvos de data/. Os
parâmetros livres têm prior = valor em config/params.yaml e limites abaixo;
a penalidade de prior evita que poucos pontos de dados empurrem parâmetros
para valores implausíveis (identificação é fraca — ver README).

Uso:  python -m argmodel.calibrate        (grava config/params_calibrated.yaml)
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import least_squares

from .model import ACTUAL, ROOT, load_actuals, load_params, metrics, simulate

FREE = {  # caminho: (min, max)
    # activity.agri_rebound fixo (ia a zero; não identificável junto com o hiato; ver sensitivity.py).
    # poverty.eta_reg fixo (ia ao teto 1,0; ver sensitivity.py).
    # catchup e zeta_rer são identificados pelos alvos de salário real e CBT/IPC.
    "inflation.lambda_inertia": (0.15, 0.85),
    "inflation.beta_fx": (0.15, 0.80),
    "inflation.beta_fx_down": (0.0, 0.80),
    "credibility.c0": (-3.0, 3.5),
    "credibility.c_embi": (0.0, 2.0),
    "income.theta_index": (0.0, 0.8),
    "income.catchup": (0.01, 0.15),
    "income.poor_activity_elast": (0.0, 2.0),
    "fiscal.revenue_base": (0.160, 0.180),
    "activity.alpha_wage": (0.05, 0.5),
    "activity.alpha_rer": (0.0, 0.08),
    "activity.alpha_conf": (0.0, 0.06),
    "activity.rho_fiscal": (0.85, 0.995),
    "country_risk.e0": (6.0, 7.5),
    "country_risk.kappa": (0.05, 0.6),
    "poverty.sigma": (0.35, 1.2),
    "poverty.zeta_rer": (0.0, 0.3),
    "external.tb_base": (-0.5, 1.0),
}
PRIOR_WEIGHT = 0.6
REL_POINTS = range(0, 25, 3)   # dez/23, mar/24, ..., dez/25 (trimestral)

EMBI_POINTS = {0: 1907, 6: 1450, 12: 640, 19: 730, 20: 829, 21: 1222, 22: 657, 24: 570}


def _get(p, path):
    a, b = path.split(".")
    return p[a][b]


def _set(p, path, v):
    a, b = path.split(".")
    p[a][b] = float(v)


def load_targets() -> dict:
    with open(ROOT / "data" / "targets.yaml") as f:
        return yaml.safe_load(f)


def residuals_breakdown(p: dict) -> pd.DataFrame:
    """Modelo vs. observado, item a item (com pesos usados na calibração)."""
    tg = load_targets()
    act = load_actuals()
    o = simulate(p, ACTUAL, n=1, stochastic=False)
    m = metrics(o).iloc[0]
    rows = []
    for t in range(25):
        obs = float(act.loc[act.t == t, "cpi_mom_pct"].iloc[0])
        rows.append(("inflação mensal", f"t={t}", o["pi"][0, t] * 100, obs, 1.0 if t < 6 else 2.0))
    for k, w in [("2024", 0.4), ("2025", 1.0)]:
        rows.append(("inflação dez/dez", k, m[f"infl_{k}"], tg["inflation_dec_dec"][int(k)], w))
    for k in ["2024", "2025"]:
        rows.append(("PIB anual", k, m[f"pib_{k}"], tg["gdp_growth"][int(k)], 3.0))
    for k in ["2024H1", "2024H2", "2025H1", "2025H2"]:
        col = f"pobreza_{k[:4]}S{k[-1]}"
        rows.append(("pobreza", k, m[col], tg["poverty_rate"][k], 1.5))
    for t, v in EMBI_POINTS.items():
        rows.append(("risco país (log×10)", f"t={t}", np.log(o["embi"][0, t]) * 10, np.log(v) * 10, 1.0))
    rp = pd.read_csv(ROOT / "data" / "relative_prices_wages.csv")
    for t in REL_POINTS:
        r_ = rp.loc[rp.t == t].iloc[0]
        # registrado privado: é o que a indexação (paritarias) descreve; o não registrado entra no
        # índice do INDEC com ~5 meses de defasagem e o público segue decisão fiscal
        rows.append(("salário real priv. reg. (log×100)", f"t={t}", np.log(o["rw"][0, t]) * 100,
                     np.log(r_.real_wage_priv_reg_rel_nov23) * 100, 1.0))
        rows.append(("linha CBT/IPC (log×100)", f"t={t}", o["lnz"][0, t] * 100,
                     np.log(r_.cbt_cpi_rel_nov23) * 100, 1.0))
    rows.append(("primário 2024", "2024", m["primario_2024"], tg["primary_balance_pct_gdp"][2024], 2.0))
    rows.append(("reservas dez/24", "2024-12", o["reserves"][0, 12],
                 tg["net_reserves_usd_bn"]["2024-12"], 0.3))
    df = pd.DataFrame(rows, columns=["bloco", "ponto", "modelo", "observado", "peso"])
    df["erro"] = df.modelo - df.observado
    return df


def _objective(x, base, x0, span):
    p = copy.deepcopy(base)
    for (k, _), v in zip(FREE.items(), x):
        _set(p, k, v)
    df = residuals_breakdown(p)
    r = (df.erro * df.peso).to_numpy()
    prior = PRIOR_WEIGHT * 10 * (x - x0) / span
    return np.concatenate([r, prior])


def calibrate(verbose: int = 1, base: dict | None = None) -> tuple[dict, pd.DataFrame]:
    base = base or load_params()
    x0 = np.array([_get(base, k) for k in FREE])
    lo = np.array([v[0] for v in FREE.values()])
    hi = np.array([v[1] for v in FREE.values()])
    x0 = np.clip(x0, lo + 1e-6, hi - 1e-6)
    span = hi - lo
    res = least_squares(_objective, x0, bounds=(lo, hi), args=(base, x0, span),
                        x_scale=span, diff_step=1e-3, max_nfev=600, verbose=verbose)
    p = copy.deepcopy(base)
    for (k, _), v in zip(FREE.items(), res.x):
        _set(p, k, v)
    table = pd.DataFrame({"parametro": list(FREE), "prior": x0, "calibrado": res.x,
                          "min": lo, "max": hi})
    return p, table


def main():
    p, table = calibrate()
    out = ROOT / "config" / "params_calibrated.yaml"
    with open(out, "w") as f:
        f.write("# Gerado por argmodel.calibrate — não editar à mão; edite params.yaml e recalibre.\n")
        yaml.safe_dump(p, f, allow_unicode=True, sort_keys=False)
    (ROOT / "outputs").mkdir(exist_ok=True)
    table.to_csv(ROOT / "outputs" / "calibracao_parametros.csv", index=False)
    fit = residuals_breakdown(p)
    fit.to_csv(ROOT / "outputs" / "calibracao_ajuste.csv", index=False)
    pd.set_option("display.width", 160)
    print(table.round(4).to_string(index=False))
    print(fit.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
