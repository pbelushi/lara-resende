"""Aplicação do choque institucional estimado no teto de gastos às finalistas da busca híbrida.

O estudo de evento (regras_fiscais_eventos.py) só identifica com clareza o choque do teto: λ_fiscal de 0–0,10
para 0,80–1,00 em até três trimestres, sem salto robusto de λ_π. Aqui, o pacote é anunciado junto com uma regra
fiscal crível: λ_fiscal parte de 1,0 (λ_fiscal anterior de 0,2–0,5 + 0,8, limitado a 1) e segue a regra de
λ endógeno (cai se o primário ficar abaixo do anunciado); λ_π parte do mesmo sorteio U(0,2; 0,5).

Comparação: mesmas finalistas, mesma regra central, com λ_fiscal inicial de 0,35 (sem regra).

Uso: python -m src.regras_fiscais_aplicacao
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import yaml

from . import lambda_dinamico_aplicacao as A
from . import modelo, varredura
from . import recessivo as R
from .busca_hibrida import SAIDA as S_HIB
from .credibilidades_separadas import RAIZ
from .regras_fiscais_eventos import SAIDA


def familia(cid: str, mult: float) -> str:
    if cid.startswith("ant_ref"):
        return "paper"
    if cid.startswith("ant_"):
        return "choque" if mult >= 0.55 else "gradual"
    return "irrestrito" if cid.startswith("u") else "hibrido"


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    lp_draw = np.random.default_rng(2027).uniform(0.2, 0.5, 1000)
    combos = json.loads((S_HIB / "combinacoes.json").read_text())
    ids = pd.read_csv(S_HIB / "fase3_finalistas.csv")["id"].unique()
    linhas = []
    for nome, lf in (("sem regra (λ_fiscal 0,35)", 0.35), ("com regra crível (λ_fiscal 1,0)", 1.0)):
        A.LF = [lf]
        for cid in ids:
            for e in ("P1", "P2", "P3_theta05"):
                for lin in A.avaliar(cid, combos[cid], p, cfg, e, choques, lp_draw, "central"):
                    linhas.append({**lin, "cenario_regra": nome})
    d = pd.DataFrame(linhas)
    d["familia"] = [familia(c, m) for c, m in zip(d["id"], d["mult_medio"])]
    d.to_csv(SAIDA / "finalistas_regra_fiscal.csv", index=False)
    pd.set_option("display.width", 250)
    print(d.groupby(["especificacao", "familia", "cenario_regra"])[["p_bil", "p", "dif_1-16", "lam_pi_ano4",
                                                                   "lam_f_ano1", "lam_f_ano4"]]
          .mean().round(3).to_string())


if __name__ == "__main__":
    main()
