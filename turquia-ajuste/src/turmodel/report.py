"""
Sensibilidade e figura da busca turca.

Sensibilidade (sem recalibrar): hiato → inflação três vezes maior (kappa = 1,5), para testar se o canal fiscal de
demanda passa a importar; corrida cambial pela metade (omega e sinal × 0,5), para testar a heterodoxa com menos
risco de fuga; credibilidade inicial mais alta (λ0 ~ U(0,3; 0,6)).

Uso:  PYTHONPATH=src python -m turmodel.report
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd

from . import search as S
from .model import MESES, T, dados, politica_observada, simulate

NOMES = {"observada": "Política observada", "ref_so_juros": "Aperto tradicional (juro real de 10% a 6%)",
         "ref_anticiclica": "Aperto tradicional + corte de demanda",
         "ref_heterodoxa": "Heterodoxa: ajuste de qualidade + juro real baixo + rendas",
         "ref_fiscal_qualidade": "Só ajuste de qualidade + juro real baixo",
         "melhor": "Melhor da busca (juro real alto + administrados pela meta)"}


def avaliar(p, c, n, lam0, base, O):
    X = simulate(p, {**S.politica(c), "lambda0": lam0}, n=n, seed=7, base=base)
    return X, S.metricas(X, O)


def main():
    combos = json.loads((S.OUT / "combinacoes.json").read_text())
    fin = pd.read_csv(S.OUT / "finalistas.csv")
    piv = fin[fin.id != "observada"].pivot_table(index="id", columns="variante", values="p_sucesso")
    # melhor: entre as finalistas a até 4 pontos do maior sucesso mínimo (nas duas variantes), a de menor custo em PIB
    pib = fin[fin.id != "observada"].pivot_table(index="id", columns="variante", values="pib_vs_obs").min(axis=1)
    smin = piv.min(axis=1)
    melhor = pib[smin >= smin.max() - 0.04].idxmax()
    est = {"ref_so_juros": combos["ref_so_juros"], "ref_anticiclica": combos["ref_anticiclica"],
           "ref_heterodoxa": combos["ref_heterodoxa"], "ref_fiscal_qualidade": combos["ref_fiscal_qualidade"],
           "melhor": combos[melhor]}
    n = 1000
    linhas, caminhos = [], {}
    cenarios = {"base": lambda p: None,
                "kappa_1,5": lambda p: p["inflacao"].__setitem__("kappa", 1.5),
                "corrida_metade": lambda p: (p["cambio"].__setitem__("omega", p["cambio"]["omega"] / 2),
                                             p["cambio"].__setitem__("sinal", p["cambio"]["sinal"] / 2)),
                "lambda0_alto": lambda p: None}
    for v in S.VARIANTES:
        for cen, muda in cenarios.items():
            p = copy.deepcopy(S.carregar(v))
            muda(p)
            obs = politica_observada(p)
            base = simulate(p, obs, n=1, stochastic=False)
            O = simulate(p, obs, n=n, seed=7)
            lam0 = np.random.default_rng(2027).uniform(*((0.3, 0.6) if cen == "lambda0_alto" else S.LAMBDA0), n)
            if cen == "base":
                caminhos[(v, "observada")] = np.median(O["yoy"], axis=0)
            for k, c in est.items():
                X, m = avaliar(p, c, n, lam0, base, O)
                linhas.append({"variante": v, "cenario": cen, "estrategia": k, **m})
                if cen == "base":
                    caminhos[(v, k)] = np.median(X["yoy"], axis=0)
    d = pd.DataFrame(linhas)
    d.to_csv(S.OUT / "sensibilidade.csv", index=False)
    (S.OUT / "melhor.json").write_text(json.dumps({"id": melhor, **combos[melhor]}, indent=1))
    pd.set_option("display.width", 220)
    print("melhor:", melhor, combos[melhor])
    print(d.pivot_table(index=["variante", "estrategia"], columns="cenario", values="p_sucesso").round(2).to_string())
    print(d.pivot_table(index=["variante", "estrategia"], columns="cenario", values="infl_set26").round(1).to_string())
    print(d.pivot_table(index=["variante", "estrategia"], columns="cenario", values="pib_vs_obs").round(1).to_string())

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x = MESES.to_timestamp()
    cores = {"observada": "#555", "ref_so_juros": "#c0392b", "ref_heterodoxa": "#2e8b57", "ref_fiscal_qualidade": "#8fbc8f",
             "melhor": "#1f6fb2"}
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, v in zip(axs, S.VARIANTES):
        ax.plot(x, dados().reindex(MESES)["cpi_yoy"].values, color="#000", lw=1, ls=":", label="Inflação observada (dados)")
        for k, cor in cores.items():
            ax.plot(x, caminhos[(v, k)], color=cor, lw=1.6, label=NOMES[k] + (" (modelo)" if k == "observada" else ""))
        ax.set_title(("Inércia baixa" if v.startswith("A") else "Inércia alta") + ": inflação em 12 meses, mediana (%)",
                     fontsize=10, loc="left")
        ax.set_ylim(0, 105)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=8, loc="lower center", ncol=3)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(S.OUT / "fig_turquia_inflacao.png", dpi=160)


if __name__ == "__main__":
    main()
