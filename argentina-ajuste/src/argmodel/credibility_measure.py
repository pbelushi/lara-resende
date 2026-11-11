"""
Parte 2: credibilidade efetiva 2024–25 medida pelo REM (BCRA).

No modelo, a expectativa de inflação do mês t é
    πe_t = π_{t−1} + c_t · (âncora_t − π_{t−1}),
com âncora = crawl anunciado (referência sem meta de juros). Então a credibilidade observada é
    c_t = (π_{t−1} − E_REM[π_t]) / (π_{t−1} − âncora_t),
com E_REM[π_t] = mediana do REM feito no fim do mês t−1 para o mês t. O mesmo vale para o câmbio,
trocando a inflação esperada pela depreciação esperada (variação da média mensal do câmbio
esperado). Agregamos por período com mínimos quadrados sem intercepto (y = E − π_{t−1},
x = âncora − π_{t−1}), o que dá mais peso aos meses em que âncora e inércia mais divergem.

λ implícito = λ_ref + [logit(c_obs) − logit(c_modelo)] / k_fx, onde c_modelo é a credibilidade
do câmbio no caminho calibrado no mesmo período.

Entrada: data/rem_medianas.csv. Uso:  python -m argmodel.credibility_measure
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import logit

from .experiment import REFERENCE, load_calibrated
from .model import ROOT, _crawl_actual, load_actuals, simulate

PERIODS = {"1º tri/24 (pós-salto)": range(1, 4), "abr–dez/24": range(4, 13),
           "jan–abr/25 (crawl 2%→1%)": range(13, 17), "mai–dez/25 (bandas)": range(17, 25)}
MIN_GAP = 1.0      # p.p.: meses em que âncora ≈ inércia não informam a credibilidade


def build(p=None) -> pd.DataFrame:
    p = p or load_calibrated()
    act = load_actuals().set_index("t")
    rem = pd.read_csv(ROOT / "data" / "rem_medianas.csv")
    rem["t_target"] = [(pd.Period(s, "M") - pd.Period("2023-12", "M")).n + 1 for s in rem.survey_month]
    rem = rem.set_index("t_target")
    o = simulate(p, REFERENCE, n=1, stochastic=False)
    rows = []
    for t in range(1, 25):
        pi_prev = act.loc[t - 1, "cpi_mom_pct"]
        anchor = 100 * _crawl_actual(t, p)
        r = rem.loc[t] if t in rem.index else None
        e_pi = r["infl_next"] if r is not None else np.nan
        nowcast = r["infl_cur"] if r is not None and pd.notna(r["infl_cur"]) else pi_prev
        e_dep = (100 * (r["fx_next"] / r["fx_cur"] - 1)
                 if r is not None and pd.notna(r.get("fx_next")) and pd.notna(r.get("fx_cur")) else np.nan)
        rows.append({"t": t, "mes": str(pd.Period("2023-12", "M") + t), "pi_prev": pi_prev, "pi_obs": act.loc[t, "cpi_mom_pct"],
                     "ancora": anchor, "rem_nowcast": nowcast, "rem_pi": e_pi, "rem_dep": e_dep,
                     "modelo_pie": 100 * o["pie"][0, t], "modelo_cred": o["cred_x"][0, t]})
    df = pd.DataFrame(rows)
    gap = df.pi_prev - df.ancora
    ok = gap.abs() >= MIN_GAP
    df["cred_rem_pi"] = np.where(ok, (df.pi_prev - df.rem_pi) / gap, np.nan)
    # variante: inércia vista pelo analista (o próprio nowcast do mês t−1, sem o dado oficial ainda)
    gap2 = df.rem_nowcast - df.ancora
    df["cred_rem_pi_nowcast"] = np.where(gap2.abs() >= MIN_GAP, (df.rem_nowcast - df.rem_pi) / gap2, np.nan)
    df["cred_rem_cambio"] = np.where(ok, (df.pi_prev - df.rem_dep) / gap, np.nan)
    return df


def by_period(df: pd.DataFrame, p=None) -> pd.DataFrame:
    p = p or load_calibrated()
    cr = p["credibility"]
    out = []
    for name, ts in PERIODS.items():
        g = df[df.t.isin(list(ts))]
        x = g.ancora - g.pi_prev
        row = {"periodo": name, "meses_informativos": int((x.abs() >= MIN_GAP).sum()),
               "cred_modelo": g.modelo_cred.mean()}
        for lab, col, base in [("inflacao", "rem_pi", "pi_prev"), ("inflacao_nowcast", "rem_pi", "rem_nowcast")]:
            x = g.ancora - g[base]
            m = (x.abs() >= MIN_GAP) & g[col].notna()
            if m.sum() == 0:
                row[f"cred_{lab}"] = np.nan; row[f"lambda_{lab}"] = np.nan; continue
            y = g[col] - g[base]
            c = float((x[m] * y[m]).sum() / (x[m] ** 2).sum())
            row[f"cred_{lab}"] = c
            cc = np.clip(c, 0.02, 0.98)
            row[f"lambda_{lab}"] = float(np.clip(cr["lambda_ref"] + (logit(cc) - logit(row["cred_modelo"])) / cr["k_fx"], 0, 1))
        out.append(row)
    return pd.DataFrame(out)


ANNOUNCED = lambda t: 2.0 if t <= 13 else 1.0    # crawl anunciado; desde mai/25, deriva do teto da banda
INFL_2024_REM_DEZ23 = 213.0   # REM dez/23: inflação esperada para 2024 (La Nación, 12/01/2024)


def fx_table(p=None) -> pd.DataFrame:
    """Credibilidade do câmbio pelo REM: depreciação mensal esperada entre o mês seguinte e dezembro
    (médias mensais esperadas) contra o crawl anunciado e a inflação esperada no período."""
    p = p or load_calibrated()
    rem = pd.read_csv(ROOT / "data" / "rem_medianas.csv")
    o = simulate(p, REFERENCE, n=1, stochastic=False)
    rows = []
    for r in rem.itertuples():
        if pd.isna(r.fx_dec) or pd.isna(r.fx_next) or pd.isna(r.fx_dec_month):
            continue
        t1 = (pd.Period(r.survey_month, "M") - pd.Period("2023-12", "M")).n + 1   # mês de fx_next
        h = (pd.Period(r.fx_dec_month, "M") - pd.Period(r.survey_month, "M")).n - 1
        if h < 2 or pd.Period(r.fx_dec_month, "M") > pd.Period("2025-12", "M"):
            continue       # 2026: a banda passa a ser indexada à inflação; fora do horizonte
        dep = 100 * ((r.fx_dec / r.fx_next) ** (1 / h) - 1)
        if r.survey_month == "2023-12":
            pie = 100 * ((1 + INFL_2024_REM_DEZ23 / 100) ** (1 / 12) - 1)
        else:
            vals = [v for v in (r.infl_next, r.infl_next2) if pd.notna(v)]
            pie = float(np.mean(vals)) if vals else np.nan
        crawl = ANNOUNCED(t1)
        gap = pie - crawl
        tt = list(range(max(t1, 1), min(t1 + h, 24) + 1))
        rows.append({"pesquisa": r.survey_month, "horizonte_meses": h, "dep_esperada": dep, "crawl_anunciado": crawl,
                     "infl_esperada": pie, "cred_cambio_rem": (pie - dep) / gap if abs(gap) >= MIN_GAP else np.nan,
                     "cred_cambio_modelo": float(o["cred_x"][0, tt].mean()) if tt else np.nan})
    return pd.DataFrame(rows)


def fig_measure(df, fx, path=None):
    from .report import plt, BLUE, ORANGE, AQUA, INK2, MONTHS
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    x = MONTHS[df.t.values]
    a.plot(x, df.pi_obs, color=ORANGE, label="Observada (INDEC)")
    a.plot(x, df.rem_pi, color=AQUA, ls="--", label="Esperada pelo REM (pesquisa do mês anterior)")
    a.plot(x, df.modelo_pie, color=BLUE, label="Esperada no modelo calibrado")
    a.set_yscale("log"); a.set_yticks([1, 2, 5, 10, 20]); a.set_yticklabels(["1", "2", "5", "10", "20"])
    a.set_title("Inflação mensal, % (escala log)", loc="left"); a.legend(fontsize=8.5)
    xb = [pd.Period(s_, "M").to_timestamp() + pd.offsets.MonthBegin(1) for s_ in fx.pesquisa]
    b.plot(xb, fx.cred_cambio_modelo, color=BLUE, marker="o", ms=4, label="Modelo calibrado")
    b.plot(xb, fx.cred_cambio_rem, color=AQUA, marker="o", ms=5, ls="--", label="REM (câmbio esperado × crawl)")
    b.axhline(0.7, color=INK2, lw=1, ls=":"); b.text(xb[0], 0.73, "limiar para baixo mult. + juros vencer", color=INK2, fontsize=8)
    b.set_ylim(-0.15, 1.1); b.set_title("Credibilidade do câmbio anunciado (0 a 1)", loc="left"); b.legend(fontsize=8.5, loc="lower right")
    for ax in (a, b):
        import matplotlib.dates as mdates
        from matplotlib.ticker import FuncFormatter
        mes = "jan fev mar abr mai jun jul ago set out nov dez".split()
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda v, _: f"{mes[mdates.num2date(v).month - 1]}/{mdates.num2date(v).year % 100:02d}"))
    fig.tight_layout()
    fig.savefig(path or (ROOT / "outputs" / "fig_credibilidade_rem.png"), dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    df = build()
    per = by_period(df)
    out = ROOT / "outputs"
    df.to_csv(out / "credibilidade_rem_mensal.csv", index=False)
    df["erro_rem"] = df.pi_obs - df.rem_pi
    per.to_csv(out / "credibilidade_rem_periodos.csv", index=False)
    fx = fx_table()
    fx.to_csv(out / "credibilidade_rem_cambio.csv", index=False)
    fig_measure(df, fx)
    pd.set_option("display.width", 220)
    print(fx.round(2).to_string(index=False))
    print(df.round(2).to_string(index=False))
    print(per.round(2).to_string(index=False))
    for name, ts in PERIODS.items():
        g = df[df.t.isin(list(ts))]
        print(f"{name}: erro médio do REM (obs − esperado) {g.erro_rem.mean():+.2f} p.p./mês")


if __name__ == "__main__":
    main()
