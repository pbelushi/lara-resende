"""Busca "contra o mercado": pacotes que funcionam sem o apoio majoritário do mercado.

Hipótese do cenário: o mercado é minoritário e hostil.
- λ_π ~ U(0; 0,3) por trajetória e λ_fiscal ∈ {0; 0,15; 0,3}: nunca mais de 30% das expectativas e do prêmio
  seguem o anúncio do governo.
- Regra hostil de λ endógeno: o mercado pune os erros (−0,071 por p.p. de inflação fora do intervalo; −0,10 por
  p.p. de primário abaixo do anunciado), mas não premia os acertos (coeficientes de alta zerados).
- Sem regra fiscal crível nem ganho institucional de credibilidade.

Instrumentos que não dependem do mercado, além dos da busca original (tamanho e composição do ajuste, ritmo,
regra de juros, venda de reservas, alongamento da dívida):
- indexação à meta: fração θ ∈ [0; 0,4] da inércia inflacionária passa a ser reajustada pela meta em vez da
  inflação passada (regra do salário mínimo e dos benefícios, preços administrados, contratos do governo),
  em rampa de 4 trimestres (modelo.simular, p["indexacao_meta"]).

Espaço sorteado: metade híbrida (busca_hibrida.sortear_hibrido), metade irrestrita (busca_aleatoria.sortear);
θ sorteado em 70% das combinações (0 nas demais, para comparação).

Fases: 4.500 combinações (P2, N = 200), 1.500 mutações em torno das melhores e da fronteira sucesso × atividade,
finalistas com N = 1.000 em P1/P2/P3, com a regra hostil e com λ fixo (sem erosão).

Uso: python -m src.busca_contra_mercado
"""
from __future__ import annotations

import argparse
import copy
import json
import logging

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from . import busca_aleatoria as B
from . import lambda_dinamico_aplicacao as A
from . import modelo, varredura
from . import recessivo as R
from .busca_hibrida import mutar_hibrido, sortear_hibrido
from .credibilidades_separadas import RAIZ
from .lambda_fundamentos_estimacao import SAIDA as S_F

log = logging.getLogger(__name__)
SAIDA = S_F.parent / "busca_contra_mercado"
LF = [0.0, 0.15, 0.3]
HOSTIL = {"b_pi_pos": 0.0, "b_pi_neg": 0.071, "b_f_pos": 0.0, "b_f_neg": 0.10, "tol": 1.5}


def sortear(rng: np.random.Generator, hibrido: bool) -> dict:
    c = sortear_hibrido(rng) if hibrido else B.sortear(rng)
    c["indexacao"] = float(rng.uniform(0, 0.4)) if rng.random() < 0.7 else 0.0
    c["hibrido"] = bool(hibrido)
    return c


def mutar(c: dict, rng: np.random.Generator, escala: float) -> dict:
    n = mutar_hibrido(c, rng, escala) if c.get("hibrido") else B.mutar(c, rng, escala)
    n["indexacao"] = float(np.clip(c.get("indexacao", 0.0) + rng.normal(0, 0.4 * escala), 0, 0.4))
    n["hibrido"] = c.get("hibrido", False)
    return n


def _lote(tarefas, p, cfg, choques, lp_draw):
    A.LF = LF
    A.REGRAS["hostil"] = HOSTIL
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    out = []
    for cid, c, espec, regra in tarefas:
        q = copy.deepcopy(p)
        q["indexacao_meta"] = c.get("indexacao", 0.0)
        for lin in A.avaliar(cid, c, q, cfg, espec, choques, lp_draw, regra):
            lin["indexacao"] = c.get("indexacao", 0.0)
            lin["hibrido"] = c.get("hibrido", False)
            out.append(lin)
    return out


def rodar(combos, p, cfg, especs, regras, choques, lp_draw, jobs, lote=20) -> pd.DataFrame:
    tarefas = [(k, c, e, r) for k, c in combos.items() for e in especs for r in regras]
    res = Parallel(n_jobs=jobs)(delayed(_lote)(tarefas[i:i + lote], p, cfg, choques, lp_draw)
                                for i in range(0, len(tarefas), lote))
    return pd.DataFrame([x for r in res for x in r])


def pivo(d: pd.DataFrame) -> pd.DataFrame:
    v = d.pivot_table(index="id", columns="lambda_fiscal_0", values=["p_bil", "p", "dif_1-16"])
    out = pd.DataFrame({"p_bil": v["p_bil"].mean(axis=1), "p_teto": v["p"].mean(axis=1),
                        "dif": v["dif_1-16"].mean(axis=1)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n1", type=int, default=4500)
    ap.add_argument("--n2", type=int, default=1500)
    ap.add_argument("--N1", type=int, default=200)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--seed", type=int, default=31)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    lp_draw = np.random.default_rng(2027).uniform(0.0, 0.3, 1000)
    rng = np.random.default_rng(a.seed)

    combos = {f"c{i:05d}": sortear(rng, i % 2 == 0) for i in range(a.n1)}
    log.info("fase 1: %d combinações", len(combos))
    d1 = rodar(combos, p, cfg, ["P2"], ["hostil"], choques[:a.N1], lp_draw[:a.N1], a.jobs)
    d1.to_csv(SAIDA / "fase1.csv", index=False)
    v = pivo(d1)
    top = list(v.sort_values("p_bil", ascending=False).head(40).index)
    top += list(v.sort_values("p_teto", ascending=False).head(20).index)
    for q in (0.75, 0.9):
        top += list(v[v.p_bil >= v.p_bil.quantile(q)].sort_values("dif", ascending=False).head(10).index)
    top = list(dict.fromkeys(top))
    filhos = {f"m{j:05d}": mutar(combos[top[j % len(top)]], rng, 0.15 if j < a.n2 // 2 else 0.3)
              for j in range(a.n2)}
    combos.update(filhos)
    log.info("fase 2: %d mutações", len(filhos))
    d2 = rodar(filhos, p, cfg, ["P2"], ["hostil"], choques[:a.N1], lp_draw[:a.N1], a.jobs)
    d2.to_csv(SAIDA / "fase2.csv", index=False)

    v = pivo(pd.concat([d1, d2]))
    v = v.join(pd.Series({k: c.get("indexacao", 0) for k, c in combos.items()}, name="indexacao"))
    fin = list(v.sort_values("p_bil", ascending=False).head(15).index)
    fin += list(v.sort_values("p_teto", ascending=False).head(8).index)
    teto = v.p_bil.max()
    for frac in (0.8, 0.9):
        fin += list(v[v.p_bil >= frac * teto].sort_values("dif", ascending=False).head(5).index)
    sem = v[v.indexacao == 0]
    fin += list(sem.sort_values("p_bil", ascending=False).head(6).index)
    fin = list(dict.fromkeys(fin))
    log.info("fase 3: %d finalistas", len(fin))
    d3 = rodar({k: combos[k] for k in fin}, p, cfg, ["P1", "P2", "P3_theta05"], ["hostil", "estatico"],
               choques, lp_draw, a.jobs, lote=4)
    d3.to_csv(SAIDA / "fase3_finalistas.csv", index=False)
    (SAIDA / "combinacoes.json").write_text(json.dumps(combos), encoding="utf-8")
    (SAIDA / "execucao.json").write_text(json.dumps({"lambda_pi": "U(0; 0,3)", "lambda_fiscal": LF,
                                                     "regra": HOSTIL, **vars(a)}), encoding="utf-8")
    log.info("pronto: %s", SAIDA)


if __name__ == "__main__":
    main()
