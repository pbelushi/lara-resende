import sys, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
base = sys.argv[1]
d = pd.read_csv(f"{base}/finalistas_lambda_dinamico.csv")
fam = {"gradual": ("Gradual de baixo custo", "#2e8b57"), "choque": ("Choque", "#c0392b"), "paper": ("Estratégias do paper", "#888")}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
x = d[(d.regra == "central") & (d.especificacao == "P2")]
anos = [0, 1, 2, 4, 10]
for f, (nome, cor) in fam.items():
    g = x[x.familia == f]
    y = [0.35] + [g[f"lam_pi_ano{k}"].mean() for k in (1, 2, 4, 10)]
    a1.plot(anos, y, "o-", color=cor, label=nome)
gS = x
a1.plot(anos, [0.35] + [gS[f"lam_pi_S_ano{k}"].mean() for k in (1, 2, 4, 10)], "o--", color="#555", label="Sem ajuste (S)")
a1.set_xlabel("anos"); a1.set_ylabel("λ_π médio"); a1.set_title("Credibilidade da meta com λ endógeno (P2, regra central)", fontsize=10, loc="left")
a1.axhline(0.5, color="#ccc", lw=0.8); a1.legend(frameon=False, fontsize=8); a1.set_ylim(0, 0.6)
regras = ["estatico", "metade", "simetrico", "central", "anual", "cruzado"]
rot = {"estatico": "λ fixo", "metade": "metade", "simetrico": "simétrica", "central": "central", "anual": "anual", "cruzado": "cruzada"}
w = 0.27
y2 = d[d.especificacao == "P2"]
for k, (f, (nome, cor)) in enumerate(fam.items()):
    v = [y2[(y2.familia == f) & (y2.regra == r)]["p_bil"].mean() for r in regras]
    a2.bar(np.arange(len(regras)) + (k - 1) * w, v, w, color=cor, label=nome)
a2.set_xticks(range(len(regras))); a2.set_xticklabels([rot[r] for r in regras], fontsize=8)
a2.set_ylabel("sucesso pela banda"); a2.set_title("Sucesso por regra de atualização do λ (P2)", fontsize=10, loc="left")
a2.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(f"{base}/fig_lambda_dinamico.png", dpi=160)
