"""Módulos intercambiáveis da equação de inflação (P1, P2, P3).

Interface comum: `inflacao(estado, params, choque) -> (pi, componentes)`, com
`estado` contendo arrays (P,) de pi_ant, pi_e, h_ant, de12 e pi_fiscal. Os
componentes (inércia, expectativa, hiato, câmbio, fiscal, choque) somam a pi e
alimentam a decomposição do gráfico 11.
"""
from __future__ import annotations

import numpy as np

COMPONENTES_PI = ("inercia", "expectativa", "hiato", "cambio", "fiscal", "choque")


def _phillips(estado: dict, p: dict, choque: np.ndarray, b2: float) -> tuple[np.ndarray, dict]:
    zeros = np.zeros_like(estado["pi_ant"])
    comp = {
        "inercia": p["b1"] * estado["pi_ant"],
        "expectativa": (1 - p["b1"]) * estado["pi_e"],
        "hiato": b2 * estado["h_ant"],
        "cambio": p["b3"] * estado["de12"],
        "fiscal": estado.get("pi_monet", zeros),
        "choque": choque,
    }
    return sum(comp.values()), comp


def p1(estado: dict, p: dict, choque: np.ndarray) -> tuple[np.ndarray, dict]:
    """Phillips híbrida: inércia, expectativas, hiato e repasse cambial."""
    return _phillips(estado, p, choque, p["b2"])


def p2(estado: dict, p: dict, choque: np.ndarray) -> tuple[np.ndarray, dict]:
    """Phillips achatada: P1 com inclinação b2_p2 (referência 0,025)."""
    return _phillips(estado, p, choque, p["b2_p2"])


def p3(estado: dict, p: dict, choque: np.ndarray) -> tuple[np.ndarray, dict]:
    """Fechamento fiscal (FTPL reduzida): sem inércia própria; a lacuna fiscal gera inflação."""
    zeros = np.zeros_like(estado["pi_ant"])
    comp = {
        "inercia": zeros,
        "expectativa": estado["pi_e"],
        "hiato": p["b2_p3"] * estado["h_ant"],
        "cambio": p["b3"] * estado["de12"],
        "fiscal": estado["pi_fiscal"] + estado.get("pi_monet", zeros),
        "choque": choque,
    }
    return sum(comp.values()), comp


INFLACAO = {"P1": p1, "P2": p2, "P3": p3}


def inflacao(especificacao: str, estado: dict, p: dict, choque: np.ndarray) -> tuple[np.ndarray, dict]:
    try:
        return INFLACAO[especificacao](estado, p, choque)
    except KeyError:
        raise ValueError(f"especificação de inflação desconhecida: {especificacao}") from None
