"""Relatório da busca aleatória: o que distingue as combinações que funcionam com adesão baixa.

Uso: python -m src.busca_aleatoria_relatorio
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .busca_aleatoria import ITENS, SAIDA, fronteira, pontuar

ROT = {"renuncias": "renúncias regressivas", "beneficios": "benefícios setoriais", "subsidios": "subsídios",
       "verbas_teto": "verbas acima do teto", "prev_militar": "previdência militar", "emendas": "emendas",
       "custeio": "custeio", "pisos": "pisos saúde/educação", "investimento": "investimento público",
       "transferencias": "transferências aos pobres"}


def carregar():
    d = pd.concat([pd.read_csv(SAIDA / "fase1.csv"), pd.read_csv(SAIDA / "fase2.csv")])
    d3 = pd.read_csv(SAIDA / "fase3_finalistas.csv")
    return d, d3


def atributos(d: pd.DataFrame) -> pd.DataFrame:
    a = d[d["lambda"] == 0.3].set_index("id")
    cols = ["total_efetivo", "mult_medio"] + [f"x_{k}" for k in ITENS] + \
        [c for c in a.columns if c.startswith("c_") and c not in ("c_total",)]
    return a[cols]


def main():
    d, d3 = carregar()
    s = pontuar(d).join(atributos(d))
    s["social_ok"] = (s["x_transferencias"] < 0.05) & (s["x_investimento"] < 0.05)
    s["pobre"] = s["x_transferencias"] + s["x_pisos"]
    s.to_csv(SAIDA / "pontuacao_triagem.csv")
    out = {}
    out["n"] = int(len(s))
    out["dist_p03"] = s["p_03"].describe(percentiles=[.5, .9, .99]).round(3).to_dict()
    out["dist_p01"] = s["p_01"].describe(percentiles=[.5, .9, .99]).round(3).to_dict()
    # correlação de cada atributo com o sucesso a λ = 0,3 e com a atividade
    num = s.select_dtypes("number").drop(columns=["p_med", "p_03", "p_01", "dif16_03", "dif16_01"])
    out["corr_p03"] = num.corrwith(s["p_03"]).sort_values().round(2).to_dict()
    out["corr_dif"] = num.corrwith(s["dif16_03"]).sort_values().round(2).to_dict()
    # decis do tamanho do pacote
    s["faixa_total"] = pd.cut(s["total_efetivo"], [0, 1, 2, 3, 4, 5, 7])
    out["por_tamanho"] = s.groupby("faixa_total", observed=True)[["p_01", "p_03", "dif16_03"]].mean().round(3) \
        .reset_index().astype(str).to_dict("records")
    out["por_regra"] = s.groupby("c_regra")[["p_01", "p_03", "dif16_03"]].mean().round(3).to_dict()
    fr = fronteira(s, "p_03", "dif16_03")
    out["fronteira_triagem"] = s.loc[fr, ["p_01", "p_03", "dif16_03", "total_efetivo", "mult_medio", "c_regra",
                                          "c_reservas", "c_along", "c_rampa"] + [f"x_{k}" for k in ITENS]] \
        .round(2).reset_index().to_dict("records")
    # finalistas: média entre especificações
    f = d3.groupby(["id", "lambda"])[["p", "p_bil", "p_liq_bil", "dif_1-16", "p_recessao_1-16"]].mean().reset_index()
    piv = f.pivot(index="id", columns="lambda", values=["p_bil", "dif_1-16"])
    piv.columns = [f"{a}_{b}" for a, b in piv.columns]
    pe = d3[d3["lambda"] == 0.3].pivot(index="id", columns="especificacao", values="p_bil").add_prefix("pbil03_")
    att = d3[(d3["lambda"] == 0.3) & (d3["especificacao"] == "P2")].set_index("id")
    tab = piv.join(pe).join(att[["total_efetivo", "mult_medio", "c_regra", "c_reservas", "c_along", "c_inicio",
                                  "c_rampa", "c_i_alvo", "c_delta0"] + [f"x_{k}" for k in ITENS]])
    tab.round(3).to_csv(SAIDA / "finalistas_resumo.csv")
    out["finalistas"] = tab.sort_values("p_bil_0.3", ascending=False).round(3).reset_index().to_dict("records")
    (SAIDA / "resumo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n", "dist_p03", "dist_p01", "por_tamanho", "por_regra")}, ensure_ascii=False,
                     indent=1, default=str))


if __name__ == "__main__":
    main()
