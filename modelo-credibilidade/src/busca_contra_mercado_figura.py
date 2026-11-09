"""Figura: sucesso pela banda por grau de indexação à meta, com mercado hostil (P2 e P1).

Uso: python -m src.busca_contra_mercado_figura
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .busca_contra_mercado import SAIDA

CORES = {"híbrido 5,5% do PIB, Taylor": "#1f6fb2", "híbrido 4,1% do PIB, alívio condicionado": "#2e8b57",
         "estratégia A com reservas do paper": "#888", "estratégia C sem piso do paper": "#bbb"}


def main():
    d = pd.read_csv(SAIDA / "curva_theta.csv")
    d = d[d.especificacao.isin(["P1", "P2"])]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, e in zip(axs, ("P2", "P1")):
        for pac, cor in CORES.items():
            g = d[(d.pacote == pac) & (d.especificacao == e)].groupby("theta")["p_bil"].mean()
            ax.plot(g.index, g.values, "o-", color=cor, label=pac)
        ax.axhline(0.5, color="#ccc", lw=0.8, ls="--")
        ax.set_xlabel("θ: fração da inércia reajustada pela meta")
        ax.set_title(f"{e}: sucesso pela banda com mercado hostil (λ ≤ 0,3, só pune)", fontsize=9.5, loc="left")
    axs[0].set_ylabel("sucesso pela banda")
    axs[0].legend(frameon=False, fontsize=7.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(SAIDA / "fig_contra_mercado.png", dpi=160)


if __name__ == "__main__":
    main()
