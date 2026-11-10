"""
Choque de juros: juro real muito alto nos primeiros 6 ou 12 meses e queda gradual depois. Concentra o custo de
PIB no primeiro ano e retoma o ritmo nos seguintes?

Grade sobre o melhor cenário da busca (c03002: meta de 5% imediata, administrados pela meta, sem ajuste fiscal):
- juro real do choque r0: 15%, 20%, 25%, 30%;
- duração do choque (platô): 6 ou 12 meses;
- queda até o juro real final em 12 ou 24 meses;
- juro real final r1: 2% (neutro), 4%, 6%, 8%, 11%;
- reação à inflação: 0 (calendário puro: o juro cai na data marcada), 0,5 e 0,95 (o juro só cai se a inflação
  cair: cada ponto de inflação acima da meta segura 0,95 ponto de juro real).
Comparação: c03002 (juro real de 17% a 11% em 27 meses, sem platô) e a política observada.

Uso:  PYTHONPATH=src python -m turmodel.choque
"""
from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from .model import T, idx, pib_anual, politica_observada, simulate
from .reservas import SAIDA as S_RES
from .search import LAMBDA0, OUT, VARIANTES, carregar, metricas, politica

SAIDA = OUT.parent / "choque"


def pol_choque(c):
    pol = politica(c)
    pol["real"]["plato"] = c.get("plato", 0)
    return pol


def avaliar(itens, variante, n=1000, seed=7):
    p = carregar(variante)
    obs = politica_observada(p)
    base = simulate(p, obs, n=1, stochastic=False)
    O = simulate(p, obs, n=n, seed=seed, base=None)
    lam0 = np.random.default_rng(2027).uniform(*LAMBDA0, n)
    out = []
    for cid, c in itens:
        X = O if cid == "observada" else simulate(p, {**pol_choque(c), "lambda0": lam0}, n=n, seed=seed, base=base)
        R = p["reservas"]["R0"] - np.cumsum(np.nan_to_num(X["vendas"][:, 1:]), axis=1)
        m = metricas(X, O)
        m.pop("reservas_min"), m.pop("reservas_set26")
        g = pib_anual(X)
        dif = (X["ly"] - O["ly"]) * 100
        out.append({"id": cid, "variante": variante, **{k: c.get(k) for k in ("r0", "r1", "plato", "meses", "reacao")}, **m,
                    **{f"pib_{a}": float(np.median(v)) for a, v in g.items()},
                    "nivel_pib_dez22": float(np.median(dif[:, idx("2022-12")])),
                    "nivel_pib_dez24": float(np.median(dif[:, idx("2024-12")])),
                    "nivel_pib_set26": float(np.median(dif[:, T])),
                    "juro_real_2o_ano": float(np.median(X["r"][:, 13:25].mean(axis=1))),
                    "juro_real_ult_ano": float(np.median(X["r"][:, -12:].mean(axis=1))),
                    "juro_nominal_pico": float(np.median(X["i"][:, 1:].max(axis=1))),
                    "infl_dez22_p": float(np.median(X["yoy"][:, idx("2022-12")])),
                    "res_set26": float(np.median(R[:, -1]))})
    return out


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    b = json.loads((S_RES / "combinacoes.json").read_text())["c03002"]
    combos = {"observada": {}, "c03002": b}
    for r0, pl, me, r1, re in itertools.product((15, 20, 25, 30), (6, 12), (12, 24), (2, 4, 6, 8, 11), (0.0, 0.5, 0.95)):
        combos[f"ch_r{r0}_p{pl}_m{me}_f{r1}_re{re}"] = {**b, "r0": float(r0), "r1": float(r1), "plato": pl, "meses": me,
                                                       "reacao": re}
    it = list(combos.items())
    res = Parallel(n_jobs=2)(delayed(avaliar)(it[i:i + 10], v) for v in VARIANTES for i in range(0, len(it), 10))
    pd.DataFrame([x for r in res for x in r]).to_csv(SAIDA / "grade.csv", index=False)


if __name__ == "__main__":
    main()
