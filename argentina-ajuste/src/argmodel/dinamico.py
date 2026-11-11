"""
Versão 2 do experimento: λ endógeno.

As credibilidades das âncoras (λ_câmbio, λ_juros) e a adesão à troca de dívida (λ_fiscal) deixam de ser
fixas: a cada trimestre, são revistas pelo resultado. Inflação perto da âncora anunciada (crawl/bandas, regra
SCRER ou meta do BC) eleva λ; longe dela, reduz. Primário acima da meta eleva λ_fiscal; abaixo, reduz.
A regra é a estimada no Brasil (Focus, 2005–2025; projeto lara-resende, lambda_dinamico_estimacao.py),
convertida para unidades de tolerância (tol = 50% da âncora) e para revisão trimestral. Ver
model._revisar_lambda e credibility.dinamica em config/params.yaml.

Passos:
 1. Recalibração com λ endógeno (regra do CLAUDE.md: toda mudança no modelo exige recalibrar).
 2. Os 48 cenários com λ endógeno, comparados aos da v1 (λ fixo).
 3. Trajetórias de λ nos cenários de interesse.
 4. Mapa de credibilidade inicial (λ_câmbio = λ_juros no ponto de partida) para as combinações de credibility.py.
 5. Sensibilidade da regra (simétrica, metade, dobro), cada uma recalibrada.

Uso:  PYTHONPATH=src python -m argmodel.dinamico
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd
import yaml

from . import calibrate as C
from . import credibility as CR
from .experiment import REFERENCE, grid, load_calibrated, run
from .model import ACTUAL, ROOT, Scenario, load_params, metrics, simulate

OUT = ROOT / "outputs" / "v2_lambda_endogeno"
TOL = {"pobreza": 2.0, "inflação dez/dez": 6.0, "PIB anual": 1.5}   # tolerâncias do CLAUDE.md
INTERESSE = {
    "Referência (Milei)": REFERENCE,
    "BMULT + Juros+": Scenario(dev=False, rate=True, fiscal="baixo_multiplicador", priv=True, swap=False),
    "BMULT + Juros+ + Troca": Scenario(dev=False, rate=True, fiscal="baixo_multiplicador", priv=True, swap=True),
    "Câmbio comp. + Juros+ + BMULT": Scenario(dev=True, rate=True, fiscal="baixo_multiplicador", priv=True, swap=False),
    "Gradual": Scenario(dev=False, rate=False, fiscal="gradual", priv=True, swap=False),
    "Motosserra + Juros+": Scenario(dev=False, rate=True, fiscal="motosserra", priv=True, swap=False),
}
VARIANTES = {"central": {}, "simetrica": {"b_up": 0.0266}, "metade": "x0.5", "dobro": "x2"}


def base_dinamica(variante: str = "central") -> dict:
    b = load_params()
    d = dict(b["credibility"]["dinamica"], on=True)
    v = VARIANTES[variante]
    if isinstance(v, dict):
        d.update(v)
    else:
        f = float(v[1:])
        d.update({k: d[k] * f for k in ("b_up", "b_dn", "b_f")})
    b["credibility"]["dinamica"] = d
    return b


def checar_ajuste(fit: pd.DataFrame) -> pd.DataFrame:
    f = fit[fit.bloco.isin(TOL)].copy()
    f["tolerancia"] = f.bloco.map(TOL)
    f["dentro"] = f.erro.abs() <= f.tolerancia
    return f


def recalibrar(variante: str) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    p, tab = C.calibrate(verbose=0, base=base_dinamica(variante))
    return p, tab, C.residuals_breakdown(p)


def trajetorias(p: dict, n: int = 400) -> pd.DataFrame:
    linhas = []
    for nome, sc in INTERESSE.items():
        o = simulate(p, sc, n=n, seed=7)
        for t in (3, 6, 12, 18, 24):
            linhas.append({"cenario": nome, "mes": t,
                           **{k: float(np.median(o[k][:, t])) for k in ("lam_fx", "lam_rate", "lam_f", "cred_x",
                                                                        "cred_i")},
                           "inflacao_mensal_p50": float(np.median(o["pi"][:, t]) * 100)})
    return pd.DataFrame(linhas)


def comparar(res_v1: pd.DataFrame, res_v2: pd.DataFrame) -> pd.DataFrame:
    cols = ["infl_2024_p50", "infl_2025_p50", "pobreza_2025S2_p50", "renda_media_2025_p50", "pib_2025_p50",
            "embi_dez25_p50", "d_infl_2025", "d_pobreza_2025S2", "d_renda_media_2025"]
    a = res_v1.set_index("cenario")[cols].add_suffix("_v1")
    b = res_v2.set_index("cenario")[cols].add_suffix("_v2")
    c = a.join(b)
    c["rank_pobreza_v1"] = c["pobreza_2025S2_p50_v1"].rank()
    c["rank_pobreza_v2"] = c["pobreza_2025S2_p50_v2"].rank()
    return c.reset_index()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    p1 = load_calibrated()

    # 0. diagnóstico: λ endógeno com a calibração da v1
    q = copy.deepcopy(p1)
    q["credibility"]["dinamica"] = base_dinamica()["credibility"]["dinamica"]
    diag = checar_ajuste(C.residuals_breakdown(q))
    diag.to_csv(OUT / "ajuste_sem_recalibrar.csv", index=False)

    # 1. recalibração (central e variantes)
    calib = {}
    for v in VARIANTES:
        p, tab, fit = recalibrar(v)
        calib[v] = p
        tab.to_csv(OUT / f"calibracao_parametros_{v}.csv", index=False)
        fit.to_csv(OUT / f"calibracao_ajuste_{v}.csv", index=False)
        with open(OUT / f"params_calibrated_dinamico_{v}.yaml", "w") as f:
            f.write("# Gerado por argmodel.dinamico — λ endógeno, variante " + v + "\n")
            yaml.safe_dump(p, f, allow_unicode=True, sort_keys=False)
        ch = checar_ajuste(fit)
        print(f"[{v}] ajuste dentro das tolerâncias: {int(ch.dentro.sum())}/{len(ch)}")
        print(ch[["bloco", "ponto", "modelo", "observado", "erro", "dentro"]].round(2).to_string(index=False))
    p2 = calib["central"]
    t0 = pd.read_csv(ROOT / "outputs" / "calibracao_parametros.csv").set_index("parametro")["calibrado"]
    t2 = pd.read_csv(OUT / "calibracao_parametros_central.csv").set_index("parametro")["calibrado"]
    pd.DataFrame({"v1": t0, "v2_central": t2}).to_csv(OUT / "parametros_v1_v2.csv")

    # 2. 48 cenários
    res1 = pd.read_csv(ROOT / "outputs" / "cenarios_resumo.csv")
    res2, sims2 = run(p2)
    res2.to_csv(OUT / "cenarios_resumo_v2.csv", index=False)
    cmp_ = comparar(res1, res2)
    cmp_.to_csv(OUT / "comparacao_v1_v2.csv", index=False)
    for v in ("simetrica", "metade", "dobro"):
        rv, _ = run(calib[v])
        rv.to_csv(OUT / f"cenarios_resumo_v2_{v}.csv", index=False)

    # 3. trajetórias de λ
    tr = trajetorias(p2)
    tr.to_csv(OUT / "trajetorias_lambda.csv", index=False)

    # 4. mapa de credibilidade inicial (λ_câmbio = λ_juros), vs. referência no ponto calibrado
    l0 = p2["credibility"]["lambda_ref"]
    ref_m = metrics(simulate(p2, REFERENCE, n=300, seed=7))
    linhas = []
    for nome, kw in CR.COMBOS.items():
        sc = CR._sc(kw)
        for lam in CR.GRID:
            m = metrics(simulate(CR._p(p2, lam, lam if sc.rate else l0), sc, n=300, seed=7))
            linhas.append({"combinacao": nome, "lambda_inicial": lam, **CR._cmp(m, ref_m)})
    mapa = pd.DataFrame(linhas)
    mapa.to_csv(OUT / "mapa_lambda_inicial_v2.csv", index=False)
    # mesmo mapa na v1 (λ fixo), para comparar
    ref1 = metrics(simulate(p1, REFERENCE, n=300, seed=7))
    l1 = []
    for nome, kw in CR.COMBOS.items():
        sc = CR._sc(kw)
        for lam in CR.GRID:
            m = metrics(simulate(CR._p(p1, lam, lam if sc.rate else l0), sc, n=300, seed=7))
            l1.append({"combinacao": nome, "lambda_inicial": lam, **CR._cmp(m, ref1)})
    pd.DataFrame(l1).to_csv(OUT / "mapa_lambda_inicial_v1.csv", index=False)

    cols = ["cenario", "infl_2025_p50_v1", "infl_2025_p50_v2", "pobreza_2025S2_p50_v1", "pobreza_2025S2_p50_v2",
            "d_pobreza_2025S2_v1", "d_pobreza_2025S2_v2", "renda_media_2025_p50_v1", "renda_media_2025_p50_v2",
            "rank_pobreza_v1", "rank_pobreza_v2"]
    print(cmp_.sort_values("pobreza_2025S2_p50_v2")[cols].round(1).to_string(index=False))
    print(tr.round(3).to_string(index=False))
    piv = mapa.pivot(index="lambda_inicial", columns="combinacao", values="P_3frentes")
    print(piv.round(2).to_string())
    print(pd.DataFrame(l1).pivot(index="lambda_inicial", columns="combinacao", values="P_3frentes").round(2).to_string())
    (OUT / "execucao.json").write_text(json.dumps({"regra": base_dinamica()["credibility"]["dinamica"],
                                                   "variantes": {k: str(v) for k, v in VARIANTES.items()}},
                                                  ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
