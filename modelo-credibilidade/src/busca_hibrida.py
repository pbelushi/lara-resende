"""Busca de pacotes híbridos com λ endógeno: ajuste concentrado no início (para trazer a inflação para dentro do
intervalo cedo e preservar λ_π) feito só com cortes de baixo multiplicador.

Espaço híbrido: itens com multiplicador ≤ 0,6 (renúncias regressivas, benefícios setoriais, subsídios, verbas
acima do teto, previdência militar, custeio; no máximo 5,5% do PIB pelos tetos por item), sem emendas, pisos,
investimento ou transferências; total de 2% a 5,5% do PIB; início no 1º ou 2º trimestre; rampa de 1 a 6
trimestres. Política monetária, reservas e alongamento sorteados como na busca original.

Grupo de controle: o espaço irrestrito da busca original (busca_aleatoria.sortear), avaliado com a mesma regra,
para saber se o melhor desenho com λ endógeno é de fato híbrido.

Avaliação: regra central de λ endógeno (lambda_dinamico_aplicacao.CENTRAL), λ_π inicial ~ U(0,2; 0,5) por
trajetória (seed 2027), λ_fiscal inicial 0,2/0,35/0,5, choques seed 42.
- Fase 1: 3.000 híbridos + 1.500 irrestritos, P2, N = 200.
- Fase 2: 1.500 mutações (dentro do espaço híbrido) em torno dos melhores híbridos e da fronteira sucesso ×
  atividade.
- Fase 3: finalistas híbridas e irrestritas + as finalistas da busca anterior, N = 1.000, P1/P2/P3, regras
  central e simétrica.

Uso: python -m src.busca_hibrida
"""
from __future__ import annotations

import argparse
import json
import logging

import numpy as np
import pandas as pd
import yaml

from . import modelo, varredura
from . import busca_aleatoria as B
from . import recessivo as R
from .credibilidades_separadas import RAIZ, rodar
from .lambda_dinamico_aplicacao import CENTRAL, ORIGEM, _lote as lote_dinamico
from .lambda_dinamico_estimacao import SAIDA as S_DIN

log = logging.getLogger(__name__)
SAIDA = S_DIN.parent / "busca_hibrida"
LF = [0.2, 0.35, 0.5]
BAIXO = [k for k in B.ITENS if R.CONF["itens"][k]["m"] <= 0.6]


def _restringir(c: dict) -> dict:
    p = np.array(c["pesos"])
    p[[i for i, k in enumerate(B.ITENS) if k not in BAIXO]] = 0.0
    if p.sum() == 0:
        p[B.ITENS.index("renuncias")] = 1.0
    c["pesos"] = (p / p.sum()).tolist()
    c["total"] = float(np.clip(c["total"], 2.0, 5.5))
    c["inicio"] = int(np.clip(c["inicio"], 1, 2))
    c["rampa"] = int(np.clip(c["rampa"], 1, 6))
    return c


def sortear_hibrido(rng: np.random.Generator) -> dict:
    c = B.sortear(rng)
    w = rng.dirichlet(np.full(len(BAIXO), 0.8))
    w[rng.random(len(BAIXO)) < 0.2] = 0.0
    p = np.zeros(len(B.ITENS))
    for k, v in zip(BAIXO, w):
        p[B.ITENS.index(k)] = v
    c.update({"pesos": (p / p.sum() if p.sum() else p).tolist(), "total": float(rng.uniform(2.0, 5.5)),
              "inicio": int(rng.integers(1, 3)), "rampa": int(rng.integers(1, 7))})
    return _restringir(c)


def mutar_hibrido(c: dict, rng: np.random.Generator, escala: float) -> dict:
    return _restringir(B.mutar(c, rng, escala))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_hib", type=int, default=3000)
    ap.add_argument("--n_irr", type=int, default=1500)
    ap.add_argument("--n2", type=int, default=1500)
    ap.add_argument("--N1", type=int, default=200)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--seed", type=int, default=23)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    SAIDA.mkdir(parents=True, exist_ok=True)
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    p["dinamica_lambda"] = CENTRAL
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    lp_draw = np.random.default_rng(2027).uniform(0.2, 0.5, 1000)
    rng = np.random.default_rng(a.seed)

    combos = {f"h{i:05d}": sortear_hibrido(rng) for i in range(a.n_hib)}
    combos.update({f"u{i:05d}": B.sortear(rng) for i in range(a.n_irr)})
    log.info("fase 1: %d combinações", len(combos))
    d1 = rodar(combos, p, cfg, "P2", choques[:a.N1], lp_draw[:a.N1], a.jobs, lf_grade=LF)
    d1.to_csv(SAIDA / "fase1.csv", index=False)

    piv = d1.pivot_table(index="id", columns="lambda_fiscal", values=["p_bil", "dif_1-16"])
    piv.columns = [f"{x}_{y}" for x, y in piv.columns]
    piv["p_med"] = piv[[f"p_bil_{x}" for x in LF]].mean(axis=1)
    piv["dif_med"] = piv[[f"dif_1-16_{x}" for x in LF]].mean(axis=1)
    hib = piv[piv.index.str.startswith("h")]
    top = list(hib.sort_values("p_med", ascending=False).head(50).index)
    for q in (0.75, 0.9):
        lim = hib["p_med"].quantile(q)
        top += list(hib[hib["p_med"] >= lim].sort_values("dif_med", ascending=False).head(15).index)
    top = list(dict.fromkeys(top))
    filhos = {f"m{j:05d}": mutar_hibrido(combos[top[j % len(top)]], rng, 0.15 if j < a.n2 // 2 else 0.3)
              for j in range(a.n2)}
    combos.update(filhos)
    log.info("fase 2: %d mutações", len(filhos))
    d2 = rodar(filhos, p, cfg, "P2", choques[:a.N1], lp_draw[:a.N1], a.jobs, lf_grade=LF)
    d2.to_csv(SAIDA / "fase2.csv", index=False)

    d12 = pd.concat([d1, d2])
    piv = d12.pivot_table(index="id", columns="lambda_fiscal", values=["p_bil", "dif_1-16"])
    piv.columns = [f"{x}_{y}" for x, y in piv.columns]
    piv["p_med"] = piv[[f"p_bil_{x}" for x in LF]].mean(axis=1)
    piv["dif_med"] = piv[[f"dif_1-16_{x}" for x in LF]].mean(axis=1)
    hm = piv[~piv.index.str.startswith("u")]
    un = piv[piv.index.str.startswith("u")]
    fin = list(hm.sort_values("p_med", ascending=False).head(15).index)
    teto = hm["p_med"].max()
    for frac in (0.8, 0.9, 0.95):  # fronteira: melhor atividade entre as que chegam perto do melhor sucesso
        fin += list(hm[hm["p_med"] >= frac * teto].sort_values("dif_med", ascending=False).head(4).index)
    fin += list(un.sort_values("p_med", ascending=False).head(8).index)
    teto_u = un["p_med"].max()
    fin += list(un[un["p_med"] >= 0.9 * teto_u].sort_values("dif_med", ascending=False).head(4).index)
    fin = list(dict.fromkeys(fin))
    anteriores = json.loads((ORIGEM / "combinacoes.json").read_text())
    ids_ant = pd.read_csv(ORIGEM / "fase3_finalistas.csv")["id"].unique()
    todos = {**{k: combos[k] for k in fin}, **{f"ant_{k}": anteriores[k] for k in ids_ant}}
    log.info("fase 3: %d finalistas (%d novas)", len(todos), len(fin))
    tarefas = [(cid, c, e, r) for cid, c in todos.items() for e in ("P1", "P2", "P3_theta05")
               for r in ("central", "simetrico")]
    from joblib import Parallel, delayed
    p3 = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")   # avaliar() define a regra
    res = Parallel(n_jobs=a.jobs)(delayed(lote_dinamico)(tarefas[i:i + 6], p3, cfg, choques, lp_draw)
                                  for i in range(0, len(tarefas), 6))
    d3 = pd.DataFrame([x for r in res for x in r])
    d3.to_csv(SAIDA / "fase3_finalistas.csv", index=False)
    (SAIDA / "combinacoes.json").write_text(json.dumps(todos | combos), encoding="utf-8")
    (SAIDA / "execucao.json").write_text(json.dumps({"regra": CENTRAL, "lambda_fiscal": LF,
                                                     "lambda_pi": "U(0,2; 0,5)", "baixo_multiplicador": BAIXO,
                                                     **vars(a)}), encoding="utf-8")
    log.info("pronto: %s", SAIDA)


if __name__ == "__main__":
    main()
