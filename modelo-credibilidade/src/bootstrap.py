"""Bootstrap pareado da comparação A × C (Tarefa 1 da v2.2).

Como A, B e C usam os mesmos choques, cada réplica reamostra os MESMOS índices de trajetória para todos os
cenários. Mede só a incerteza do Monte Carlo, não a dos parâmetros.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CENSURA = 1.01  # λ* atribuído quando o limiar não é atingido na réplica


def indices(N: int, R: int, seed: int, identidade: bool = False) -> np.ndarray:
    """(R, N) índices de trajetória, comuns a todos os cenários. identidade=True devolve a amostra original."""
    if identidade:
        return np.tile(np.arange(N), (R, 1))
    return np.random.default_rng(seed).integers(0, N, size=(R, N))


def _lambda_star(P: np.ndarray, grade: np.ndarray, limiar: float) -> np.ndarray:
    """P: (R, n_λ) → λ* por réplica, com censura em 1,01."""
    acima = P >= limiar
    primeiro = acima.argmax(axis=1)
    return np.where(acima.any(axis=1), grade[primeiro], CENSURA)


def prob_replicas(ok: np.ndarray, idx: np.ndarray, bloco: int = 100) -> np.ndarray:
    """ok: (..., N) booleano; idx: (R, N). Devolve P(sucesso) por réplica: (R, ...)."""
    saida = []
    for k in range(0, idx.shape[0], bloco):
        sub = idx[k:k + bloco]
        saida.append(ok[..., sub].mean(axis=-1).transpose(-1, *range(ok.ndim - 1)))  # (r, ...)
    return np.concatenate(saida)


def diagonal(ok_A: np.ndarray, ok_C: np.ndarray, grade: np.ndarray, idx: np.ndarray) -> dict:
    """ok_*: (n_λ, N). Δλ* = λ*(C) − λ*(A) para 80% e 50%, com IC, fração C > A e censura."""
    PA, PC = prob_replicas(ok_A, idx), prob_replicas(ok_C, idx)
    pA, pC = ok_A.mean(axis=-1)[None], ok_C.mean(axis=-1)[None]
    out = {}
    for lim, rot in ((0.8, "80"), (0.7, "70"), (0.5, "50")):
        lA, lC = _lambda_star(PA, grade, lim), _lambda_star(PC, grade, lim)
        d = lC - lA
        out.update({
            f"A_{rot}": float(_lambda_star(pA, grade, lim)[0]), f"C_{rot}": float(_lambda_star(pC, grade, lim)[0]),
            f"delta_{rot}": float(_lambda_star(pC, grade, lim)[0] - _lambda_star(pA, grade, lim)[0]),
            f"ic_lo_{rot}": float(np.percentile(d, 2.5)), f"ic_hi_{rot}": float(np.percentile(d, 97.5)),
            # λ* de C menor = C exige menos adesão = C supera A
            f"frac_C_supera_{rot}": float((lC < lA).mean()),
            f"censura_A_{rot}": float((lA == CENSURA).mean()), f"censura_C_{rot}": float((lC == CENSURA).mean()),
        })
        out[f"pouco_confiavel_{rot}"] = max(out[f"censura_A_{rot}"], out[f"censura_C_{rot}"]) > 0.2
    return out


def area(ok_A: np.ndarray, ok_C: np.ndarray, idx: np.ndarray, limiar: float = 0.8) -> dict:
    """ok_*: (n_λπ, n_λf, N). ΔÁrea = Área(A) − Área(C), com IC e fração C > A."""
    aA = (prob_replicas(ok_A, idx, bloco=20) >= limiar).mean(axis=(1, 2))
    aC = (prob_replicas(ok_C, idx, bloco=20) >= limiar).mean(axis=(1, 2))
    d = aA - aC
    pontual = float((ok_A.mean(-1) >= limiar).mean() - (ok_C.mean(-1) >= limiar).mean())
    return {"area_A": float((ok_A.mean(-1) >= limiar).mean()), "area_C": float((ok_C.mean(-1) >= limiar).mean()),
            "delta_area": pontual, "ic_lo": float(np.percentile(d, 2.5)), "ic_hi": float(np.percentile(d, 97.5)),
            "frac_C_supera": float((aC > aA).mean())}


def leitura_diagonal(r: dict, rot: str = "80") -> str:
    lo, hi = r[f"ic_lo_{rot}"], r[f"ic_hi_{rot}"]
    if lo <= 0 <= hi:
        return "empate estatístico"
    return "vantagem significativa de A" if lo > 0 else "vantagem significativa de C"


def leitura_area(r: dict) -> str:
    if r["ic_lo"] > 0:
        return "A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal"
    if r["ic_hi"] < 0:
        return "C significativamente mais robusto ao descompasso entre λ_π e λ_fiscal"
    return "empate estatístico"


def carregar_trajetorias(arq) -> dict:
    z = np.load(arq)
    N = int(z["N"])
    ok = np.unpackbits(z["ok"], axis=-1, count=N).astype(bool)
    out = {"cenarios": list(z["cenarios"]), "grade": z["grade"], "ok": ok, "codigo": z["codigo"]}
    for k in ("ok_bil", "ok_liq", "ok_liq_bil"):
        if k in z:
            out[k] = np.unpackbits(z[k], axis=-1, count=N).astype(bool)
    return out


def rodar_diagonal(trajs: dict, R: int, seed: int, refs: dict | None = None, chave: str = "ok") -> pd.DataFrame:
    """trajs: {(espec, variante): dict de carregar_trajetorias}. Variantes só de C usam o A da variante de
    referência (refs; padrão: base), com os mesmos choques."""
    refs = refs or {}
    linhas = []
    for (espec, var), tj in trajs.items():
        cen = dict(zip(tj["cenarios"], tj[chave]))
        if "C" not in cen:
            continue
        ok_A = cen.get("A")
        if ok_A is None:
            ref = refs.get(var, "base") if (espec, refs.get(var, "base")) in trajs else "base"
            ok_A = dict(zip(trajs[(espec, ref)]["cenarios"], trajs[(espec, ref)][chave]))["A"]
        idx = indices(ok_A.shape[-1], R, seed)
        linhas.append({"especificacao": espec, "variante": var, **diagonal(ok_A, cen["C"], tj["grade"], idx)})
    df = pd.DataFrame(linhas)
    if len(df):
        for rot in ("80", "70", "50"):
            df[f"leitura_{rot}"] = [leitura_diagonal(r, rot) for r in df.to_dict("records")]
    return df


def rodar_area(sup_trajs: dict, R: int, seed: int, pos: int = 0) -> pd.DataFrame:
    """sup_trajs: {(espec, variante, cenário): (ok, código, ok_banda)} com ok (n_λπ, n_λf, N); pos = 0 (teto) ou
    2 (banda simétrica)."""
    linhas = []
    for (espec, var, ch), tup in sup_trajs.items():
        okC = tup[pos]
        if ch != "C" or (espec, var, "A") not in sup_trajs:
            continue
        okA = sup_trajs[(espec, var, "A")][pos]
        idx = indices(okA.shape[-1], R, seed)
        r = area(okA, okC, idx)
        linhas.append({"especificacao": espec, "variante": var, **r, "leitura": leitura_area(r)})
    return pd.DataFrame(linhas)


def _ok(trajs: dict, espec: str, var: str, cen: str, chave: str = "ok"):
    tj = trajs.get((espec, var))
    if tj is None or cen not in tj["cenarios"]:
        return None
    return tj[chave][list(tj["cenarios"]).index(cen)]


def comparar(trajs: dict, pares: list[dict], R: int, seed: int, chave: str = "ok") -> pd.DataFrame:
    """Comparações cruzadas pareadas: Δλ* = λ*(alt) − λ*(ref), mesmos índices de trajetória.

    pares: [{"rotulo", "especificacao", "ref": (variante, cenário), "alt": (variante, cenário)}].
    """
    linhas = []
    for par in pares:
        e = par["especificacao"]
        ok_ref, ok_alt = _ok(trajs, e, *par["ref"], chave), _ok(trajs, e, *par["alt"], chave)
        if ok_ref is None or ok_alt is None:
            continue
        grade = trajs[(e, par["ref"][0])]["grade"]
        r = diagonal(ok_ref, ok_alt, grade, indices(ok_ref.shape[-1], R, seed))
        r = {k.replace("_A_", "_ref_").replace("_C_", "_alt_"): v for k, v in r.items()}
        r = {("ref_" + k[2:] if k.startswith("A_") else "alt_" + k[2:] if k.startswith("C_") else k): v
             for k, v in r.items()}
        linhas.append({"rotulo": par["rotulo"], "especificacao": e, "ref": "/".join(par["ref"]),
                       "alt": "/".join(par["alt"]), **r})
    df = pd.DataFrame(linhas)
    if len(df):
        for rot in ("80", "70", "50"):
            df[f"leitura_{rot}"] = [("empate estatístico" if r[f"ic_lo_{rot}"] <= 0 <= r[f"ic_hi_{rot}"] else
                                     "alternativa exige menos adesão" if r[f"ic_hi_{rot}"] < 0 else
                                     "referência exige menos adesão") for r in df.to_dict("records")]
    return df


def comparar_did(trajs: dict, pares: list[dict], R: int, seed: int, chave: str = "ok") -> pd.DataFrame:
    """Diferença das diferenças pareada: [λ*(b2) − λ*(b1)] − [λ*(a2) − λ*(a1)] com os mesmos índices.

    pares: [{"rotulo", "especificacao", "a": ((var, cen), (var, cen)), "b": ((var, cen), (var, cen))}]. Usado para
    saber se o choque custa mais a um cenário que a outro (custo de cauda).
    """
    linhas = []
    for par in pares:
        e = par["especificacao"]
        oks = [_ok(trajs, e, *vc, chave) for vc in (*par["a"], *par["b"])]
        if any(o is None for o in oks):
            continue
        grade = trajs[(e, par["a"][0][0])]["grade"]
        idx = indices(oks[0].shape[-1], R, seed)
        linha = {"rotulo": par["rotulo"], "especificacao": e}
        for lim, rot in ((0.8, "80"), (0.7, "70"), (0.5, "50")):
            ls_rep = [_lambda_star(prob_replicas(o, idx), grade, lim) for o in oks]
            ls_pt = [_lambda_star(o.mean(axis=-1)[None], grade, lim)[0] for o in oks]
            d = (ls_rep[3] - ls_rep[2]) - (ls_rep[1] - ls_rep[0])
            linha.update({f"custo_a_{rot}": float(ls_pt[1] - ls_pt[0]), f"custo_b_{rot}": float(ls_pt[3] - ls_pt[2]),
                          f"did_{rot}": float((ls_pt[3] - ls_pt[2]) - (ls_pt[1] - ls_pt[0])),
                          f"ic_lo_{rot}": float(np.percentile(d, 2.5)), f"ic_hi_{rot}": float(np.percentile(d, 97.5)),
                          f"censura_{rot}": float(max((x == CENSURA).mean() for x in ls_rep))})
        linhas.append(linha)
    return pd.DataFrame(linhas)


def comparar_area(sup_trajs: dict, pares: list[dict], R: int, seed: int, pos: int = 0) -> pd.DataFrame:
    """ΔÁrea = Área(ref) − Área(alt) na superfície, pares como em `comparar` (com cenários)."""
    linhas = []
    for par in pares:
        e = par["especificacao"]
        a = sup_trajs.get((e, *par["ref"]))
        b = sup_trajs.get((e, *par["alt"]))
        if a is None or b is None:
            continue
        r = area(a[pos], b[pos], indices(a[pos].shape[-1], R, seed))
        linhas.append({"rotulo": par["rotulo"], "especificacao": e, "ref": "/".join(par["ref"]),
                       "alt": "/".join(par["alt"]), "area_ref": r["area_A"], "area_alt": r["area_C"],
                       "delta_area": r["delta_area"], "ic_lo": r["ic_lo"], "ic_hi": r["ic_hi"],
                       "frac_alt_supera": r["frac_C_supera"],
                       "leitura": ("empate estatístico" if r["ic_lo"] <= 0 <= r["ic_hi"] else
                                   "referência mais robusta" if r["ic_lo"] > 0 else "alternativa mais robusta")})
    return pd.DataFrame(linhas)


def ordem_com_empate(ordem_txt: str, empate: bool) -> str:
    """"A > C > B" → "A ≈ C > B" quando A e C estão estatisticamente empatados e adjacentes."""
    if not empate:
        return ordem_txt
    partes = ordem_txt.split(" > ")
    for k in range(len(partes) - 1):
        if {partes[k], partes[k + 1]} == {"A", "C"}:
            partes[k:k + 2] = ["A ≈ C"]
            break
    return " > ".join(partes)
