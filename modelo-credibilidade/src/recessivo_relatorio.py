"""Gráficos e relatorio_recessivo.md a partir dos CSVs de outputs/v2_2/recessivo (python -m src.recessivo).

Uso: python -m src.recessivo_relatorio
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .recessivo import CONF, MIPD, SAIDA, fm  # noqa: E402

GRAF = SAIDA / "graficos"
# paleta categórica de referência (slots 1–6 na ordem documentada); a referência S em cinza neutro
CORES = {"A": "#2a78d6", "A_res60": "#eb6834", "A_res100": "#1baf7a", "B": "#eda100", "C": "#e87ba4",
         "C_sem_piso": "#008300", "S": "#8a8984"}
ROT = {k: v["rotulo"] for k, v in CONF["estrategias"].items()}
ROT["A_res100"] = "A com venda de até US$ 100 bi (efetiva: 76)"
ROT["C_sem_piso"] = "C sem piso (venda efetiva: 76)"
CURTO = {"S": "S", "A": "A", "A_res60": "A_res60", "A_res100": "A_res100 (ef. 76)", "B": "B", "C": "C",
         "C_sem_piso": "C_sem_piso"}
ESPEC_ROT = {"P1": "P1 · Phillips híbrida", "P2": "P2 · Phillips achatada", "P3_theta05": "P3 · FTPL, θ = 0,5",
             "P3_theta025": "P3 · FTPL, θ = 0,25"}
TINTA, TINTA2, GRADE = "#0b0b0b", "#52514e", "#e4e3df"


def _estilo(ax):
    ax.grid(axis="y", color=GRADE, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9b8b2")
    ax.tick_params(colors=TINTA2, labelsize=8)


def _salvar(fig, nome):
    GRAF.mkdir(parents=True, exist_ok=True)
    fig.savefig(GRAF / f"{nome}.png", dpi=150, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)


def g1_crescimento(cr: pd.DataFrame):
    especs = list(CONF["especificacoes"])
    fig, axs = plt.subplots(2, len(especs), figsize=(4 * len(especs), 7), sharey=True, facecolor="#fcfcfb")
    for i, lam in enumerate((0.5, 0.9)):
        for j, e in enumerate(especs):
            ax = axs[i, j]
            d = cr[(cr["especificacao"] == e) & (cr["lambda"] == lam)]
            for est in CONF["estrategias"]:
                x = d[d["estrategia"] == est]
                ls = "--" if est == "S" else "-"
                ax.fill_between(x["ano"], x["p10"], x["p90"], color=CORES[est], alpha=0.08, lw=0)
                ax.plot(x["ano"], x["mediana"], ls, color=CORES[est], lw=2, label=CURTO[est])
            ax.axhline(0, color="#b9b8b2", lw=0.8)
            ax.set_title(f"{ESPEC_ROT[e]} · λ = {fm(lam)}", fontsize=9, color=TINTA, loc="left")
            _estilo(ax)
            if j == 0:
                ax.set_ylabel("crescimento do PIB (% a.a.)", fontsize=8, color=TINTA2)
    axs[0, -1].legend(fontsize=7, frameon=False, loc="upper right")
    fig.suptitle("Crescimento anual do PIB: mediana e faixa de 10% a 90%", x=0.01, ha="left", fontsize=11, color=TINTA)
    _salvar(fig, "1_crescimento_anual")


def g2_recessao(at: pd.DataFrame):
    especs = list(CONF["especificacoes"])
    fig, axs = plt.subplots(2, len(especs), figsize=(4 * len(especs), 6.5), sharey=True, facecolor="#fcfcfb")
    for i, jan in enumerate(("1-8", "1-16")):
        for j, e in enumerate(especs):
            ax = axs[i, j]
            d = at[(at["especificacao"] == e) & (at["janela"] == jan)]
            for est in CONF["estrategias"]:
                x = d[d["estrategia"] == est]
                ax.plot(x["lambda"], 100 * x["p_recessao_todas"], "--" if est == "S" else "-", marker="o", ms=4,
                        color=CORES[est], lw=2, label=CURTO[est])
            ax.set_title(f"{ESPEC_ROT[e]} · trimestres {jan}", fontsize=9, color=TINTA, loc="left")
            ax.set_xticks(CONF["lambdas"])
            _estilo(ax)
            if j == 0:
                ax.set_ylabel("P(recessão técnica) (%)", fontsize=8, color=TINTA2)
            if i == 1:
                ax.set_xlabel("adesão λ", fontsize=8, color=TINTA2)
    axs[0, -1].legend(fontsize=7, frameon=False)
    fig.suptitle("Probabilidade de recessão técnica (dois trimestres seguidos de queda do PIB)", x=0.01, ha="left",
                 fontsize=11, color=TINTA)
    _salvar(fig, "2_recessao")


def g3_fronteira(fr: pd.DataFrame, at: pd.DataFrame):
    marc = {"P1": "o", "P2": "s", "P3_theta05": "^", "P3_theta025": "D"}
    fig, ax = plt.subplots(figsize=(8, 5.5), facecolor="#fcfcfb")
    d = at[(at["janela"] == "1-16") & (at["lambda"] == 0.7)]
    for r in fr.itertuples():
        if r.estrategia == "S":
            continue
        y = d[(d["estrategia"] == r.estrategia) & (d["especificacao"] == r.especificacao)]["dif_mediana"]
        if y.empty:
            continue
        x = min(r.lambda70_liq_banda, 1.02)
        ax.scatter(x, y.iloc[0], s=60, marker=marc[r.especificacao], color=CORES[r.estrategia],
                   edgecolor="#fcfcfb", lw=1.5, zorder=3)
    for est in CONF["estrategias"]:
        if est != "S":
            ax.scatter([], [], color=CORES[est], label=CURTO[est])
    for e, m in marc.items():
        ax.scatter([], [], marker=m, color="#8a8984", label=ESPEC_ROT[e])
    ax.axvline(1.0, color="#b9b8b2", lw=0.8, ls=":")
    ax.text(1.005, ax.get_ylim()[1], "não atinge 70%", fontsize=7, color=TINTA2, va="top")
    ax.axhline(0, color="#b9b8b2", lw=0.8)
    ax.set_xlabel("λ*₇₀ pela dívida líquida, banda de inflação (menor = mais robusta)", fontsize=8, color=TINTA2)
    ax.set_ylabel("diferença de produto acumulada até a eleição contra S\n(% do PIB de um ano; positivo = acima de S; "
                  "λ = 0,7)", fontsize=8, color=TINTA2)
    _estilo(ax)
    ax.legend(fontsize=7, frameon=False, ncol=2, loc="best")
    ax.set_title("Robustez × custo recessivo", fontsize=11, color=TINTA, loc="left")
    _salvar(fig, "3_fronteira_robustez_custo")


def g4_composicao(cp: pd.DataFrame):
    especs = list(CONF["especificacoes"])
    comps = list(CONF["composicoes"])
    ests = ["A", "C", "C_sem_piso"]
    fig, axs = plt.subplots(1, len(especs), figsize=(4 * len(especs), 4.2), sharey=True, facecolor="#fcfcfb")
    d = cp[(cp["janela"] == "1-16") & (cp["lambda"] == 0.7) & (~cp["ciclo"].astype(bool))]
    w = 0.26
    for j, e in enumerate(especs):
        ax = axs[j]
        for k, est in enumerate(ests):
            for i, comp in enumerate(comps):
                q = d[(d["especificacao"] == e) & (d["estrategia"] == est) & (d["composicao"] == comp)]
                c = q.set_index("multiplicadores")["dif_mediana"]
                x = k + (i - 1) * w
                ax.bar(x, c["central"], w * 0.92, color=["#2a78d6", "#1baf7a", "#eb6834"][i],
                       label=comp if (k == 0 and j == 0) else None)
                ax.vlines(x, min(c["baixo"], c["alto"]), max(c["baixo"], c["alto"]), color=TINTA, lw=1)
        ax.set_xticks(range(len(ests)), [CURTO[s] for s in ests])
        ax.axhline(0, color="#b9b8b2", lw=0.8)
        ax.set_title(ESPEC_ROT[e], fontsize=9, color=TINTA, loc="left")
        _estilo(ax)
    axs[0].set_ylabel("diferença de produto até a eleição contra S\n(% do PIB de um ano; positivo = acima de S)",
                      fontsize=8, color=TINTA2)
    axs[0].legend(fontsize=7, frameon=False)
    fig.suptitle("Composição do pacote (λ = 0,7; barra = multiplicadores centrais, traço = faixa baixa–alta)",
                 x=0.01, ha="left", fontsize=11, color=TINTA)
    _salvar(fig, "4_composicao_pacote")


def g5_emprego(em: pd.DataFrame, espec="P1"):
    ests = [e for e in CONF["estrategias"] if e != "S"]
    d = em[(em["especificacao"] == espec) & (em["lambda"] == 0.7) & (em["janela"] == "1-16")]
    fig, axs = plt.subplots(1, len(ests), figsize=(3.1 * len(ests), 5.2), sharey=True, sharex=True,
                            facecolor="#fcfcfb")
    for j, est in enumerate(ests):
        ax = axs[j]
        x = d[d["estrategia"] == est].sort_values("grupo")
        y = np.arange(len(x))
        ax.barh(y, x["formais_mil"], color="#2a78d6", height=0.7, label="formais")
        ax.barh(y, x["informais_mil"], left=np.where(np.sign(x["informais_mil"]) == np.sign(x["formais_mil"]),
                                                      x["formais_mil"], 0), color="#eb6834", height=0.7,
                label="informais")
        ax.axvline(0, color="#b9b8b2", lw=0.8)
        ax.set_yticks(y, x["grupo_nome"].str.slice(0, 28), fontsize=7)
        ax.invert_yaxis()
        ax.set_title(CURTO[est], fontsize=9, color=TINTA, loc="left")
        _estilo(ax)
        ax.grid(axis="x", color=GRADE, lw=0.6)
        ax.grid(axis="y", visible=False)
    axs[0].legend(fontsize=7, frameon=False, loc="lower right")
    fig.supxlabel("ocupações contra S (mil; média dos trimestres 1–16)", fontsize=8, color=TINTA2)
    fig.suptitle(f"Emprego por setor ({ESPEC_ROT[espec]}, λ = 0,7)", x=0.01, ha="left", fontsize=11, color=TINTA)
    _salvar(fig, "5_emprego_setores")


def g6_mapa_va(va: pd.DataFrame, espec="P1"):
    ests = [e for e in CONF["estrategias"] if e != "S"]
    d = va[(va["especificacao"] == espec) & (va["lambda"] == 0.7) & (va["janela"] == "1-16")]
    M = d.pivot_table(index="grupo_nome", columns="estrategia", values="dVA_pct_do_setor")[ests]
    ordem = d.drop_duplicates("grupo").sort_values("grupo")["grupo_nome"]
    M = M.loc[ordem]
    lim = float(np.nanmax(np.abs(M.to_numpy())))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])
    fig, ax = plt.subplots(figsize=(8.5, 6), facecolor="#fcfcfb")
    im = ax.imshow(M.to_numpy(), cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(ests)), [CURTO[s] for s in ests], fontsize=8)
    ax.set_yticks(range(len(M)), M.index, fontsize=8)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, fm(M.iat[i, j], 2), ha="center", va="center", fontsize=7, color=TINTA)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label("Δ valor adicionado contra S (% do VA do setor)", fontsize=8, color=TINTA2)
    ax.set_title(f"Valor adicionado setorial ({ESPEC_ROT[espec]}, λ = 0,7, trimestres 1–16)", fontsize=11,
                 color=TINTA, loc="left")
    _salvar(fig, "6_mapa_va_setorial")


# ---------------------------------------------------------------------------------------------- relatório

def _tab(df: pd.DataFrame, cols: dict, nd: dict | None = None) -> list[str]:
    nd = nd or {}
    L = ["| " + " | ".join(cols.values()) + " |", "|" + "---|" * len(cols)]
    for r in df.to_dict("records"):
        L.append("| " + " | ".join(fm(r[c], nd.get(c, 1)) if isinstance(r[c], (float, np.floating)) else str(r[c])
                                   for c in cols) + " |")
    return L


def relatorio(sintese: list[str] | None = None) -> Path:
    at = pd.read_csv(SAIDA / "atividade_agregada.csv")
    cr = pd.read_csv(SAIDA / "crescimento_anual.csv")
    bt = pd.read_csv(SAIDA / "bootstrap_atividade.csv")
    cp = pd.read_csv(SAIDA / "composicao_pacote.csv")
    bc = pd.read_csv(SAIDA / "bootstrap_composicao.csv")
    va = pd.read_csv(SAIDA / "setorial_va.csv")
    em = pd.read_csv(SAIDA / "setorial_emprego.csv")
    dg = pd.read_csv(SAIDA / "setorial_diagnostico.csv")
    dc = pd.read_csv(SAIDA / "decomposicao_hiato.csv")
    fr = pd.read_csv(SAIDA / "fronteira.csv") if (SAIDA / "fronteira.csv").stat().st_size > 5 else pd.DataFrame()
    pc = pd.read_csv(SAIDA / "pnad_coeficientes.csv")
    sid = pd.read_csv(SAIDA / "pnad_coeficientes_tabelas_sidra.csv")
    ok = pd.read_csv(MIPD / "okun.csv").iloc[0]
    meta = json.loads((MIPD / "pnad_meta.json").read_text(encoding="utf-8"))
    ex = json.loads((SAIDA / "execucao.json").read_text(encoding="utf-8"))
    g1_crescimento(cr)
    g2_recessao(at)
    if len(fr):
        g3_fronteira(fr, at)
    g4_composicao(cp)
    g5_emprego(em)
    g6_mapa_va(va)

    ests = list(CONF["estrategias"])
    L = ["# Efeito recessivo das estratégias: PIB, composição do pacote, setores e emprego", "",
         f"Modelo v2.2 calibrado (R_min = US$ 300 bi), N = {ex['N']} trajetórias por estratégia e λ (seed "
         f"{ex['seed_choques']}, as mesmas da rodada principal), bootstrap pareado com R = {ex['R']} (seed "
         f"{ex['seed_bootstrap']}). Especificações P1, P2 e P3 (θ = 0,5 e 0,25); adesão λ ∈ "
         f"{{{'; '.join(fm(x) for x in CONF['lambdas'])}}} na diagonal. t0 = 2026T3: a eleição de outubro de 2030 "
         "é o trimestre 16. Os multiplicadores por item do pacote substituem a3 = 0,4 só neste módulo; a lógica de "
         "sucesso já reportada não muda.", "",
         "**Diferença de produto acumulada contra S** = Σ (PIB da estratégia − PIB de S) / PIB de S, em % do PIB de "
         "um ano (positivo = produto acima de S; negativo = a estratégia é recessiva contra S).", "",
         "**Efeito fiscal em nível.** Cada item do pacote entra na equação do hiato como m · (medida_t − ρ_f · "
         "medida_{t−1}), com ρ_f = a1 (= " + fm(float(pd.read_csv(SAIDA / "multiplicadores_efetivos.csv")["rho_f"].iloc[0]), 3) + "): o efeito direto sobre o hiato é "
         "m × medida em vigor, e o multiplicador acumulado direto é m em 4, 8 e 16 trimestres (seção 2). A versão "
         "anterior, com o efeito pelo impulso (m · (−Δmedida)), está em `relatorio_recessivo_impulso.md`.", "",
         "**Inflação alta.** O modelo não tem custo de produto da inflação alta. Por isso as trajetórias com inflação "
         "acima de 20% em algum trimestre (da estratégia ou de S) saem das métricas de produto; a fração aparece ao "
         "lado. Na probabilidade de recessão, a trajetória explosiva (π > 50%) conta como recessão na janela em que "
         "rompe.", "",
         "Estratégias: " + "; ".join(f"**{k}** = {ROT[k]}" for k in ests) + ".", ""]
    if sintese:
        L += ["## Síntese", ""] + sintese + [""]

    # 1. atividade agregada
    L += ["## 1. Produto e recessão", "",
          "Mediana da diferença de produto acumulada contra S [faixa 10–90%] e P(recessão técnica), λ = 0,7:", ""]
    d = at[at["lambda"] == 0.7]
    cab = "| Especificação | Estratégia | Inflação > 20% | " + " | ".join(
        f"Dif. {j} | P(rec.) {j}" for j in CONF["janelas"]) + " |"
    L += [cab, "|---|---|---|" + "---|---|" * len(CONF["janelas"])]
    for e in CONF["especificacoes"]:
        for est in ests:
            q = d[(d["especificacao"] == e) & (d["estrategia"] == est)].set_index("janela")
            cel = []
            for j in CONF["janelas"]:
                r = q.loc[j]
                cel += [f"{fm(r['dif_mediana'], 2)} [{fm(r['dif_p10'], 1)}; {fm(r['dif_p90'], 1)}]",
                        f"{fm(100 * r['p_recessao_todas'], 0)}%"]
            L.append(f"| {e} | {CURTO[est]} | {fm(100 * q.iloc[0]['fracao_inflacao_alta'], 0)}% | " + " | ".join(cel) + " |")
    L += ["", "Diferença de produto até a eleição contra S (trimestres 1–16, mediana) por λ; entre parênteses, a "
          "fração de trajetórias com inflação acima de 20%, quando houver:", "",
          "| Especificação | Estratégia | " + " | ".join(f"λ = {fm(l)}" for l in CONF["lambdas"]) + " |",
          "|---|---|" + "---|" * len(CONF["lambdas"])]
    d = at[at["janela"] == "1-16"]
    for e in CONF["especificacoes"]:
        for est in ests:
            q = d[(d["especificacao"] == e) & (d["estrategia"] == est)].set_index("lambda")
            cel = [fm(q.loc[l, "dif_mediana"], 2) + (f" ({fm(100 * q.loc[l, 'fracao_inflacao_alta'], 0)}%)"
                                                     if q.loc[l, "fracao_inflacao_alta"] > 0.005 else "")
                   for l in CONF["lambdas"]]
            L.append(f"| {e} | {CURTO[est]} | " + " | ".join(cel) + " |")
    L += ["", "Hiato mínimo (mediana, trimestres 1–40) e trimestre em que ocorre, anos com crescimento negativo (média, "
          "2027–2035) e taxa de sacrifício (perda de produto até o trimestre 16 ÷ queda da inflação média do ano 1 para os anos "
          "3–4, só quando a inflação cai), λ = 0,7:", "",
          "| Especificação | Estratégia | Hiato mínimo | Trimestre | Anos negativos | Sacrifício | Trajetórias com queda |",
          "|---|---|---|---|---|---|---|"]
    d = at[(at["lambda"] == 0.7) & (at["janela"] == "1-40")]
    for e in CONF["especificacoes"]:
        for est in ests:
            r = d[(d["especificacao"] == e) & (d["estrategia"] == est)].iloc[0]
            L.append(f"| {e} | {CURTO[est]} | {fm(r['hiato_min_mediana'], 2)} | {fm(r['trim_hiato_min_mediana'], 0)} | "
                     f"{fm(r['anos_negativos_media'], 1)} | {fm(r['sacrificio_mediana'], 2)} | "
                     f"{fm(100 * r['sacrificio_validas'], 0)}% |")
    L += ["", "Bootstrap pareado (diferença de médias, IC de 95%; * = exclui zero). Diferença de produto em % do PIB "
          "de um ano (positivo = o primeiro tem mais produto); "
          "P(recessão) em p.p.; λ = 0,7:", "",
          "| Especificação | Par | Produto 1–8 | Produto 1–16 | P(rec.) 1–8 | P(rec.) 1–16 |", "|---|---|---|---|---|---|"]
    d = bt[bt["lambda"] == 0.7]
    for e in CONF["especificacoes"]:
        for par in d["par"].unique():
            q = d[(d["especificacao"] == e) & (d["par"] == par)].set_index(["metrica", "janela"])
            cel = [ic(q.loc[(m, j)], 2 if m == "dif" else 0) for m in ("dif", "recessao") for j in ("1-8", "1-16")]
            L.append(f"| {e} | {par} | " + " | ".join(cel) + " |")
    L += ["", "Decomposição da diferença de hiato contra S (média dos trimestres 1–16, p.p. do PIB, λ = 0,7): "
          "efeito direto do pacote (soma dos itens), juro real longo, câmbio real, CAPEX e restante.", "",
          "| Especificação | Estratégia | Δ hiato | Pacote direto | Juro real longo | Câmbio | CAPEX | Fiscal fora do pacote | Outros |",
          "|---|---|---|---|---|---|---|---|---|"]
    d = dc[(dc["lambda"] == 0.7) & (dc["janela"] == "1-16")]
    for r in d.to_dict("records"):
        L.append(f"| {r['especificacao']} | {CURTO[r['estrategia']]} | {fm(r['dh_total'], 2)} | "
                 f"{fm(r['pacote_direto'], 2)} | {fm(r.get('dem_juro', np.nan), 2)} | {fm(r.get('dem_cambio', np.nan), 2)} | "
                 f"{fm(r.get('dem_capex', np.nan), 2)} | {fm(r.get('dem_fiscal_resto', np.nan), 2)} | "
                 f"{fm(r['outros'] + r.get('dem_choque', 0), 2)} |")
    L += ["", "Gráficos: `graficos/1_crescimento_anual.png`, `graficos/2_recessao.png`.", ""]

    # 2. composição
    L += ["## 2. Composição do pacote fiscal", "",
          "Mesmo valor total (2,7% do PIB) em todos os trimestres. Multiplicadores por item e fontes em "
          "`config/recessivo.yaml`; multiplicador efetivo = média ponderada pelo valor de cada item em vigor.", "",
          "| Item | Canal | Multiplicador | Faixa |", "|---|---|---|---|"]
    for k, it in CONF["itens"].items():
        L.append(f"| {it['nome']} | {it['canal']} | {fm(it['m'])} | {fm(it['faixa'][0])}–{fm(it['faixa'][1])} |")
    me = pd.read_csv(SAIDA / "multiplicadores_efetivos.csv")
    L += ["", "Multiplicador acumulado efetivo de cada item (medida permanente de 1% do PIB desde o trimestre 1, "
          "estratégia A só com esse item contra S, sem choques, λ = 0,7): −Σ Δhiato ÷ Σ medida em 4, 8 e 16 "
          "trimestres. \"Direto\" acumula só o termo do item (calibração: igual a m; teste `test_calibracao_rho_f`); "
          "\"modelo\" inclui a resposta da Selic, do prêmio, do juro longo e do câmbio.", "",
          "| Especificação | Item | m | Direto 4/8/16 | Modelo 4 | Modelo 8 | Modelo 16 |", "|---|---|---|---|---|---|---|"]
    for r in me.to_dict("records"):
        L.append(f"| {r['especificacao']} | {r['nome']} | {fm(r['m'])} | {fm(r['direto_4'], 2)} / {fm(r['direto_8'], 2)} / "
                 f"{fm(r['direto_16'], 2)} | {fm(r['modelo_4'], 2)} | {fm(r['modelo_8'], 2)} | {fm(r['modelo_16'], 2)} |")
    L += ["", "Diferença de produto até a eleição contra S (mediana, trimestres 1–16, λ = 0,7) por composição; entre "
          "parênteses, a faixa "
          "com multiplicadores baixos e altos; \"ciclo\" = multiplicadores dependentes do hiato (γ = "
          f"{fm(CONF['gamma_ciclo'], 3)}):", "",
          "| Especificação | Estratégia | Composição | Mult. efetivo | Central | (baixo; alto) | Com ciclo |",
          "|---|---|---|---|---|---|---|"]
    d = cp[(cp["lambda"] == 0.7) & (cp["janela"] == "1-16")]
    for e in CONF["especificacoes"]:
        for est in ("A", "C", "C_sem_piso"):
            for comp in CONF["composicoes"]:
                q = d[(d["especificacao"] == e) & (d["estrategia"] == est) & (d["composicao"] == comp)]
                g = {(r["multiplicadores"], bool(r["ciclo"])): r for r in q.to_dict("records")}
                L.append(f"| {e} | {CURTO[est]} | {comp} | {fm(g[('central', False)]['mult_efetivo_medio'], 2)} | "
                         f"{fm(g[('central', False)]['dif_mediana'], 2)} | ({fm(g[('baixo', False)]['dif_mediana'], 2)}; "
                         f"{fm(g[('alto', False)]['dif_mediana'], 2)}) | {fm(g[('central', True)]['dif_mediana'], 2)} |")
    L += ["", "Pergunta 2: produto com pacote_qualidade − produto com pacote_linear (positivo = a composição de "
          "qualidade preserva mais produto), bootstrap pareado, λ = 0,7:", "",
          "| Especificação | Estratégia | 1–8 | 1–16 | 1–40 | 1–16, mult. baixos | 1–16, mult. altos | 1–16, ciclo |",
          "|---|---|---|---|---|---|---|---|"]
    d = bc[bc["lambda"] == 0.7]
    for e in CONF["especificacoes"]:
        for est in ("A", "C", "C_sem_piso"):
            q = d[(d["especificacao"] == e) & (d["estrategia"] == est)]
            sel = lambda j, m="central", c=False: q[(q["janela"] == j) & (q["multiplicadores"] == m)  # noqa: E731
                                                    & (q["ciclo"].astype(bool) == c)].iloc[0]
            cel = [ic(sel(j), 2, "qualidade_menos_linear") for j in ("1-8", "1-16", "1-40")]
            cel += [ic(sel("1-16", "baixo"), 2, "qualidade_menos_linear"),
                    ic(sel("1-16", "alto"), 2, "qualidade_menos_linear"),
                    ic(sel("1-16", "central", True), 2, "qualidade_menos_linear")]
            L.append(f"| {e} | {CURTO[est]} | " + " | ".join(cel) + " |")
    L += ["", "A composição também afeta a credibilidade (um pacote de receita e de itens de difícil aprovação pode "
          "ter λ_fiscal menor); isso não é modelado: as tabelas mostram o produto para cada λ, e a comparação entre "
          "composições deve ser feita também em λ diferentes.", "", "Gráfico: `graficos/4_composicao_pacote.png`.", ""]

    # 3. setores e emprego
    L += ["## 3. Setores e emprego", "",
          "A diferença de hiato contra S é decomposta pelos componentes da equação de demanda (juro real longo → "
          "metade consumo, metade FBCF; itens do pacote → canal de cada item; câmbio real → exportações; CAPEX → "
          "construção e máquinas; choques e restante → absorção doméstica), convertida em demanda final pelo PIB de "
          "2015, distribuída pela Leontief tipo I da MIP 2015 (67 atividades) e reconciliada com o PIB do modelo macro "
          "trimestre a trimestre: o resíduo entre o PIB do modelo e o VA da matriz entra como demanda de absorção "
          "doméstica (reconciliação aditiva; a escala proporcional fica instável quando o efeito direto do pacote e o "
          "do juro, de sinais opostos, se cancelam). Emprego = variação % da produção de cada atividade × ocupados de 2025 (PNAD).", "",
          "Valor adicionado por grupo da TRU (% do VA do setor, média dos trimestres 1–16, λ = 0,7, P1):", "",
          "| Grupo | " + " | ".join(CURTO[s] for s in ests if s != "S") + " |", "|---|" + "---|" * (len(ests) - 1)]
    d = va[(va["especificacao"] == "P1") & (va["lambda"] == 0.7) & (va["janela"] == "1-16")]
    for g in sorted(d["grupo"].unique()):
        q = d[d["grupo"] == g].set_index("estrategia")
        L.append(f"| {q['grupo_nome'].iloc[0]} | " + " | ".join(fm(q.loc[s, 'dVA_pct_do_setor'], 2)
                                                             for s in ests if s != "S") + " |")
    L += ["", "Ocupações contra S (mil; média dos trimestres de cada janela; λ = 0,7, P1). Formais pela fração "
          "formal de cada atividade (Censo 2022 calibrado à PNAD de 2025); induzido = tipo II − tipo I sem "
          "reconciliação (propensão a consumir 0,9, impostos 15%; sensibilidade em data/processed/mip/sensibilidade_tipo2.csv):", "",
          "| Estratégia | Janela | Total | Formais | Informais | Massa salarial (R$ bi/ano) | Induzido tipo II | Desocupação (p.p.) [IC] |",
          "|---|---|---|---|---|---|---|---|"]
    d = em[(em["especificacao"] == "P1") & (em["lambda"] == 0.7)]
    dd = dg[(dg["especificacao"] == "P1") & (dg["lambda"] == 0.7)]
    for est in ests:
        if est == "S":
            continue
        for jan in ("1-8", "1-16"):
            q = d[(d["estrategia"] == est) & (d["janela"] == jan)]
            g = dd[(dd["estrategia"] == est) & (dd["janela"] == jan)].iloc[0]
            L.append(f"| {CURTO[est]} | {jan} | {fm(q['ocupacoes_mil'].sum(), 0)} | {fm(q['formais_mil'].sum(), 0)} | "
                     f"{fm(q['informais_mil'].sum(), 0)} | {fm(q['massa_salarial_rs_bi_ano'].sum(), 1)} | "
                     f"{fm(q['induzido_tipo2_mil'].sum(), 0)} | {fm(g['desocupacao_pp'], 2)} "
                     f"[{fm(g['desocupacao_ic_lo'], 2)}; {fm(g['desocupacao_ic_hi'], 2)}] |")
    L += ["", "Ocupações totais contra S por especificação (mil, trimestres 1–16, λ = 0,7):", "",
          "| Especificação | " + " | ".join(CURTO[s] for s in ests if s != "S") + " |", "|---|" + "---|" * (len(ests) - 1)]
    d = em[(em["lambda"] == 0.7) & (em["janela"] == "1-16")]
    for e in CONF["especificacoes"]:
        q = d[d["especificacao"] == e].groupby("estrategia")["ocupacoes_mil"].sum()
        L.append(f"| {e} | " + " | ".join(fm(q.get(s, np.nan), 0) for s in ests if s != "S") + " |")
    L += ["", "Diagnósticos (λ = 0,7, trimestres 1–16): fator de escala (VA do modelo macro ÷ VA da matriz, somando "
          "os componentes em módulo; fora de 0,7–1,3 indicaria incoerência entre os multiplicadores do bloco fiscal e "
          "os da matriz; o fator com sinal, instável quando os componentes se cancelam, está no CSV), "
          "efeito de volta sobre a balança comercial (exportações pelo canal do câmbio real; importações pelo "
          "conteúdo importado da demanda final e dos insumos) e retorno fiscal da massa salarial formal adicional "
          "(contribuições previdenciárias/FGTS pela razão da TRU 2015 e IRPF 2026 pela alíquota efetiva no "
          "rendimento médio do setor) contra a receita cíclica do modelo macro (rec_base × ε_rec × Δhiato). O "
          "retorno setorial não é somado ao primário: é uma decomposição parcial da receita cíclica.", "",
          "| Especificação | Estratégia | Fator de escala | Exportações (% PIB) | Importações (% PIB) | Contribuições (R$ bi) | IRPF (R$ bi) | Receita cíclica macro (R$ bi) |",
          "|---|---|---|---|---|---|---|---|"]
    d = dg[(dg["lambda"] == 0.7) & (dg["janela"] == "1-16")]
    for r in d.to_dict("records"):
        L.append(f"| {r['especificacao']} | {CURTO[r['estrategia']]} | {fm(r['fator_escala'], 2)} | "
                 f"{fm(r['exportacoes_pct_pib'], 3)} | {fm(r['importacoes_pct_pib'], 3)} | {fm(r['contrib_prev_rs_bi'], 1)} | "
                 f"{fm(r['ir_rs_bi'], 1)} | {fm(r['receita_ciclica_macro_rs_bi'], 1)} |")
    L += ["", f"Fator de escala médio (todas as estratégias, especificações, λ e janelas): "
          f"{fm(dg['fator_escala'].mean(), 2)} (mín. {fm(dg['fator_escala'].min(), 2)}, máx. {fm(dg['fator_escala'].max(), 2)}). "
          f"Fora de 0,7–1,3 em {int(((dg['fator_escala'] > 1.3) | (dg['fator_escala'] < 0.7)).sum())} de {len(dg)} "
          "casos. O fator reflete o vazamento da demanda final para importações e impostos na matriz (o VA por "
          "unidade de demanda final é menor que 1), não uma divergência entre os multiplicadores.",
          "", "Efeito sobre os setores mais expostos ao câmbio (VA pelo canal das exportações, R$ milhões de 2015, "
          "trimestres 1–16, λ = 0,7, P1):", "", "| Grupo | " + " | ".join(CURTO[s] for s in ests if s != "S") + " |",
          "|---|" + "---|" * (len(ests) - 1)]
    d = va[(va["especificacao"] == "P1") & (va["lambda"] == 0.7) & (va["janela"] == "1-16") & va["grupo"].isin([1, 2, 3])]
    for g in (1, 2, 3):
        q = d[d["grupo"] == g].set_index("estrategia")
        L.append(f"| {q['grupo_nome'].iloc[0]} | " + " | ".join(fm(q.loc[s, 'dVA_exportacoes_rs_mi_2015'], 0)
                                                             for s in ests if s != "S") + " |")
    L += ["", "Gráficos: `graficos/5_emprego_setores.png`, `graficos/6_mapa_va_setorial.png`.", ""]

    # 4. fronteira
    L += ["## 4. Robustez × custo recessivo", ""]
    if len(fr):
        L += ["λ\\*₇₀ pela dívida líquida (banda e teto; 1,01 = não atinge 70%) e diferença de produto até a eleição "
              "contra S (mediana, λ = 0,7):", "",
              "| Especificação | Estratégia | λ\\*₇₀ banda | λ\\*₇₀ teto | Produto 1–16 |", "|---|---|---|---|---|"]
        d = at[(at["janela"] == "1-16") & (at["lambda"] == 0.7)]
        for r in fr.to_dict("records"):
            y = d[(d["estrategia"] == r["estrategia"]) & (d["especificacao"] == r["especificacao"])]["dif_mediana"]
            nao = lambda x: "não atinge" if x > 1 else fm(x, 2)  # noqa: E731
            L.append(f"| {r['especificacao']} | {CURTO[r['estrategia']]} | {nao(r['lambda70_liq_banda'])} | "
                     f"{nao(r['lambda70_liq_teto'])} | {fm(y.iloc[0], 2) if len(y) else '—'} |")
        L += ["", "Gráfico: `graficos/3_fronteira_robustez_custo.png`.", ""]

    # validação 2015–2016 e sensibilidade do canal de credibilidade
    vv = pd.read_csv(SAIDA / "validacao_2015_2016.csv")
    vd = pd.read_csv(SAIDA / "validacao_2015_2016_decomposicao.csv")
    L += ["## 5. Validação no ajuste de 2015–2016", "",
          "Episódio 2015T1–2016T4 (t0 = 2014T4) com Selic, primário e câmbio observados. O impulso fiscal vem do "
          "primário estrutural observado (primário − rec_base·ε_rec·hiato observado), em nível, com multiplicador 0,5; "
          "λ (e θ em P3) é escolhido pelo ajuste de inflação e NTN-B 10 anos, como nos demais episódios. Crescimento "
          "anual ≈ crescimento potencial + variação da média anual do hiato. O episódio fica fora da escolha da "
          "especificação de referência da rodada principal.", "",
          "| Especificação | Caso | λ | θ | Potencial | PIB 2015 simulado | PIB 2016 simulado | Hiato 2016T4 sim. / obs. |",
          "|---|---|---|---|---|---|---|---|"]
    for r in vv.to_dict("records"):
        L.append(f"| {r['especificacao']} | {r['caso']} | {fm(r['lambda'], 2)} | {fm(r['theta'], 2)} | "
                 f"{fm(r['g_potencial'], 2)} | {fm(r['pib_2015_sim'], 1)} | {fm(r['pib_2016_sim'], 1)} | "
                 f"{fm(r['hiato_fim_sim'], 1)} / {fm(r['hiato_fim_obs'], 1)} |")
    r0 = vv.iloc[0]
    L += ["", f"Observado: PIB {fm(r0['pib_2015_oficial'], 1)}% em 2015 e {fm(r0['pib_2016_oficial'], 1)}% em 2016 "
          f"(IBGE; pela média anual do índice dessazonalizado do painel, {fm(r0['pib_2015_obs'], 1)}% e "
          f"{fm(r0['pib_2016_obs'], 1)}%).", "",
          "Contribuição de cada canal ao crescimento anual simulado (p.p., λ de melhor ajuste):", "",
          "| Especificação | Canal | 2015 | 2016 |", "|---|---|---|---|"]
    for r in vd.to_dict("records"):
        L.append(f"| {r['especificacao']} | {r['canal']} | {fm(r['pib_2015'], 2)} | {fm(r['pib_2016'], 2)} |")
    from .validacao import NAO_MODELADOS
    L += ["", "Fatores não modelados: " + "; ".join(NAO_MODELADOS) + ".", ""]
    sc = pd.read_csv(SAIDA / "sensibilidade_credibilidade.csv")
    L += ["## 6. Sensibilidade do canal de credibilidade em S", "",
          "S e A com a sensibilidade do prêmio à dívida (p1, p2 e p2 de P3) pela metade e a2 nos limites da faixa "
          "(0,05 e 0,30; o valor estimado é " + fm(float(sc[sc['combinacao'] == 'base']['a2'].iloc[0]), 3) + "). "
          "Diferença de produto de A contra S até a eleição (mediana; IC de 95% da média) e fração das trajetórias "
          "em que A fica abaixo de S. **Negrito** = A recessivo contra S (mediana negativa).", "",
          "| Especificação | Combinação | " + " | ".join(f"λ = {fm(l)}" for l in CONF["lambdas"]) + " |",
          "|---|---|" + "---|" * len(CONF["lambdas"])]
    d = sc[sc["janela"] == "1-16"]
    for e in CONF["especificacoes"]:
        for comb in d["combinacao"].unique():
            q = d[(d["especificacao"] == e) & (d["combinacao"] == comb)].set_index("lambda")
            cel = []
            for l in CONF["lambdas"]:
                r = q.loc[l]
                s = f"{fm(r['dif_mediana'], 2)} [{fm(r['ic_lo'], 2)}; {fm(r['ic_hi'], 2)}], {fm(100 * r['fracao_A_abaixo_de_S'], 0)}%"
                cel.append(f"**{s}**" if r["dif_mediana"] < 0 else s)
            L.append(f"| {e} | {comb} | " + " | ".join(cel) + " |")
    rec = sc[(sc["dif_mediana"] < 0)]
    L += ["", "Combinações em que A é recessivo contra S (mediana negativa), por janela: " + (
        "; ".join(f"{r['janela']}: {r['especificacao']}, {r['combinacao']}, λ = {fm(r['lambda'])}"
                  for r in rec.sort_values(["janela", "especificacao", "combinacao", "lambda"]).to_dict("records"))
        if len(rec) else "nenhuma") + ".", ""]

    # 5. dados
    L += ["## 7. Dados e coeficientes", "",
          "Matriz insumo-produto: MIP 2015 nível 67 (IBGE), tabelas 03, 04, 12, 13, 14 e 15; TRU 2015 nível 68 (valor "
          "adicionado, remunerações, ocupações); TRU 2023 nível 12 (valor da produção e VA; a TRU 2023 publica zeradas "
          "as ocupações e os componentes da renda). Multiplicador de produção tipo I da transformação: 2,16 (MIP 2015) "
          "e 2,21 (TRU 2023, aproximação). Scripts: `src/extrair_mip.py`, `src/extrair_emprego.py`.", "",
          "Tabelas do SIDRA usadas (validadas pelo nome e pela variável no metadado):", "",
          "| Tabela | Nome | Variável |", "|---|---|---|"]
    for r in sid.to_dict("records"):
        L.append(f"| {r['tabela']} | {r['nome']} | {r['nome_variavel']} ({r['unidade']}) |")
    L += ["", f"Ocupados de 2025 (média dos 4 trimestres, PNAD): {fm(meta['ocupados_pnad_2025_mil'], 0)} mil; "
          f"distribuídos pelas 67 atividades: {fm(meta['ocupados_distribuidos_mil'], 0)} mil. Informalidade: PNAD 2025 "
          f"{fm(100 * meta['informalidade_pnad_2025'], 1)}%, Censo 2022 {fm(100 * meta['informalidade_censo_2022'], 1)}% "
          "(a estrutura setorial do Censo é calibrada à taxa da PNAD por razão de chances constante).", "",
          "| Grupo | Ocupados 2025 (mil) | Ocupações TRU 2015 (mil) | Fração formal | Rendimento médio (R$/mês) | Coef. emprego 2025 | Coef. 2015 | Variação real | Mult. emprego tipo I 2015 → 2025 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in pc.to_dict("records"):
        L.append(f"| {r['grupo_nome']} | {fm(r['ocupados_2025_mil'], 0)} | {fm(r['ocupados_2015_mil'], 0)} | "
                 f"{fm(100 * r['fracao_formal'], 0)}% | {fm(r['rendimento_medio_mensal'], 0)} | {fm(r['coef_emprego_2025'], 2)} | "
                 f"{fm(r['coef_emprego_2015'], 2)} | {fm(r['var_coef_real_pct'], 0)}% | "
                 f"{fm(r['mult_emprego_tipo1_2015'], 1)} → {fm(r['mult_emprego_tipo1_2025'], 1)} |")
    L += ["", f"Coeficiente de emprego: ocupações por R$ milhão de produção (2015: R$ de 2015; 2025: R$ de 2025, "
          "e a variação real deflaciona pelo deflator implícito do VA de cada grupo nas Contas Trimestrais). Ordem "
          f"relativa dos multiplicadores de emprego preservada: Spearman {fm(pc['spearman_tipo1'].iloc[0], 2)} (tipo I) "
          f"e {fm(pc['spearman_tipo2'].iloc[0], 2)} (tipo II). A queda real na agropecuária reflete sobretudo a "
          "diferença de conceito: a TRU conta ocupações (inclusive trabalhos secundários e familiares); a PNAD, "
          "pessoas pelo trabalho principal.", "",
          f"Lei de Okun (PNAD 4099 e hiato do modelo, diferenças de 4 trimestres, {ok['inicio'][:4]}–{ok['fim'][:4]}, "
          f"erro-padrão de Newey-West): Δ desocupação = {fm(ok['beta'], 3)} × Δ hiato, IC de 95% "
          f"[{fm(ok['ic_lo'], 3)}; {fm(ok['ic_hi'], 3)}], n = {int(ok['n'])}.", "",
          "Elasticidades setoriais (CNT, tabela 1621; crescimento trimestral anualizado do VA sobre Δ hiato, Δ juro "
          "real longo, depreciação real e variação do IC-Br em US$, 2005–2026) em "
          "`data/processed/mip/elasticidades_cnt.csv`: servem de verificação da distribuição pela matriz. As do câmbio "
          "real saíram pequenas e quase todas não significativas, por isso não foram usadas para as exportações: o "
          "canal do câmbio usa o vetor de exportações da MIP.", ""]

    L += ["## 8. Limitações", "",
          "- Os multiplicadores por item vêm da literatura e têm incerteza grande; os resultados de composição devem "
          "ser lidos pelas faixas de sensibilidade. No modelo, o multiplicador acumulado em 4 trimestres de uma medida "
          "permanente é cerca de 0,7 × m: os valores centrais ficam abaixo das estimativas SVAR mais altas para "
          "investimento e transferências.",
          "- A matriz de 2015 supõe coeficientes técnicos fixos; a atualização para 2025 corrige o emprego, não a "
          "estrutura de insumos.",
          "- A credibilidade de cada composição do pacote não é modelada.",
          "- A lei de Okun é uma relação reduzida e pode variar com a formalidade do mercado de trabalho.",
          "- O bloco setorial não retroalimenta o modelo macro: a distribuição setorial não altera inflação, câmbio, "
          "reservas ou dívida; o efeito sobre a balança comercial é reportado, não realimentado.",
          "- Sem a POF por faixa de renda, os itens com canal no consumo de alta, média e baixa renda usam o vetor "
          "total de consumo das famílias: a distribuição setorial dos itens de consumo é a mesma.",
          "- O juro real longo divide-se meio a meio entre consumo e investimento (premissa).",
          "- A alíquota efetiva do IRPF é aplicada ao rendimento médio de cada setor; com a isenção até R$ 5.000 de "
          "2026, quase todos os setores ficam com alíquota zero, o que subestima o IR da massa salarial adicional.",
          "- Os coeficientes de emprego de 2025 usam o conceito da PNAD (pessoas no trabalho principal); os da TRU "
          "2015, ocupações.",
          "- O critério de produto exclui as trajetórias com inflação acima de 20%: o modelo não tem o custo de "
          "produto da inflação alta (desorganização de preços relativos, encurtamento de contratos), o que favorece "
          "B e C com adesão baixa.",
          "- A referência S também sofre com a falta de ajuste (prêmio e juro longo maiores): a diferença de cada "
          "estratégia contra S inclui esse ganho de credibilidade, decomposto na seção 1.", ""]
    arq = SAIDA / "relatorio_recessivo.md"
    arq.write_text("\n".join(L), encoding="utf-8")
    return arq


def ic(r, nd=1, est="estimativa") -> str:
    s = f"{fm(r[est], nd)} [{fm(r['ic_lo'], nd)}; {fm(r['ic_hi'], nd)}]"
    return s + (" *" if (r["ic_lo"] > 0 or r["ic_hi"] < 0) else "")


SINTESE = None  # preenchida depois de ler os resultados (ver sintese.md em outputs/v2_2/recessivo, se existir)


if __name__ == "__main__":
    s = SAIDA / "sintese.md"
    print(relatorio(s.read_text(encoding="utf-8").strip().splitlines() if s.exists() else None))
