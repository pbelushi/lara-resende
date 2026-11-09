"""Validação conjunta do canal de fundamentos nos três episódios (2015–16, 2016–19, 2020–22; P2).

Mesma medida de erro da validação 2D (inflação 12 meses e NTN-B 10 anos; credibilidades_separadas.validar_2d).
Para cada conjunto de coeficientes β, duas medidas:

- erro livre: soma, entre os episódios, do menor erro com λ_π e λ_fiscal iniciais escolhidos por episódio;
- erro comum: menor soma de erros com o MESMO par (λ_π, λ_fiscal) inicial nos três episódios.

O teste forte do canal é o segundo: se os fundamentos explicam as variações de credibilidade entre os
episódios, um único ponto de partida deve ajustar os três quase tão bem quanto um λ por episódio.

Grade: β_s,f ∈ {0; 0,06; 0,12; 0,20; 0,35} (logit por p.p. de primário − estabilizador), β_d,f ∈ {0; −0,05;
−0,13; −0,25} (por p.p. de dívida), e o canal fiscal → λ_π (Montes, Oliveira e Nicolay, 2019; não sustentado no
Focus) com β_s,π ∈ {0; 0,12}. Central (estimado no Focus): β_s,f = 0,12, β_d,f = −0,13, β_π = 0.

Uso: python -m src.lambda_fundamentos_validacao
"""
from __future__ import annotations

import copy
import itertools
import json

import numpy as np
import pandas as pd

from . import modelo, validacao
from .credibilidades_separadas import EPIS, RAIZ
from .lambda_fundamentos_estimacao import SAIDA

G = validacao.GRADE_LAMBDA
CENTRAL = {"b_s_f": 0.12, "b_d_f": -0.13, "b_s_pi": 0.0, "b_d_pi": 0.0}


def preparar_episodios(p: dict, espec: str = "P2") -> list[dict]:
    painel = pd.read_csv(validacao.PROC / "trimestral.csv", index_col=0, parse_dates=True)
    arq = validacao.RAW / "focus_anuais_historico.csv"
    anuais = pd.read_csv(arq, parse_dates=["Data"]) if arq.exists() else None
    eps = []
    for nome, (ini, fim) in EPIS.items():
        ini, fim = pd.Timestamp(ini), pd.Timestamp(fim)
        jan = painel.loc[ini:fim]
        T = len(jan) - 1
        q = copy.deepcopy(p)
        q["especificacao"] = espec
        q["ini"] = validacao._ini_historico(painel, ini, p["ini"])
        q.pop("g_potencial", None)
        q = modelo.preparar(q)
        i_h, s_h = jan["meta_selic"].values, jan["s_spc"].values
        z = np.zeros(T + 1)
        cen = {"chave": "hist", "nome": "h", "cor": "#333", "regra": "exogena", "delta": z, "i_exog": i_h,
               "medidas_receita": z, "medidas_despesa": z, "venda_reservas": z, "capex_ppp": z, "T": T}
        s_est = modelo.s_estabilizador(jan["selic"].iloc[-4:].mean(), jan["gamma"].iloc[-1], jan["dbgg"].iloc[-1])
        F = q["p1"] * (jan["dbgg"].iloc[-1] - q["d_ref"]) + modelo.p2_efetivo(q) * (s_est - s_h[-1])
        plano = {"F": float(F), "i": np.concatenate([i_h, np.full(8, i_h[-1])]),
                 "s_mat": validacao.plano_s_focus(anuais, jan.index, s_h, int(q["H_vp"]))}
        eps.append({"nome": nome, "q": q, "cen": cen, "plano": plano,
                    "override": {"i": i_h, "s": s_h, "de": jan["de"].values},
                    "dados": {"pi": jan["ipca12"].values, "r_long": jan["ntnb10"].values}})
    return eps


def grades_de_erro(eps: list[dict], fund: dict | None) -> list[np.ndarray]:
    LP, LF = np.meshgrid(G, G, indexing="ij")
    out = []
    for e in eps:
        q = {**e["q"], "fundamentos_lambda": fund}
        tr = modelo.simular(q, e["cen"], LP.ravel(), LF.ravel(), plano=e["plano"], override=e["override"],
                            guardar=("pi", "r_long"))
        out.append(validacao._erro(tr, e["dados"]).reshape(LP.shape))
    return out


def resumo(erros: list[np.ndarray], eps: list[dict]) -> dict:
    r = {"erro_livre": float(sum(np.nanmin(x) for x in erros))}
    soma = sum(erros)
    k = np.unravel_index(np.nanargmin(soma), soma.shape)
    r.update({"erro_comum": float(soma[k]), "lambda_pi_comum": float(G[k[0]]), "lambda_f_comum": float(G[k[1]])})
    for e, x in zip(eps, erros):
        j = np.unravel_index(np.nanargmin(x), x.shape)
        tag = e["nome"][:7]
        r[f"{tag}_lambda_pi"], r[f"{tag}_lambda_f"], r[f"{tag}_erro"] = float(G[j[0]]), float(G[j[1]]), float(x[j])
    return r


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    eps = preparar_episodios(p)
    linhas = []
    for bs, bd, bpi in itertools.product([0, 0.06, 0.12, 0.20, 0.35], [0, -0.05, -0.13, -0.25], [0, 0.12]):
        fund = {"b_s_f": bs, "b_d_f": bd, "b_s_pi": bpi, "b_d_pi": 0.0}
        linhas.append({"b_s_f": bs, "b_d_f": bd, "b_s_pi": bpi, **resumo(grades_de_erro(eps, fund), eps)})
    d = pd.DataFrame(linhas)
    d.to_csv(SAIDA / "validacao_conjunta.csv", index=False)
    # trajetórias de λ efetivo no ajuste central (λ iniciais do erro comum)
    c = d[(d.b_s_f == CENTRAL["b_s_f"]) & (d.b_d_f == CENTRAL["b_d_f"]) & (d.b_s_pi == 0)].iloc[0]
    traj = []
    for e in eps:
        q = {**e["q"], "fundamentos_lambda": CENTRAL}
        tr = modelo.simular(q, e["cen"], [c.lambda_pi_comum], [c.lambda_f_comum], plano=e["plano"],
                            override=e["override"], guardar=("pi", "r_long"))
        traj.append({"episodio": e["nome"], "lam_f_ef": np.round(tr["lam_f_ef"][0], 3).tolist(),
                     "lam_pi_ef": np.round(tr["lam_pi_ef"][0], 3).tolist()})
    (SAIDA / "trajetorias_validacao.json").write_text(json.dumps(traj, ensure_ascii=False, indent=1))
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(d.sort_values("erro_comum").head(12).round(3).to_string(index=False))
    print(d[(d.b_s_f == 0) & (d.b_d_f == 0) & (d.b_s_pi == 0)].round(3).to_string(index=False))
    print(c.round(3).to_string())
    for t in traj:
        print(t["episodio"], t["lam_f_ef"][::2])


if __name__ == "__main__":
    main()
