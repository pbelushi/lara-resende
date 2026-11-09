"""Figura do estudo de evento: EMBI+ Brasil em torno do anúncio das três regras (mês −1 = 100).

Uso: python -m src.regras_fiscais_figura
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .regras_fiscais_eventos import EVENTOS, SAIDA, serie_mensal

CORES = {"LRF": "#888", "Teto de gastos": "#1f6fb2", "Arcabouço": "#e67e22"}


def main():
    d = serie_mensal()
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, marco in zip(axs, ("anuncio", "aprovacao")):
        for ev, datas in EVENTOS.items():
            t0 = pd.Timestamp(datas[marco])
            ks = range(-6, 13)
            base = d["embi"].get(t0 - pd.DateOffset(months=1))
            y = [100 * d["embi"].get(t0 + pd.DateOffset(months=k), float("nan")) / base for k in ks]
            ax.plot(list(ks), y, "o-", ms=3, color=CORES[ev], label=f"{ev} ({t0:%m/%Y})")
        ax.axvline(0, color="#ccc", lw=0.8)
        ax.axhline(100, color="#eee", lw=0.8)
        ax.set_xlabel("meses em relação ao " + ("anúncio" if marco == "anuncio" else "mês de aprovação"))
        ax.set_title("EMBI+ Brasil, mês −1 = 100", fontsize=10, loc="left")
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(SAIDA / "fig_embi_eventos.png", dpi=160)


if __name__ == "__main__":
    main()
