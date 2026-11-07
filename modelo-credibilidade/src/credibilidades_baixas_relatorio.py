"""Resumo da busca com as duas credibilidades baixas (λ_fiscal travado em 0,2/0,35/0,5; λ_π ~ U(0,2; 0,5)),
comparada às rodadas anteriores (diagonal λ ≤ 0,3; λ_fiscal baixo com λ_π ~ U(0,5; 1,0)).

Uso: python -m src.credibilidades_baixas_relatorio [--tag ambas_0_2_a_0_5]
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from .busca_aleatoria import ITENS
from .credibilidades_separadas import SAIDA as BASE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="ambas_0_2_a_0_5")
    a = ap.parse_args()
    S = BASE / a.tag
    ex = json.loads((S / "execucao.json").read_text())
    LF = ex["lambda_fiscal"]
    ref = LF[len(LF) // 2]
    out = {"execucao": ex}

    # estratégias do paper na grade
    g = pd.read_csv(S / "estrategias_grade.csv")
    out["estrategias"] = g.pivot_table(index=["especificacao", "estrategia"], columns="lambda_pi",
                                       values="p_banda", aggfunc="mean").round(3).reset_index() \
        .astype(str).to_dict("records")

    # triagem
    d = pd.concat([pd.read_csv(S / "fase1.csv"), pd.read_csv(S / "fase2.csv")])
    piv = d.pivot_table(index="id", columns="lambda_fiscal", values=["p_bil", "p", "dif_1-16"])
    out["triagem"] = {
        "n": int(piv.shape[0]),
        "max_banda_por_lf": piv["p_bil"].max().round(3).to_dict(),
        "max_teto_por_lf": piv["p"].max().round(3).to_dict(),
        "n_banda_ge_50_ref": int((piv[("p_bil", ref)] >= 0.5).sum()),
        "n_banda_ge_40_ref": int((piv[("p_bil", ref)] >= 0.4).sum()),
        "n_teto_ge_80_ref": int((piv[("p", ref)] >= 0.8).sum()),
        "efeito_lf_no_melhor": piv["p_bil"].loc[piv[("p_bil", ref)].idxmax()].round(3).to_dict(),
    }
    # o que explica o sucesso e a atividade a λ_f de referência
    att = d[d["lambda_fiscal"] == ref].set_index("id")
    num = att[["total_efetivo", "mult_medio"] + [f"x_{k}" for k in ITENS] +
              [c for c in att.columns if c.startswith("c_") and att[c].dtype != object]].copy()
    out["corr_sucesso_banda"] = num.corrwith(att["p_bil"]).dropna().sort_values().round(2).to_dict()
    out["corr_atividade"] = num.corrwith(att["dif_1-16"]).dropna().sort_values().round(2).to_dict()
    out["por_regra"] = att.groupby("c_regra")[["p_bil", "p", "dif_1-16"]].mean().round(3).to_dict()

    # finalistas (N = 1000, três especificações)
    f = pd.read_csv(S / "fase3_finalistas.csv")
    t = f[f["lambda_fiscal"] == ref].pivot_table(index="id", columns="especificacao", values=["p_bil", "p", "dif_1-16"])
    t.columns = [f"{x}_{y}" for x, y in t.columns]
    at = f[(f["lambda_fiscal"] == ref) & (f["especificacao"] == "P2")].set_index("id")
    cols = ["total_efetivo", "mult_medio", "c_regra", "c_inicio", "c_rampa", "c_i_alvo", "c_delta0", "c_reservas",
            "c_along"] + [f"x_{k}" for k in ITENS]
    t = t.join(at[[c for c in cols if c in at.columns]])
    lfv = f[f["especificacao"] == "P2"].pivot_table(index="id", columns="lambda_fiscal", values="p_bil")
    lfv.columns = [f"p_bil_P2_lf{c}" for c in lfv.columns]
    t = t.join(lfv).sort_values("p_bil_P2", ascending=False)
    t.round(3).to_csv(S / "finalistas_resumo.csv")
    out["finalistas"] = t.round(3).reset_index().to_dict("records")
    (S / "resumo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(json.dumps(out["triagem"], indent=1, default=str))
    print(pd.DataFrame(out["estrategias"]).to_string(index=False))
    print(json.dumps(out["corr_sucesso_banda"], ensure_ascii=False))
    print(json.dumps(out["corr_atividade"], ensure_ascii=False))
    print(json.dumps(out["por_regra"], ensure_ascii=False))
    show = ["p_bil_P1", "p_bil_P2", "p_bil_P3", "p_P2", "dif_1-16_P1", "dif_1-16_P2", "dif_1-16_P3", "total_efetivo",
            "mult_medio", "c_regra", "c_inicio", "c_rampa", "c_i_alvo", "c_reservas"] + \
        [c for c in t.columns if c.startswith("p_bil_P2_lf")] + [f"x_{k}" for k in ITENS]
    print(t[[c for c in show if c in t.columns]].round(2).to_string())


if __name__ == "__main__":
    main()
