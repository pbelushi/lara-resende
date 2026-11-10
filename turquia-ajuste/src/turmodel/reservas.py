"""
Reservas nas alternativas: a Turquia recompõe as reservas líquidas?

No modelo calibrado, as reservas recebem uma entrada autônoma constante (a0 ≈ US$ 5,5 bi por mês), que reflete o
regime observado (obrigação de conversão de receitas de exportação, depósitos e swaps de países amigos) e compensa
as vendas em defesa do câmbio administrado. Aplicada a um regime de câmbio flutuante, ela faz as reservas subirem
US$ 330 bi em qualquer cenário: não informa nada.

Aqui as reservas das alternativas seguem a regra do câmbio flutuante: só mudam quando o banco central compra.
    R_t = R_0 + Σ compras
As compras são endógenas: o banco central compra dólares para impedir que a lira se aprecie além de um piso em
relação à trajetória da âncora (`compra`, por mês). Compra mais quem atrai mais capital (juro real acima do neutro)
e quem aceita menos apreciação; o custo é perder parte da desinflação que viria do câmbio.
`compra` negativo = o banco central compra mesmo sem pressão de apreciação (meta de depreciação real).

Fases: (1) reavalia as 6.000 combinações da busca com essa medida; (2) sorteia 3.000 combinações novas na região
de juro real positivo, com `compra` de −1% a +1% ao mês; (3) finalistas com N = 1.000.

Uso:  PYTHONPATH=src python -m turmodel.reservas
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from .model import T, idx, politica_observada, simulate
from .search import LAMBDA0, OUT, REFERENCIAS, VARIANTES, carregar, metricas, politica, sortear

SAIDA = OUT.parent / "reservas"


def avaliar(itens, variante, n, seed=7):
    p = carregar(variante)
    obs = politica_observada(p)
    base = simulate(p, obs, n=1, stochastic=False)
    O = simulate(p, obs, n=n, seed=seed, base=None)
    lam0 = np.random.default_rng(2027).uniform(*LAMBDA0, n)
    out = []
    for cid, c in itens:
        X = simulate(p, {**politica(c), "lambda0": lam0}, n=n, seed=seed, base=base)
        R = p["reservas"]["R0"] - np.cumsum(np.nan_to_num(X["vendas"][:, 1:]), axis=1)
        yoy = X["yoy"]
        ok = (yoy[:, 1:].max(axis=1) <= 30) & (yoy[:, T] <= 10) & (yoy[:, T] >= 0)
        pos = (R > 0)
        mes_pos = np.where(pos.any(axis=1), pos.argmax(axis=1) + 1, np.inf)
        m = metricas(X, O)
        m.pop("reservas_min"), m.pop("reservas_set26")
        out.append({"id": cid, "variante": variante, **c, **m,
                    "res_dez23": float(np.median(R[:, idx("2023-12") - 1])), "res_set26": float(np.median(R[:, -1])),
                    "res_set26_p25": float(np.percentile(R[:, -1], 25)),
                    "p_res_pos": float((R[:, -1] > 0).mean()), "p_res_50": float((R[:, -1] >= 50).mean()),
                    "p_sucesso_e_res_pos": float((ok & (R[:, -1] > 0)).mean()),
                    "p_sucesso_e_res_50": float((ok & (R[:, -1] >= 50)).mean()),
                    "meses_ate_positivas": float(np.median(mes_pos)),
                    "apreciacao_real_set26": float(np.median(-X["q"][:, T]) * 100)})
    return out


def rodar(combos, variante, n, jobs=2, lote=100):
    it = list(combos.items())
    res = Parallel(n_jobs=jobs)(delayed(avaliar)(it[i:i + lote], variante, n) for i in range(0, len(it), lote))
    return pd.DataFrame([x for r in res for x in r])


def sortear_reservas(rng):
    c = sortear(rng)
    c["r0"], c["r1"] = float(rng.uniform(4, 20)), float(rng.uniform(3, 12))
    c["compra"] = float(rng.uniform(-0.01, 0.01))
    if rng.random() < 0.5:
        c["ajuste"] = 0.0
    return c


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    combos = json.loads((OUT / "combinacoes.json").read_text())
    rng = np.random.default_rng(99)
    novos = {f"r{i:05d}": sortear_reservas(rng) for i in range(3000)}
    combos.update(novos)
    d = pd.concat([rodar(combos, v, 200) for v in VARIANTES])
    d.to_csv(SAIDA / "triagem.csv", index=False)
    m = d.groupby("id")[["p_sucesso", "p_sucesso_e_res_pos", "p_sucesso_e_res_50", "pib_vs_obs"]].mean()
    fin = list(REFERENCIAS) + ["c03002"]
    for col in ("p_sucesso_e_res_pos", "p_sucesso_e_res_50", "p_sucesso"):
        fin += list(m.sort_values(col, ascending=False).head(12).index)
        top = m[m[col] >= 0.85 * m[col].max()]
        fin += list(top.sort_values("pib_vs_obs", ascending=False).head(6).index)
    fin = [k for k in dict.fromkeys(fin) if k in combos]
    f = pd.concat([rodar({k: combos[k] for k in fin}, v, 1000, lote=10) for v in VARIANTES])
    f.to_csv(SAIDA / "finalistas.csv", index=False)
    (SAIDA / "combinacoes.json").write_text(json.dumps(combos), encoding="utf-8")


if __name__ == "__main__":
    main()
