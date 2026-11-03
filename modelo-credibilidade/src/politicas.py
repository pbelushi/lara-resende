"""Regras de Selic, cronograma de venda de reservas e pacote fiscal de cada cenário."""
from __future__ import annotations

import numpy as np


def trajetoria_exogena(i0: float, i_alvo: float, T_corte: int, T: int) -> np.ndarray:
    """Selic descendo linearmente de i0 até i_alvo no trimestre T_corte; índice 0 = valor inicial."""
    t = np.arange(T + 1)
    return np.where(t < T_corte, i0 + (i_alvo - i0) * t / T_corte, i_alvo)


def rampa(inicio: int, duracao: int, impacto: float, T: int) -> np.ndarray:
    """Impacto que cresce linearmente a partir de `inicio` até `impacto` em `duracao` trimestres."""
    t = np.arange(T + 1)
    frac = np.clip((t - inicio + 1) / max(duracao, 1), 0, 1)
    return impacto * frac


def capex_ppp(cfg: dict, T: int) -> np.ndarray:
    t = np.arange(T + 1)
    sobe = rampa(cfg["inicio"], cfg["subida"], cfg["pico"], T)
    inicio_queda = cfg["inicio"] + cfg["subida"] + cfg["plato"]
    desce = rampa(inicio_queda, cfg["descida"], cfg["pico"], T)
    return np.where(t >= 1, sobe - desce, 0.0)


def medidas_fiscais(pacote: list[dict], T: int) -> tuple[np.ndarray, np.ndarray]:
    """Soma das medidas do pacote por tipo: (receita adicional, despesa reduzida), em % do PIB."""
    rec = np.zeros(T + 1)
    desp = np.zeros(T + 1)
    for m in pacote:
        trilha = m["trilha"] if "trilha" in m else rampa(m["inicio"], m["rampa"], m["impacto_final"], T)
        if m["tipo"] == "receita":
            rec += trilha
        else:
            desp += trilha
    return rec, desp


def itens_pacote(pacote: list[dict], T: int) -> list[dict]:
    """Trilha de cada medida (% PIB em vigor), canal de demanda e multiplicador (None = a3 da calibração)."""
    return [{"nome": m["nome"], "tipo": m["tipo"], "canal": m.get("canal"), "multiplicador": m.get("multiplicador"),
             "trilha": m["trilha"] if "trilha" in m else rampa(m["inicio"], m["rampa"], m["impacto_final"], T)}
            for m in pacote]


def cronograma_reservas(vendas: list[float], T: int) -> np.ndarray:
    v = np.zeros(T + 1)
    for k, x in enumerate(vendas, start=1):
        if k <= T:
            v[k] = x
    return v


def trajetoria_delta(delta0: float, T_corte: int | None, T_delta: int | None, T: int) -> np.ndarray:
    """Tolerância de C: δ0 até o fim do corte, depois cai linearmente a zero em T_delta trimestres.

    Sem T_delta (configuração da v1), δ fica constante.
    """
    t = np.arange(T + 1)
    if T_delta is None or T_corte is None:
        return np.full(T + 1, float(delta0))
    return np.where(t <= T_corte, delta0, delta0 * np.maximum(0, 1 - (t - T_corte) / T_delta))


def montar_cenario(chave: str, cfg: dict, i0: float, T: int | None = None, ajustes: dict | None = None) -> dict:
    """Trilhas exógenas de um cenário a partir de cenarios.yaml; `ajustes` sobrescreve chaves do cenário."""
    T = T or cfg["horizonte"]
    c = {**cfg["cenarios"][chave], **(ajustes or {})}
    regra = c["politica_monetaria"]
    if regra == "taylor":
        i_exog = np.full(T + 1, np.nan)
    else:
        i_exog = trajetoria_exogena(i0, c["i_alvo"], c["T_corte"], T)
        if c.get("piso_final") is not None and c.get("T_delta") is not None:
            # depois de T_corte + T_δ o piso da trajetória deixa de valer: com δ = 0, i = max(piso_final, Taylor)
            fim = c["T_corte"] + c["T_delta"]
            i_exog = np.where(np.arange(T + 1) > fim, float(c["piso_final"]), i_exog)
    if c.get("pacote_fiscal"):
        med_rec, med_desp = medidas_fiscais(cfg["pacote_fiscal"], T)
        itens = itens_pacote(cfg["pacote_fiscal"], T)
    else:
        med_rec, med_desp = np.zeros(T + 1), np.zeros(T + 1)
        itens = []
    # parada súbita (choque_t em trimestres): depreciação, prêmio com decaimento geométrico e defesa com reservas
    choque_de, choque_prem, defesa = np.zeros(T + 1), np.zeros(T + 1), np.zeros(T + 1)
    if c.get("choque_t"):
        t0 = int(c["choque_t"])
        k = np.arange(T + 1) - t0
        choque_de[t0] = c.get("choque_de", 30.0)
        choque_prem = np.where(k >= 0, c.get("choque_prem", 3.0) * c.get("choque_decai", 0.8) ** np.maximum(k, 0), 0.0)
        d = c.get("defesa_reservas", 50.0)
        defesa[t0:t0 + 2] = d / 2  # metade no trimestre do choque, metade no seguinte
    return {
        "choque_de": choque_de, "choque_prem": choque_prem, "defesa": defesa,
        "chave": chave,
        "nome": c["nome"],
        "cor": c["cor"],
        "regra": regra,
        "delta": trajetoria_delta(c.get("delta0", c.get("delta", 0.0)), c.get("T_corte"), c.get("T_delta"), T),
        "T_corte": c.get("T_corte"),
        "i_exog": i_exog,
        "medidas_receita": med_rec,
        "medidas_despesa": med_desp,
        "itens": itens,
        "venda_reservas": cronograma_reservas(c.get("venda_reservas", []), T),
        "capex_ppp": capex_ppp(cfg["comum"]["capex_ppp"], T),
        "T": T,
    }


def selic(regra: str, i_taylor: np.ndarray, i_exog_t: float, delta_t: float, i_min: float) -> np.ndarray:
    if regra == "taylor":
        return np.maximum(i_taylor, i_min)
    if regra == "exogena":
        return np.full_like(i_taylor, i_exog_t)
    if regra == "condicionada":
        return np.maximum(i_exog_t, i_taylor - delta_t)
    if regra == "condicionada_sem_piso":
        # trajetória exógena como TETO: a Selic segue a Taylor quando ela está abaixo da trajetória; acima, fica na
        # trajetória, mas nunca mais que δ abaixo da Taylor. Com δ = 0 (depois de T_corte + T_δ), i = Taylor sem piso.
        return np.maximum(np.minimum(i_taylor, np.maximum(i_exog_t, i_taylor - delta_t)), i_min)
    raise ValueError(f"regra de política desconhecida: {regra}")
