"""Validação por especificação de inflação (seção 10 da v2).

Em cada episódio, Selic, primário e depreciação cambial seguem as trilhas observadas (o câmbio
inclui choques externos que o modelo não gera). Em P3, o primário anunciado é o que o Focus
esperava em cada data. Calibra-se λ (diagonal) e, em P3, θ; o erro é o RMSE normalizado
(RMSE / desvio-padrão) de inflação e NTN-B 10 anos.
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from . import modelo
from .dados import PROC, RAW, pesquisa_focus

EPISODIOS = {
    "2016–2019: âncora fiscal e queda da Selic": ("2016-06-30", "2019-12-31"),
    "2020–2022: Selic a 2%, expansão fiscal e aperto": ("2020-06-30", "2022-12-31"),
}
JANELA_PICO = ("2021-07-01", "2022-09-30")
FRACAO_PICO = 0.75  # reproduz o pico se o máximo simulado atinge 75% do observado
GRADE_LAMBDA = np.round(np.arange(0, 1.0001, 0.05), 2)
GRADE_THETA = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0)


def _ini_historico(painel: pd.DataFrame, inicio: pd.Timestamp, base: dict) -> dict:
    ate = painel.loc[:inicio]
    ult = lambda c: float(ate[c].dropna().iloc[-1])  # noqa: E731
    ini = copy.deepcopy(base)
    ini.update({
        "i0": ult("meta_selic"), "pi0": ult("ipca12"), "pi_e0": ult("pi_e"), "h0": ult("h"), "g0": ult("g_12m"),
        "g_potencial": float(ate["g_tend"].dropna().iloc[-20:].mean()), "d_gross0": ult("dbgg"),
        "d_net0": ult("dlsp"), "R0": ult("reservas_bi"), "E0": ult("cambio"), "Y0": ult("pib_12m_bi"),
        "s0": ult("s_spc"), "s_gc0": ult("s_gc"), "gamma0": ult("gamma"),
        "w_lft": ult("w_lft"), "w_pre": ult("w_pre"), "w_ipca": ult("w_ipca"), "w_fx": ult("w_fx"),
        "w_oma": ult("w_oma"), "prazo_pre_meses": ult("prazo_ltn"), "prazo_ipca_meses": ult("prazo_ntnb"),
        "r_long0": ult("ntnb10"),
        "i_pre_estoque0": float(ate["selic"].dropna().iloc[-8:].mean()),
        "r_long_estoque0": float(ate["ntnb10"].dropna().iloc[-28:].mean()),
        "de_ult4": [float(x) for x in ate["de"].dropna().iloc[-4:]],
    })
    if "prazo_lft" in ate and ate["prazo_lft"].notna().any():
        ini["prazo_lft_meses"] = ult("prazo_lft")
    futuro = painel.loc[inicio:, "meta_selic"].iloc[1:9]
    ini["selic_focus_8t"] = [float(x) for x in futuro]  # previsão perfeita da Selic no t0
    return ini


def plano_s_focus(anuais: pd.DataFrame | None, datas: pd.DatetimeIndex, s_hist: np.ndarray, H: int) -> np.ndarray:
    """(T+1, H): primário esperado pelo Focus, em cada data, para os H trimestres seguintes."""
    mat = np.empty((len(datas), H))
    for t, d in enumerate(datas):
        esp = pesquisa_focus(anuais, "Resultado primário", d) if anuais is not None else pd.Series(dtype=float)
        for k in range(1, H + 1):
            ano = (d + pd.offsets.QuarterEnd(k)).year
            if esp.empty:
                mat[t, k - 1] = s_hist[t]
            else:
                mat[t, k - 1] = esp.get(ano, esp.iloc[-1] if ano > esp.index.max() else esp.iloc[0])
    return mat


def _erro(tr: dict, dados: dict) -> np.ndarray:
    return sum(np.sqrt(np.nanmean((tr[v][:, 1:] - dados[v][1:]) ** 2, axis=1)) / np.nanstd(dados[v])
               for v in dados)


def rodar_episodio(p: dict, painel: pd.DataFrame, anuais: pd.DataFrame | None, inicio: str, fim: str,
                   espec: str, theta: float | None = None) -> dict:
    inicio, fim = pd.Timestamp(inicio), pd.Timestamp(fim)
    janela = painel.loc[inicio:fim]
    T = len(janela) - 1
    q = copy.deepcopy(p)
    q["especificacao"] = espec
    if theta is not None:
        q["theta"] = theta
    q["ini"] = _ini_historico(painel, inicio, p["ini"])
    q.pop("g_potencial", None)
    q = modelo.preparar(q)
    i_hist = janela["meta_selic"].values
    s_hist = janela["s_spc"].values
    zeros = np.zeros(T + 1)
    cen = {"chave": "hist", "nome": "histórico", "cor": "#333333", "regra": "exogena", "delta": zeros,
           "i_exog": i_hist, "medidas_receita": zeros, "medidas_despesa": zeros,
           "venda_reservas": zeros, "capex_ppp": zeros, "T": T}
    # Fundamentos "anunciados" aproximados pelos realizados no fim do episódio.
    s_estab_fim = modelo.s_estabilizador(janela["selic"].iloc[-4:].mean(), janela["gamma"].iloc[-1],
                                         janela["dbgg"].iloc[-1])
    F = q["p1"] * (janela["dbgg"].iloc[-1] - q["d_ref"]) + modelo.p2_efetivo(q) * (s_estab_fim - s_hist[-1])
    plano = {"F": float(F), "i": np.concatenate([i_hist, np.full(8, i_hist[-1])]),
             "s_mat": plano_s_focus(anuais, janela.index, s_hist, int(q["H_vp"]))}
    override = {"i": i_hist, "s": s_hist, "de": janela["de"].values}
    tr = modelo.simular(q, cen, GRADE_LAMBDA, plano=plano, override=override, guardar=("pi", "r_long"))
    dados = {"pi": janela["ipca12"].values, "r_long": janela["ntnb10"].values}
    erro = _erro(tr, dados)
    return {"datas": janela.index, "dados": dados, "erro": erro, "tr": tr}


def _pico(r: dict, k: int) -> tuple[float, float]:
    m = (r["datas"] >= JANELA_PICO[0]) & (r["datas"] <= JANELA_PICO[1])
    if not m.any():
        return np.nan, np.nan
    return float(np.nanmax(r["dados"]["pi"][m])), float(np.nanmax(r["tr"]["pi"][k][m]))


def validar(p: dict, especs=("P1", "P2", "P3")) -> tuple[dict, pd.DataFrame]:
    painel = pd.read_csv(PROC / "trimestral.csv", index_col=0, parse_dates=True)
    arq = RAW / "focus_anuais_historico.csv"
    anuais = pd.read_csv(arq, parse_dates=["Data"]) if arq.exists() else None
    resultados, linhas = {}, []
    for espec in especs:
        for nome, (ini, fim) in EPISODIOS.items():
            thetas = GRADE_THETA if espec == "P3" else (None,)
            rodadas = {th: rodar_episodio(p, painel, anuais, ini, fim, espec, th) for th in thetas}
            th_best, r = min(rodadas.items(), key=lambda kv: np.nanmin(kv[1]["erro"]))
            k = int(np.nanargmin(r["erro"]))
            pico_obs, pico_sim = _pico(r, k)
            pegar = lambda lam: {v: r["tr"][v][int(np.argmin(np.abs(GRADE_LAMBDA - lam)))]  # noqa: E731
                                 for v in r["dados"]}
            resultados[(espec, nome)] = {
                "datas": r["datas"], "dados": r["dados"], "lambda_melhor": float(GRADE_LAMBDA[k]), "theta": th_best,
                "simulado": {0.1: pegar(0.1), 0.5: pegar(0.5), 0.9: pegar(0.9), "melhor": pegar(GRADE_LAMBDA[k])},
            }
            linha = {"especificacao": espec, "episodio": nome, "inicio": ini, "fim": fim,
                     "lambda_melhor_ajuste": float(GRADE_LAMBDA[k]), "theta": th_best,
                     "erro_normalizado_min": float(np.nanmin(r["erro"])),
                     "erro_lambda_0": float(r["erro"][0]), "erro_lambda_1": float(r["erro"][-1]),
                     "erro_theta_fixo_05": (float(np.nanmin(rodadas[0.5]["erro"])) if espec == "P3" else np.nan),
                     "pico_observado": pico_obs, "pico_simulado": pico_sim,
                     "reproduz_pico": (bool(pico_sim >= FRACAO_PICO * pico_obs) if np.isfinite(pico_obs) else None)}
            linhas.append(linha)
    return resultados, pd.DataFrame(linhas)


def especificacao_referencia(val_df: pd.DataFrame) -> str:
    """Menor erro combinado (soma dos erros mínimos nos dois episódios)."""
    return val_df.groupby("especificacao")["erro_normalizado_min"].sum().idxmin()


# ---------------------------------------------------------------- episódio recessivo 2015–2016

EPISODIO_RECESSAO = ("2014-12-31", "2016-12-31")  # t0 = 2014T4; simula 2015T1–2016T4
PIB_OFICIAL = {2015: -3.5, 2016: -3.3}            # IBGE, variação anual do PIB real
NAO_MODELADOS = ("queda dos preços das commodities (IC-Br em US$ −40% de meados de 2014 ao início de 2016)",
                 "crise política e processo de impeachment (2015–2016)",
                 "Operação Lava Jato: paralisação de investimentos da Petrobras e das construtoras",
                 "realinhamento de preços administrados (energia e combustíveis) em 2015",
                 "aperto de crédito dos bancos públicos")


def _anual(h: np.ndarray, h_antes: np.ndarray, g_pot: float) -> dict:
    """Crescimento anual ≈ g_pot + média do hiato no ano − média no ano anterior (log do PIB = potencial + hiato).
    h: hiato simulado nos trimestres 1–8 (2015T1–2016T4); h_antes: hiato observado de 2014T1–T4."""
    m14, m15, m16 = h_antes.mean(), h[..., 0:4].mean(axis=-1), h[..., 4:8].mean(axis=-1)
    return {2015: g_pot + m15 - m14, 2016: g_pot + m16 - m15}


def validar_recessao_2015(p: dict, especs=("P1", "P2", "P3"), m_fiscal: float = 0.5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """O modelo reproduz a recessão de 2015–2016 com Selic, primário e câmbio observados?

    O impulso fiscal vem do primário estrutural observado (primário − rec_base·ε_rec·hiato observado), aplicado em
    nível com multiplicador m_fiscal (o efetivo do pacote atual é ≈ 0,5); as regras fiscais do modelo, calibradas
    para 2026, não entram. λ é escolhido pelo ajuste de inflação e NTN-B 10 anos, como nos demais episódios.
    Devolve (crescimento simulado × observado; decomposição por canal no λ de melhor ajuste)."""
    painel = pd.read_csv(PROC / "trimestral.csv", index_col=0, parse_dates=True)
    arq = RAW / "focus_anuais_historico.csv"
    anuais = pd.read_csv(arq, parse_dates=["Data"]) if arq.exists() else None
    inicio, fim = (pd.Timestamp(x) for x in EPISODIO_RECESSAO)
    janela = painel.loc[inicio:fim]
    T = len(janela) - 1
    h_antes = painel.loc["2014-01-01":"2014-12-31", "h"].to_numpy()
    obs_nivel = painel["pib_real"]
    g_obs = {a: 100 * (obs_nivel.loc[str(a)].mean() / obs_nivel.loc[str(a - 1)].mean() - 1) for a in (2015, 2016)}
    linhas, decomp = [], []
    for espec in especs:
        q = copy.deepcopy(p)
        q.update({"especificacao": espec, "fiscal_nivel": True, "rho_f": None, "gamma_ciclo": 0.0})
        q["ini"] = _ini_historico(painel, inicio, p["ini"])
        q.pop("g_potencial", None)
        q = modelo.preparar(q)
        g_pot = q["ini"]["g_potencial"]
        i_hist = janela["meta_selic"].to_numpy()
        s_hist = janela["s_spc"].to_numpy()
        h_hist = janela["h"].to_numpy()
        s_estr = s_hist - q["rec_base"] * q["eps_rec"] * h_hist / 100
        ajuste = s_estr - s_estr[0]  # > 0 = contração em relação a 2014T4
        zeros = np.zeros(T + 1)
        cen = {"chave": "hist", "nome": "histórico", "cor": "#333333", "regra": "exogena", "delta": zeros,
               "i_exog": i_hist, "medidas_receita": zeros, "medidas_despesa": zeros, "venda_reservas": zeros,
               "capex_ppp": zeros, "T": T,
               "itens": [{"nome": "primário estrutural observado", "canal": "governo", "multiplicador": m_fiscal,
                          "trilha": ajuste}]}
        s_estab_fim = modelo.s_estabilizador(janela["selic"].iloc[-4:].mean(), janela["gamma"].iloc[-1],
                                             janela["dbgg"].iloc[-1])
        F = q["p1"] * (janela["dbgg"].iloc[-1] - q["d_ref"]) + modelo.p2_efetivo(q) * (s_estab_fim - s_hist[-1])
        plano = {"F": float(F), "i": np.concatenate([i_hist, np.full(8, i_hist[-1])]),
                 "s_mat": plano_s_focus(anuais, janela.index, s_hist, int(q["H_vp"]))}
        # o impulso total = o do item: o restante do termo fiscal (a3 × resto) fica zerado
        override = {"i": i_hist, "s": s_hist, "de": janela["de"].to_numpy(),
                    "impulso": np.concatenate([[0.0], -np.diff(ajuste)])}
        guardar = ("pi", "r_long", "h") + modelo.DEMANDA
        thetas = GRADE_THETA if espec == "P3" else (None,)
        melhor = None
        for th in thetas:
            qq = q if th is None else modelo.preparar({**q, "theta": th})
            tr = modelo.simular(qq, cen, GRADE_LAMBDA, plano=plano, override=override, guardar=guardar)
            dados = {"pi": janela["ipca12"].to_numpy(), "r_long": janela["ntnb10"].to_numpy()}
            erro = _erro(tr, dados)
            if melhor is None or np.nanmin(erro) < np.nanmin(melhor[1]):
                melhor = (th, erro, tr, qq)
        th, erro, tr, qq = melhor
        k = int(np.nanargmin(erro))
        an = _anual(tr["h"][:, 1:], h_antes, g_pot)
        for lam_rot, j in (("melhor ajuste", k), ("λ = 0,1", 2), ("λ = 0,5", 10), ("λ = 0,9", 18)):
            linhas.append({"especificacao": espec, "lambda": float(GRADE_LAMBDA[j]), "caso": lam_rot, "theta": th,
                           "g_potencial": g_pot, "pib_2015_sim": float(an[2015][j]), "pib_2016_sim": float(an[2016][j]),
                           "pib_2015_obs": g_obs[2015], "pib_2016_obs": g_obs[2016],
                           "pib_2015_oficial": PIB_OFICIAL[2015], "pib_2016_oficial": PIB_OFICIAL[2016],
                           "hiato_fim_sim": float(tr["h"][j, -1]), "hiato_fim_obs": float(h_hist[-1]),
                           "erro_normalizado": float(erro[j])})
        # decomposição no λ de melhor ajuste: cada termo acumulado com a persistência a1
        a1 = qq["a1"]
        termos = {"fiscal (primário estrutural)": tr["dem_item0"][k],
                  "juro real longo": tr["dem_juro"][k], "câmbio real": tr["dem_cambio"][k],
                  "fiscal fora do item": tr["dem_fiscal_resto"][k], "CAPEX": tr["dem_capex"][k]}
        contrib = {}
        for nome, x in termos.items():
            c = np.zeros(T + 1)
            for t in range(1, T + 1):
                c[t] = a1 * c[t - 1] + np.nan_to_num(x[t])
            contrib[nome] = c[1:]
        inicial = qq["ini"]["h0"] * a1 ** np.arange(1, T + 1)
        contrib["hiato inicial (persistência)"] = inicial
        for nome, c in contrib.items():
            # contribuição ao crescimento anual: Δ da média anual do componente (2014 = 0, exceto o hiato inicial,
            # cuja média de 2014 é a do hiato observado)
            base14 = h_antes.mean() if nome.startswith("hiato inicial") else 0.0
            decomp.append({"especificacao": espec, "lambda": float(GRADE_LAMBDA[k]), "canal": nome,
                           "pib_2015": float(c[0:4].mean() - base14), "pib_2016": float(c[4:8].mean() - c[0:4].mean())})
        decomp.append({"especificacao": espec, "lambda": float(GRADE_LAMBDA[k]), "canal": "crescimento potencial",
                       "pib_2015": g_pot, "pib_2016": g_pot})
    return pd.DataFrame(linhas), pd.DataFrame(decomp)
