"""Teste do PLP 299/2026 na versão aprovada pelo Senado (Parecer nº 221/2026-PLEN/SF, substitutivo, 12/11/2026).

O que mudou em relação à proposta original (src/pacote_governo_2026.py), no que afeta o primário de 2027:
- Impacto informado pelo Executivo no parecer: R$ 45,1 a 56,1 bi (antes R$ 50 a 60 bi / R$ 43 a 54 bi), soma de
  contingenciamento com foco no centro da meta (R$ 12,8 a 18,3 bi), redução das compensações tributárias
  (R$ 12,8 a 18,3 bi), corte de 10% no gasto tributário (R$ 15 bi) e limite do benefício ao DGT 2026 (R$ 4,5 bi).
- Supersalários saem do impacto: o art. 10 remete a regulamentação do art. 37, § 11, da CF a projeto a ser apreciado
  em 120 dias, e a economia dos demais Poderes fica com eles (§ 3º). Sem os R$ 3 bi.
- A contenção é temporária: o limite de 2,0% vale só no exercício em que houver contingenciamento e a redução não
  entra na base dos anos seguintes (art. 6º-E, § 1º); o excedente sobre o piso da meta pode virar crédito para
  investimentos fora do limite no ano seguinte, até o montante contido (art. 12).
- Outras mudanças sem valor informado e fora da simulação: Lei Kandir (LC 176) limitada a R$ 1 bi/ano em 2027-2030 com
  devolução até 2037 (diferimento); PROEX-equalização limitado a R$ 1 bi/ano; art. 8º-C da Lei 9.796 limitado a
  R$ 3 bi/ano; piso da saúde sem a receita do imposto de exportação de petróleo até 2030; exceção ao FCDF; restos a
  pagar plurianuais só canceláveis após 2027; dedução de até R$ 10,5 bi da meta de 2026 (subvenção ao diesel).

Tradução (valores centrais, % do PIB de 2027 = R$ 14.640 bi, início 2027T1, rampa de 1 trimestre, regra de Taylor):
- benefícios setoriais: 15 + 4,5 + 15,55 = 35,05 bi → 0,239%
- custeio e investimento: 15,55 bi divididos 60/40 → 0,064% e 0,042%
Total central R$ 50,6 bi = 0,346% do PIB; piso R$ 45,1 bi; teto R$ 56,1 bi (mesma composição).
Variante "contenção devolvida": a parcela de custeio e investimento vale só em 2027 e zera a partir de 2028T1
(arts. 6º-E e 12); fica o pedaço tributário, R$ 35 bi = 0,239% do PIB.

Uso: python -m src.pacote_senado_2026
"""
import copy
import json

import numpy as np
import pandas as pd
import yaml

from . import busca_aleatoria as B
from . import modelo, varredura
from . import recessivo as R
from .busca_contra_mercado import HOSTIL, SAIDA as SAIDA_CM
from .credibilidades_separadas import RAIZ, REF, simular_combo
from .lambda_dinamico_aplicacao import CENTRAL
from .pacote_governo_2026 import PIB27, combo_governo, lambda_star, rodar_grupo
from .pacote_governo_2026_diagnostico import medir

SAIDA = RAIZ / "outputs" / "v2_2" / "pacote_senado_2026"
N = 1000
T_2028T1 = 6

_ITENS = {"beneficios": 35.05, "custeio": 0.6 * 15.55, "investimento": 0.4 * 15.55}
_TEMPORARIOS = ("custeio", "investimento")

_pacote_de_original = B.pacote_de


def _pacote_de(c, T):
    pac, aloc = _pacote_de_original(c, T)
    if c.get("fim_contencao") is not None:
        for it in pac:
            if it["chave"] in _TEMPORARIOS:
                tr = it["trilha"].copy()
                tr[c["fim_contencao"]:] = 0.0
                it["trilha"] = tr
    return pac, aloc


B.pacote_de = _pacote_de


def combo_senado(total_rs: float, temporario: bool = False) -> dict:
    base = sum(_ITENS.values())
    c = combo_governo(total_rs)
    c["pesos"] = [(_ITENS.get(k, 0.0) / base) for k in B.ITENS]
    c["fim_contencao"] = T_2028T1 if temporario else None
    return c


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    for k in ("R", "s"):
        if k not in R.GUARDAR:
            R.GUARDAR = R.GUARDAR + (k,)
    choques = varredura.sortear_choques(p, N, cfg["horizonte"], 42)
    combos = json.loads((SAIDA_CM / "combinacoes.json").read_text())

    sen = combo_senado(50.6)
    temp = combo_senado(50.6, temporario=True)
    casos = [("aprovado (R$ 50,6 bi; 0,35% do PIB)", sen),
             ("aprovado, piso (R$ 45,1 bi)", combo_senado(45.1)),
             ("aprovado, teto (R$ 56,1 bi)", combo_senado(56.1)),
             ("aprovado, contenção devolvida em 2028", temp),
             ("proposta original (R$ 53,5 bi)", combo_governo(53.5)),
             ("sem ajuste (S)", REF["S"])]

    # 1) λ fixo, diagonal: adesão mínima
    ls = []
    for e in ("P2", "P1", "P3_theta05"):
        ls += lambda_star([casos[0], casos[3]], p, cfg, e, choques)
    d0 = pd.DataFrame(ls)
    d0.to_csv(SAIDA / "lambda_star.csv", index=False)
    print(d0.to_string(index=False))

    # 2) cenários: credibilidades baixas (regra central), mercado hostil, hostil com θ = 0,32
    lp_baixa = np.random.default_rng(2027).uniform(0.2, 0.5, N)
    lp_hostil = np.random.default_rng(2027).uniform(0.0, 0.3, N)
    linhas = []
    for e in ("P2", "P1"):
        for lf in (0.2, 0.35, 0.5):
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("baixa, regra central", casos, p, cfg, e, choques, lp_baixa, np.full(N, lf), CENTRAL)]
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("baixa, regra central, salto +0,8", casos[:1], p, cfg, e, choques, lp_baixa,
                                   np.full(N, lf), CENTRAL, salto=0.8)]
        for lf in (0.0, 0.15, 0.3):
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("hostil", casos, p, cfg, e, choques, lp_hostil, np.full(N, lf), HOSTIL)]
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("hostil, θ = 0,32", [casos[0], casos[3]], p, cfg, e, choques, lp_hostil,
                                   np.full(N, lf), HOSTIL, theta=0.32)]
    df = pd.DataFrame(linhas)
    df.to_csv(SAIDA / "cenarios_detalhe.csv", index=False)
    agg = (df.groupby(["grupo", "especificacao", "pacote"], sort=False)
           [["p_banda", "p_teto", "atividade_ate_2030", "divida_t0", "divida_2030T4"]].mean().round(3).reset_index())
    agg.to_csv(SAIDA / "cenarios_resumo.csv", index=False)
    print(agg.to_string(index=False))

    # 3) diagnóstico (P2): critério que falha, primário 2027/2030, dívida 2030
    grupos = [("baixa, regra central", lp_baixa, (0.2, 0.35, 0.5), CENTRAL, 0.0),
              ("hostil", lp_hostil, (0.0, 0.15, 0.3), HOSTIL, 0.0),
              ("hostil, θ = 0,32", lp_hostil, (0.0, 0.15, 0.3), HOSTIL, 0.32)]
    linhas = []
    for g, lp, lfs, regra, th in grupos:
        for rot, c in (casos[0], casos[3], casos[4]):
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

    # 4) escala com a composição aprovada
    linhas = []
    for total in (0.35, 1.0, 1.5, 2.0, 2.5, 3.0):
        c = combo_senado(total * PIB27 / 100)
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
