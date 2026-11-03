"""Restrição de rolagem: LFT com juro real abaixo do piso migra para títulos indexados (ou é monetizada)."""
from __future__ import annotations

import numpy as np


def migracao(d_lft, d_oma, i, pi_e, giro_lft: float, r_min: float, banda: float) -> np.ndarray:
    """Estoque de LFT do Tesouro (% PIB) que não é rolado no trimestre.

    As compromissadas do BCB (d_oma) não migram: o BCB precisa enxugar a liquidez.
    """
    r_real = i - pi_e
    intensidade = np.clip((r_min - r_real) / banda, 0, 1)
    return np.maximum(d_lft - d_oma, 0) * giro_lft * intensidade


def aplicar(d_k: dict, r_long_est, r_long, migr, monetizar: bool) -> tuple[dict, np.ndarray]:
    """Move `migr` da LFT para NTN-B ao r_long corrente; com monetização, o estoque sai da dívida."""
    d_k = dict(d_k)
    d_k["lft"] = d_k["lft"] - migr
    if monetizar:
        return d_k, r_long_est
    novo = d_k["ipca"] + migr
    r_long_est = np.where(novo > 0, (d_k["ipca"] * r_long_est + migr * r_long) / np.where(novo > 0, novo, 1), r_long_est)
    d_k["ipca"] = novo
    return d_k, r_long_est
