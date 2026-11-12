"""Teste do pacote fiscal anunciado pelo governo em 11/11/2026 (PLP 299/2026), com as mesmas regras do paper.

Fontes do pacote: Agência Brasil (11/11/2026), Agência Senado (11/11/2026), O Povo (11/11/2026). Impacto informado:
R$ 50 a 60 bi em 2027 (governo) e R$ 43 a 54 bi no primário (tabela do relator). PIB de 2027 implícito na meta
(R$ 73,2 bi = 0,5% do PIB): R$ 14.640 bi.

Tradução para os itens do modelo (valores centrais, % do PIB, em vigor a partir de 2027T1, rampa de 1 trimestre):
- benefícios setoriais: corte de 10% nos gastos tributários (R$ 15 bi) + limite aos benefícios (R$ 4,5 bi)
  + restrição às compensações tributárias (R$ 12,8 a 18,3 bi; central 15,5)  → 35,0 bi = 0,239% do PIB
- custeio e investimento: contingenciamento/trava de 2% (R$ 12,8 a 18,3 bi; central 15,5), dividido 60/40
  entre custeio e investimento (hipótese: o contingenciamento atinge discricionárias)         → 0,064 e 0,042
- verbas acima do teto (supersalários): R$ 3 bi                                                → 0,020
- piso da saúde sem receitas do petróleo: sem valor informado, fora do pacote simulado.
Total central: 0,366% do PIB (R$ 53,5 bi). Variantes: 0,30% (R$ 43 bi) e 0,41% (R$ 60 bi), mesma composição.

Política monetária: regra de Taylor (o anúncio não trata de juros); sem venda de reservas nem alongamento; θ = 0.

Uso: python -m src.pacote_governo_2026
"""
import copy

import numpy as np
import pandas as pd
import yaml

from . import busca_aleatoria as B
from . import metricas, varredura
from . import recessivo as R
from .busca_contra_mercado import HOSTIL, SAIDA as SAIDA_CM
from .credibilidades_separadas import RAIZ, REF, simular_combo
from .lambda_dinamico_aplicacao import CENTRAL

SAIDA = RAIZ / "outputs" / "v2_2" / "pacote_governo_2026"
PIB27 = 14640.0
T_2027T4, T_2030T4 = 5, 17
N = 1000

_ITENS = {"beneficios": 35.0, "custeio": 0.6 * 15.5, "investimento": 0.4 * 15.5, "verbas_teto": 3.0}


def combo_governo(total_rs: float) -> dict:
    base = sum(_ITENS.values())
    pesos = [(_ITENS.get(k, 0.0) / base) for k in B.ITENS]
    return {"total": 100 * total_rs / PIB27, "pesos": pesos, "inicio": 2, "rampa": 1, "regra": "taylor",
            "i_alvo": 7.5, "T_corte": 6, "delta0": 1.0, "T_delta": 8, "reservas": 0.0, "T_res": 4,
            "along": False, "w_lft": 0.4, "T_along": 20}


def resumo(tr, trS, q, mask_lf=None):
    a = {k: v for k, v in tr.items()}
    ok_b = metricas.sucesso(a, q, bilateral=True)[0]
    ok_t = metricas.sucesso(a, q)[0]
    rs = lambda t: {k: v[None] if v.ndim > 1 else v[None] for k, v in t.items()}  # noqa: E731
    m = R.atividade(rs(tr), rs(trS), q)
    v = m["valida"][0]
    d = tr["d_gross"]
    return {"p_banda": float(ok_b.mean()), "p_teto": float(ok_t.mean()),
            "atividade_ate_2030": float(np.nanmean(np.where(v, m["dif_1-16"][0], np.nan))) if v.any() else np.nan,
            "divida_2030T4": float(np.nanmedian(d[:, T_2030T4])),
            "divida_t0": float(np.nanmedian(d[:, 0]))}


def rodar_grupo(nome, casos, p, cfg, espec, choques, lp, lf, regra, theta=0.0, salto=0.0):
    q0 = copy.deepcopy(p)
    q0["indexacao_meta"] = theta
    q0["dinamica_lambda"] = regra
    lf_ini = np.minimum(1.0, lf + salto)
    trS, _, _ = simular_combo(REF["S"], q0, cfg, espec, choques, lp, lf_ini)
    linhas = []
    for rotulo, c in casos:
        tr, q, _ = simular_combo(c, q0, cfg, espec, choques, lp, lf_ini)
        linhas.append({"grupo": nome, "especificacao": espec, "pacote": rotulo, **resumo(tr, trS, q)})
    return linhas


def lambda_star(casos, p, cfg, espec, choques):
    """λ_π = λ_fiscal fixos (diagonal), grade de 0 a 1 em 0,05; λ* = menor λ com P(sucesso) ≥ 80% e ≥ 50%."""
    grade = np.round(np.arange(0, 1.0001, 0.05), 2)
    lam = np.repeat(grade, N)
    ch = np.tile(choques, (len(grade), 1, 1))
    q0 = copy.deepcopy(p)
    q0["indexacao_meta"] = 0.0
    linhas = []
    for rotulo, c in casos:
        tr, q, _ = simular_combo(c, q0, cfg, espec, ch, lam, lam)
        for crit, bil in (("banda", True), ("teto", False)):
            ok = metricas.sucesso(tr, q, bilateral=bil)[0].reshape(len(grade), N).mean(axis=1)
            def primeiro(x):
                idx = np.where(ok >= x)[0]
                return float(grade[idx[0]]) if len(idx) else np.nan
            linhas.append({"especificacao": espec, "pacote": rotulo, "criterio": crit, "p_max": float(ok.max()),
                           "lambda_star_80": primeiro(0.8), "lambda_star_50": primeiro(0.5)})
    return linhas


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = R.modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml") if hasattr(R, "modelo") else None
    if p is None:
        from . import modelo
        p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    choques = varredura.sortear_choques(p, N, cfg["horizonte"], 42)
    import json
    combos = json.loads((SAIDA_CM / "combinacoes.json").read_text())
    gov = combo_governo(53.5)
    casos = [("governo (R$ 53,5 bi; 0,37% do PIB)", gov),
             ("governo, piso (R$ 43 bi)", combo_governo(43.0)),
             ("governo, teto (R$ 60 bi)", combo_governo(60.0)),
             ("estratégia A (2,7% do PIB)", REF["A"]),
             ("híbrido 5,5% (pacote do paper, sem θ)", combos["m01231"]),
             ("sem ajuste (S)", REF["S"])]

    # 1) λ fixo, diagonal: adesão mínima
    ls = []
    for e in ("P2", "P1", "P3_theta05"):
        ls += lambda_star(casos[:1] + casos[3:5], p, cfg, e, choques)
    pd.DataFrame(ls).to_csv(SAIDA / "lambda_star.csv", index=False)
    print(pd.DataFrame(ls).to_string(index=False))

    linhas = []
    rng = np.random.default_rng(2027)
    lp_baixa = rng.uniform(0.2, 0.5, N)
    lp_hostil = np.random.default_rng(2027).uniform(0.0, 0.3, N)
    for e in ("P2", "P1"):
        # 2) credibilidades baixas, regra central
        for lf in (0.2, 0.35, 0.5):
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("baixa, regra central", casos, p, cfg, e, choques, lp_baixa, np.full(N, lf), CENTRAL)]
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("baixa, regra central, salto +0,8", casos[:1], p, cfg, e, choques, lp_baixa,
                                   np.full(N, lf), CENTRAL, salto=0.8)]
        # 3) mercado hostil, com e sem reindexação
        for lf in (0.0, 0.15, 0.3):
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("hostil", casos, p, cfg, e, choques, lp_hostil, np.full(N, lf), HOSTIL)]
            linhas += [{**l, "lambda_fiscal": lf} for l in
                       rodar_grupo("hostil, θ = 0,32", [casos[0], casos[4]], p, cfg, e, choques, lp_hostil,
                                   np.full(N, lf), HOSTIL, theta=0.32)]
    df = pd.DataFrame(linhas)
    df.to_csv(SAIDA / "cenarios_detalhe.csv", index=False)
    agg = (df.groupby(["grupo", "especificacao", "pacote"], sort=False)
           [["p_banda", "p_teto", "atividade_ate_2030", "divida_t0", "divida_2030T4"]].mean().round(3).reset_index())
    agg.to_csv(SAIDA / "cenarios_resumo.csv", index=False)
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
