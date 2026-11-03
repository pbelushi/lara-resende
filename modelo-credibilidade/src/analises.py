"""Análises da v2.2: arrays de sucesso por trajetória, tabelas e métricas do alongamento da dívida."""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pandas as pd

from . import bootstrap, dados, metricas, modelo, varredura

VARIANTES_ALONG = {"sem": None, "along_20": "along_20", "along_12": "along_12", "along_28": "along_28",
                   "along_pre": "along_pre", "along_50": "along_50"}


# ---------------------------------------------------------------- sucesso por trajetória

def montar_diagonal(pasta: Path, saida: Path, especs: list[str], variantes: list[str], cenarios: list[str]) -> dict:
    """Junta os npz parciais em sucesso_trajetorias.npz: (especificação, variante, cenário, λ, trajetória)."""
    trajs, grade, N = {}, None, None
    for e in especs:
        for v in variantes:
            arq = pasta / f"trajetorias_{e}_{v}.npz"
            if arq.exists():
                trajs[(e, v)] = bootstrap.carregar_trajetorias(arq)
                grade, N = trajs[(e, v)]["grade"], trajs[(e, v)]["ok"].shape[-1]
    forma = (len(especs), len(variantes), len(cenarios), len(grade), N)
    ok = np.zeros(forma, dtype=bool)
    extras = {k: np.zeros(forma, dtype=bool) for k in ("ok_bil", "ok_liq", "ok_liq_bil")}
    codigo = np.full(forma, -1, dtype=np.int8)
    disponivel = np.zeros(forma[:3], dtype=bool)
    for (e, v), tj in trajs.items():
        for k, c in enumerate(tj["cenarios"]):
            i, j, m = especs.index(e), variantes.index(v), cenarios.index(c)
            ok[i, j, m], codigo[i, j, m], disponivel[i, j, m] = tj["ok"][k], tj["codigo"][k], True
            for x, arr in extras.items():
                if x in tj:
                    arr[i, j, m] = tj[x][k]
    np.savez_compressed(saida / "sucesso_trajetorias.npz", ok=np.packbits(ok, axis=-1), codigo=codigo,
                        ok_banda_simetrica=np.packbits(extras["ok_bil"], axis=-1),
                        ok_divida_liquida=np.packbits(extras["ok_liq"], axis=-1),
                        ok_divida_liquida_banda=np.packbits(extras["ok_liq_bil"], axis=-1),
                        disponivel=disponivel, especificacoes=np.array(especs), variantes=np.array(variantes),
                        cenarios=np.array(cenarios), grade=grade, N=N,
                        codigos_falha=np.array([f"{k}={v}" for k, v in metricas.CODIGOS_FALHA.items()]))
    return trajs


def salvar_superficie(sup_trajs: dict, saida: Path, variantes: list[str], especs: list[str], cenarios: list[str],
                      grade: np.ndarray) -> None:
    """sucesso_superficie.npz: (variante, especificação, cenário, λ_π, λ_fiscal, trajetória)."""
    N = next(iter(sup_trajs.values()))[0].shape[-1]
    forma = (len(variantes), len(especs), len(cenarios), len(grade), len(grade), N)
    ok = np.zeros(forma, dtype=bool)
    codigo = np.full(forma, -1, dtype=np.int8)
    okb = np.zeros(forma, dtype=bool)
    for (e, v, c), (o, cod, ob) in sup_trajs.items():
        ok[variantes.index(v), especs.index(e), cenarios.index(c)] = o
        okb[variantes.index(v), especs.index(e), cenarios.index(c)] = ob
        codigo[variantes.index(v), especs.index(e), cenarios.index(c)] = cod
    np.savez_compressed(saida / "sucesso_superficie.npz", ok=np.packbits(ok, axis=-1), codigo=codigo,
                        ok_banda_simetrica=np.packbits(okb, axis=-1),
                        variantes=np.array(variantes), especificacoes=np.array(especs), cenarios=np.array(cenarios),
                        grade=grade, N=N)


# ---------------------------------------------------------------- alongamento

def _phi_var(var: str) -> tuple[float, str]:
    """Variante → (φ, alongamento)."""
    phi = 0.25 if var.startswith("phi_025") else 0.5 if var.startswith("phi_05") else 0.0
    resto = var.replace("phi_025", "").replace("phi_05", "").strip("_")
    return phi, ("sem" if resto in ("", "base") else resto)


def tabela_alongamento(df: pd.DataFrame, ls: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    alvo = {"P3": ["base", "phi_025", "phi_05", "along_20", "phi_025_along_20", "phi_05_along_20",
                   "phi_025_along_12", "phi_025_along_28", "phi_025_along_pre", "phi_025_along_50"],
            "P1": ["base", "along_20"], "P2": ["base", "along_20"]}
    for espec, vars_ in alvo.items():
        for var in vars_:
            l = ls[(ls["especificacao"] == espec) & (ls["variante"] == var)]
            if l.empty:
                continue
            todos_falham = l["lambda_star_50"].isna().all()
            phi, al = _phi_var(var)
            for r in l.itertuples():
                m = df[(df["especificacao"] == espec) & (df["variante"] == var) & (df["cenario"] == r.cenario)]
                linhas.append({"especificacao": espec, "phi": phi, "alongamento": al, "variante": var,
                               "cenario": r.cenario, "p_sucesso_max": r.p_sucesso_max,
                               "lambda_star_50": r.lambda_star_50, "lambda_star_80": r.lambda_star_80,
                               "todos_falham": todos_falham,
                               **{f"falha_{k}": m[f"falha_{k}"].mean() for k in metricas.CRITERIOS}})
    return pd.DataFrame(linhas)


def _rodar(p: dict, cfg: dict, espec: str, ajustes: dict, lams=(0.5, 0.9)) -> dict:
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": espec, **ajustes})
    saida = {}
    for ch, c in varredura.preparar_cenarios(q, cfg).items():
        saida[ch] = modelo.simular(q, c["cen"], np.array(lams), plano=c["plano"])
    return saida


AJUSTE_ALONG = {"alongamento": True, "w_lft_alvo": 0.40, "T_along": 20, "s_ipca": 0.7}


def erosao(p: dict, cfg: dict, phis=(0.0, 0.25), lams=(0.5, 0.9)) -> pd.DataFrame:
    """Redução da dívida real pela inflação e a parte não antecipada, P3, com e sem alongamento (determinístico)."""
    linhas = []
    for phi in phis:
        for nome, aj in (("sem", {}), ("along_20", AJUSTE_ALONG)):
            trs = _rodar(p, cfg, "P3", {"phi": phi, **aj}, lams)
            for ch, tr in trs.items():
                for k, lam in enumerate(lams):
                    na, tot = np.nansum(tr["erosao_na"][k, 1:]), np.nansum(tr["erosao_total"][k, 1:])
                    linhas.append({"phi": phi, "alongamento": nome, "cenario": ch, "lambda": lam,
                                   "erosao_total_pp": tot, "erosao_nao_antecipada_pp": na,
                                   "fracao_nao_antecipada": na / tot if abs(tot) > 1e-9 else np.nan,
                                   "d_final": tr["d_gross"][k, -1], "pi_media_final": np.nanmean(tr["pi"][k, -8:]),
                                   "ruptura": int(tr["ruptura"][k])})
    return pd.DataFrame(linhas)


def custo(p: dict, cfg: dict, especs=("P1", "P2", "P3"), lams=(0.5, 0.9)) -> pd.DataFrame:
    """Custo real efetivo médio da dívida e estoque final, com e sem alongamento, φ = 0."""
    linhas = []
    for espec in especs:
        res = {nome: _rodar(p, cfg, espec, aj, lams) for nome, aj in (("sem", {}), ("along_20", AJUSTE_ALONG))}
        for ch in res["sem"]:
            for k, lam in enumerate(lams):
                r = {}
                for nome, trs in res.items():
                    tr = trs[ch]
                    r[nome] = (np.nanmean(tr["i_ef"][k, 1:] - tr["pi"][k, 1:]), tr["d_gross"][k, -1],
                               np.nanmin(tr["w_lft"][k]), tr["duracao"][k, -1])
                linhas.append({"especificacao": espec, "cenario": ch, "lambda": lam,
                               "custo_real_sem": r["sem"][0], "custo_real_along": r["along_20"][0],
                               "delta_custo_pp": r["along_20"][0] - r["sem"][0],
                               "d_final_sem": r["sem"][1], "d_final_along": r["along_20"][1],
                               "delta_d_final": r["along_20"][1] - r["sem"][1],
                               "w_lft_min_along": r["along_20"][2], "duracao_final_sem": r["sem"][3],
                               "duracao_final_along": r["along_20"][3]})
    return pd.DataFrame(linhas)


def decomposicao_lft_t0(p: dict) -> dict:
    """LFT do Tesouro × compromissadas em t0 (SGS) e conferência com o estoque do Tesouro."""
    ini = p["ini"]
    out = {"lft_total": ini["w_lft"], "compromissadas": ini["w_oma"], "lft_tesouro": ini["w_lft"] - ini["w_oma"]}
    try:
        est = dados.baixar_estoque_dpf(offline=True)
        out.update({f"tesouro_{k}": v for k, v in dados.decomposicao_lft(est, pd.Timestamp(ini["data_base"])).items()})
    except Exception as e:  # noqa: BLE001
        out["tesouro_erro"] = str(e)
    return out


# ---------------------------------------------------------------- diagnóstico de C

def diagnostico_c(p: dict, cfg: dict, choques: np.ndarray, espec: str = "P1", lam: float = 0.9,
                  ultimos: int = 12) -> dict:
    """Selic, Taylor e dívida de A e C no fim do horizonte (medianas), e se há aperto tardio em C.

    Depois que δ chega a zero, i_C = max(i_alvo; Taylor): quando a Taylor cai abaixo do piso, C fica MAIS apertado
    que a regra (e que A, que segue a Taylor sem piso de 7,5%).
    """
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": espec})
    cens = varredura.preparar_cenarios(q, cfg, ["A", "C"])
    N, n = choques.shape[0], q["criterios"]["janela_final"]
    tr = {ch: modelo.simular(q, c["cen"], np.full(N, lam), choques=choques, plano=c["plano"],
                             guardar=("i", "i_taylor", "d_gross", "pi", "R")) for ch, c in cens.items()}
    T = tr["A"]["i"].shape[1] - 1
    ts = np.arange(T - ultimos + 1, T + 1)
    i_alvo = cfg["cenarios"]["C"]["i_alvo"]
    piso = (tr["C"]["i"] <= i_alvo + 1e-9) & (tr["C"]["i_taylor"] < i_alvo)  # piso de C acima da Taylor
    med = lambda x: np.nanmedian(x[:, ts], axis=0)  # noqa: E731
    tabela = pd.DataFrame({"t": ts, "i_A": med(tr["A"]["i"]), "tay_A": med(tr["A"]["i_taylor"]),
                           "d_A": med(tr["A"]["d_gross"]), "i_C": med(tr["C"]["i"]), "tay_C": med(tr["C"]["i_taylor"]),
                           "d_C": med(tr["C"]["d_gross"]), "piso_acima_taylor_C": np.nanmean(piso[:, ts], axis=0)})
    sobe = {ch: metricas.inclinacao_final(tr[ch]["d_gross"], n) > 0 for ch in tr}
    fim = slice(T - n + 1, T + 1)
    iC, tC, pC = tr["C"]["i"][:, fim], tr["C"]["i_taylor"][:, fim], piso[:, fim]
    s = sobe["C"]
    resumo = {"subindo_A": float(sobe["A"].mean()), "subindo_C": float(s.mean()),
              "i_C_subindo": float(np.nanmean(iC[s])), "i_C_estavel": float(np.nanmean(iC[~s])),
              "tay_C_subindo": float(np.nanmean(tC[s])), "tay_C_estavel": float(np.nanmean(tC[~s])),
              "piso_C_subindo": float(np.nanmean(pC[s])), "piso_C_estavel": float(np.nanmean(pC[~s])),
              "i_A_fim": float(np.nanmean(tr["A"]["i"][:, fim])), "i_C_fim": float(np.nanmean(iC))}
    delta = cens["C"]["cen"]["delta"]
    t_zero = int(np.argmax((np.arange(len(delta)) > cens["C"]["cen"]["T_corte"]) & (delta <= 0)))
    aperto_nivel = resumo["i_C_fim"] - resumo["i_A_fim"] > 0.2 and float(np.nanmean(piso[:, fim])) > 0.2
    explica = resumo["subindo_C"] > resumo["subindo_A"] and resumo["piso_C_subindo"] > resumo["piso_C_estavel"] + 0.1
    resumo["piso_C_fim"] = float(np.nanmean(piso[:, fim]))
    leitura = (("**Há aperto tardio em nível em C:** depois que δ zera, o piso de 7,5% fica acima da Taylor em "
                f"{100 * resumo['piso_C_fim']:.0f}% dos trimestres finais, e a Selic média de C nos últimos 8 trimestres é "
                f"{resumo['i_C_fim']:.2f}% contra {resumo['i_A_fim']:.2f}% em A. ".replace(".", ",").replace(",% ", ".% ")
                .replace("A, ", "A. "))
               if aperto_nivel else "**Não há aperto tardio em nível em C.** ") + (
               "Em λ = 0,9, esse aperto explica a dívida de C ainda subindo." if explica else
               f"Em λ = 0,9, porém, ele não explica a dívida ainda subindo: só {100 * resumo['subindo_C']:.0f}% das "
               f"trajetórias de C sobem no fim, contra {100 * resumo['subindo_A']:.0f}% de A.")
    return {"tabela": tabela, "resumo": resumo, "N": N, "t_delta_zero": t_zero, "leitura": leitura,
            "series": {ch: {k: np.nanpercentile(tr[ch][k], [25, 50, 75], axis=0) for k in ("i", "i_taylor", "d_gross")}
                       for ch in tr}, "i_alvo": i_alvo}
