"""
Crédito direcionado: dá para manter o aperto monetário que funciona e sustentar o PIB com uma linha de crédito
subsidiado para investimento?

Alavanca (model.simulate, pol["credito"]): uma fração ψ do gasto sensível a juros toma crédito ao juro real
neutro (2%) em vez do juro de mercado. Efeitos no modelo:
- atividade: o efeito contracionista do juro acima do neutro cai na proporção (1 − ψ);
- inflação: o hiato menos negativo tira parte da desinflação pela demanda (κ);
- fiscal: o Tesouro paga a diferença entre o juro de mercado e o subsidiado sobre o estoque da linha
  (desembolso de ψ × 12% do PIB por ano, amortização de 25% ao ano); o custo entra no primário e na dívida;
- câmbio: uma parte `vaz` do crédito subsidiado vaza para a compra de dólares (foi o que aconteceu com o crédito
  barato turco em 2022) e reduz, na mesma proporção, o efeito do juro sobre o câmbio.
Rampa de 6 meses. Não há efeito do investimento sobre o PIB potencial (hipótese conservadora) nem sobre as
importações.

Fases: (1) grade sobre os cenários de referência: ψ × vazamento × κ; (2) busca aleatória de 3.000 combinações na
região de juro real positivo com ψ ~ U(0; 0,8) e vazamento de 25%, para ver se o ótimo muda; (3) finalistas com
N = 1.000 e vazamento de 0%, 25% e 50%.

Uso:  PYTHONPATH=src python -m turmodel.credito
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from .model import T, idx, politica_observada, simulate
from .reservas import SAIDA as S_RES
from .reservas import sortear_reservas
from .search import LAMBDA0, OUT, VARIANTES, carregar, metricas, politica

SAIDA = OUT.parent / "credito"
VOLUME, AMORT = 12.0, 0.25


def pol_credito(c: dict) -> dict:
    pol = politica(c)
    if c.get("psi", 0) > 0:
        pol["credito"] = {"psi": np.clip(np.arange(T + 1) / 6, 0, 1) * c["psi"], "vaz": c.get("vaz", 0.25),
                          "volume": VOLUME, "amort": AMORT}
    return pol


def avaliar(itens, variante, n, kappa=None, seed=7):
    p = carregar(variante)
    if kappa is not None:
        p = copy.deepcopy(p)
        p["inflacao"]["kappa"] = kappa
    obs = politica_observada(p)
    base = simulate(p, obs, n=1, stochastic=False)
    O = simulate(p, obs, n=n, seed=seed, base=None)
    lam0 = np.random.default_rng(2027).uniform(*LAMBDA0, n)
    out = []
    for cid, c in itens:
        X = simulate(p, {**pol_credito(c), "lambda0": lam0}, n=n, seed=seed, base=base)
        R = p["reservas"]["R0"] - np.cumsum(np.nan_to_num(X["vendas"][:, 1:]), axis=1)
        m = metricas(X, O)
        m.pop("reservas_min"), m.pop("reservas_set26")
        out.append({"id": cid, "variante": variante, "kappa": p["inflacao"]["kappa"], **c, **m,
                    "res_set26": float(np.median(R[:, -1])), "p_res_pos": float((R[:, -1] > 0).mean()),
                    "subsidio_medio": float(np.median(X["sub"][:, 1:].mean(axis=1))),
                    "subsidio_pico": float(np.median(X["sub"][:, 1:].max(axis=1))),
                    "subsidio_acum": float(np.median(X["sub"][:, 1:].sum(axis=1) / 12)),
                    "divida_vs_obs": float(np.median(X["d"][:, T] - O["d"][:, T])),
                    "pib_2022_23": float(np.median((X["ly"][:, idx("2023-12")] - X["ly"][:, idx("2021-12")]) * 50))})
    return out


def rodar(combos, variante, n, kappa=None, jobs=2, lote=50):
    it = list(combos.items())
    res = Parallel(n_jobs=jobs)(delayed(avaliar)(it[i:i + lote], variante, n, kappa) for i in range(0, len(it), lote))
    return pd.DataFrame([x for r in res for x in r])


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    todos = json.loads((S_RES / "combinacoes.json").read_text())
    refs = {"melhor": todos["c03002"], "melhor_reservas": todos["r01540"], "aperto_tradicional": todos["ref_so_juros"],
            "heterodoxa": todos["ref_heterodoxa"]}
    grade = {}
    for nome, c in refs.items():
        for psi in (0.0, 0.2, 0.4, 0.6, 0.8):
            for vaz in ((0.25,) if psi == 0 else (0.0, 0.25, 0.5)):
                grade[f"{nome}|psi{psi}|vaz{vaz}"] = {**c, "psi": psi, "vaz": vaz, "base": nome}
    g = pd.concat([rodar(grade, v, 1000, k, lote=8) for v in VARIANTES for k in (None, 1.5)])
    g.to_csv(SAIDA / "grade.csv", index=False)

    rng = np.random.default_rng(123)
    combos = {}
    for i in range(3000):
        c = sortear_reservas(rng)
        c["psi"], c["vaz"] = float(rng.uniform(0, 0.8)) if rng.random() < 0.8 else 0.0, 0.25
        combos[f"k{i:05d}"] = c
    d = pd.concat([rodar(combos, v, 200) for v in VARIANTES])
    d.to_csv(SAIDA / "triagem.csv", index=False)
    m = d.groupby("id")[["p_sucesso", "pib_vs_obs"]].mean()
    fin = list(m.sort_values("p_sucesso", ascending=False).head(15).index)
    for frac in (0.7, 0.8, 0.9):
        fin += list(m[m.p_sucesso >= frac * m.p_sucesso.max()].sort_values("pib_vs_obs", ascending=False).head(8).index)
    fin = list(dict.fromkeys(fin))
    fc = {f"{k}|vaz{vz}": {**combos[k], "vaz": vz} for k in fin for vz in (0.0, 0.25, 0.5)}
    f = pd.concat([rodar(fc, v, 1000, lote=8) for v in VARIANTES])
    f.to_csv(SAIDA / "finalistas.csv", index=False)
    (SAIDA / "combinacoes.json").write_text(json.dumps(combos), encoding="utf-8")


if __name__ == "__main__":
    main()
