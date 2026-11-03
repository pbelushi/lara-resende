"""Carregamento das reservas com tendência de depreciação e parada súbita com canal reservas → prêmio.

Estratégias: A, A com venda de US$ 30, 60 e 100 bi (em 4 trimestres) e C_sem_piso, todas com R_min = US$ 300 bi.

1. Tendência da depreciação (0; diferencial de inflação; paridade descoberta) × rendimento das reservas (2, 4, 6%),
   pela dívida líquida, limiares 80/70/50, teto e banda.
2. Parada súbita: diagnóstico ano a ano com e sem choque, métricas de trajetória (picos e trimestres acima do teto) e
   diferença das diferenças com κ_R ∈ {0, 2, 5} e R_adequado ∈ {300 (central), 363 (pessimista)}, choque no ano 2,
   persistente e no ano 7. A defesa pode romper R_min; o critério de reservas olha a janela final.
3. Sensibilidade de c3 e R_min pela dívida líquida.

Mesmos choques (seed 42) e mesmos índices de bootstrap (seed 2026) da rodada principal.
Uso: python -m src.reservas_choque [--N 1000] [--R 1000] [--partes 1,2,3]
"""
from __future__ import annotations

import argparse
import copy
import itertools
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from . import bootstrap, modelo, varredura

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "outputs" / "v2_2" / "reservas_choque"
ESPECS = ("P1", "P2", "P3")
SEM_PISO = {"politica_monetaria": "condicionada_sem_piso"}
ESTRATEGIAS = {"A": ("A", {}), "A_res30": ("A", {"venda_reservas": [7.5] * 4}),
               "A_res60": ("A", {"venda_reservas": [15.0] * 4}), "A_res100": ("A", {"venda_reservas": [25.0] * 4}),
               "C_sem_piso": ("C", SEM_PISO)}
ALTS = tuple(k for k in ESTRATEGIAS if k != "A")
PARES = tuple(itertools.combinations(ESTRATEGIAS, 2))
# (alternativa, referência): mesma venda efetiva (isola o alívio monetário) e tamanho da venda
PARES_EXTRA = (("C_sem_piso", "A_res100"), ("A_res60", "A_res30"), ("A_res100", "A_res60"))
SUFS = ("", "_bil", "_liq", "_liq_bil")
LIMIARES = ("80", "70", "50")
LAMS_TRAJ = (0.5, 0.7, 0.9)
TENDENCIAS = {"zero": 0.0, "dif_inflacao": None, "pdj": "pdj"}  # None = π_meta − π_ext
CHOQUES = {"sem": {}, "ano2": {"choque_t": 8}, "ano2_persistente": {"choque_t": 8, "choque_decai": 0.95},
           "ano7": {"choque_t": 28}}
ROT_CHOQUE = {"ano2": "ano 2", "ano2_persistente": "ano 2 persistente", "ano7": "ano 7"}
CANAIS = ((0.0, 300.0), (2.0, 300.0), (5.0, 300.0), (2.0, 363.0), (5.0, 363.0))  # (κ_R, R_adequado)
METRICAS_TRAJ = {"pico_d_gross": "pico da dívida bruta (% PIB)", "pico_d_net": "pico da dívida líquida (% PIB)",
                 "pico_pi": "pico da inflação (% a.a.)", "trim_acima_teto": "trimestres com inflação > 4,5% (de 40)"}
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------- simulação

def _trajetoria(tr: dict, p: dict) -> dict:
    """Métricas ao longo do horizonte (t = 1..T). Trimestres depois da ruptura (π > 50%) contam como acima do teto."""
    teto = p["pi_meta"] + p["criterios"]["tolerancia_inflacao"]
    pi = tr["pi"][:, 1:]
    return {"pico_d_gross": np.nanmax(tr["d_gross"][:, 1:], axis=1), "pico_d_net": np.nanmax(tr["d_net"][:, 1:], axis=1),
            "pico_pi": np.nanmax(pi, axis=1), "trim_acima_teto": (np.isnan(pi) | (pi > teto)).sum(axis=1).astype(float)}


def rodar_bloco(p_base: dict, cfg: dict, espec: str, params: dict, ajuste: dict, choques: np.ndarray,
                grade: np.ndarray) -> dict:
    """Diagonal (sucesso por trajetória nas 4 métricas) e trajetórias em λ fixo para cada estratégia."""
    p = modelo.preparar({**copy.deepcopy(p_base), "especificacao": espec, **params})
    N = choques.shape[0]
    out = {"oks": {}, "pmax": {}, "traj": {}, "carrego": {}}
    for nome, (chave, aj) in ESTRATEGIAS.items():
        cens = varredura.preparar_cenarios(p, cfg, [chave], {**aj, **ajuste})
        mc, oks_m, _ = varredura.diagonal(p, cens, grade, choques, trajetorias=True)
        out["oks"][nome] = {s: oks_m[s][chave] for s in SUFS}
        out["pmax"][nome] = {s: float(mc[f"p_sucesso{s}"].max()) for s in SUFS}
        c = cens[chave]
        out["traj"][nome] = {}
        for lam in LAMS_TRAJ:
            tr = modelo.simular(p, c["cen"], np.full(N, lam), choques=choques, plano=c["plano"],
                                guardar=("pi", "d_gross", "d_net", "i", "R", "prem", "de", "de_tend", "E", "venda"))
            out["traj"][nome][lam] = _trajetoria(tr, p)
            if lam == 0.7:
                # carregamento anual: rendimento + depreciação média (pelo câmbio acumulado) − Selic média
                T = tr["E"].shape[1] - 1
                dep = ((tr["E"][:, -1] / tr["E"][:, 0]) ** (4 / T) - 1) * 100
                selic = np.nanmean(tr["i"][:, 1:], axis=1)
                out["carrego"][nome] = {"selic": float(np.nanmedian(selic)), "deprec": float(np.nanmedian(dep)),
                                        "carrego": float(np.nanmedian(p["rend_reservas"] + dep - selic)),
                                        "venda_prog": float(np.nanmedian(tr["venda"][:, 1:5].sum(axis=1))),
                                        "R_min_traj": float(np.nanmedian(np.nanmin(tr["R"][:, 1:], axis=1))),
                                        "d_net_fim": float(np.nanmedian(tr["d_net"][:, -1])),
                                        "d_gross_fim": float(np.nanmedian(tr["d_gross"][:, -1])),
                                        "prem_medio": float(np.nanmedian(np.nanmean(tr["prem"][:, 1:], axis=1)))}
    return out


# ---------------------------------------------------------------------------------------------- bootstrap

def _comparar(oks: dict, grade, idx, suf: str) -> dict:
    """{(a, b): {limiar: (λ*a, λ*b, λ*b − λ*a, ic_lo, ic_hi)}} para todos os pares."""
    r = {}
    for a, b in PARES:
        bt = bootstrap.diagonal(oks[a][suf], oks[b][suf], grade, idx)
        r[(a, b)] = {rot: (bt[f"A_{rot}"], bt[f"C_{rot}"], bt[f"delta_{rot}"], bt[f"ic_lo_{rot}"], bt[f"ic_hi_{rot}"])
                     for rot in LIMIARES}
    return r


def ordem(comp: dict, pmax: dict, rot: str, suf: str, nomes=None) -> str:
    lam = {}
    for (a, b), v in comp.items():
        lam[a], lam[b] = v[rot][0], v[rot][1]
    if nomes:
        lam = {k: v for k, v in lam.items() if k in nomes}
    o = sorted(lam, key=lambda k: (lam[k], -pmax[k][suf]))
    if all(v >= bootstrap.CENSURA for v in lam.values()):
        return " ≈ ".join(o) + " †"
    s = o[0]
    for a, b in zip(o, o[1:]):
        v = comp.get((a, b)) or comp.get((b, a))
        s += (" ≈ " if v[rot][3] <= 0 <= v[rot][4] else " > ") + b
    return s


def did_lambda(ok: dict, grade, idx) -> dict:
    """ok[(estratégia, 'sem'|'choque')] = (n_λ, N). Devolve o custo do choque de cada estratégia, Δλ* = λ*(com) −
    λ*(sem), e a diferença das diferenças contra A, com IC pareado."""
    r = {}
    for rot in LIMIARES:
        lim = float(rot) / 100
        rep = {k: bootstrap._lambda_star(bootstrap.prob_replicas(v, idx), grade, lim) for k, v in ok.items()}
        pt = {k: bootstrap._lambda_star(v.mean(axis=-1)[None], grade, lim)[0] for k, v in ok.items()}
        custo_rep = {c: rep[(c, "choque")] - rep[(c, "sem")] for c in ESTRATEGIAS}
        custo = {c: pt[(c, "choque")] - pt[(c, "sem")] for c in ESTRATEGIAS}
        for c in ESTRATEGIAS:
            r[("custo", c, rot)] = (custo[c], *np.percentile(custo_rep[c], [2.5, 97.5]))
        for x, ref in [(x, "A") for x in ALTS] + list(PARES_EXTRA):
            r[("did", f"{x}|{ref}", rot)] = (custo[x] - custo[ref],
                                            *np.percentile(custo_rep[x] - custo_rep[ref], [2.5, 97.5]))
    return r


def did_traj(tr: dict, idx, lam: float) -> dict:
    """Média por trajetória do custo do choque em cada métrica e da diferença das diferenças contra A (IC bootstrap)."""
    r = {}
    for m in METRICAS_TRAJ:
        custo = {c: tr[(c, "choque")][lam][m] - tr[(c, "sem")][lam][m] for c in ESTRATEGIAS}
        for c in ESTRATEGIAS:
            r[("custo", c, m)] = (float(np.nanmean(custo[c])), np.nan, np.nan)
        for x, ref in [(x, "A") for x in ALTS] + list(PARES_EXTRA):
            d = custo[x] - custo[ref]
            rep = np.nanmean(d[idx], axis=1)
            r[("did", f"{x}|{ref}", m)] = (float(np.nanmean(d)), *np.percentile(rep, [2.5, 97.5]))
    return r


# ---------------------------------------------------------------------------------------------- texto

def f2(x) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return "não atinge" if x >= bootstrap.CENSURA else f"{x:.2f}".replace(".", ",")


def fs(x, nd=2) -> str:
    return "0," + "0" * nd if abs(x) < 0.5 * 10 ** -nd else f"{x:.{nd}f}".replace(".", ",")


def ic(t, nd=2) -> str:
    return f"{fs(t[0], nd)} [{fs(t[1], nd)}; {fs(t[2], nd)}]" + (" *" if not (t[1] <= 0 <= t[2]) else "")


def fm(x, nd=1) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def _delta(comp: dict, x: str, ref: str, rot: str) -> tuple:
    """Δλ* = λ*(x) − λ*(ref) com IC, qualquer que seja a ordem do par em `comp`."""
    if (ref, x) in comp:
        return comp[(ref, x)][rot][2:]
    d, lo, hi = comp[(x, ref)][rot][2:]
    return (-d, -hi, -lo)


def _rot_par(x, ref) -> str:
    return f"{x} − {ref}"


def _canal(k, ra) -> str:
    return "sem canal" if k == 0 else f"κ = {fm(k, 0)}, R_adeq = {fm(ra, 0)}"


def _csv_comp(linhas, base: dict, comps: dict):
    for s, comp in comps.items():
        for (a, b), v in comp.items():
            for rot, (la, lb, d, lo, hi) in v.items():
                linhas.append({**base, "metrica": s or "bruta", "par": f"{a} × {b}", "limiar": rot, "lambda_a": la,
                               "lambda_b": lb, "delta": d, "ic_lo": lo, "ic_hi": hi})


# ---------------------------------------------------------------------------------------------- partes

def parte1(p, cfg, choques, grade, idx, n_jobs):
    dif = p["pi_meta"] - p["pi_ext"]
    combos = [(e, tn, tv if tv is not None else dif, rend) for e in ESPECS for tn, tv in TENDENCIAS.items()
              for rend in (2.0, 4.0, 6.0)]
    res = Parallel(n_jobs=n_jobs)(delayed(rodar_bloco)(p, cfg, e, {"de_tendencia": tv, "rend_reservas": rend}, {},
                                                      choques, grade) for e, _, tv, rend in combos)
    rot_t = {"zero": "0", "dif_inflacao": f"dif. inflação ({fm(dif)})", "pdj": "paridade descoberta"}
    linhas, L_ord, L_d, L_c, L_x = [], [], [], [], []
    for (e, tn, tv, rend), r in zip(combos, res):
        comps = {s: _comparar(r["oks"], grade, idx, s) for s in SUFS}
        cab = f"| {e} | {rot_t[tn]} | {fm(rend, 0)}% |"
        L_ord.append(cab + " | ".join(ordem(comps[s], r["pmax"], rot, s) for s in ("_liq", "_liq_bil")
                                      for rot in LIMIARES) + " |")
        for x in ALTS:
            L_d.append(cab + f" {x} | " + " | ".join(ic(comps[s][("A", x)][rot][2:]) for s in ("_liq", "_liq_bil")
                                                    for rot in LIMIARES) + " |")
        for x, ref in PARES_EXTRA:
            L_x.append(cab + f" {_rot_par(x, ref)} | " + " | ".join(ic(_delta(comps[s], x, ref, rot))
                                                                    for s in ("_liq", "_liq_bil") for rot in LIMIARES) + " |")
        cr = r["carrego"]
        L_c.append(cab + f" {fm(cr['A']['selic'])} | {fm(cr['A_res100']['deprec'])} | {fm(cr['A_res100']['carrego'])} | "
                   + " | ".join(fm(cr[k]["d_net_fim"]) for k in ESTRATEGIAS) + " |")
        _csv_comp(linhas, {"especificacao": e, "tendencia": tn, "rend_reservas": rend}, comps)
        log.info("parte 1: %s %s rend %.0f", e, tn, rend)
    pd.DataFrame(linhas).to_csv(SAIDA / "carregamento_bootstrap.csv", index=False, float_format="%.4f")
    vendas = res[1]["carrego"]  # P1, tendência 0, rendimento 4%
    cab = "| Especificação | Tendência | Rendimento |"
    L = ["## 1. Tendência de depreciação e custo de carregamento", "",
         "Venda programada efetiva com R_min = US$ 300 bi (mediana, P1, λ = 0,7): "
         + "; ".join(f"{k}: US$ {fm(vendas[k]['venda_prog'], 0)} bi" for k in ESTRATEGIAS if k != "A")
         + ". Com reservas iniciais de US$ 363 bi, a venda de 100 bi fica limitada pelo piso.", "",
         "A tendência entra só na valorização do câmbio (reservas e dívida cambial); o repasse e o câmbio real da demanda "
         "usam o componente cíclico. Paridade descoberta: tendência trimestral = [(1 + Selic − prêmio)/(1 + juro "
         f"externo)]^¼ − 1, por trimestre e trajetória (juro externo = {fm(p['i_ext'])}%).", "",
         "Carregamento (λ = 0,7, medianas, % a.a.; depreciação pelo câmbio acumulado) e DLSP final (% PIB):", "",
         cab + " Selic (A) | Depreciação | Carregamento: rend. + deprec. − Selic | " + " | ".join(
             f"DLSP final {k}" for k in ESTRATEGIAS) + " |", "|---|---|---|" + "---|" * (3 + len(ESTRATEGIAS)), *L_c, "",
         "Ordem pela dívida líquida (1º = menor adesão necessária; \"≈\": o bootstrap pareado não distingue vizinhos; "
         "†: nenhum atinge o limiar):", "",
         cab + " Teto 80% | Teto 70% | Teto 50% | Banda 80% | Banda 70% | Banda 50% |", "|---|---|---|" + "---|" * 6,
         *L_ord, "",
         "Δλ\\* = λ\\*(alternativa) − λ\\*(A) pela dívida líquida (negativo = a alternativa exige menos adesão; * = IC de "
         "95% exclui zero):", "",
         cab + " Alternativa | Teto 80% | Teto 70% | Teto 50% | Banda 80% | Banda 70% | Banda 50% |",
         "|---|---|---|---|" + "---|" * 6, *L_d, "",
         "Pares de mesma venda efetiva (C_sem_piso − A_res100: efeito do alívio monetário) e de tamanho da venda, pela "
         "dívida líquida (negativo = o primeiro exige menos adesão):", "",
         cab + " Par | Teto 80% | Teto 70% | Teto 50% | Banda 80% | Banda 70% | Banda 50% |",
         "|---|---|---|---|" + "---|" * 6, *L_x]
    return L


def diagnostico(p, cfg, choques, nome: str, params: dict) -> list[str]:
    """Estratégia com e sem choque no ano 2 (P1, λ = 0,7): medianas ano a ano e mediana da diferença pareada."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1", **params})
    chave, aj = ESTRATEGIAS[nome]
    N = choques.shape[0]
    tr = {}
    for k, ajc in (("sem", {}), ("choque", CHOQUES["ano2"])):
        c = varredura.preparar_cenarios(q, cfg, [chave], {**aj, **ajc})[chave]
        tr[k] = modelo.simular(q, c["cen"], np.full(N, 0.7), choques=choques, plano=c["plano"],
                               guardar=("pi", "d_gross", "d_net", "i", "R", "prem", "de"))
    nomes = (("pi", "Inflação", "media"), ("d_gross", "Dívida bruta", "fim"), ("d_net", "Dívida líquida", "fim"),
             ("i", "Selic", "media"), ("R", "Reservas", "fim"), ("prem", "Prêmio", "media"),
             ("de", "Depreciação", "soma"))
    L = [f"### Diagnóstico: {nome} com e sem choque no ano 2 (P1, λ = 0,7, {_canal(q['kappa_R'], q['R_adequado'])})", "",
         "Medianas por ano: sem choque / com choque (mediana da diferença pareada). Inflação, Selic e prêmio: média do "
         "ano; depreciação: soma dos trimestres; dívidas (% PIB) e reservas (US$ bi): fim do ano.", "",
         "| Ano | " + " | ".join(n for _, n, _ in nomes) + " |", "|---|" + "---|" * len(nomes)]
    linhas = []
    for ano in range(1, 11):
        s = slice(4 * ano - 3, 4 * ano + 1)
        cel, lin = [], {"estrategia": nome, "ano": ano}
        for v, _, agg in nomes:
            x = {k: (np.nanmean(t[v][:, s], axis=1) if agg == "media" else
                     np.nansum(t[v][:, s], axis=1) if agg == "soma" else t[v][:, 4 * ano]) for k, t in tr.items()}
            a, b, d = np.nanmedian(x["sem"]), np.nanmedian(x["choque"]), np.nanmedian(x["choque"] - x["sem"])
            lin.update({f"{v}_sem": a, f"{v}_choque": b, f"{v}_dif": d})
            cel.append(f"{fm(a)} / {fm(b)} ({fs(d, 1)})")
        linhas.append(lin)
        L.append(f"| {ano} | " + " | ".join(cel) + " |")
    pd.DataFrame(linhas).to_csv(SAIDA / f"diagnostico_choque_{nome}.csv", index=False, float_format="%.4f")
    return L


def parte2(p, cfg, choques, grade, idx, n_jobs):
    combos = [(e, k, ra, ch) for e in ESPECS for k, ra in CANAIS for ch in CHOQUES]
    res = Parallel(n_jobs=n_jobs)(delayed(rodar_bloco)(p, cfg, e, {"kappa_R": k, "R_adequado": ra}, CHOQUES[ch],
                                                      choques, grade) for e, k, ra, ch in combos)
    res = dict(zip(combos, res))
    L_k, L_c, L_l, L_x, csv = [], [], [], [], []
    L_t = {m: [] for m in METRICAS_TRAJ}
    for e in ESPECS:
        for k, ra in CANAIS:
            sem = res[(e, k, ra, "sem")]
            comps = {s: _comparar(sem["oks"], grade, idx, s) for s in ("_liq", "_liq_bil")}
            L_k.append(f"| {e} | {_canal(k, ra)} | " + " | ".join(
                f2(comps[s][("A", "A_res30")]["70"][0]) + " / " + " / ".join(f2(comps[s][("A", x)]["70"][1]) for x in ALTS)
                for s in ("_liq", "_liq_bil")) + " | "
                + " | ".join(ordem(comps[s], sem["pmax"], "70", s) for s in ("_liq", "_liq_bil")) + " |")
            _csv_comp(csv, {"especificacao": e, "kappa_R": k, "R_adequado": ra, "choque": "sem"}, comps)
            for ch in ("ano2", "ano2_persistente", "ano7"):
                com = res[(e, k, ra, ch)]
                cab = f"| {e} | {_canal(k, ra)} | {ROT_CHOQUE[ch]} |"
                dl = {s: did_lambda({(c, w): r["oks"][c][s] for c in ESTRATEGIAS for w, r in (("sem", sem), ("choque", com))},
                                    grade, idx) for s in SUFS}
                L_c.append(cab + " | ".join(ic(dl[s][("custo", c, "70")]) for s in ("_liq", "_liq_bil")
                                            for c in ESTRATEGIAS) + " |")
                L_l.append(cab + " | ".join(ic(dl[s][("did", f"{x}|A", "70")]) for s in ("_liq", "_liq_bil")
                                            for x in ALTS) + " |")
                L_x.append(cab + " | ".join(ic(dl[s][("did", f"{x}|{ref}", "70")]) for s in ("_liq", "_liq_bil")
                                            for x, ref in PARES_EXTRA) + " |")
                dt = did_traj({(c, w): r["traj"][c] for c in ESTRATEGIAS for w, r in (("sem", sem), ("choque", com))},
                              idx, 0.7)
                for m in METRICAS_TRAJ:
                    L_t[m].append(cab + f" {fs(dt[('custo', 'A', m)][0], 1)} | "
                                  + " | ".join(ic(dt[("did", f"{x}|A", m)], 1) for x in ALTS) + " | "
                                  + ic(dt[("did", "C_sem_piso|A_res100", m)], 1) + " |")
                base = {"especificacao": e, "kappa_R": k, "R_adequado": ra, "choque": ch}
                for s, d in dl.items():
                    for kk, v in d.items():
                        csv.append({**base, "metrica": s or "bruta", "tipo": kk[0], "estrategia": kk[1], "limiar": kk[2],
                                    "delta": v[0], "ic_lo": v[1], "ic_hi": v[2]})
                for kk, v in dt.items():
                    csv.append({**base, "metrica": f"traj_{kk[2]}", "tipo": kk[0], "estrategia": kk[1], "limiar": "λ=0,7",
                                "delta": v[0], "ic_lo": v[1], "ic_hi": v[2]})
        log.info("parte 2: %s", e)
    pd.DataFrame(csv).to_csv(SAIDA / "parada_subita_did.csv", index=False, float_format="%.4f")
    cab = "| Especificação | Canal | Choque |"
    L = ["## 2. Parada súbita redesenhada", "",
         "R_min = US$ 300 bi (100% da ARA) para a venda programada. Na parada súbita o BC defende o câmbio com até US$ 50 bi "
         "e pode romper R_min; o critério de reservas exige R ≥ R_min só nos últimos 8 trimestres. Canal reservas → "
         "prêmio: prêmio += κ_R × max(0, R_adequado − R)/R_adequado, com R do fim do trimestre anterior; R_adequado = "
         "300 (central) ou 363 (pessimista: cobra prêmio sempre que as reservas ficam abaixo do nível inicial, mesmo "
         "sem choque). Com R_adequado = 300 o canal só age quando a defesa rompe o piso.", "",
         "Choques: depreciação de 30% e +3 p.p. de prêmio no trimestre 8 (ano 2) ou 28 (ano 7); o prêmio decai 20% por "
         "trimestre (5% no persistente).", "",
         "### Sem choque: efeito do canal sobre λ\\*₇₀ pela dívida líquida", "",
         "λ\\*₇₀ na ordem A / A_res30 / A_res60 / A_res100 / C_sem_piso.", "",
         "| Especificação | Canal | λ\\*₇₀, teto | λ\\*₇₀, banda | Ordem, teto 70% | Ordem, banda 70% |",
         "|---|---|---|---|---|---|", *L_k, "",
         "### Custo do choque: Δλ\\*₇₀ = λ\\*(com choque) − λ\\*(sem), dívida líquida", "",
         "Positivo = o choque exige mais adesão; * = IC de 95% exclui zero.", "",
         cab + " " + " | ".join(f"{c}, teto" for c in ESTRATEGIAS) + " | " + " | ".join(f"{c}, banda" for c in ESTRATEGIAS)
         + " |", "|---|---|---|" + "---|" * (2 * len(ESTRATEGIAS)), *L_c, "",
         "### Custo de cauda: diferença das diferenças de λ\\*₇₀ contra A, dívida líquida", "",
         "Custo do choque da estratégia − custo do choque de A; positivo = a estratégia sofre mais com o choque. Bruta e "
         "limiares 80/50 em parada_subita_did.csv.", "",
         cab + " " + " | ".join(f"{x}, teto" for x in ALTS) + " | " + " | ".join(f"{x}, banda" for x in ALTS) + " |",
         "|---|---|---|" + "---|" * (2 * len(ALTS)), *L_l, "",
         "### Custo de cauda entre pares de mesma venda e de tamanho da venda (λ\\*₇₀, dívida líquida)", "",
         "Custo do choque do primeiro − custo do choque do segundo; positivo = o primeiro sofre mais.", "",
         cab + " " + " | ".join(f"{_rot_par(x, r)}, teto" for x, r in PARES_EXTRA) + " | "
         + " | ".join(f"{_rot_par(x, r)}, banda" for x, r in PARES_EXTRA) + " |",
         "|---|---|---|" + "---|" * (2 * len(PARES_EXTRA)), *L_x]
    for m, rot in METRICAS_TRAJ.items():
        L += ["", f"### Métrica de trajetória: {rot}, λ = 0,7", "",
              "Custo do choque para A (média por trajetória) e diferença das diferenças contra A [IC 95%].", "",
              cab + " Custo para A | " + " | ".join(f"{x} − A" for x in ALTS) + " | C_sem_piso − A_res100 |",
              "|---|---|---|---|" + "---|" * (len(ALTS) + 1), *L_t[m]]
    return L


def parte3(p, cfg, choques, grade, idx, n_jobs):
    combos = [(e, nome, v) for e in ("P1", "P3") for nome, v in
              (("c3 = 0,5", {"c3": 0.5}), ("c3 = 1", {"c3": 1.0}), ("c3 = 2 (padrão)", {}), ("c3 = 4", {"c3": 4.0}),
               ("R_min = 250 (anterior)", {"R_min": 250.0}), ("R_min = 350", {"R_min": 350.0}))]
    res = Parallel(n_jobs=n_jobs)(delayed(rodar_bloco)(p, cfg, e, v, {}, choques, grade) for e, _, v in combos)
    L = ["## 3. Sensibilidade de c3 e R_min pela dívida líquida", "",
         "Δλ\\*₇₀ = λ\\*(alternativa) − λ\\*(A) [IC 95%], sem choque e sem canal κ_R. A venda efetiva depende de "
         "R_min, por isso esta seção a informa linha a linha (US$ bi, trajetória determinística, P1, na ordem "
         + " / ".join(ALTS) + ").", "",
         "| Especificação | Parâmetro | Venda efetiva | Critério | " + " | ".join(f"{x} − A" for x in ALTS)
         + " | C_sem_piso − A_res100 | Ordem |", "|---|---|---|---|" + "---|" * (len(ALTS) + 2)]
    ef_r = {}
    for (e, nome, v), r in zip(combos, res):
        chave = (("R_min", v["R_min"]),) if "R_min" in v else ()
        if chave not in ef_r:
            ef_r[chave] = vendas_efetivas({**p, **dict(chave)}, cfg)
        vend = " / ".join(f"{ef_r[chave][x]:.0f}" for x in ALTS)
        for s, rot_s in (("_liq", "teto"), ("_liq_bil", "banda")):
            c = _comparar(r["oks"], grade, idx, s)
            L.append(f"| {e} | {nome} | {vend} | {rot_s} | " + " | ".join(ic(c[("A", x)]["70"][2:]) for x in ALTS)
                     + f" | {ic(_delta(c, 'C_sem_piso', 'A_res100', '70'))} | {ordem(c, r['pmax'], '70', s)} |")
    return L


def vendas_efetivas(p, cfg) -> dict:
    """Venda programada efetiva (US$ bi) de cada estratégia: trajetória determinística, P1, λ = 1."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1"})
    out = {}
    for nome, (chave, aj) in ESTRATEGIAS.items():
        c = varredura.preparar_cenarios(q, cfg, [chave], aj)[chave]
        tr = modelo.simular(q, c["cen"], 1.0, plano=c["plano"], guardar=("venda",))
        out[nome] = float(tr["venda"][0, 1:5].sum())
    return out


def rotular(texto: str, ef: dict) -> str:
    """Rótulo pela venda efetiva quando o piso limita a venda programada: A_res100 → A_res100 (efetiva: 76)."""
    for nome, (_, aj) in ESTRATEGIAS.items():
        anunciada = sum(aj.get("venda_reservas", []))
        if anunciada and ef[nome] < anunciada - 0.5:
            texto = texto.replace(nome, f"{nome} (efetiva: {ef[nome]:.0f})")
    return texto


def conclusoes(ef: dict) -> list[str]:
    """Seção final, interpretativa (revisada à mão a partir das partes 1 a 3)."""
    r100 = f"A_res100 (efetiva: {ef['A_res100']:.0f})"
    return ["## 4. Conclusões", "",
            "- A venda de reservas melhora a dívida líquida enquanto o carregamento (rendimento + depreciação − Selic) "
            "é negativo, e o ganho encolhe à medida que ele se aproxima de zero (seção 1).",
            f"- O ganho tem retorno decrescente: A_res60 captura a maior parte do efeito de {r100}.",
            f"- O alívio monetário (C_sem_piso − {r100}, mesma venda efetiva) acrescenta um ganho pequeno e "
            "significativo, que aumenta quando há menos reservas para vender (R_min = 350, seção 3).",
            "- Choques transitórios não produzem custo de cauda mensurável. Choques persistentes ou tardios eliminam a "
            "vantagem da venda. O canal reservas → prêmio tem efeito pequeno com R_adequado = 300 e moderado com 363 "
            "(seção 2).",
            "- O critério de fim de horizonte não capta crises que se dissipam antes da janela final; por isso o custo "
            "de cauda é medido também pelas métricas de trajetória e pelos choques persistente e no ano 7."]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=1000)
    ap.add_argument("--R", type=int, default=1000)
    ap.add_argument("--partes", default="1,2,3")
    ap.add_argument("--jobs", type=int, default=-1)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)[:a.N]  # mesmos choques da rodada principal
    grade = varredura.grade_lambda(0.01)
    idx = bootstrap.indices(a.N, a.R, 2026)
    partes = set(a.partes.split(","))
    ef = vendas_efetivas(p, cfg)
    L = ["# Reservas: carregamento, parada súbita e seguro", "",
         f"N = {a.N} trajetórias (seed 42), bootstrap pareado com R = {a.R} (seed 2026). Estratégias: A; A com venda de "
         "US$ 30, 60 e até 100 bi em 4 trimestres (A_res30, A_res60, A_res100); C_sem_piso (venda de até 100 bi do "
         "cenário C). Venda efetiva com o piso (trajetória determinística, P1): "
         + "; ".join(f"{k} US$ {v:.0f} bi" for k, v in ef.items() if k != "A")
         + ". O par que isola o alívio monetário é C_sem_piso × A_res100 (mesma venda efetiva); os demais pares medem "
         "o efeito do tamanho da venda. "
         f"R_min = US$ {fm(p['R_min'], 0)} bi. Dívida líquida: inclinação da DLSP ≤ 0 nos últimos 8 trimestres e DLSP "
         "final ≤ inicial + 5 p.p. Teto: inflação média final ≤ 4,5%; banda: entre 1,5% e 4,5%.", ""]
    if "1" in partes:
        L += parte1(p, cfg, choques, grade, idx, a.jobs) + [""]
    if "2" in partes:
        L += parte2(p, cfg, choques, grade, idx, a.jobs) + [""]
        for nome, prm in (("A", {}), ("A_res100", {}), ("A_res100", {"kappa_R": 5.0, "R_adequado": 300.0})):
            L += diagnostico(p, cfg, choques, nome, prm) + [""]
    # o cabeçalho (L[:3]) já traz as vendas anunciadas e efetivas; as partes 1 e 2 (R_min padrão) usam o rótulo pela
    # venda efetiva; a parte 3 varia R_min e informa a venda efetiva de cada linha
    texto = "\n".join(L[:3]) + "\n" + rotular("\n".join(L[3:]), ef)
    arq = SAIDA / "relatorio_reservas_choque.md"
    if "3" in partes:
        if partes == {"3"} and arq.exists():  # só a parte 3: substitui a seção 3 do relatório existente
            texto = arq.read_text(encoding="utf-8").split("## 3. ")[0].rstrip("\n") + "\n\n"
        else:
            texto += "\n"
        texto += "\n".join(parte3(p, cfg, choques, grade, idx, a.jobs)) + "\n\n" + "\n".join(conclusoes(ef)) + "\n"
    arq.write_text(texto, encoding="utf-8")
    log.info("pronto: %s", SAIDA / "relatorio_reservas_choque.md")


if __name__ == "__main__":
    main()
