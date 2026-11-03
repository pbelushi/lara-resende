"""Visualizações (seção 8 da v2). Cada figura sai em PNG (300 dpi) e SVG.

Gráficos 1 a 7 são gerados por especificação de inflação (sufixo _P1, _P2, _P3); 8 a 12 comparam
especificações. Identidade de cenário = cor + estilo de linha, nunca só a cor.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ESTILO = {"A": "-", "B": "--", "C": ":"}
TINTA = "#333333"
TINTA_SEC = "#6b6b6b"
GRADE = "#e6e6e6"
NOMES_ESPEC = {"P1": "P1 · Phillips híbrida", "P2": "P2 · Phillips achatada", "P3": "P3 · Fechamento fiscal (FTPL)"}

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": TINTA_SEC, "axes.labelcolor": TINTA, "xtick.color": TINTA_SEC,
    "ytick.color": TINTA_SEC, "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "lines.linewidth": 2, "figure.dpi": 100, "svg.fonttype": "none",
})


def _salvar(fig, saida: Path, nome: str) -> list[Path]:
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = [saida / f"{nome}.png", saida / f"{nome}.svg"]
    fig.savefig(arquivos[0], dpi=300, bbox_inches="tight")
    fig.savefig(arquivos[1], bbox_inches="tight")
    plt.close(fig)
    return arquivos


def _eixo_lambda(ax, rotulo="Adesão do mercado (λ)"):
    ax.set_xlabel(rotulo)
    ax.set_xlim(0, 1)


def _curvas_prob(ax, mc, ls, cens, anotar=True):
    for chave, c in cens.items():
        m = mc[mc["cenario"] == chave]
        if m.empty:
            continue
        cor = c["cor"]
        ax.plot(m["lambda"], 100 * m["p_sucesso"], color=cor, ls=ESTILO.get(chave, "-"), label=c["nome"])
        l80 = ls.loc[ls["cenario"] == chave, "lambda_star_80"]
        l80 = l80.iloc[0] if len(l80) else np.nan
        if np.isfinite(l80):
            ax.axvline(l80, color=cor, lw=1, ls=ESTILO.get(chave, "-"), alpha=0.7)
            if anotar:
                ax.annotate(f"λ*₈₀ = {l80:.2f}", (l80, 3), xytext=(3, 0), textcoords="offset points",
                            color=TINTA, fontsize=7.5, rotation=90, va="bottom")
    for y in (50, 80):
        ax.axhline(y, color=TINTA_SEC, lw=0.8, alpha=0.6)
    ax.set_ylim(0, 100)


# ---------------------------------------------------------------- 1 a 7 (por especificação)

def prob_sucesso(mc, ls, cens, saida: Path, sufixo: str, titulo_extra: str = ""):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    _curvas_prob(ax, mc, ls, cens)
    for y in (50, 80):
        ax.text(1.005, y, f"{y}%", color=TINTA_SEC, va="center", fontsize=8, transform=ax.get_yaxis_transform())
    ax.set_ylabel("Probabilidade de sucesso (%)")
    _eixo_lambda(ax, "Adesão do mercado (λ_π = λ_fiscal)")
    ax.set_title(f"Probabilidade de estabilizar a dívida com inflação controlada{titulo_extra}", loc="left",
                 color=TINTA)
    ax.legend(loc="upper left")
    return _salvar(fig, saida, f"1_prob_sucesso_lambda_{sufixo}")


def _faixa(mc, cens, saida, col, ylabel, titulo, nome, referencia, banda=None):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    if banda is not None:
        ax.axhspan(*banda, color=GRADE, alpha=0.7, lw=0, label="Faixa de tolerância")
    for chave, c in cens.items():
        m = mc[mc["cenario"] == chave]
        cor = c["cor"]
        ax.fill_between(m["lambda"], m[f"{col}_p10"], m[f"{col}_p90"], color=cor, alpha=0.15, lw=0)
        ax.plot(m["lambda"], m[f"{col}_p50"], color=cor, ls=ESTILO.get(chave, "-"),
                label=f"{c['nome']} (mediana; faixa 10–90%)")
    ax.axhline(referencia[0], color=TINTA, lw=1, ls="-.", label=referencia[1])
    ax.set_ylabel(ylabel)
    _eixo_lambda(ax)
    ax.set_title(titulo, loc="left", color=TINTA)
    ax.text(0, -0.16, "Percentis calculados só sobre trajetórias não explosivas.", transform=ax.transAxes,
            fontsize=7.5, color=TINTA_SEC)
    ax.legend(loc="best", fontsize=8)
    return _salvar(fig, saida, nome)


def divida_final(mc, cens, p, saida, sufixo):
    d0 = p["ini"]["d_gross0"]
    return _faixa(mc, cens, saida, "d_final", "Dívida bruta no fim do horizonte (% PIB)",
                  "Dívida bruta no fim do horizonte", f"2_divida_final_lambda_{sufixo}",
                  (d0, f"Dívida inicial ({d0:.1f}%)"))


def inflacao_final(mc, cens, p, saida, sufixo):
    meta, tol = p["pi_meta"], p["criterios"]["tolerancia_inflacao"]
    return _faixa(mc, cens, saida, "pi_final", "Inflação média nos últimos 8 trimestres (% a.a.)",
                  "Inflação média no fim do horizonte", f"3_inflacao_final_lambda_{sufixo}",
                  (meta, f"Meta ({meta:.1f}%)"), banda=(meta - tol, meta + tol))


def barras_lambda_star(ls, cens, saida, sufixo):
    medidas = [("lambda_star_det", "λ* determinístico"), ("lambda_star_50", "λ*₅₀"), ("lambda_star_80", "λ*₈₀")]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    larg = 0.26
    x = np.arange(len(medidas))
    for k, (chave, c) in enumerate(cens.items()):
        linha = ls[ls["cenario"] == chave].iloc[0]
        vals = [linha.get(m, np.nan) for m, _ in medidas]
        pos = x + (k - 1) * larg
        barras = ax.bar(pos, [v if np.isfinite(v) else 0 for v in vals], width=larg - 0.03, color=c["cor"],
                        label=c["nome"])
        for b, v in zip(barras, vals):
            if not np.isfinite(v):
                ax.bar(b.get_x() + b.get_width() / 2, 1.0, width=b.get_width(), fill=False,
                       edgecolor=c["cor"], hatch="//", lw=0.8)
            ax.text(b.get_x() + b.get_width() / 2, (v if np.isfinite(v) else 1.0) + 0.02,
                    f"{v:.2f}" if np.isfinite(v) else "não\natinge", ha="center", va="bottom",
                    fontsize=7.5, color=TINTA)
    ax.set_xticks(x, [r for _, r in medidas])
    ax.set_ylim(0, 1.2)
    ax.set_ylabel("Adesão mínima (λ*)")
    ax.set_title("Adesão mínima necessária por cenário (menor = mais robusto)", loc="left", color=TINTA)
    ax.legend(loc="upper left", fontsize=8, ncol=3)
    return _salvar(fig, saida, f"4_lambda_star_{sufixo}")


ROTULOS_LEQUE = {"d_gross": ("Dívida bruta (% PIB)", "divida"), "i": ("Selic (% a.a.)", "selic"),
                 "pi": ("Inflação 12m (% a.a.)", "inflacao"), "E": ("Câmbio (R$/US$, escala log)", "cambio")}


def leques(fans: dict, cens: dict, saida: Path, sufixo: str, lams=(0.3, 0.6, 0.9)):
    arquivos = []
    alfas = dict(zip(lams, (0.12, 0.2, 0.3)))
    estilos = dict(zip(lams, (":", "--", "-")))
    for var, (rotulo, nome) in ROTULOS_LEQUE.items():
        fig, axs = plt.subplots(1, len(cens), figsize=(11, 3.8), sharey=True)
        for ax, (chave, c) in zip(np.atleast_1d(axs), cens.items()):
            cor = c["cor"]
            notas = []
            for lam in lams:
                q = fans[(chave, lam)][var]
                t = np.arange(q.shape[1]) / 4
                ax.fill_between(t, q[0], q[2], color=cor, alpha=alfas[lam], lw=0)
                ax.plot(t, q[1], color=cor, ls=estilos[lam], lw=1.6, label=f"λ = {lam:.1f}")
                notas.append(f"λ={lam:.1f}: {100 * fans[(chave, lam)]['frac_explosiva']:.0f}%")
            ax.set_title(c["nome"], loc="left", color=TINTA, fontsize=9)
            ax.set_xlabel("Anos")
            if var == "pi":
                ax.set_ylim(-2, 25)
                ax.text(0.02, 0.97, "explosivas: " + " · ".join(notas), transform=ax.transAxes, fontsize=7,
                        color=TINTA_SEC, va="top")
            if var == "E":
                ax.set_yscale("log")
        np.atleast_1d(axs)[0].set_ylabel(rotulo)
        np.atleast_1d(axs)[0].legend(fontsize=8, title="mediana e faixa 10–90%\n(não explosivas)",
                                     title_fontsize=7.5, loc="upper right" if var != "pi" else "center right")
        fig.suptitle(f"Leques de trajetórias: {rotulo.split(' (')[0].lower()}", x=0.01, ha="left", color=TINTA)
        fig.tight_layout()
        arquivos += _salvar(fig, saida, f"5_leque_{nome}_{sufixo}")
    return arquivos


def mapas_sensibilidade(sens: dict, cens: dict, saida: Path, sufixo: str, rotulos: dict | None = None):
    rotulos = rotulos or {}
    params = list(sens)
    fig, axs = plt.subplots(len(params), len(cens), figsize=(11, 2.5 * len(params)), squeeze=False,
                            layout="constrained")
    im = None
    for i, nome in enumerate(params):
        s = sens[nome]
        for j, (chave, c) in enumerate(cens.items()):
            ax = axs[i, j]
            ax.grid(False)
            im = ax.pcolormesh(s["grade"], np.arange(len(s["valores"])), 100 * s[chave], cmap="Blues",
                               vmin=0, vmax=100, shading="nearest")
            ax.set_yticks(np.arange(len(s["valores"])), [f"{v:g}" for v in s["valores"]])
            l80 = [s["grade"][np.argmax(linha >= 0.8)] if (linha >= 0.8).any() else np.nan for linha in s[chave]]
            ax.plot(l80, np.arange(len(s["valores"])), color="#111111", lw=1.5, marker="o", ms=3, label="λ*₈₀")
            if i == 0:
                ax.set_title(c["nome"], loc="left", color=TINTA, fontsize=9)
            if j == 0:
                ax.set_ylabel(rotulos.get(nome, nome))
            if i == len(params) - 1:
                ax.set_xlabel("Adesão do mercado (λ)")
    axs[0, 0].legend(fontsize=7.5, loc="upper left")
    cb = fig.colorbar(im, ax=axs, shrink=0.6)
    cb.set_label("Probabilidade de sucesso (%)")
    fig.suptitle(f"Sensibilidade ({NOMES_ESPEC.get(sufixo, sufixo)}): P(sucesso) por λ e parâmetro "
                 "(linha = λ*₈₀)", x=0.01, ha="left", color=TINTA)
    return _salvar(fig, saida, f"6_sensibilidade_{sufixo}")


def decomposicao(dec, cens, saida, sufixo, lam=0.5):
    comps = [("juros", "Juros", "#4c6a92"), ("crescimento", "Crescimento nominal", "#9bb3cf"),
             ("primario", "Primário", "#b07a3b"), ("reservas", "Reservas / monetização", "#c9b18a")]
    anual = dec.groupby(["cenario", "ano"]).sum(numeric_only=True).reset_index()
    fig, axs = plt.subplots(1, len(cens), figsize=(11, 3.8), sharey=True)
    for ax, (chave, c) in zip(np.atleast_1d(axs), cens.items()):
        _barras_empilhadas(ax, anual[anual["cenario"] == chave], comps)
        a = anual[anual["cenario"] == chave]
        ax.plot(a["ano"], a["variacao"], color=TINTA, marker="o", ms=4, lw=1.4, label="Variação total")
        ax.set_title(c["nome"], loc="left", color=TINTA, fontsize=9)
        ax.set_xlabel("Ano")
    np.atleast_1d(axs)[0].set_ylabel("Contribuição para Δ dívida bruta (p.p. do PIB)")
    np.atleast_1d(axs)[0].legend(fontsize=7.5, loc="lower left")
    fig.suptitle(f"Decomposição da variação da dívida bruta (λ = {lam:.1f}, sem choques, "
                 f"{NOMES_ESPEC.get(sufixo, sufixo)})", x=0.01, ha="left", color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, f"7_decomposicao_divida_{sufixo}")


def _barras_empilhadas(ax, a, comps):
    pos = np.zeros(len(a))
    neg = np.zeros(len(a))
    for col, rot, cor in comps:
        v = a[col].values
        base = np.where(v >= 0, pos, neg)
        ax.bar(a["ano"], v, bottom=base, color=cor, width=0.75, label=rot, edgecolor="white", linewidth=1)
        pos += np.where(v >= 0, v, 0)
        neg += np.where(v < 0, v, 0)
    ax.axhline(0, color=TINTA_SEC, lw=0.8)


# ---------------------------------------------------------------- 8 a 12

def prob_por_especificacao(df, ls, cens, saida, variante="base", nome="8_prob_sucesso_especificacoes"):
    especs = [e for e in NOMES_ESPEC if e in df["especificacao"].unique()]
    fig, axs = plt.subplots(1, len(especs), figsize=(12, 4), sharey=True)
    for ax, e in zip(np.atleast_1d(axs), especs):
        m = df[(df["especificacao"] == e) & (df["variante"] == variante)]
        l = ls[(ls["especificacao"] == e) & (ls["variante"] == variante)]
        _curvas_prob(ax, m, l, cens, anotar=False)
        for chave, c in cens.items():
            v = l.loc[l["cenario"] == chave, "lambda_star_80"]
            txt = f"{v.iloc[0]:.2f}" if len(v) and np.isfinite(v.iloc[0]) else "—"
            ax.plot([], [], " ", label=f"λ*₈₀ {chave}: {txt}")
        ax.set_title(NOMES_ESPEC[e], loc="left", color=TINTA, fontsize=9)
        _eixo_lambda(ax, "λ (λ_π = λ_fiscal)")
        ax.legend(fontsize=7, loc="upper left")
    np.atleast_1d(axs)[0].set_ylabel("Probabilidade de sucesso (%)")
    fig.suptitle(f"P(sucesso) × adesão, por especificação de inflação (variante {variante})", x=0.01, ha="left",
                 color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, nome)


def fronteira(df, cens, saida, variante="base", marcas=(0.3, 0.6, 0.9)):
    especs = [e for e in NOMES_ESPEC if e in df["especificacao"].unique()]
    fig, axs = plt.subplots(1, len(especs), figsize=(12, 4.2), sharey=True, sharex=True)
    for ax, e in zip(np.atleast_1d(axs), especs):
        for chave, c in cens.items():
            m = df[(df["especificacao"] == e) & (df["variante"] == variante) & (df["cenario"] == chave)]
            m = m.sort_values("lambda")
            ax.plot(100 * m["p_divida_ok"], 100 * m["p_inflacao_ok"], color=c["cor"], ls=ESTILO[chave],
                    lw=1.6, label=c["nome"])
            for lam in marcas:
                r = m.iloc[(m["lambda"] - lam).abs().argmin()]
                ax.plot(100 * r["p_divida_ok"], 100 * r["p_inflacao_ok"], "o", ms=6, color=c["cor"],
                        mec="white", mew=1.2)
                ax.annotate(f"{lam:.1f}", (100 * r["p_divida_ok"], 100 * r["p_inflacao_ok"]), xytext=(4, 3),
                            textcoords="offset points", fontsize=7, color=TINTA)
        ax.set_xlim(-2, 102)
        ax.set_ylim(-2, 102)
        ax.set_xlabel("P(dívida estabilizada) (%)")
        ax.set_title(NOMES_ESPEC[e], loc="left", color=TINTA, fontsize=9)
    np.atleast_1d(axs)[0].set_ylabel("P(inflação controlada) (%)")
    np.atleast_1d(axs)[0].legend(fontsize=7.5, loc="lower left")
    fig.suptitle("Fronteira dívida × inflação: cada curva percorre λ de 0 a 1 (pontos em λ = 0,3; 0,6; 0,9)",
                 x=0.01, ha="left", color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, "9_fronteira_divida_inflacao")


def superficie(sup, areas, cens, saida, variante="base"):
    especs = [e for e in NOMES_ESPEC if e in sup["especificacao"].unique()]
    fig, axs = plt.subplots(len(cens), len(especs), figsize=(11, 10), squeeze=False, layout="constrained")
    im = None
    for j, e in enumerate(especs):
        for i, (chave, c) in enumerate(cens.items()):
            ax = axs[i, j]
            ax.grid(False)
            m = sup[(sup["especificacao"] == e) & (sup["variante"] == variante) & (sup["cenario"] == chave)]
            if m.empty:  # variante restrita a outro cenário
                ax.axis("off")
                ax.text(0.5, 0.5, f"{chave}: não simulado nesta variante", ha="center", va="center", fontsize=8,
                        color=TINTA_SEC, transform=ax.transAxes)
                continue
            Z = m.pivot(index="lambda_pi", columns="lambda_fiscal", values="p_sucesso")
            im = ax.pcolormesh(Z.columns, Z.index, 100 * Z.values, cmap="Blues", vmin=0, vmax=100, shading="nearest")
            if (Z.values >= 0.8).any() and (Z.values < 0.8).any():
                ax.contour(Z.columns, Z.index, Z.values, levels=[0.8], colors="#111111", linewidths=1.5)
            a = areas[(areas["especificacao"] == e) & (areas["variante"] == variante)
                      & (areas["cenario"] == chave)]["area_sucesso"]
            ax.set_title(f"{chave} · {e} · área ≥80%: {100 * a.iloc[0]:.0f}%", loc="left", color=TINTA, fontsize=8.5)
            ax.plot([0, 1], [0, 1], color=TINTA_SEC, lw=0.6, ls="--")
            if i == len(cens) - 1:
                ax.set_xlabel("λ_fiscal (crença nos superávits)")
            if j == 0:
                ax.set_ylabel(f"{c['nome']}\nλ_π (crença na meta)")
    cb = fig.colorbar(im, ax=axs, shrink=0.5)
    cb.set_label("Probabilidade de sucesso (%)")
    fig.suptitle(f"Superfície λ_π × λ_fiscal (variante {variante}); contorno = 80%, tracejado = diagonal",
                 x=0.01, ha="left", color=TINTA)
    return _salvar(fig, saida, f"10_superficie_{variante}")


def decomposicao_inflacao(decs: dict, cens: dict, saida: Path, lam: float = 0.5):
    comps = [("inercia", "Inércia", "#4c6a92"), ("expectativa", "Expectativa", "#9bb3cf"),
             ("hiato", "Hiato", "#6f9a6a"), ("cambio", "Câmbio", "#b07a3b"),
             ("fiscal", "Fiscal / monetização", "#a9473f"), ("choque", "Choque", "#c9b18a")]
    especs = [e for e in NOMES_ESPEC if e in decs]
    fig, axs = plt.subplots(len(especs), len(cens), figsize=(12, 3.2 * len(especs)), sharex=True, squeeze=False)
    for i, e in enumerate(especs):
        anual = decs[e].groupby(["cenario", "ano"]).mean(numeric_only=True).reset_index()
        for j, (chave, c) in enumerate(cens.items()):
            ax = axs[i, j]
            a = anual[anual["cenario"] == chave]
            _barras_empilhadas(ax, a, comps)
            ax.plot(a["ano"], a["pi"], color=TINTA, marker="o", ms=3.5, lw=1.4, label="Inflação")
            ax.set_title(f"{c['nome']} · {e}", loc="left", color=TINTA, fontsize=8.5)
            if j == 0:
                ax.set_ylabel("p.p. (média anual)")
            if i == len(especs) - 1:
                ax.set_xlabel("Ano")
    axs[0, 0].legend(fontsize=7, loc="upper right", ncol=2)
    fig.suptitle(f"Decomposição da inflação por especificação (λ = {lam:.1f}, sem choques)", x=0.01, ha="left",
                 color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, "11_decomposicao_inflacao")


def ordenamento(ordem: pd.DataFrame, cens: dict, saida: Path, variantes: list[str]):
    """Heatmap de posições 1–3: linhas = variante, colunas = especificação × cenário."""
    especs = [e for e in NOMES_ESPEC if e in ordem["especificacao"].unique()]
    variantes = [v for v in variantes if v in ordem["variante"].unique()]
    chaves = list(cens)
    M = np.full((len(variantes), len(especs) * len(chaves)), np.nan)
    for i, v in enumerate(variantes):
        for j, e in enumerate(especs):
            for k, ch in enumerate(chaves):
                r = ordem[(ordem["variante"] == v) & (ordem["especificacao"] == e) & (ordem["cenario"] == ch)]
                if len(r):
                    M[i, j * len(chaves) + k] = r["posicao"].iloc[0]
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["#2b6a99", "#9cc3df", "#eef3f8"])
    fig, ax = plt.subplots(figsize=(1.0 + 0.55 * M.shape[1], 0.9 + 0.38 * len(variantes)))
    ax.grid(False)
    ax.imshow(M, cmap=cmap, vmin=0.5, vmax=3.5, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if np.isfinite(M[i, j]):
                ax.text(j, i, f"{int(M[i, j])}º", ha="center", va="center", fontsize=8,
                        color="white" if M[i, j] == 1 else TINTA)
    ax.set_xticks(np.arange(M.shape[1]), [ch for _ in especs for ch in chaves])
    ax.set_yticks(np.arange(len(variantes)), variantes)
    for j, e in enumerate(especs):
        ax.text(j * len(chaves) + (len(chaves) - 1) / 2, -0.9, e, ha="center", va="bottom", fontsize=9, color=TINTA)
        if j:
            ax.axvline(j * len(chaves) - 0.5, color="white", lw=3)
    ax.set_title("Ordenamento por robustez (1º = menor λ*₈₀) por especificação e variante", loc="left",
                 color=TINTA, pad=22)
    for s in ax.spines.values():
        s.set_visible(False)
    return _salvar(fig, saida, "12_ordenamento_variantes")


def validacao(resultados: dict, saida: Path):
    chaves = list(resultados)
    especs = sorted({e for e, _ in chaves})
    episodios = list(dict.fromkeys(ep for _, ep in chaves))
    fig, axs = plt.subplots(2, len(episodios), figsize=(11, 6.5), squeeze=False)
    cores = {"P1": "#0072B2", "P2": "#56B4E9", "P3": "#D55E00"}
    estilos = {"P1": "-", "P2": "--", "P3": "-."}
    for j, ep in enumerate(episodios):
        for i, (var, rot) in enumerate((("pi", "Inflação 12m (% a.a.)"), ("r_long", "NTN-B 10 anos (% a.a.)"))):
            ax = axs[i, j]
            r0 = resultados[(especs[0], ep)]
            ax.plot(r0["datas"], r0["dados"][var], color=TINTA, lw=2.2, label="Observado")
            for e in especs:
                r = resultados[(e, ep)]
                th = f", θ={r['theta']}" if r["theta"] is not None else ""
                ax.plot(r["datas"], r["simulado"]["melhor"][var], color=cores[e], ls=estilos[e], lw=1.6,
                        label=f"{e} (λ={r['lambda_melhor']:.2f}{th})")
            if i == 0:
                ax.set_title(ep, loc="left", color=TINTA, fontsize=9)
            if j == 0:
                ax.set_ylabel(rot)
            ax.tick_params(axis="x", labelrotation=30)
            ax.legend(fontsize=7)
    fig.suptitle("Validação por especificação: melhor ajuste com a política efetivamente adotada", x=0.01,
                 ha="left", color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, "17_validacao_historica")


# ---------------------------------------------------------------- v2.2

def bootstrap_delta(bd: pd.DataFrame, saida: Path, variantes: list[str]):
    """Forest plot de Δλ*₈₀ = λ*₈₀(C) − λ*₈₀(A) com IC de 95% (bootstrap pareado)."""
    especs = [e for e in NOMES_ESPEC if e in bd["especificacao"].unique()]
    variantes = [v for v in variantes if v in bd["variante"].unique()]
    cores = {"P1": "#0072B2", "P2": "#56B4E9", "P3": "#D55E00"}
    marc = {"P1": "o", "P2": "s", "P3": "D"}
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(variantes) + 1.6))
    for j, e in enumerate(especs):
        for i, v in enumerate(variantes):
            r = bd[(bd["especificacao"] == e) & (bd["variante"] == v)]
            if r.empty:
                continue
            r = r.iloc[0]
            y = i + (j - 1) * 0.22
            ax.plot([r["ic_lo_80"], r["ic_hi_80"]], [y, y], color=cores[e], lw=1.6)
            ax.plot(r["delta_80"], y, marc[e], color=cores[e], ms=5, mec="white", mew=0.8,
                    label=NOMES_ESPEC[e] if i == 0 else None, alpha=0.5 if r["pouco_confiavel_80"] else 1)
    ax.axvline(0, color=TINTA, lw=1)
    ax.set_yticks(range(len(variantes)), variantes)
    ax.invert_yaxis()
    ax.set_xlabel("Δλ*₈₀ = λ*₈₀(C) − λ*₈₀(A)   (negativo: C exige menos adesão)")
    ax.set_title("Bootstrap pareado: IC de 95% da diferença de adesão mínima (marcadores claros: >20% censura)",
                 loc="left", color=TINTA, fontsize=9)
    ax.legend(fontsize=7.5, loc="lower right")
    return _salvar(fig, saida, "13_bootstrap_delta")


def alongamento(df: pd.DataFrame, info: dict, saida: Path, pares: list[tuple[str, str]]):
    """P(sucesso) × λ em P3 com φ = 0,25, sem e com alongamento."""
    fig, axs = plt.subplots(1, len(pares), figsize=(5.2 * len(pares), 4), sharey=True)
    for ax, (var, titulo) in zip(np.atleast_1d(axs), pares):
        m = df[(df["especificacao"] == "P3") & (df["variante"] == var)]
        for ch, c in info.items():
            mm = m[m["cenario"] == ch]
            ax.plot(mm["lambda"], 100 * mm["p_sucesso"], color=c["cor"], ls=ESTILO[ch], label=c["nome"])
        for y in (50, 80):
            ax.axhline(y, color=TINTA_SEC, lw=0.8, alpha=0.6)
        ax.set_ylim(0, 100)
        _eixo_lambda(ax)
        ax.set_title(titulo, loc="left", color=TINTA, fontsize=9)
    np.atleast_1d(axs)[0].set_ylabel("Probabilidade de sucesso (%)")
    np.atleast_1d(axs)[0].legend(fontsize=7.5, loc="upper left")
    fig.suptitle("Alongamento da dívida em P3 com lacuna inicial não precificada (φ = 0,25)", x=0.01, ha="left",
                 color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, "14_alongamento")


def erpt_lp(est: pd.DataFrame, saida: Path):
    """Repasse acumulado por horizonte (IPCA, amostra completa), OLS e IV, com IC por bootstrap em blocos."""
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for metodo, cor, est_l in (("LP OLS", "#0072B2", "-"), ("LP IV", "#D55E00", "--")):
        m = est[(est["metodo"] == metodo) & (est["indice"] == "ipca") & (est["amostra"] == "completa (dummy 2020)")]
        m = m.sort_values("h")
        ax.plot(m["h"], 100 * m["erpt"], color=cor, ls=est_l, label=metodo)
        ic = m.dropna(subset=["ic_lo"])
        ax.errorbar(ic["h"] + (0.15 if metodo == "LP IV" else 0), 100 * ic["erpt"],
                    # o ponto pode cair fora do IC percentil do bootstrap: barras truncadas em zero
                    yerr=[np.maximum(100 * (ic["erpt"] - ic["ic_lo"]), 0), np.maximum(100 * (ic["ic_hi"] - ic["erpt"]), 0)],
                    fmt="o", color=cor, ms=4, capsize=3, lw=1.2)
    ax.axhline(0, color=TINTA_SEC, lw=0.8)
    ax.set_xlabel("Horizonte (meses)")
    ax.set_ylabel("Repasse acumulado ao IPCA (% da depreciação)")
    ax.set_title("Repasse cambial por projeções locais (IC de 95% por bootstrap em blocos)", loc="left", color=TINTA)
    ax.legend(fontsize=8)
    return _salvar(fig, saida, "15_erpt_lp")


def taylor_premio(est: pd.DataFrame, saida: Path):
    """ψ por subamostra e método, com IC de 95% de Fieller (setas indicam conjunto ilimitado)."""
    est = est.dropna(subset=["psi"]).reset_index(drop=True)
    xmin, xmax = -4, 14
    fig, ax = plt.subplots(figsize=(8.5, 0.55 * len(est) + 1.6))
    cores = {"NLS": "#0072B2", "2SLS/GMM": "#D55E00"}
    for k, r in est.iterrows():
        cor = cores[r["metodo"]]
        if r["ic_tipo"] == "limitado":
            ax.plot([max(r["ic_lo"], xmin), min(r["ic_hi"], xmax)], [k, k], color=cor, lw=1.6)
        elif r["ic_tipo"] == "reta inteira":
            ax.annotate("", xy=(xmin, k), xytext=(xmax, k), arrowprops=dict(arrowstyle="<->", color=cor, lw=1.2))
        else:  # (−∞, lo] ∪ [hi, ∞)
            ax.annotate("", xy=(xmin, k), xytext=(max(min(r["ic_lo"], xmax), xmin), k),
                        arrowprops=dict(arrowstyle="->", color=cor, lw=1.2))
            ax.annotate("", xy=(xmax, k), xytext=(min(max(r["ic_hi"], xmin), xmax), k),
                        arrowprops=dict(arrowstyle="->", color=cor, lw=1.2))
        if xmin <= r["psi"] <= xmax:
            ax.plot(r["psi"], k, "o", color=cor, ms=5)
        else:
            ax.text(xmax, k, f" ψ = {r['psi']:.0f}".replace(".", ","), va="center", fontsize=7, color=cor)
    ax.set_yticks(range(len(est)), [f"{a} · {m}" for a, m in zip(est["amostra"], est["metodo"])], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(xmin, xmax)
    ax.axvspan(0, 1, color=GRADE, alpha=0.8, lw=0, label="Domínio do modelo, ω ∈ [0, 1]")
    ax.axvline(0, color=TINTA_SEC, lw=0.8)
    ax.set_xlabel("ψ (p.p. de Selic de longo prazo por p.p. de prêmio)")
    ax.set_title("Regra de Taylor com prêmio (EMBI+): ψ e IC de 95% de Fieller (setas: conjunto ilimitado)",
                 loc="left", color=TINTA, fontsize=9)
    ax.legend(fontsize=7.5, loc="lower right")
    return _salvar(fig, saida, "16_taylor_premio")


def diagnostico_c(dg: dict, info: dict, saida: Path):
    """Selic, Taylor e dívida (mediana e faixa 25–75%) de A e C, P1 base, λ = 0,9."""
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    t = np.arange(dg["series"]["A"]["i"].shape[1]) / 4
    for ch in ("A", "C"):
        s, cor = dg["series"][ch], info[ch]["cor"]
        axs[0].plot(t, s["i"][1], color=cor, ls=ESTILO[ch], label=f"Selic {ch}")
        axs[0].plot(t, s["i_taylor"][1], color=cor, ls=ESTILO[ch], lw=1, alpha=0.6, label=f"Taylor {ch}")
        axs[1].fill_between(t, s["d_gross"][0], s["d_gross"][2], color=cor, alpha=0.15, lw=0)
        axs[1].plot(t, s["d_gross"][1], color=cor, ls=ESTILO[ch], label=info[ch]["nome"])
    axs[0].axhline(dg["i_alvo"], color=TINTA_SEC, lw=0.8, ls="-.", label="Piso de C (7,5%)")
    axs[0].axvline(dg["t_delta_zero"] / 4, color=TINTA_SEC, lw=0.8)
    axs[0].text(dg["t_delta_zero"] / 4, axs[0].get_ylim()[1], " δ = 0", va="top", fontsize=7.5, color=TINTA_SEC)
    axs[0].set_ylabel("% a.a. (mediana)")
    axs[1].set_ylabel("Dívida bruta (% PIB): mediana e faixa 25–75%")
    for ax in axs:
        ax.set_xlabel("Anos")
        ax.legend(fontsize=7.5)
    fig.suptitle("Diagnóstico da dívida de C (P1 base, λ = 0,9)", x=0.01, ha="left", color=TINTA)
    fig.tight_layout()
    return _salvar(fig, saida, "18_diagnostico_C")
