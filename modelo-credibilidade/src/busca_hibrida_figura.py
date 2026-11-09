"""Figura da busca híbrida: sucesso × atividade das finalistas (P2 e P1, λ endógeno, regra central).

Uso: python -m src.busca_hibrida_figura
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .busca_hibrida import SAIDA


def familia(r):
    if r["id"].startswith("ant_ref"):
        return "paper"
    if r["id"].startswith("ant_"):
        return "choque" if r["mult_medio"] >= 0.55 else "gradual"
    return "irrestrito" if r["id"].startswith("u") else "hibrido"


def main():
    f = pd.read_csv(SAIDA / "fase3_finalistas.csv")
    f["familia"] = f.apply(familia, axis=1)
    f.to_csv(SAIDA / "fase3_finalistas.csv", index=False)
    x = f[f.regra == "central"].groupby(["id", "familia", "especificacao"])[["p_bil", "dif_1-16"]].mean().reset_index()
    est = {"hibrido": ("Híbrido (início concentrado, baixo multiplicador)", "#1f6fb2", "o"),
           "choque": ("Choque (busca anterior)", "#c0392b", "s"),
           "gradual": ("Gradual longo (busca anterior)", "#2e8b57", "^"),
           "irrestrito": ("Espaço irrestrito (controle)", "#e67e22", "D"),
           "paper": ("Estratégias do paper", "#888", "x")}
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, esp in zip(axs, ("P2", "P1")):
        for k, (nome, cor, mk) in est.items():
            g = x[(x.familia == k) & (x.especificacao == esp)]
            ax.scatter(g["dif_1-16"], g["p_bil"], color=cor, marker=mk, s=28, label=nome, alpha=0.85)
        ax.axvline(0, color="#ccc", lw=0.8)
        ax.set_xlabel("atividade contra a referência sem ajuste até 2030 (pontos do PIB de um ano)")
        ax.set_title(f"{esp}: sucesso pela banda × atividade, λ endógeno", fontsize=10, loc="left")
    axs[0].set_ylabel("sucesso pela banda")
    axs[0].legend(frameon=False, fontsize=7.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(SAIDA / "fig_busca_hibrida.png", dpi=160)


if __name__ == "__main__":
    main()
