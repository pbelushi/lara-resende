"""
Credibilidade das âncoras: λ_câmbio × λ_juros.

Parte 1 (contrafactual): para combinações selecionadas, varia a credibilidade das âncoras
do pacote alternativo (λ_câmbio: crawl/banda ou regra SCRER; λ_juros: meta do BC, só com
JUROS+) e compara com a referência, que fica na credibilidade calibrada (λ_ref, o caminho
observado). Variante "choque comum": o mesmo λ_câmbio também na referência.

Uso:  python -m argmodel.credibility
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from .experiment import REFERENCE, load_calibrated
from .model import ROOT, Scenario, metrics, simulate

GRID = np.round(np.arange(0, 1.0001, 0.125), 3)
COMBOS = {
    "Juros+ (só)": dict(rate=True),
    "BMULT": dict(fiscal="baixo_multiplicador"),
    "BMULT + Juros+": dict(fiscal="baixo_multiplicador", rate=True),
    "BMULT + Juros+ + Troca": dict(fiscal="baixo_multiplicador", rate=True, swap=True),
    "Câmbio comp. + Juros+": dict(dev=True, rate=True),
    "Câmbio comp. + Juros+ + BMULT": dict(dev=True, rate=True, fiscal="baixo_multiplicador"),
}
OUTS = {"infl_2024": -1, "infl_2025": -1, "pobreza_2025S2": -1, "pobreza_media_24_25": -1,
        "renda_media_2025": +1, "reservas_dez25": +1, "embi_dez25": -1}


def _sc(kw):
    base = dict(dev=REFERENCE.dev, rate=REFERENCE.rate, fiscal=REFERENCE.fiscal,
                priv=REFERENCE.priv, swap=REFERENCE.swap)
    return Scenario(**{**base, **kw})


def _p(p, lx, li):
    q = copy.deepcopy(p)
    q["credibility"]["lambda_fx"] = float(lx)
    q["credibility"]["lambda_rate"] = float(li)
    return q


def _cmp(m, ref_m):
    r = {}
    for o, sgn in OUTS.items():
        d = (m[o] - ref_m[o]).to_numpy()
        r[f"d_{o}"] = float(np.nanmedian(d))
        r[f"P_{o}"] = float(np.mean(sgn * d > 0))
    r["P_3frentes"] = float(np.mean((m["infl_2025"] < ref_m["infl_2025"]).to_numpy()
                                    & (m["pobreza_2025S2"] < ref_m["pobreza_2025S2"]).to_numpy()
                                    & (m["renda_media_2025"] > ref_m["renda_media_2025"]).to_numpy()))
    for k in ["cred_cambio_2024", "cred_juros_2024", "infl_2025", "pobreza_2025S2", "pobreza_media_24_25"]:
        r[k] = float(np.nanmedian(m[k]))
    r["P_abandono_crawl"] = float(np.mean(m["cambio_real_min"] < -0.15))
    return r


def run(n: int = 300, seed: int = 7):
    p = load_calibrated()
    l0 = p["credibility"]["lambda_ref"]
    ref_m = metrics(simulate(p, REFERENCE, n=n, seed=seed))
    rows = []
    for name, kw in COMBOS.items():
        sc = _sc(kw)
        rates = GRID if sc.rate else [l0]
        for lx in GRID:
            for li in rates:
                m = metrics(simulate(_p(p, lx, li), sc, n=n, seed=seed))
                rows.append({"combinacao": name, "lambda_cambio": lx, "lambda_juros": li, "choque": "só alternativa",
                             **_cmp(m, ref_m)})
        # choque comum: referência com o mesmo λ_câmbio (λ_juros na referência; ela não usa a meta)
        for lx in GRID:
            ref_x = metrics(simulate(_p(p, lx, l0), REFERENCE, n=n, seed=seed))
            m = metrics(simulate(_p(p, lx, l0), sc, n=n, seed=seed))
            rows.append({"combinacao": name, "lambda_cambio": lx, "lambda_juros": l0, "choque": "comum",
                         **_cmp(m, ref_x)})
    return pd.DataFrame(rows)


def thresholds(df: pd.DataFrame, l0: float = 0.75) -> pd.DataFrame:
    """Menor λ em que a combinação ainda vence a referência (mediana) em inflação 2025 e pobreza 2º sem/25."""
    out = []
    d = df[df.choque == "só alternativa"]
    for name, g in d.groupby("combinacao", sort=False):
        win = g[(g.d_infl_2025 < 0) & (g.d_pobreza_2025S2 < 0)]
        gx = g[np.isclose(g.lambda_juros, l0)]
        gi = g[np.isclose(g.lambda_cambio, l0)]
        wx = gx[(gx.d_infl_2025 < 0) & (gx.d_pobreza_2025S2 < 0)]
        wi = gi[(gi.d_infl_2025 < 0) & (gi.d_pobreza_2025S2 < 0)]
        out.append({"combinacao": name,
                    "lambda_cambio_min (juros em λ_ref)": wx.lambda_cambio.min() if len(wx) else np.nan,
                    "lambda_juros_min (câmbio em λ_ref)": wi.lambda_juros.min() if len(wi) and g.lambda_juros.nunique() > 1 else np.nan,
                    "fração do mapa em que vence": len(win) / len(g)})
    return pd.DataFrame(out)


def fig_map(df: pd.DataFrame, observed: dict | None = None, path=None):
    """Mapa λ_câmbio × λ_juros: chance de vencer a referência nas três frentes."""
    from matplotlib.colors import LinearSegmentedColormap
    from .report import plt, INK, INK2, SURF   # aplica o estilo do projeto
    cmap = LinearSegmentedColormap.from_list("seq", ["#f1f6fd", "#9ec5f2", "#2a78d6", "#0d3b75"])
    names = ["Juros+ (só)", "BMULT + Juros+", "Câmbio comp. + Juros+", "Câmbio comp. + Juros+ + BMULT"]
    fig, axs = plt.subplots(2, 2, figsize=(10, 8.6), sharex=True, sharey=True)
    d = df[df.choque == "só alternativa"]
    for a, name in zip(axs.flat, names):
        g = d[d.combinacao == name].pivot(index="lambda_juros", columns="lambda_cambio", values="P_3frentes")
        im = a.imshow(g.values, origin="lower", cmap=cmap, vmin=0, vmax=1, aspect="auto",
                      extent=[-0.0625, 1.0625, -0.0625, 1.0625])
        a.contour(g.columns, g.index, g.values, levels=[0.5], colors=[INK], linewidths=1.4)
        a.scatter([0.75], [0.75], marker="o", s=46, facecolor=SURF, edgecolor=INK, zorder=5)
        if observed:
            a.scatter([observed["lambda_cambio"]], [observed.get("lambda_juros", 0.75)], marker="D", s=46,
                      facecolor="#eb6834", edgecolor=INK, zorder=6)
        a.set_title(name, loc="left"); a.grid(False)
        a.set_xticks([0, .25, .5, .75, 1]); a.set_yticks([0, .25, .5, .75, 1])
    for a in axs[1]: a.set_xlabel("λ câmbio (crença no câmbio anunciado)")
    for a in axs[:, 0]: a.set_ylabel("λ juros (crença na meta do BC)")
    cb = fig.colorbar(im, ax=axs, shrink=0.8, pad=0.02)
    cb.set_label("chance de vencer a referência em inflação, pobreza e renda (2025)")
    note = "Linha: 50% de chance. Círculo: credibilidade calibrada (λ = 0,75)."
    if observed:
        note += " Losango: credibilidade medida pelo REM."
    fig.text(0.01, 0.005, note, color=INK2, fontsize=8.5)
    fig.savefig(path or (ROOT / "outputs" / "fig_credibilidade_mapa.png"), dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    df = run()
    out = ROOT / "outputs"
    df.to_csv(out / "credibilidade_mapa.csv", index=False)
    th = thresholds(df)
    th.to_csv(out / "credibilidade_limiares.csv", index=False)
    pd.set_option("display.width", 250)
    print(th.round(3).to_string(index=False))
    fig_map(df)


if __name__ == "__main__":
    main()
