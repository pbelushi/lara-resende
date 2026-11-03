"""Checagem de consistência (seção 2 da v2.1) e portão de qualidade do ranking.

Para cada (r_long_neutro, ω): juros neutros, custo real efetivo da dívida em estado estacionário,
primário estabilizador (dívida bruta e líquida) e folga do primário final de cada cenário
(trajetória determinística, P1, λ = 1).
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from . import metricas, modelo, varredura

GRADE_RLONG = (4.5, 5.5, 6.5)
GRADE_OMEGA = (0.0, 0.5, 1.0)
AVISO_PORTAO = ("Com esta calibração, o pacote fiscal é insuficiente mesmo com adesão total; o ranking compara "
                "graus de fracasso e não deve ser lido como robustez relativa.")


def s_estabilizador_ss(r_ef: float, g: float, d: float) -> float:
    """Primário (% PIB) que estabiliza a dívida em estado estacionário: (r − g)/(1 + g) · d."""
    return (r_ef - g) / (100 + g) * d


def _p1(p: dict, **ajustes) -> dict:
    return modelo.preparar({**copy.deepcopy(p), "especificacao": "P1", **ajustes})


def divida_estabiliza(p: dict, cfg: dict, chave: str = "A") -> bool:
    """O cenário estabiliza a dívida na trajetória determinística com P1 e λ = 1?"""
    c = varredura.preparar_cenarios(p, cfg, [chave])[chave]
    tr = modelo.simular(p, c["cen"], 1.0, plano=c["plano"], guardar=("d_gross", "pi", "R"))
    _, det = metricas.sucesso(tr, p)
    return bool(metricas.divida_ok(det)[0])


def linha(p_base: dict, cfg: dict, r_long_neutro: float, omega: float) -> dict:
    p = _p1(p_base, r_long_neutro=r_long_neutro, omega=omega)
    ini = p["ini"]
    g = p.get("g_potencial") or ini["g_potencial"]
    out = {"r_long_neutro": r_long_neutro, "omega": omega, "r_neutro_base": p["r_neutro_base"],
           "tp_lp": p["tp_lp"]}
    finais = {}
    for chave, c in varredura.preparar_cenarios(p, cfg).items():
        tr = modelo.simular(p, c["cen"], 1.0, plano=c["plano"])
        n = p["criterios"]["janela_final"]
        finais[chave] = float(np.nanmean(tr["s"][0, -n:]))
        if chave == "A":
            w = {k: tr[f"w_{k}"][0, -1] for k in ("lft", "pre", "ipca", "fx")}
            _, det = metricas.sucesso(tr, p)
            out["A_estabiliza"] = bool(metricas.divida_ok(det)[0])
    r_ef = w["lft"] * p["r_neutro_base"] + (w["pre"] + w["ipca"] + w["fx"]) * p["r_long_neutro"]
    out["r_efetivo_ss"] = r_ef
    out["w_lft_final"] = w["lft"]
    out["s_estab_bruta"] = s_estabilizador_ss(r_ef, g, ini["d_gross0"])
    out["s_estab_liquida"] = s_estabilizador_ss(r_ef, g, ini["d_net0"])
    for chave, s in finais.items():
        out[f"s_final_{chave}"] = s
        out[f"folga_{chave}"] = s - out["s_estab_bruta"]
    return out


def tabela(p: dict, cfg: dict) -> pd.DataFrame:
    return pd.DataFrame([linha(p, cfg, r, w) for r in GRADE_RLONG for w in GRADE_OMEGA])


def pacote_necessario(p: dict, cfg: dict, maximo: float = 10.0, tol: float = 0.02) -> float:
    """Pacote ADICIONAL (% PIB, receita com a rampa da primeira medida) para A estabilizar com λ = 1."""
    q = _p1(p)
    modelo_medida = cfg["pacote_fiscal"][0] if cfg["pacote_fiscal"] else {"inicio": 2, "rampa": 8}

    def ok(x: float) -> bool:
        c = copy.deepcopy(cfg)
        c["pacote_fiscal"] = c["pacote_fiscal"] + [{"nome": "Adicional", "tipo": "receita",
                                                     "inicio": modelo_medida["inicio"],
                                                     "rampa": modelo_medida["rampa"], "impacto_final": x}]
        return divida_estabiliza(q, c)

    if ok(0.0):
        return 0.0
    if not ok(maximo):
        return np.nan
    lo, hi = 0.0, maximo
    while hi - lo > tol:
        meio = (lo + hi) / 2
        lo, hi = (lo, meio) if ok(meio) else (meio, hi)
    return hi


def portao(p: dict, cfg: dict) -> dict:
    """Portão de qualidade na calibração base: aviso e pacote adicional necessário, se A não estabilizar."""
    estabiliza = divida_estabiliza(_p1(p), cfg)
    return {"A_estabiliza": estabiliza,
            "aviso": None if estabiliza else AVISO_PORTAO,
            "pacote_adicional": 0.0 if estabiliza else pacote_necessario(p, cfg)}
