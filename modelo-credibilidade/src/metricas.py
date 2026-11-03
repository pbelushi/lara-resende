"""Critério de sucesso de uma trajetória, adesão mínima λ* e área de sucesso."""
from __future__ import annotations

import numpy as np

CRITERIOS = ("inflacao_explosiva", "divida_inclinacao", "divida_nivel", "inflacao", "reservas")


def inclinacao_final(x: np.ndarray, n: int) -> np.ndarray:
    """Inclinação (MQO) dos últimos n pontos de cada linha de x (P, T+1)."""
    y = x[:, -n:]
    t = np.arange(n) - (n - 1) / 2
    return (y - y.mean(axis=1, keepdims=True)) @ t / (t @ t)


def sucesso(traj: dict, p: dict, tolerancia_inflacao: float | None = None,
            bilateral: bool = False, divida: str = "bruta") -> tuple[np.ndarray, dict]:
    """Avalia os quatro critérios da seção 6 da v2. Devolve (sucesso, {critério: atendido}).

    O critério de inflação explosiva tem precedência: uma trajetória que o viola não é avaliada pelos
    demais (os outros critérios só contam como atendidos/violados entre as não explosivas).
    bilateral=True: a inflação média final precisa ficar DENTRO da banda [meta − tol, meta + tol]
    (com tol = 1,5, entre 1,5% e 4,5%); com False, vale só o teto (meta + tol), como até a v2.2 inicial.
    divida = "bruta" (DBGG, padrão) ou "liquida" (DLSP): a variável usada nos dois critérios de dívida.
    """
    c = p["criterios"]
    n = c["janela_final"]
    tol = c["tolerancia_inflacao"] if tolerancia_inflacao is None else tolerancia_inflacao
    d, pi = traj["d_gross" if divida == "bruta" else "d_net"], traj["pi"]
    with np.errstate(invalid="ignore"):
        nao_explosiva = (traj["ruptura"] < 0) & (np.nanmax(pi, axis=1) <= c.get("teto_explosivo", 20.0))
        nao_explosiva &= np.isfinite(d).all(axis=1) & np.isfinite(pi).all(axis=1)
        detalhe = {
            "inflacao_explosiva": nao_explosiva,
            "divida_inclinacao": nao_explosiva & (inclinacao_final(d, n) <= 0),
            "divida_nivel": nao_explosiva & (d[:, -1] <= d[:, 0] + c["tolerancia_divida"]),
            "inflacao": nao_explosiva & (pi[:, -n:].mean(axis=1) <= p["pi_meta"] + tol)
            & ((pi[:, -n:].mean(axis=1) >= p["pi_meta"] - tol) if bilateral else True),
            # reservas ≥ R_min em todos os trimestres, ou só na janela final (quando a defesa pode romper o piso)
            "reservas": nao_explosiva & ((traj["R"][:, -n:] if c.get("reservas_janela") else traj["R"])
                                         >= p["R_min"] - 1e-9).all(axis=1),
        }
    ok = np.logical_and.reduce(list(detalhe.values()))
    return ok, detalhe


# código do primeiro critério que falhou, na ordem de precedência (0 = sucesso)
CODIGOS_FALHA = {0: "sucesso", 1: "inflacao_explosiva", 2: "divida_inclinacao", 3: "divida_nivel", 4: "inflacao",
                 5: "reservas"}


# combinações de critério: (sufixo, inflação bilateral?, dívida)
METRICAS = {"": (False, "bruta"), "_bil": (True, "bruta"), "_liq": (False, "liquida"), "_liq_bil": (True, "liquida")}
CHAVE_OK = {"": "ok", "_bil": "ok_bil", "_liq": "ok_liq", "_liq_bil": "ok_liq_bil"}


def sucesso_todas(traj: dict, p: dict) -> dict:
    """Sucesso por trajetória nas quatro combinações de critério (dívida bruta/líquida × inflação teto/banda)."""
    return {suf: sucesso(traj, p, bilateral=b, divida=d)[0] for suf, (b, d) in METRICAS.items()}


def codigo_falha(detalhe: dict) -> np.ndarray:
    cod = np.zeros(len(detalhe["inflacao_explosiva"]), dtype=np.int8)
    for c in (5, 4, 3, 2, 1):  # do menos ao mais prioritário: o último a escrever prevalece
        cod[~detalhe[CODIGOS_FALHA[c]]] = c
    return cod


def falhas(detalhe: dict) -> dict:
    """Fração de falhas por critério: explosivas sobre o total; as demais só entre as não explosivas."""
    base = detalhe["inflacao_explosiva"]
    saida = {"inflacao_explosiva": 1 - base.mean()}
    for k, v in detalhe.items():
        if k != "inflacao_explosiva":
            saida[k] = (base & ~v).mean()
    return saida


def divida_ok(detalhe: dict) -> np.ndarray:
    return detalhe["divida_inclinacao"] & detalhe["divida_nivel"]


def intervalos(grade: np.ndarray, ok: np.ndarray) -> list[tuple[float, float]]:
    """Intervalos contíguos da grade em que ok é verdadeiro."""
    saida, inicio = [], None
    for k, (lam, v) in enumerate(zip(grade, ok)):
        if v and inicio is None:
            inicio = lam
        if inicio is not None and (not v or k == len(grade) - 1):
            saida.append((float(inicio), float(lam if v else grade[k - 1])))
            inicio = None
    return saida


def lambda_star_det(grade: np.ndarray, ok: np.ndarray) -> dict:
    """Menor λ com sucesso, se o sucesso é monotônico em λ, e os intervalos de sucesso."""
    iv = intervalos(grade, ok)
    return {
        "lambda_star": iv[0][0] if iv else np.nan,
        "monotonico": len(iv) <= 1 and (not iv or iv[0][1] == float(grade[-1])),
        "intervalos": iv,
    }


def lambda_star_prob(grade: np.ndarray, prob: np.ndarray, limiar: float) -> float:
    acima = np.nonzero(prob >= limiar)[0]
    return float(grade[acima[0]]) if acima.size else np.nan


def violacoes_monotonia(prob: np.ndarray, tolerancia: float = 0.0) -> int:
    """Número de quedas de P_sucesso ao aumentar λ (acima da tolerância de ruído amostral)."""
    return int((np.diff(prob) < -tolerancia).sum())


def area_sucesso(prob: np.ndarray, limiar: float = 0.8) -> float:
    """Fração dos pontos da superfície λ_π × λ_fiscal com P(sucesso) ≥ limiar."""
    return float((prob >= limiar).mean())
