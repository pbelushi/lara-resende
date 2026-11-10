"""
Calibração do modelo turco na trajetória observada (set/2021–set/2026), com a política observada como insumo:
taxa básica, câmbio administrado fora das janelas de flutuação (set–dez/2021 e jun–jul/2023), reajustes do salário
mínimo, impostos de jul/2023, KKM e a troca da equipe em jun/2023.

Alvos: inflação em 12 meses (mensal), câmbio nas janelas de flutuação, crescimento anual do PIB (2022–2025) e
reservas líquidas em pontos selecionados (aproximadas).

Uso:  PYTHONPATH=src python -m turmodel.calibrate
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import least_squares

from .model import MESES, ROOT, T, dados, idx, load_params, pib_anual, politica_observada, simulate

FREE = {  # (bloco, chave): (mín, máx). Fixos por não identificação: phi, gamma_w, kappa, eta, alpha_q, energia, demanda (params.yaml)
    ("inflacao", "b1"): (0.1, 0.8), ("inflacao", "beta"): (0.05, 0.8), ("inflacao", "beta_dn"): (0.0, 0.8),
    ("cambio", "k_kkm"): (0.0, 1.0), ("cambio", "omega"): (0.0, 4.0), ("cambio", "sinal"): (0.0, 60.0),
    ("cambio", "nu"): (0.1, 8.0),
    ("atividade", "alpha_r"): (0.0, 0.5),
    ("reservas", "a0"): (-3.0, 6.0), ("reservas", "a_r"): (0.0, 15.0),
    ("cred", "lambda0"): (0.0, 0.8), ("cred", "salto_2023"): (0.0, 1.0),
}
JANELAS_FX = [("2021-09", "2021-12"), ("2023-06", "2023-07")]


def aplicar(p: dict, x) -> dict:
    q = copy.deepcopy(p)
    for (b, k), v in zip(FREE, x):
        q[b][k] = float(v)
    return q


def alvos():
    d = dados().reindex(MESES)
    an = pd.read_csv(ROOT / "data" / "anual.csv").set_index("ano")
    ra = pd.read_csv(ROOT / "data" / "reservas_liquidas_ancoras.csv")
    return d, an, {idx(m): v for m, v in zip(ra["mes"], ra["reservas_liquidas_ex_swaps_usd_bi"]) if 0 < idx(m) <= T}


def residuos(x, p0, d, an, ra, detalhe=False):
    p = aplicar(p0, x)
    X = simulate(p, politica_observada(p), n=1, stochastic=False)
    r_pi = (np.log1p(X["yoy"][0, 1:] / 100) - np.log1p(d["cpi_yoy"].values[1:] / 100)) / 0.08
    e_obs = np.log(d["usdtry"].values)
    r_fx = np.concatenate([(X["e"][0, idx(a):idx(b) + 1] - e_obs[idx(a):idx(b) + 1]) / 0.05 for a, b in JANELAS_FX])
    g = pib_anual(X)
    r_y = np.array([(g[a][0] - an.loc[a, "pib_crescimento"]) / 1.0 for a in (2022, 2023, 2024, 2025)])
    r_R = np.array([(X["R"][0, t] - v) / 15.0 for t, v in ra.items()])
    if detalhe:
        return p, X, {"inflacao": r_pi * 0.08, "cambio": r_fx * 0.05, "pib": r_y, "reservas": r_R * 15.0}
    return np.concatenate([r_pi, r_fx * 2.0, r_y * 2.0, r_R])


def calibrate(verbose: int = 0, fixos: dict | None = None):
    """fixos: {(bloco, chave): valor} mantidos fora da otimização (variantes de sensibilidade)."""
    global FREE
    p0 = load_params()
    livres_orig = dict(FREE)
    for (b, k), v in (fixos or {}).items():
        p0[b][k] = v
        FREE = {kk: vv for kk, vv in FREE.items() if kk != (b, k)}
    d, an, ra = alvos()
    x0 = [p0[b][k] for b, k in FREE]
    lo, hi = zip(*FREE.values())
    best = None
    rng = np.random.default_rng(0)
    for k in range(14):       # múltiplos pontos de partida
        xs = np.array(x0) if k == 0 else np.array(lo) + rng.random(len(lo)) * (np.array(hi) - np.array(lo))
        sol = least_squares(residuos, xs, bounds=(lo, hi), args=(p0, d, an, ra), x_scale="jac", max_nfev=400)
        if best is None or sol.cost < best.cost:
            best = sol
        if verbose:
            print(k, round(sol.cost, 2))
    p, X, det = residuos(best.x, p0, d, an, ra, detalhe=True)
    tab = pd.DataFrame([{"parametro": f"{b}.{k}", "inicial": p0[b][k], "calibrado": round(float(v), 4), "min": mn,
                         "max": mx, "no_limite": bool(min(abs(v - mn), abs(v - mx)) < 1e-3 * (mx - mn))}
                        for ((b, k), (mn, mx)), v in zip(FREE.items(), best.x)])
    tab.attrs["custo"] = float(best.cost)
    FREE = livres_orig
    return p, X, det, tab


VARIANTES = {
    # o peso da inércia de contratos anuais (b1) é mal identificado: 0,3 e 0,8 ajustam os dados quase igualmente. Nas
    # duas variantes, a guinada de 2023 quase não eleva a credibilidade efetiva (salto ≈ 0). As buscas rodam nas duas.
    "A_inercia_baixa": {("inflacao", "b1"): 0.3},
    "B_inercia_alta": {("inflacao", "b1"): 0.8},
}


def main():
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    d, an, ra = alvos()
    resumo = []
    for nome, fixos in VARIANTES.items():
        p, X, det, tab = calibrate(verbose=0, fixos=fixos)
        res_pi = X["pi"][0, 1:] - d["cpi_mm"].values[1:] / 100
        p["choques"]["pi"] = round(float(np.std(res_pi)), 4)
        with open(ROOT / "config" / f"params_calibrated_{nome}.yaml", "w") as f:
            f.write("# Gerado por turmodel.calibrate; não edite.\n")
            yaml.safe_dump(p, f, allow_unicode=True, sort_keys=False)
        tab.to_csv(out / f"calibracao_parametros_{nome}.csv", index=False)
        aj = pd.DataFrame({"mes": [str(m) for m in MESES], "inflacao_12m_modelo": X["yoy"][0],
                           "inflacao_12m_obs": d["cpi_yoy"].values, "cambio_modelo": np.exp(X["e"][0]),
                           "cambio_obs": d["usdtry"].values, "reservas_liq_modelo": X["R"][0], "lambda": X["lam"][0],
                           "juro_real_ex_ante": X["r"][0], "hiato": X["y"][0], "divida": X["d"][0]})
        aj.to_csv(out / f"calibracao_ajuste_mensal_{nome}.csv", index=False)
        g = pib_anual(X)
        mae = float(np.mean(np.abs(X["yoy"][0, 1:] - d["cpi_yoy"].values[1:])))
        resumo.append({"variante": nome, "custo": round(tab.attrs["custo"], 1), "erro_abs_medio_inflacao_12m": round(mae, 1),
                       **{r.parametro: r.calibrado for r in tab.itertuples()},
                       **{f"pib_{a}": round(float(g[a][0]), 1) for a in g},
                       **{f"R_{MESES[t]}": round(float(X["R"][0, t])) for t in ra},
                       "inflacao_dez22": round(float(X["yoy"][0, idx("2022-12")]), 1),
                       "inflacao_dez23": round(float(X["yoy"][0, idx("2023-12")]), 1),
                       "inflacao_dez24": round(float(X["yoy"][0, idx("2024-12")]), 1),
                       "inflacao_set26": round(float(X["yoy"][0, T]), 1),
                       "cambio_dez21": round(float(np.exp(X["e"][0, idx("2021-12")])), 2),
                       "lambda_dez24": round(float(X["lam"][0, idx("2024-12")]), 2),
                       "parametros_no_limite": ", ".join(tab.loc[tab.no_limite, "parametro"])})
    r = pd.DataFrame(resumo).set_index("variante").T
    r.to_csv(out / "calibracao_resumo.csv")
    pd.set_option("display.width", 200)
    print(r.to_string())
    print("observado: inflação dez/22 64,3; dez/23 64,8; dez/24 44,4; set/26 29,7; câmbio dez/21 13,56; PIB",
          an["pib_crescimento"].loc[2022:2025].tolist(), "; reservas", ra)


if __name__ == "__main__":
    main()
