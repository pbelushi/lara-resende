"""Dívida bruta em 2030 do pacote resultante do paper (seção 7.7) contra as referências, com mercado hostil.

Pacote: híbrido de 5,5% do PIB com regra de Taylor (m01231 da busca contra o mercado), reindexação à meta com
θ = 0,32 (tarifas reguladas, planos de saúde e medicamentos). Referências: o mesmo pacote sem reindexação, a
trajetória sem ajuste (S) e a estratégia A com reservas. Mesmos choques (semente 42) e mesmos λ_π iniciais
(semente 2027, U(0; 0,3)) da busca; mediana das trajetórias, média entre λ_fiscal 0; 0,15 e 0,3.

Uso: python -m src.divida_pacote_resultante  (grava outputs/v2_2/busca_contra_mercado/divida_pacote_resultante.csv)
"""
import copy
import json

import numpy as np
import pandas as pd
import yaml

from . import modelo, varredura
from .busca_contra_mercado import HOSTIL, SAIDA
from .credibilidades_separadas import RAIZ, REF, simular_combo

T_2030T4 = 17  # trimestres depois de t0 = 2026T3


def main():
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    lp = np.random.default_rng(2027).uniform(0.0, 0.3, 1000)
    combos = json.loads((SAIDA / "combinacoes.json").read_text())
    casos = [("pacote resultante (híbrido 5,5%, θ = 0,32)", combos["m01231"], 0.32),
             ("híbrido 5,5% sem reindexação", combos["m01231"], 0.0),
             ("sem ajuste (S)", REF["S"], 0.0),
             ("estratégia A com reservas", REF["A_reservas"], 0.0)]
    linhas = []
    for nome, c, th in casos:
        for e in ("P2", "P1"):
            vals = []
            for lf in (0.0, 0.15, 0.3):
                q = copy.deepcopy(p)
                q["indexacao_meta"] = th
                q["dinamica_lambda"] = HOSTIL
                d = simular_combo(c, q, cfg, e, choques, lp, np.full(1000, lf))[0]["d_gross"]
                vals.append((np.nanmedian(d[:, 0]), np.nanmedian(d[:, T_2030T4])))
            v = np.mean(vals, axis=0)
            linhas.append({"caso": nome, "especificacao": e, "divida_t0": round(v[0], 1), "divida_2030T4": round(v[1], 1)})
    out = pd.DataFrame(linhas)
    out.to_csv(SAIDA / "divida_pacote_resultante.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
