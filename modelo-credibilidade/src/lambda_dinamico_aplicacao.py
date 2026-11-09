"""λ endógeno aplicado às finalistas da busca com as duas credibilidades baixas (ambas_0_2_a_0_5).

A cada 4 trimestres, λ_π e λ_fiscal são revistos pelo resultado do ano (modelo.atualizar_lambda):
inflação dentro do intervalo de tolerância eleva λ_π, fora dele reduz; primário acima do anunciado eleva
λ_fiscal, abaixo reduz. Ponto de partida igual ao da busca: λ_π ~ U(0,2; 0,5) por trajetória (seed 2027),
λ_fiscal ∈ {0,2; 0,35; 0,5}; choques com seed 42, N = 1.000; P1, P2 e P3.

Regras (coeficientes por p.p.; ver lambda_dinamico_estimacao.py e o relatório):
- central: λ_π estimado no painel trimestral do Focus (índice de de Mendonça, HAC): +0,028 por p.p. de folga
  dentro do intervalo, −0,071 por p.p. fora dele; λ_fiscal calibrado na transição 2019–20 do λ efetivo
  (−0,75 com primário 7,7 p.p. abaixo do plano ≈ 0,10 por p.p.), simétrico;
- anual: λ_π com as estimativas do painel anual (+0,035 / −0,113);
- fiscal forte: λ_fiscal com 0,30 por p.p. nos dois sentidos (ordem de grandeza da recuperação de 2016–19);
- cruzado: central + o descumprimento fiscal também reduz λ_π (−0,05 por p.p.; Montes, Oliveira e Nicolay,
  2019 — não confirmado nos dados do Focus);
- dobro e metade: central com todos os coeficientes ×2 e ×0,5;
- simétrico: λ_π sobe na mesma taxa em que cai (0,071 por p.p.), para separar o efeito da assimetria.

Uso: python -m src.lambda_dinamico_aplicacao
"""
from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from . import metricas, modelo, varredura
from . import recessivo as R
from .busca_aleatoria import ITENS
from .credibilidades_separadas import RAIZ, REF, SAIDA as BASE, simular_combo
from .lambda_dinamico_estimacao import SAIDA

ORIGEM = BASE / "ambas_0_2_a_0_5"
LF = [0.2, 0.35, 0.5]
CENTRAL = {"b_pi_pos": 0.028, "b_pi_neg": 0.071, "b_f_pos": 0.10, "b_f_neg": 0.10, "tol": 1.5}
REGRAS = {
    "estatico": None,
    "central": CENTRAL,
    "anual": {**CENTRAL, "b_pi_pos": 0.035, "b_pi_neg": 0.113},
    "fiscal_forte": {**CENTRAL, "b_f_pos": 0.30, "b_f_neg": 0.30},
    "cruzado": {**CENTRAL, "b_cruzado": 0.05},
    "dobro": {k: (v * 2 if k.startswith("b_") else v) for k, v in CENTRAL.items()},
    "metade": {k: (v * 0.5 if k.startswith("b_") else v) for k, v in CENTRAL.items()},
    "simetrico": {**CENTRAL, "b_pi_pos": 0.071},
}
MARCOS = {"ano1": 4, "ano2": 8, "ano4": 16, "ano10": 40}


def familia(row) -> str:
    if str(row["id"]).startswith("ref_"):
        return "paper"
    return "choque" if row["mult_medio"] >= 0.55 else "gradual"


def avaliar(cid, c, p_base, cfg, espec, choques, lp_draw, regra):
    p = copy.deepcopy(p_base)
    p["dinamica_lambda"] = REGRAS[regra]
    N = choques.shape[0]
    lam_pi = np.tile(lp_draw, len(LF))
    lam_f = np.repeat(LF, N)
    ch = np.tile(choques, (len(LF), 1, 1))
    tr, q, aloc = simular_combo(c, p, cfg, espec, ch, lam_pi, lam_f)
    trS = simular_combo(REF["S"], p, cfg, espec, ch, lam_pi, lam_f)[0]
    rs = lambda t: {k: (v.reshape(len(LF), N, -1) if v.ndim > 1 else v.reshape(len(LF), N))  # noqa: E731
                    for k, v in t.items()}
    a, s = rs(tr), rs(trS)
    m = R.atividade(a, s, q)
    mult = sum(R.CONF["itens"][k]["m"] * v for k, v in aloc.items()) / max(sum(aloc.values()), 1e-9)
    out = []
    for i, lf in enumerate(LF):
        sub = {k: v[i] for k, v in a.items()}
        ok = {suf: metricas.sucesso(sub, q, bilateral=b, divida=d)[0] for suf, (b, d) in metricas.METRICAS.items()}
        v = m["valida"][i]
        lin = {"id": cid, "regra": regra, "especificacao": espec.replace("_theta05", ""), "lambda_fiscal_0": lf,
               **{f"p{suf}": float(o.mean()) for suf, o in ok.items()},
               "dif_1-16": float(np.nanmean(np.where(v, m["dif_1-16"][i], np.nan))) if v.any() else np.nan,
               "p_recessao_1-16": float(m["recessao_1-16"][i].mean()),
               "total_efetivo": float(sum(aloc.values())), "mult_medio": float(mult)}
        if "lam_pi" in sub:
            for nome, t in MARCOS.items():
                lin[f"lam_pi_{nome}"] = float(np.nanmean(sub["lam_pi"][:, t]))
                lin[f"lam_f_{nome}"] = float(np.nanmean(sub["lam_f"][:, t]))
                lin[f"lam_pi_S_{nome}"] = float(np.nanmean(s["lam_pi"][i][:, t]))
            # quem acaba com a meta crível: fração das trajetórias com λ_π ≥ 0,5 no fim do horizonte
            lin["frac_lam_pi_ge_05_ano10"] = float(np.mean(sub["lam_pi"][:, -1] >= 0.5))
            # sucesso entre as trajetórias que começaram com λ_π abaixo e acima da mediana do sorteio
            med = np.median(lp_draw)
            lin["p_bil_lp0_baixo"] = float(ok["_bil"][lp_draw < med].mean())
            lin["p_bil_lp0_alto"] = float(ok["_bil"][lp_draw >= med].mean())
        out.append(lin)
    return out


def _lote(tarefas, p, cfg, choques, lp_draw):
    if "R" not in R.GUARDAR:
        R.GUARDAR = R.GUARDAR + ("R",)
    res = []
    for cid, c, espec, regra in tarefas:
        res += avaliar(cid, c, p, cfg, espec, choques, lp_draw, regra)
    return res


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--regras", default=",".join(REGRAS))
    regras = ap.parse_args().regras.split(",")
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    lp_draw = np.random.default_rng(2027).uniform(0.2, 0.5, 1000)
    combos = json.loads((ORIGEM / "combinacoes.json").read_text())
    fin = pd.read_csv(ORIGEM / "fase3_finalistas.csv")["id"].unique()
    tarefas = [(cid, combos[cid], e, r) for cid in fin for e in ("P1", "P2", "P3_theta05") for r in regras]
    res = Parallel(n_jobs=2)(delayed(_lote)(tarefas[i:i + 6], p, cfg, choques, lp_draw)
                             for i in range(0, len(tarefas), 6))
    d = pd.DataFrame([x for r in res for x in r])
    d["familia"] = d.apply(familia, axis=1)
    arq = SAIDA / "finalistas_lambda_dinamico.csv"
    if arq.exists() and set(regras) != set(REGRAS):   # rodada parcial: substitui só as regras rodadas
        velho = pd.read_csv(arq)
        d = pd.concat([velho[~velho["regra"].isin(regras)], d])
    d.to_csv(arq, index=False)
    print(d.groupby(["especificacao", "familia", "regra"])[["p_bil", "p", "dif_1-16", "lam_pi_ano4", "lam_pi_ano10"]]
          .mean().round(3).to_string())


if __name__ == "__main__":
    main()
