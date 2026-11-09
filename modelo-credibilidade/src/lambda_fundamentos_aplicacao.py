"""Sensibilidade: finalistas da busca híbrida (λ endógeno, regra central) com o canal de fundamentos.

A validação conjunta (lambda_fundamentos_validacao.py) não sustenta o canal no Brasil; isto é um exercício
"e se": quanto mudariam os resultados das seções 2.9 e 2.10 se a credibilidade brasileira tivesse um canal de
fundamentos.

Variantes:
- sem canal (seção 2.10);
- Focus: β estimados no painel do Focus, só sobre λ_fiscal (primário − estabilizador +0,12; dívida −0,13 por p.p.);
- tipo Argentina: um único índice de fundamentos sobre as duas credibilidades, com o coeficiente argentino do
  primário (0,35 de logit por p.p.; params.yaml do experimento argentino, credibility.c_pb), aplicado ao primário
  menos o estabilizador, e −0,13 por p.p. de dívida.

Uso: python -m src.lambda_fundamentos_aplicacao
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from . import modelo, varredura
from .busca_hibrida import SAIDA as S_HIB
from .credibilidades_separadas import RAIZ
from .lambda_dinamico_aplicacao import _lote
from .lambda_fundamentos_estimacao import SAIDA

VARIANTES = {
    "sem_canal": None,
    "focus": {"b_s_f": 0.12, "b_d_f": -0.13},
    "tipo_argentina": {"b_s_f": 0.35, "b_d_f": -0.13, "b_s_pi": 0.35, "b_d_pi": -0.13},
}


def familia(cid: str, mult: float) -> str:
    if cid.startswith("ant_ref"):
        return "paper"
    if cid.startswith("ant_"):
        return "choque" if mult >= 0.55 else "gradual"
    return "irrestrito" if cid.startswith("u") else "hibrido"


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    base = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    choques = varredura.sortear_choques(base, 1000, cfg["horizonte"], 42)
    lp_draw = np.random.default_rng(2027).uniform(0.2, 0.5, 1000)
    combos = json.loads((S_HIB / "combinacoes.json").read_text())
    ids = pd.read_csv(S_HIB / "fase3_finalistas.csv")["id"].unique()
    res = []
    for nome, fund in VARIANTES.items():
        p = copy.deepcopy(base)
        p["fundamentos_lambda"] = fund
        tarefas = [(cid, combos[cid], e, "central") for cid in ids for e in ("P1", "P2", "P3_theta05")]
        r = Parallel(n_jobs=2)(delayed(_lote)(tarefas[i:i + 6], p, cfg, choques, lp_draw)
                               for i in range(0, len(tarefas), 6))
        d = pd.DataFrame([x for rr in r for x in rr])
        d["canal"] = nome
        res.append(d)
    d = pd.concat(res)
    d["familia"] = [familia(c, m) for c, m in zip(d["id"], d["mult_medio"])]
    d.to_csv(SAIDA / "finalistas_com_canal.csv", index=False)
    pd.set_option("display.width", 250)
    print(d.groupby(["especificacao", "familia", "canal"])[["p_bil", "p", "dif_1-16", "lam_pi_ano4", "lam_f_ano4"]]
          .mean().round(3).to_string())
    best = d[d.especificacao == "P2"].groupby(["canal", "familia"])["p_bil"].max().unstack().round(3)
    print(best)


if __name__ == "__main__":
    main()
