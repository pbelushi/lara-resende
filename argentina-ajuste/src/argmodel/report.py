"""
Gráficos de validação e resultados (PNG em outputs/).

Uso:  python -m argmodel.report
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .calibrate import EMBI_POINTS, load_targets
from .experiment import REFERENCE, load_calibrated
from .model import ACTUAL, ROOT, Scenario, load_actuals, simulate

# paleta de referência (skill dataviz), slots 1–3
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
OUT = ROOT / "outputs"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 9.5, "axes.titlesize": 11, "axes.titleweight": "bold",
    "legend.frameon": False, "lines.linewidth": 2,
})
MONTHS = pd.date_range("2023-12-01", periods=25, freq="MS")


def fig_validation(p):
    o = simulate(p, ACTUAL, n=1, stochastic=False)
    act, tg = load_actuals(), load_targets()
    fig, ax = plt.subplots(2, 2, figsize=(11, 7))
    a = ax[0, 0]
    a.plot(MONTHS, act.cpi_mom_pct.values[1:], color=ORANGE, label="Observado (INDEC)")
    a.plot(MONTHS, o["pi"][0] * 100, color=BLUE, label="Modelo")
    a.set_title("Inflação mensal, %"); a.legend()
    a = ax[0, 1]
    sem = ["2024H1", "2024H2", "2025H1", "2025H2"]
    xs = np.arange(4)
    model = [o["poverty"][0, s:s + 6].mean() * 100 for s in (1, 7, 13, 19)]
    a.bar(xs - 0.2, [tg["poverty_rate"][k] for k in sem], 0.38, color=ORANGE, label="Observado (EPH)")
    a.bar(xs + 0.2, model, 0.38, color=BLUE, label="Modelo")
    a.set_xticks(xs, ["1º sem 24", "2º sem 24", "1º sem 25", "2º sem 25"])
    a.axhline(41.7, color=INK2, lw=1, ls="--"); a.text(3.45, 43, "partida (2º sem 23): 41,7", ha="right", color=INK2, fontsize=8.5)
    a.set_title("Pobreza, % das pessoas"); a.legend(loc="upper right"); a.set_ylim(0, 62)
    a = ax[1, 0]
    a.plot(MONTHS, o["embi"][0], color=BLUE, label="Modelo")
    a.scatter([MONTHS[t] for t in EMBI_POINTS], list(EMBI_POINTS.values()), color=ORANGE, s=36,
              zorder=3, label="Observado (fim de mês)")
    a.set_title("Risco país (EMBI, pb)"); a.legend()
    a = ax[1, 1]
    labels = ["PIB 2024", "PIB 2025", "Inflação 2025\n(dez/dez ÷10)", "Primário 2024\n(% PIB)"]
    obs = [tg["gdp_growth"][2024], tg["gdp_growth"][2025], tg["inflation_dec_dec"][2025] / 10,
           tg["primary_balance_pct_gdp"][2024]]
    lp = np.log1p(o["pi"][0])
    mod = [(o["gdp_idx"][0, 1:13].mean() / 100 - 1) * 100,
           (o["gdp_idx"][0, 13:25].mean() / o["gdp_idx"][0, 1:13].mean() - 1) * 100,
           np.expm1(lp[13:25].sum()) * 10, o["pb"][0, 1:13].mean() * 100]
    xs = np.arange(4)
    a.bar(xs - 0.2, obs, 0.38, color=ORANGE, label="Observado"); a.bar(xs + 0.2, mod, 0.38, color=BLUE, label="Modelo")
    a.axhline(0, color=INK2, lw=0.8); a.set_xticks(xs, labels); a.set_title("Agregados anuais"); a.legend()
    for a_ in (ax[0, 0], ax[1, 0]):
        a_.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
        a_.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    fig.suptitle("Validação: o modelo reproduz a trajetória efetiva (dez/23–dez/25)?", fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig1_validacao.png", dpi=150); plt.close(fig)


def fig_tradeoff(summary):
    fig, ax = plt.subplots(figsize=(10, 6.2))
    groups = [("DEV− (crawl âncora)", summary.dev == 0, BLUE),
              ("DEV+ e JUROS+", (summary.dev == 1) & (summary.juros == 1), AQUA),
              ("DEV+ e JUROS−", (summary.dev == 1) & (summary.juros == 0), ORANGE)]
    marks = {"motosserra": "o", "baixo_multiplicador": "s", "gradual": "^"}
    for lab, mask, col in groups:
        for f, mk in marks.items():
            d = summary[mask & (summary.fiscal == f)]
            ax.scatter(d.infl_2025_p50, d.pobreza_2025S2_p50, color=col, marker=mk, s=60,
                       edgecolor=SURF, linewidth=1.5, zorder=3)
        ax.scatter([], [], color=col, s=60, label=lab)
    for f, mk in marks.items():
        ax.scatter([], [], color=INK2, marker=mk, s=50, label={"motosserra": "fiscal: motosserra",
                   "baixo_multiplicador": "fiscal: baixo multiplicador", "gradual": "fiscal: gradual"}[f])
    ref = summary[summary.cenario == REFERENCE.label()].iloc[0]
    ax.scatter(ref.infl_2025_p50, ref.pobreza_2025S2_p50, s=260, facecolor="none", edgecolor=INK, lw=1.5, zorder=4)
    ax.annotate("referência ≈ política efetiva", (ref.infl_2025_p50, ref.pobreza_2025S2_p50),
                xytext=(40, 22), textcoords="offset points", color=INK, fontsize=9,
                arrowprops=dict(arrowstyle="-", color=INK2))
    ax.set_xscale("log"); ax.set_xticks([20, 30, 50, 100, 200]); ax.set_xticklabels(["20", "30", "50", "100", "200"]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Inflação 2025, % dez/dez (escala log)"); ax.set_ylabel("Pobreza 2º sem 2025, %")
    ax.set_title("48 combinações: inflação × pobreza no fim de 2025 (mediana de 400 simulações)")
    ax.legend(loc="upper left", ncol=2, fontsize=8.5)
    fig.tight_layout(); fig.savefig(OUT / "fig2_tradeoff.png", dpi=150); plt.close(fig)


def fig_effects(allsims):
    """Δ vs referência, por simulação (números aleatórios comuns), p10–p90."""
    keyc = ["dev", "juros", "fiscal", "priv", "swap"]
    ref = allsims.query("dev==0 and juros==0 and fiscal=='motosserra' and priv==1 and swap==0").set_index("sim")
    comps = [("Câmbio competitivo", dict(dev=1)), ("Juros reais positivos", dict(juros=1)),
             ("Câmbio comp. + juros", dict(dev=1, juros=1)), ("Ajuste baixo multiplicador", dict(fiscal="baixo_multiplicador")),
             ("Ajuste gradual", dict(fiscal="gradual")), ("Sem privatizações", dict(priv=0)),
             ("Troca de dívida", dict(swap=1)), ("Baixo mult. + troca + juros", dict(fiscal="baixo_multiplicador", swap=1, juros=1))]
    outs = [("pobreza_2025S2", "Pobreza 2º sem 25 (p.p.)"), ("renda_media_2025", "Renda média 2025 (pontos, nov/23=100)"),
            ("infl_2025", "Inflação 2025 (p.p.)"), ("embi_dez25", "Risco país dez/25 (pb)")]
    fig, axes = plt.subplots(1, 4, figsize=(14, 5.2), sharey=True)
    y = np.arange(len(comps))[::-1]
    for a, (col, title) in zip(axes, outs):
        for yi, (lab, kw) in zip(y, comps):
            spec = {"dev": 0, "juros": 0, "fiscal": "motosserra", "priv": 1, "swap": 0, **kw}
            q = " and ".join(f"{k}=={v!r}" for k, v in spec.items())
            d = (allsims.query(q).set_index("sim")[col] - ref[col]).dropna()
            lo, med, hi = np.percentile(d, [10, 50, 90])
            small = abs(med) < {"pobreza_2025S2": 0.5, "renda_media_2025": 0.5, "infl_2025": 1.0, "embi_dez25": 20}[col]
            col_ = INK2 if small else (ORANGE if (med > 0) == (col != "renda_media_2025") else BLUE)
            a.plot([lo, hi], [yi, yi], color=col_, lw=2, solid_capstyle="round")
            a.scatter(med, yi, color=col_, s=40, zorder=3, edgecolor=SURF, linewidth=1.5)
            a.text(hi, yi + 0.22, f"{med:+.1f}" if abs(med) < 100 else f"{med:+.0f}", fontsize=8, color=INK2, ha="right")
        a.axvline(0, color=INK2, lw=0.8); a.set_title(title, fontsize=9.5)
        if col == "infl_2025":
            a.set_xscale("symlog", linthresh=10); a.set_xticks([-10, 0, 10, 100]); a.set_xticklabels(["−10", "0", "+10", "+100"])
    axes[0].set_yticks(y, [c[0] for c in comps])
    fig.suptitle("Efeito de cada mudança contra a referência (política efetiva) — mediana e faixa p10–p90\n"
                 "laranja = pior, azul = melhor para a população, cinza = efeito desprezível", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(OUT / "fig3_efeitos.png", dpi=150); plt.close(fig)


def fig_paths(p):
    picks = [("Referência (política efetiva)", REFERENCE, INK2),
             ("Baixo mult. + troca + juros", Scenario(fiscal="baixo_multiplicador", swap=True, rate=True), BLUE),
             ("Câmbio comp. + juros", Scenario(dev=True, rate=True), AQUA),
             ("Câmbio comp., juros reprimidos", Scenario(dev=True), ORANGE)]
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))
    for lab, sc, col in picks:
        o = simulate(p, sc, n=400, seed=7)
        for a, k, sc_ in [(ax[0], "pi", 100), (ax[1], "poverty", 100), (ax[2], "reserves", 1)]:
            v = o[k] * sc_
            a.fill_between(MONTHS, np.percentile(v, 10, 0), np.percentile(v, 90, 0), color=col, alpha=0.12, lw=0)
            a.plot(MONTHS, np.median(v, 0), color=col, label=lab)
    ax[0].set_yscale("log"); ax[0].set_yticks([1, 2, 5, 10, 20]); ax[0].set_yticklabels(["1", "2", "5", "10", "20"])
    ax[0].set_title("Inflação mensal, % (log)"); ax[1].set_title("Pobreza mensal implícita, %")
    ax[2].set_title("Reservas líquidas, US$ bi"); ax[2].axhline(0, color=INK2, lw=0.8)
    ax[1].legend(fontsize=8.5, loc="upper right")
    for a_ in ax:
        a_.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
        a_.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    fig.suptitle("Trajetórias de cenários selecionados (mediana e faixa p10–p90)", fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig4_trajetorias.png", dpi=150); plt.close(fig)


def main():
    p = load_calibrated()
    summary = pd.read_csv(OUT / "cenarios_resumo.csv")
    allsims = pd.read_parquet(OUT / "cenarios_simulacoes.parquet")
    fig_validation(p); fig_tradeoff(summary); fig_effects(allsims); fig_paths(p)
    print("ok")


if __name__ == "__main__":
    main()
