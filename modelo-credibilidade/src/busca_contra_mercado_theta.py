"""Curva de sucesso por grau de indexação à meta (θ) para os melhores pacotes da busca contra o mercado, e custo
distributivo da indexação: perda real acumulada de quem passa a ser reajustado pela meta.

Perda real de um rendimento reajustado pela meta, em vez da inflação passada, no ano y: θ_efetivo × (π_y − meta)
quando π_y > meta (e ganho quando π_y < meta). Reporta a perda acumulada 2027–2030 (mediana das trajetórias), para
quem é reajustado integralmente pela meta (θ = 1 para aquele rendimento) — o teto do custo para salário mínimo e
benefícios.

Uso: python -m src.busca_contra_mercado_theta
"""
import copy
import json

import numpy as np
import pandas as pd
import yaml

from . import lambda_dinamico_aplicacao as A
from . import modelo, varredura
from . import recessivo as R
from .busca_contra_mercado import HOSTIL, LF, SAIDA
from .credibilidades_separadas import RAIZ, REF, simular_combo

PACOTES = {"m00295": "híbrido 4,1% do PIB, alívio condicionado", "m01231": "híbrido 5,5% do PIB, Taylor",
           "ref_C_sem_piso": "estratégia C sem piso do paper", "ref_A_reservas": "estratégia A com reservas do paper"}
THETAS = [0.0, 0.1, 0.2, 0.3, 0.4]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--thetas", default=",".join(str(t) for t in THETAS))
    ap.add_argument("--saida", default="curva_theta.csv")
    a = ap.parse_args()
    thetas = [float(t) for t in a.thetas.split(",")]
    A.LF = LF
    A.REGRAS["hostil"] = HOSTIL
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    lp = np.random.default_rng(2027).uniform(0.0, 0.3, 1000)
    combos = json.loads((SAIDA / "combinacoes.json").read_text())
    combos.update({"ref_C_sem_piso": REF["C_sem_piso"], "ref_A_reservas": REF["A_reservas"]})
    linhas = []
    for cid in PACOTES:
        for th in thetas:
            q = copy.deepcopy(p)
            q["indexacao_meta"] = th
            for e in ("P1", "P2"):
                for lin in A.avaliar(cid, combos[cid], q, cfg, e, choques, lp, "hostil"):
                    linhas.append({**lin, "theta": th, "pacote": PACOTES[cid]})
            # custo distributivo (P2, λ_fiscal 0,15, regra hostil)
            q2 = copy.deepcopy(q)
            q2["dinamica_lambda"] = HOSTIL
            tr = simular_combo(combos[cid], q2, cfg, "P2", choques, lp, np.full(1000, 0.15))[0]
            anos = [np.nanmean(tr["pi"][:, 4 * k + 1:4 * k + 5], axis=1) for k in range(4)]   # 2027–2030
            perda = sum(np.maximum(a - p["pi_meta"], 0) - np.maximum(p["pi_meta"] - a, 0) for a in anos)
            linhas.append({"id": cid, "pacote": PACOTES[cid], "theta": th, "especificacao": "custo",
                           "perda_real_acum_p50": float(np.nanmedian(perda)),
                           "perda_real_acum_p90": float(np.nanpercentile(perda, 90)),
                           "inflacao_media_2027_30_p50": float(np.nanmedian(np.mean(anos, axis=0)))})
    d = pd.DataFrame(linhas)
    d.to_csv(SAIDA / a.saida, index=False)
    s = d[d.especificacao != "custo"].groupby(["pacote", "especificacao", "theta"])[["p_bil", "p", "dif_1-16"]].mean()
    pd.set_option("display.width", 220)
    print(s.round(3).unstack("especificacao").to_string())
    print(d[d.especificacao == "custo"][["pacote", "theta", "perda_real_acum_p50", "perda_real_acum_p90",
                                         "inflacao_media_2027_30_p50"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
