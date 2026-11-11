"""Figura da v2 (λ endógeno): trajetórias medianas de λ_câmbio, λ_juros e λ_fiscal nos cenários de interesse.

Uso:  PYTHONPATH=src python -m argmodel.dinamico_figura
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .dinamico import OUT

CORES = {"Referência (Milei)": "#555", "BMULT + Juros+": "#1f6fb2", "Câmbio comp. + Juros+ + BMULT": "#e67e22",
         "Gradual": "#2e8b57", "Motosserra + Juros+": "#c0392b"}


def main():
    tr = pd.read_csv(OUT / "trajetorias_lambda.csv")
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, (col, tit) in zip(axs, [("lam_fx", "λ câmbio (crawl/bandas ou SCRER)"), ("lam_rate", "λ juros (meta do BC)"),
                                     ("lam_f", "λ fiscal (adesão à troca)")]):
        for nome, cor in CORES.items():
            g = tr[tr.cenario == nome]
            ax.plot([0] + list(g.mes), [0.75] + list(g[col]), "o-", color=cor, ms=3, label=nome)
        ax.set_title(tit, fontsize=10, loc="left")
        ax.set_xlabel("meses desde dez/2023")
        ax.axhline(0.75, color="#ddd", lw=0.8)
    axs[0].set_ylabel("λ (mediana)")
    axs[0].legend(frameon=False, fontsize=7.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_lambda_endogeno.png", dpi=160)


if __name__ == "__main__":
    main()
