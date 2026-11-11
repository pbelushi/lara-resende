"""Sucesso por credibilidade inicial e por instrumento (figura 9.1 do paper).

Para cada λ inicial (λ_π = λ_fiscal = λ0, de 0 a 1), simula com a regra central de λ endógeno (P2, N = 1.000,
mesmos choques da busca, semente 42) três pacotes: a estratégia A com reservas (ortodoxa), o híbrido de 5,5% do
PIB sem reindexação e o mesmo híbrido com reindexação à meta (θ = 0,32: tarifas reguladas, planos de saúde e
medicamentos). Sucesso pelo critério do intervalo (dívida bruta, inflação entre 1,5% e 4,5%).

Uso: python -m src.mapa_lambda_instrumentos  (grava outputs/v2_2/busca_contra_mercado/mapa_lambda_instrumentos.csv)
"""
import copy
import json

import numpy as np
import pandas as pd
import yaml

from . import metricas, modelo, varredura
from .busca_contra_mercado import SAIDA
from .credibilidades_separadas import RAIZ, REF, simular_combo
from .lambda_dinamico_aplicacao import CENTRAL

LAMBDAS = [round(x, 2) for x in np.arange(0, 1.01, 0.1)]


def main():
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    combos = json.loads((SAIDA / "combinacoes.json").read_text())
    pacotes = [("Estratégia A com reservas (ortodoxa)", REF["A_reservas"], 0.0),
               ("Híbrido de 5,5% do PIB, sem reindexação", combos["m01231"], 0.0),
               ("Híbrido de 5,5% do PIB, com reindexação (θ = 0,32)", combos["m01231"], 0.32)]
    linhas = []
    for nome, c, th in pacotes:
        for l0 in LAMBDAS:
            q = copy.deepcopy(p)
            q["indexacao_meta"] = th
            q["dinamica_lambda"] = CENTRAL
            tr, qq, _ = simular_combo(c, q, cfg, "P2", choques, np.full(1000, l0), np.full(1000, l0))
            ok = metricas.sucesso(tr, qq, bilateral=True, divida="bruta")[0]
            linhas.append({"pacote": nome, "theta": th, "lambda0": l0, "p_sucesso": round(float(ok.mean()) * 100, 1)})
            print(linhas[-1])
    pd.DataFrame(linhas).to_csv(SAIDA / "mapa_lambda_instrumentos.csv", index=False)


if __name__ == "__main__":
    main()
