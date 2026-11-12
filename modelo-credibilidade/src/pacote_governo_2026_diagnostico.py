"""Diagnóstico do pacote do governo (PLP 299/2026): por que falha, que primário entrega e de que tamanho precisaria ser.

1) Critério que falha primeiro, primário em 2027 e 2030 e dívida em 2030 (medianas), no pacote do governo e nas
   referências, com credibilidades baixas (regra central) e com mercado hostil, P2.
2) Escala: a mesma composição do pacote do governo (benefícios setoriais, custeio, investimento, supersalários)
   com tamanho de 0,37% a 3,0% do PIB (teto da composição), credibilidades baixas e mercado hostil com θ = 0,32.

Uso: python -m src.pacote_governo_2026_diagnostico
"""
import copy
import json

import numpy as np
import pandas as pd
import yaml

from . import metricas, modelo, varredura
from . import recessivo as R
from .busca_contra_mercado import HOSTIL, SAIDA as SAIDA_CM
from .credibilidades_separadas import RAIZ, REF, simular_combo
from .lambda_dinamico_aplicacao import CENTRAL
from .pacote_governo_2026 import PIB27, SAIDA, T_2027T4, T_2030T4, combo_governo

N = 1000
T_2027 = slice(2, 6)    # 2027T1..T4
T_2030 = slice(14, 18)  # 2030T1..T4


def medir(tr, q):
    ok, det = metricas.sucesso(tr, q, bilateral=True)
    cod = metricas.codigo_falha(det)
    falha = {f"falha_{metricas.CODIGOS_FALHA[c]}": float((cod == c).mean()) for c in range(1, 6)}
    return {"p_banda": float(ok.mean()), **falha,
            "primario_2027": float(np.nanmedian(tr["s"][:, T_2027].mean(axis=1))),
            "primario_2030": float(np.nanmedian(tr["s"][:, T_2030].mean(axis=1))),
            "divida_2030T4": float(np.nanmedian(tr["d_gross"][:, T_2030T4])),
            "inflacao_final": float(np.nanmedian(tr["pi"][:, -8:].mean(axis=1)))}


def main():
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    for k in ("R", "s"):
        if k not in R.GUARDAR:
            R.GUARDAR = R.GUARDAR + (k,)
    choques = varredura.sortear_choques(p, N, cfg["horizonte"], 42)
    combos = json.loads((SAIDA_CM / "combinacoes.json").read_text())
    lp_baixa = np.random.default_rng(2027).uniform(0.2, 0.5, N)
    lp_hostil = np.random.default_rng(2027).uniform(0.0, 0.3, N)
    grupos = [("baixa, regra central", lp_baixa, (0.2, 0.35, 0.5), CENTRAL, 0.0),
              ("hostil", lp_hostil, (0.0, 0.15, 0.3), HOSTIL, 0.0),
              ("hostil, θ = 0,32", lp_hostil, (0.0, 0.15, 0.3), HOSTIL, 0.32)]

    # 1) diagnóstico
    casos = [("governo (0,37% do PIB)", combo_governo(53.5)), ("sem ajuste (S)", REF["S"]),
             ("estratégia A (2,7%)", REF["A"]), ("híbrido 5,5%", combos["m01231"])]
    linhas = []
    for g, lp, lfs, regra, th in grupos:
        for rot, c in casos:
            vals = []
            for lf in lfs:
                q0 = copy.deepcopy(p)
                q0["dinamica_lambda"], q0["indexacao_meta"] = regra, th
                tr, q, _ = simular_combo(c, q0, cfg, "P2", choques, lp, np.full(N, lf))
                vals.append(medir(tr, q))
            linhas.append({"grupo": g, "pacote": rot, **pd.DataFrame(vals).mean().round(3).to_dict()})
    d1 = pd.DataFrame(linhas)
    d1.to_csv(SAIDA / "diagnostico.csv", index=False)
    print(d1.to_string(index=False))

    # 2) escala
    linhas = []
    for total in (0.37, 1.0, 1.5, 2.0, 2.5, 3.0):
        c = combo_governo(total * PIB27 / 100)
        for g, lp, lfs, regra, th in (grupos[0], grupos[2]):
            vals = []
            for lf in lfs:
                q0 = copy.deepcopy(p)
                q0["dinamica_lambda"], q0["indexacao_meta"] = regra, th
                tr, q, _ = simular_combo(c, q0, cfg, "P2", choques, lp, np.full(N, lf))
                vals.append(medir(tr, q))
            linhas.append({"tamanho_pct_pib": total, "grupo": g, **pd.DataFrame(vals).mean().round(3).to_dict()})
    d2 = pd.DataFrame(linhas)
    d2.to_csv(SAIDA / "escala.csv", index=False)
    print(d2.to_string(index=False))


if __name__ == "__main__":
    main()
