"""Valor presente dos superávits esperados, lacuna fiscal e inflação fiscal (módulo P3)."""
from __future__ import annotations

import numpy as np

D_MIN = 10.0  # piso da dívida líquida (% PIB) no denominador da fração não lastreada


def valor_presente(s_plan: np.ndarray, s_corr: np.ndarray, lam_fiscal: np.ndarray, r_desc: np.ndarray,
                   g_esp: float, delta_min: float, escala_vt: float = 100.0, r_terminal=None) -> np.ndarray:
    """VP (% do PIB) dos superávits esperados nos próximos H trimestres mais o valor terminal.

    s_plan: (H,) primário anunciado para t+1..t+H (% PIB a.a.); s_corr: (P,) primário corrente,
    persistido por quem não acredita no plano. r_desc e g_esp em % a.a.
    Valor terminal: escala_vt · s_H / max(r_terminal − g, Δ_min) · fator_H, com r_terminal = juro real longo
    neutro (taxa de desconto de estado estacionário; sem ela, usa r_desc). Com escala_vt = 100 é a
    perpetuidade em unidades consistentes (r − g em p.p.); com 1, é a fórmula literal da especificação.
    """
    H = s_plan.shape[-1]
    k = np.arange(1, H + 1)
    razao = (1 + g_esp / 100) / (1 + r_desc / 100)
    fator = razao[:, None] ** (k[None, :] / 4)                     # (P, H)
    lam = lam_fiscal[:, None]
    s_esp = lam * s_plan[None, :] + (1 - lam) * s_corr[:, None]     # (P, H)
    vp = (s_esp / 4 * fator).sum(axis=1)
    r_term = r_desc if r_terminal is None else r_terminal
    vt = escala_vt * s_esp[:, -1] / np.maximum(r_term - g_esp, delta_min) * fator[:, -1]
    return vp + vt


def duracao(w_lft, w_pre, w_ipca, w_fx, dur_pre: float, dur_ipca: float, dur_fx: float):
    """Duração da dívida em anos; a LFT reprecifica a cada trimestre (0,25 ano)."""
    return w_lft * 0.25 + w_pre * dur_pre + w_ipca * dur_ipca + w_fx * dur_fx


def fracao_nao_lastreada(lacuna, d_net):
    """Lacuna como fração da dívida líquida: a parte que o nível de preços teria de absorver."""
    return lacuna / np.maximum(d_net, D_MIN)


def inflacao_fiscal(fracao, fracao0, dur, theta: float, phi: float, fracao_ref=None):
    """Inflação (% a.a.) que absorve a fração θ da REVISÃO da lacuna ao longo da duração da dívida.

    fracao_ref: fração não lastreada ao longo da trajetória anunciada, deslocada para partir de fracao0.
    Sem ela, a referência é a fração inicial constante. Só revisões em relação ao que já estava
    precificado em t0 geram inflação; φ é a parte da lacuna inicial ainda não precificada:
    θ · (fracao − fracao_ref + φ·fracao0) / duração · 100.
    """
    ref = fracao0 if fracao_ref is None else fracao_ref
    return theta * (fracao - ref + phi * fracao0) / dur * 100
