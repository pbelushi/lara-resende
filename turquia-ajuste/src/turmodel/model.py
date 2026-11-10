"""
Modelo mensal semiestrutural da Turquia, ago/2021 (t = 0) a set/2026 (t = 61).

Terceiro caso do projeto de credibilidade (Brasil, Argentina, Turquia). Estrutura enxuta, na mesma lógica dos dois
primeiros: a credibilidade λ é a fração das expectativas que segue a âncora anunciada; o restante repete a
inflação passada. λ é revista a cada trimestre pelos resultados (regra estimada no Brasil, em unidades de
tolerância, como na v2 argentina) e pode saltar com uma troca institucional.

Blocos (taxas mensais em decimal; câmbio em log):
  expectativas   πe = λ·π* + (1 − λ)·π̄                          π̄ = média dos 3 meses anteriores; π* = âncora
  inflação       π  = b1·[(1 − θ)·π̄₁₂ + θ·π*] + (1 − b1)·πe + β±·(Δe_suav − π̄) + κ·y/1200     (π̄₁₂ = média de 12 meses;
                      β₊ para depreciação real, β₋ para apreciação real)
                      + γw·choque do salário mínimo + imposto indireto + energia + ε
  câmbio (flut.) Δe = πe − π_us + [−φ·(r − r_n)/1200 + f·(ω·max(Δe₋₁ − πe, 0) + ς·corte da taxa)]·(1 − k·KKM) − η·q + ε
                 r = juro real ex ante; f = fuga da moeda, de 0 (juro real no neutro) a 1 (10 pontos abaixo):
                 ω realimenta a depreciação do mês anterior; ς é o sinal de cada corte da taxa nominal
  câmbio (adm.)  Δe = desvalorização administrada; as reservas pagam a diferença para a flutuação
  atividade      y  = ρ·y − αr·(r − r_n)/12 + αq·q − m·Δajuste + exógeno + ε
  reservas       R  = R + a0 + a_q·q + a_r·max(r − r_n, 0)/10 − vendas + exógeno   (líquidas, ex-swaps, US$ bi)
  dívida         d  = d·[(1 − fx)(1 + i_ef/12) + fx·(1 + Δe + i_us/12)] / [(1 + π)(1 + g)] − primário/12

Política (dict `pol`): taxa nominal dada ('i') ou regra de juro real ex ante ('real': r0, r1, meses); câmbio
administrado ('crawl', NaN = flutua); ajuste fiscal ('adj' em % do PIB, 'mult', 'tax'); salário mínimo ('wage');
indexação de preços administrados à âncora ('theta'); âncora anunciada ('anchor', % a.a.); salto institucional de
λ ('jump'); depósitos protegidos KKM ('kkm').
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
T = 61                      # set/2021 … set/2026
MESES = pd.period_range("2021-08", periods=T + 1, freq="M")
PI_US = 0.003               # inflação externa mensal
I_US = 3.0                  # juro externo, % a.a.


def load_params(nome: str = "params.yaml") -> dict:
    return yaml.safe_load((ROOT / "config" / nome).read_text(encoding="utf-8"))


def dados() -> pd.DataFrame:
    d = pd.read_csv(ROOT / "data" / "mensal.csv")
    d["mes"] = pd.PeriodIndex(d["mes"], freq="M")
    return d.set_index("mes")


def idx(mes: str) -> int:
    return int((pd.Period(mes, "M") - MESES[0]).n)


def mensal(anual_pct):
    return (1 + np.asarray(anual_pct, dtype=float) / 100) ** (1 / 12) - 1


# ------------------------------------------------------------------ choques exógenos comuns a todos os cenários
def exogenos(p: dict) -> dict:
    ex = {k: np.zeros(T + 1) for k in ("energia", "politico", "fiscal", "demanda", "reservas", "administrados")}
    # choque global de energia e alimentos (invasão da Ucrânia): mar–ago/2022
    ex["energia"][idx("2022-03"):idx("2022-08") + 1] = p["exo"]["energia"]
    # terremoto de fev/2023: gasto de reconstrução (primário pior) e demanda
    ex["fiscal"][idx("2023-02"):idx("2024-06") + 1] = -p["exo"]["terremoto_fiscal"]
    # choque político de mar/2025 (prisão do prefeito de Istambul): pressão cambial em dois meses
    ex["politico"][idx("2025-03")] = p["exo"]["politico"]
    ex["politico"][idx("2025-04")] = p["exo"]["politico"] * 0.5
    # intervenção de dez/2021 (vendas diretas e indiretas do banco central para deter a corrida)
    ex["reservas"][idx("2021-12")] = -p["exo"]["intervencao_dez21"]
    # reabertura e crédito em 2021–22: demanda
    ex["demanda"][1:idx("2022-06") + 1] = p["exo"]["demanda_2021_22"]
    return ex


# ------------------------------------------------------------------ política observada
def politica_observada(p: dict) -> dict:
    d = dados().reindex(MESES)
    # sem_ruptura: no observado, o câmbio administrado foi sustentado por entradas não modeladas (swaps, depósitos
    # de bancos centrais do Golfo e da Rússia, exigência de conversão de exportadores)
    pol = {"nome": "observada", "i": d["taxa_basica"].values.astype(float), "sem_ruptura": True}
    de = np.r_[0.0, np.diff(np.log(d["usdtry"].values))]
    crawl = de.copy()
    for a, b in (("2021-09", "2021-12"), ("2023-06", "2023-07")):   # janelas de flutuação
        crawl[idx(a):idx(b) + 1] = np.nan
    pol["crawl"] = crawl
    pol["adj"] = np.zeros(T + 1)
    pol["mult"], pol["tax"] = 0.6, 0.0
    w = pd.read_csv(ROOT / "data" / "salario_minimo.csv")
    pol["wage"] = {"modo": "dado", "reajustes": {idx(m): h / 100 for m, h in zip(w["mes"], w["reajuste_pct"])}}
    pol["theta"] = np.zeros(T + 1)
    anc = np.full(T + 1, 5.0)                                       # meta oficial de 5% até a guinada
    # metas intermediárias do programa de 2023 (fim de ano): 65% (2023), 36% (2024), 24% (2025), 16% (2026)
    pts = {idx("2023-06"): 40.0, idx("2023-12"): 65.0, idx("2024-12"): 36.0, idx("2025-12"): 24.0, T: 18.0}
    ks = sorted(pts)
    anc[ks[0]:] = np.interp(np.arange(ks[0], T + 1), ks, [pts[k] for k in ks])
    pol["anchor"] = anc
    jump = np.zeros(T + 1)
    jump[idx("2023-06")] = p["cred"]["salto_2023"]
    pol["jump"] = jump
    kkm = np.zeros(T + 1)
    kkm[idx("2021-12"):idx("2023-08") + 1] = 1.0
    pol["kkm"] = kkm
    # impostos indiretos de jul/2023 (IVA de 18% para 20%, combustíveis): cerca de 1,5% do PIB
    pol["imposto_exo"] = np.zeros(T + 1)
    pol["imposto_exo"][idx("2023-07")] = p["exo"]["imposto_2023"]
    return pol


# ------------------------------------------------------------------ simulação
def simulate(p: dict, pol: dict, n: int = 1, seed: int = 7, stochastic: bool = True, base: dict | None = None) -> dict:
    """Simula n trajetórias. `base` = saída da política observada (para o primário: primário = observado + ajuste
    + cíclico em relação à atividade observada)."""
    inf, fxp, act, res, cr, fis = p["inflacao"], p["cambio"], p["atividade"], p["reservas"], p["cred"], p["fiscal"]
    ex = exogenos(p)
    d = dados()
    rng = np.random.default_rng(seed)
    sd = p["choques"]
    eps = {k: (rng.normal(0, sd[k], (n, T + 1)) if stochastic else np.zeros((n, T + 1))) for k in ("pi", "e", "y")}

    X = {k: np.full((n, T + 1), np.nan) for k in ("pi", "pie", "e", "de", "q", "y", "R", "d", "lam", "i", "r", "s",
                                                   "vendas", "w_real")}
    # histórico: 12 meses de inflação mensal até ago/2021
    hist = d.loc[:MESES[0], "cpi_mm"].values[-12:] / 100
    pi_hist = [np.full(n, v) for v in hist]
    X["pi"][:, 0] = hist[-1]
    X["e"][:, 0] = np.log(d.loc[MESES[0], "usdtry"])
    X["de"][:, 0] = 0.0
    X["q"][:, 0] = 0.0
    X["y"][:, 0] = act["y0"]
    X["R"][:, 0] = res["R0"]
    X["d"][:, 0] = fis["d0"]
    X["i"][:, 0] = d.loc[MESES[0], "taxa_basica"]
    X["w_real"][:, 0] = 0.0
    lam = np.full(n, float(cr["lambda0"])) if pol.get("lambda0") is None else np.asarray(pol["lambda0"], dtype=float).copy()
    X["lam"][:, 0] = lam
    anc_m = mensal(pol["anchor"])
    de_hist = [np.zeros(n), np.zeros(n)]
    cum_pi = np.zeros(n)        # inflação acumulada desde o último reajuste do mínimo (log)
    cum_anc = np.zeros(n)
    w_real = np.zeros(n)        # log do salário mínimo real (0 em ago/2021)
    # o mínimo de jan/2021 já foi corroído por 8 meses de inflação
    cum_pi += np.log1p(hist[-8:]).sum()
    cum_anc += np.log1p(mensal(5.0)) * 8
    w_real -= np.log1p(hist[-8:]).sum()
    w_choque = [np.zeros(n), np.zeros(n)]
    floating_break = np.zeros(n, dtype=bool)
    jan_pi, jan_anc = [], []
    adj_prev = 0.0
    pot = (1 + act["potencial"] / 100) ** (1 / 12) - 1
    ly = np.zeros((n, T + 1))
    ly[:, 0] = act["y0"] / 100
    i_prev = X["i"][:, 0].copy()
    estoque = 0.0
    X["sub"] = np.zeros((n, T + 1))

    for t in range(1, T + 1):
        pibar = np.mean(pi_hist[-3:], axis=0)
        pie = lam * anc_m[t] + (1 - lam) * pibar
        # ---- juros
        if "i" in pol:
            i = np.full(n, pol["i"][t])
        else:
            rr = pol["real"]
            frac = min(1.0, t / max(1, rr["meses"]))
            yoy_prev = (np.exp(np.sum(np.log1p(pi_hist[-12:]), axis=0)) - 1) * 100
            # juro real ex ante: trajetória anunciada + reação ao desvio da inflação em relação à âncora
            r_traj = rr["r0"] + (rr["r1"] - rr["r0"]) * frac
            # a reação não leva o juro real abaixo do neutro (nem abaixo da trajetória, se ela já for menor)
            r_alvo = np.clip(r_traj + rr.get("reacao", 0.0) * (yoy_prev - pol["anchor"][t]), min(r_traj, act["r_n"]), 30.0)
            alvo = ((1 + r_alvo / 100) * (1 + pie) ** 12 - 1) * 100
            i = np.clip(rr.get("suav", 0.5) * i_prev + (1 - rr.get("suav", 0.5)) * alvo, 1.0, 150.0)
        r = ((1 + i / 100) / (1 + pie) ** 12 - 1) * 100
        r_c = np.clip(r, -60, 40)
        q_prev, y_prev, R_prev = X["q"][:, t - 1], X["y"][:, t - 1], X["R"][:, t - 1]
        # ---- crédito direcionado: uma fração psi do gasto sensível a juros (investimento) toma crédito ao juro
        # real neutro; o Tesouro paga a diferença (equalização); uma parte `vaz` do crédito vaza para a compra de
        # dólares e enfraquece o efeito do juro sobre o câmbio
        cd_ = pol.get("credito")
        psi = float(cd_["psi"][t]) if cd_ else 0.0
        excesso = np.maximum(r_c - act["r_n"], 0.0)
        r_y = r_c - psi * excesso
        r_fx = r_c - (cd_["vaz"] * psi * excesso if cd_ else 0.0)
        if cd_:
            estoque = estoque * (1 - cd_["amort"] / 12) + psi * cd_["volume"] / 12      # % do PIB
        subsidio = estoque * excesso / 100                                              # % do PIB por ano
        # ---- câmbio
        # corrida: com juro real abaixo do neutro, a depreciação do mês anterior acima da inflação esperada
        # realimenta a dolarização (omega); o KKM contém parte da pressão
        # intensidade da fuga: 0 com juro real no neutro, 1 com juro real 10 pontos ou mais abaixo dele
        abaixo = np.clip((act["r_n"] - r_fx) / 10.0, 0.0, 1.0)
        corrida = fxp["omega"] * np.maximum(de_hist[-1] - pie, 0.0) * abaixo
        # sinal: cada ponto de corte da taxa nominal com o juro real abaixo do neutro é lido como abandono da meta
        sinal = fxp["sinal"] * np.maximum(i_prev - i, 0.0) / 100 * abaixo
        de_float = (pie - PI_US + (-fxp["phi"] * (r_fx - act["r_n"]) / 1200 + corrida + sinal) * (1 - fxp["k_kkm"] * pol["kkm"][t])
                    - fxp["eta"] * q_prev + ex["politico"][t] + eps["e"][:, t])
        crawl = pol["crawl"][t] if "crawl" in pol else np.nan
        if np.isnan(crawl):
            de, vendas = de_float, np.zeros(n)
            if pol.get("compra_reservas") is not None:
                # o banco central compra reservas para impedir apreciação além de `compra_reservas` por mês em
                # relação à trajetória da âncora (como o TCMB fez depois de 2023); comprar é sempre possível
                piso_de = anc_m[t] - PI_US - pol["compra_reservas"]
                de = np.maximum(de_float, piso_de)
                vendas = -(de - de_float) * 100 / fxp["nu"]
        else:
            de = np.where(floating_break, de_float, crawl)
            vendas = np.where(floating_break, 0.0, (de_float - crawl) * 100 / fxp["nu"])   # US$ bi por mês
        # ---- reservas
        R = R_prev + res["a0"] + res["a_q"] * q_prev * 10 + res["a_r"] * np.clip(r - act["r_n"], 0, 30) / 10 - vendas \
            + ex["reservas"][t]
        # regime administrado se rompe quando as reservas líquidas passam do piso
        rompe = (R < res["piso"]) & ~np.isnan(crawl) & (not pol.get("sem_ruptura", False))
        if rompe.any():
            floating_break |= rompe
            de = np.where(rompe, de_float, de)
            R = np.where(rompe, R_prev, R)
        de_hist.append(de)
        de_s = 0.5 * de_hist[-1] + 0.3 * de_hist[-2] + 0.2 * de_hist[-3]
        # ---- fiscal (ajuste) e imposto indireto
        adj = float(pol["adj"][t])
        dadj = adj - adj_prev
        adj_prev = adj
        imposto = inf["p_imposto"] * (pol.get("tax", 0.0) * max(dadj, 0.0) + pol.get("imposto_exo", np.zeros(T + 1))[t]) / 100
        # ---- salário mínimo
        wg = pol["wage"]
        ch = np.zeros(n)
        reaj = None
        if wg["modo"] == "dado" and t in wg["reajustes"]:
            reaj = np.full(n, np.log1p(wg["reajustes"][t]))
        elif wg["modo"] == "regra" and t in wg["meses"]:
            reaj = (1 - wg["theta_w"]) * cum_pi + wg["theta_w"] * cum_anc + wg.get("ganho", 0.0)
        if reaj is not None:
            ch = reaj - cum_pi                   # reajuste acima (+) ou abaixo (−) da inflação acumulada
            w_real = w_real + reaj
            cum_pi, cum_anc = np.zeros(n), np.zeros(n)
        w_choque.append(ch)
        w_term = inf["gamma_w"] * (0.6 * w_choque[-1] + 0.4 * w_choque[-2])
        # ---- inflação
        th = float(pol["theta"][t])
        pibar12 = np.mean(pi_hist[-12:], axis=0)        # contratos anuais (aluguéis, mensalidades, tarifas)
        inercia = inf["b1"] * ((1 - th) * pibar12 + th * anc_m[t])
        gap_fx = de_s - pibar
        repasse = np.where(gap_fx > 0, inf["beta"], inf["beta_dn"]) * gap_fx     # repasse assimétrico
        pi = (inercia + (1 - inf["b1"]) * pie + repasse + inf["kappa"] * y_prev / 1200
              + w_term + imposto + ex["energia"][t] + ex["administrados"][t] + eps["pi"][:, t])
        pi = np.clip(pi, -0.03, 0.6)
        pi_hist.append(pi)
        cum_pi = cum_pi + np.log1p(pi)
        cum_anc = cum_anc + np.log1p(anc_m[t])
        w_real = w_real - np.log1p(pi)
        # ---- atividade
        y = (act["rho"] * y_prev - act["alpha_r"] * (r_y - act["r_n"]) / 12 + act["alpha_q"] * q_prev * 100 / 12
             - pol.get("mult", 0.6) * dadj + ex["demanda"][t] + eps["y"][:, t])
        ly[:, t] = pot * t + y / 100
        q = q_prev + de - pi + PI_US
        # ---- primário e dívida
        if base is not None:
            s = base["s"][0, t] + adj + fis["ciclico"] * (y - base["y"][0, t]) \
                + fis["kkm_custo"] * (base["kkm"][t] - pol["kkm"][t])
        else:
            s = np.full(n, fis["s_obs"][str(MESES[t].year)]) + adj
        s = s - subsidio
        g_m = pot + (y - y_prev) / 100
        i_ef = fis["i_peso"] * i + (1 - fis["i_peso"]) * 15.0
        fator = ((1 - fis["fx"]) * (1 + i_ef / 1200) + fis["fx"] * (1 + de + I_US / 1200)) / ((1 + pi) * (1 + g_m))
        dd = X["d"][:, t - 1] * fator - s / 12
        # ---- credibilidade: salto institucional e revisão trimestral pelos resultados
        lam = np.clip(lam + pol["jump"][t], 0, 1)
        jan_pi.append(pi)
        jan_anc.append(anc_m[t])
        if t % 3 == 0:
            a = np.mean(jan_anc)
            tol = max(cr["tol_frac"] * a, cr["tol_min"])
            g = np.clip((tol - np.abs(np.mean(jan_pi, axis=0) - a)) / tol, cr["g_min"], 1.0)
            lam = np.clip(lam + cr["b_up"] * np.maximum(g, 0) + cr["b_dn"] * np.minimum(g, 0), 0, 1)
            jan_pi, jan_anc = [], []
        for k, v in (("pi", pi), ("pie", pie), ("e", X["e"][:, t - 1] + de), ("de", de), ("q", q), ("y", y), ("R", R),
                     ("d", dd), ("lam", lam), ("i", i), ("r", r), ("s", s), ("vendas", vendas), ("w_real", w_real)):
            X[k][:, t] = v
        X["sub"][:, t] = subsidio
        i_prev = i
    X["ly"] = ly
    X["kkm"] = np.asarray(pol["kkm"], dtype=float)
    # inflação em 12 meses (%), com o histórico
    full = np.concatenate([np.tile(hist, (n, 1)), X["pi"][:, 1:]], axis=1)
    lp = np.log1p(full)
    c = np.cumsum(lp, axis=1)
    yoy = np.exp(c[:, 12:] - c[:, :-12]) - 1
    X["yoy"] = np.concatenate([np.exp(c[:, 11:12]) - 1, yoy], axis=1) * 100       # t = 0 … T
    return X


def pib_anual(X: dict) -> dict:
    """Crescimento anual do PIB (média do ano sobre média do ano anterior), 2022–2025, em %."""
    ly = X["ly"]
    anos = np.array([m.year for m in MESES])
    out = {}
    med = {a: ly[:, anos == a].mean(axis=1) for a in (2022, 2023, 2024, 2025, 2026)}
    # 2021: só set–dez no modelo; usa a média disponível como base de 2022 (aproximação)
    med[2021] = ly[:, anos == 2021].mean(axis=1) - 0.026   # ago–dez → média do ano (PIB de 2021 crescia ~0,75% ao mês)
    for a in (2022, 2023, 2024, 2025):
        out[a] = (np.exp(med[a] - med[a - 1]) - 1) * 100
    return out
