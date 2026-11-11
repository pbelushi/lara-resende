"""
Modelo semiestrutural mensal da Argentina (dez/2023 – dez/2025).

Blocos: câmbio/brecha → inflação (inércia, expectativas, repasse, emissão)
        → salários e renda → pobreza; fiscal por categoria de gasto com
        multiplicadores próprios; setor externo e reservas; risco país
        endógeno; Congresso estocástico para medidas que exigem lei;
        popularidade alimentando o Congresso.

Tudo é vetorizado sobre N simulações (Monte Carlo). Choques e desfechos
legislativos são as fontes de incerteza.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.special import expit
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
CATS = ["pensions", "targeted_transfers", "subsidies", "capex",
        "provinces", "payroll_operating", "other"]


# --------------------------------------------------------------------- inputs
def load_params(path: Path | str = ROOT / "config" / "params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_actuals() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "actuals_monthly.csv")


@dataclass(frozen=True)
class Scenario:
    """Uma combinação de medidas.

    dev    – desvalorização sustentada: crawl indexado à inflação (câmbio real
             competitivo) em vez do crawl fixo de 2% usado como âncora nominal.
    rate   – juro real ex-ante positivo desde o início (vs. repressão financeira
             efetiva: juro abaixo da inflação, "licuadora").
    fiscal – 'motosserra' (composição efetiva), 'baixo_multiplicador' (mesmo
             tamanho, concentrado em gastos de baixo multiplicador) ou 'gradual'.
    priv   – envio ao Congresso de programa amplo de privatizações/venda de ativos.
    swap   – troca de dívida externa por interna (canje + refinanciamento em pesos).
    validation – força os desfechos observados (Lei Bases jun/24, escopo 20%).
    """
    dev: bool = False
    rate: bool = False
    fiscal: str = "motosserra"
    priv: bool = True
    swap: bool = False
    validation: bool = False
    name: str = field(default="")

    def label(self) -> str:
        if self.name:
            return self.name
        bits = [f"DEV{'+' if self.dev else '-'}", f"JUROS{'+' if self.rate else '-'}",
                {"motosserra": "MOTO", "baixo_multiplicador": "BMULT",
                 "gradual": "GRAD"}[self.fiscal],
                f"PRIV{'+' if self.priv else '-'}", f"SWAP{'+' if self.swap else '-'}"]
        return " ".join(bits)


ACTUAL = Scenario(dev=False, rate=False, fiscal="motosserra", priv=True, swap=False,
                  validation=True, name="Milei efetivo (validação)")


# --------------------------------------------------------------------- helpers
def _ramp(t: int, mode: str, p: dict) -> float:
    """Fração do corte fiscal já implementada no mês t."""
    if mode == "gradual":
        return min(1.0, (t + 1) / p["fiscal"]["gradual_months"])
    if t <= 6:
        return 0.7 * (t + 1) / 7
    return min(1.0, 0.7 + 0.3 * (t - 6) / 6)


def _pension_ramp(t: int, mode: str, p: dict) -> float:
    """Aposentadorias caem mais rápido via liquefação inflacionária no 1º tri."""
    if mode == "gradual":
        return _ramp(t, mode, p)
    liq = p["income"]["pension_initial_liquefaction"]
    if t <= 3:
        return liq * (t + 1) / 4
    return min(1.0, liq + (1 - liq) * (t - 3) / 9)


def _actual_rate_tna(t: int, act: pd.DataFrame) -> float:
    row = act.loc[act.t == min(t, 24), "policy_rate_tna_pct"]
    return float(row.iloc[0]) / 100.0


def _crawl_actual(t: int, p: dict) -> float:
    c = p["exchange"]["crawl_actual"]
    if t >= 16:
        return c[16]
    return c.get(t, c["default"])


# --------------------------------------------------------------------- core
def simulate(p: dict, sc: Scenario, n: int | None = None, seed: int | None = None,
             stochastic: bool = True) -> dict[str, np.ndarray]:
    n = n or p["n_sims"]
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    T = p["horizon_months"]
    act = load_actuals()
    I0 = p["init"]
    inf, cr, ac, ex, xr = p["inflation"], p["credibility"], p["activity"], p["external"], p["exchange"]
    crk, fi, pv, ds, lg = p["country_risk"], p["fiscal"], p["privatization"], p["debt_swap"], p["legislative"]
    pop_p, inc, pov = p["popularity"], p["income"], p["poverty"]
    sd = (lambda x: x) if stochastic else (lambda x: 0.0)

    def Z():
        return rng.standard_normal(n)

    # ---------- states (vetores n)
    pi_prev = np.full(n, I0["pi"])
    pie_prev = np.full(n, I0["pi"])
    y = np.full(n, I0["y_gap"])
    lnE = np.zeros(n)
    lnP = np.zeros(n)
    q = np.zeros(n)
    b = np.full(n, I0["brecha_log"])
    R = np.full(n, I0["reserves"])
    lembi = np.full(n, np.log(I0["embi"]))
    pop = np.full(n, I0["popularity"])
    base = np.full(n, I0["base_gdp"])
    ql = np.full(n, I0["ql_gdp"])
    dpeso = np.full(n, I0["d_peso_gdp"])
    # --- adesão do mercado à troca de dívida (λ). Valor de referência lambda_ref reproduz a calibração.
    # λ_fiscal: adesão ao canje, prêmio da dívida trocada, risco de rolagem no EMBI, dolarização na rolagem.
    # λ_π: quanto a dívida trocada desancora as expectativas (tentação de inflacioná-la).
    l0 = ds.get("lambda_ref", 0.75)
    lf = ds.get("lambda_fiscal", l0)
    lp = ds.get("lambda_pi", l0)
    sw_adh = float(np.clip(ds.get("adh_floor", 0.25) + (1 - ds.get("adh_floor", 0.25)) * lf / l0, 0, 1))
    sw_prem = ds.get("prem_slope", 0.0) * (l0 - lf)
    sw_e = max(-crk["e_debt_peso"], ds.get("e_slope", 0.0) * (l0 - lf))
    sw_roll = ds.get("roll_max", 0.0) * max(0.0, (l0 - lf) / l0)
    sw_c = max(-1.0, ds.get("c_slope", 0.0) * (l0 - lp)) * cr["c_peso_debt"]
    swap_stock = np.zeros(n)
    # --- credibilidade das âncoras (λ). lambda_ref reproduz a calibração.
    # λ_câmbio: crença no caminho anunciado do câmbio (crawl/banda; regra SCRER se DEV+) →
    #   peso do crawl nas expectativas, brecha, fuga de capitais e repasse do salto.
    # λ_juros: crença na meta do BC (só JUROS+) → peso da meta nas expectativas, bônus de
    #   credibilidade do juro real positivo e prêmio no juro nominal necessário.
    lr0 = cr.get("lambda_ref", 0.75)
    dx = lr0 - cr.get("lambda_fx", lr0)
    di = lr0 - cr.get("lambda_rate", lr0)
    dfx_usd = np.full(n, I0["d_fx_gdp"] * ex["gdp_usd_bn"])
    lnW = np.zeros(n)
    lnYpot = 0.0
    pb_prev = np.full(n, fi["revenue_base"] - sum(fi["spending_2023"].values()))
    lnrw_prev = np.zeros(n)
    soe_saved = np.zeros(n)
    leg = np.zeros(n)
    y0 = I0["y_gap"]
    ycyc = np.full(n, I0["y_gap"])
    F = np.zeros(n)
    rate_drag = np.zeros(n)
    crowd = np.zeros(n)
    ql_fiscalized = np.zeros(n)
    cumreg = np.zeros(n)          # contribuição acumulada das tarifas ao log do IPC
    q_line = np.zeros(n)          # câmbio real visto pela cesta básica (repasse defasado)

    # brecha: calibra o alvo para reproduzir a brecha inicial
    b_const = I0["brecha_log"] + xr["brecha_res"] * I0["reserves"]

    # ---------- fiscal composition
    cuts_full = fi["modes"][sc.fiscal]
    s23 = fi["spending_2023"]
    tt_boost = 0.0 if sc.fiscal == "gradual" else fi["targeted_transfer_boost_actual"]
    prov_cut_pp = cuts_full["provinces"] * 100

    # ---------- legislative setup
    bills = [b_ for b_, on in (("privatization", sc.priv), ("debt_swap", sc.swap)) if on]
    nb = len(bills)
    approved = {b_: np.zeros(n, bool) for b_ in bills}
    t_appr = {b_: np.full(n, -1) for b_ in bills}
    scope = {b_: np.zeros(n) for b_ in bills}
    failed_once = {b_: np.zeros(n, bool) for b_ in bills}
    blocked_until = {b_: np.zeros(n, int) for b_ in bills}
    if sc.validation and sc.priv:
        fa = pv["force_actual"]

    out = {k: np.zeros((n, T)) for k in [
        "pi", "pie", "cred", "cred_x", "cred_i", "i", "r_ann", "q", "brecha", "reserves", "embi", "y",
        "gdp_idx", "rw", "inc_mean", "inc_poor", "poverty", "pb", "overall",
        "dfx_gdp", "dpeso", "pop", "leg", "priv_proceeds", "mu", "tb", "lnz"]}
    out["priv_t"] = np.full(n, -1)
    out["priv_scope"] = np.zeros(n)
    out["swap_auth_t"] = np.full(n, -1)

    gdp_idx_prev = np.full(n, I0["gdp_index"])
    a0_pov = norm.ppf(0.417)
    pt_w = inf["passthrough_weights"]
    pt_hist = [np.zeros(n) for _ in pt_w]       # (Δe_eff − πe) defasados
    pi_lag2 = np.full(n, I0["pi"])

    for t in range(T):
        month = (t + 11) % 12 + 1          # t=0 → dez
        ramp = _ramp(t, sc.fiscal, p)
        ramp_prev = _ramp(t - 1, sc.fiscal, p) if t > 0 else 0.0
        pramp = _pension_ramp(t, sc.fiscal, p)
        pramp_prev = _pension_ramp(t - 1, sc.fiscal, p) if t > 0 else 0.0
        cut = {k: cuts_full[k] * (pramp if k == "pensions" else ramp) for k in CATS}
        dcut = {k: cuts_full[k] * ((pramp - pramp_prev) if k == "pensions" else (ramp - ramp_prev))
                for k in CATS}

        # ---------- câmbio oficial
        if t == 0:
            de = xr["jump_log"]
        elif sc.dev:
            # câmbio real competitivo e estável: indexação parcial + correção à meta de q
            c_rule = (xr["screr_index"] * pi_prev + (1 - xr["screr_index"]) * xr["screr_floor"]
                      + xr["screr_correction"] * (xr["screr_target_q"] - q))
            de = np.log1p(np.maximum(c_rule, 0.0))
        else:
            de = np.log1p(_crawl_actual(t, p)) * np.ones(n)
            # abandono forçado da âncora: se o câmbio real se valoriza além de q_break (crawl perdeu
            # crédito e a inflação o ultrapassou), o BC desvaloriza para fechar parte do desalinhamento.
            # Não dispara no caminho calibrado (mínimo de q ≈ −0,09 no 1º percentil dos 48 cenários).
            if t > 0:
                de = de + xr.get("break_adj", 0.0) * np.maximum(0, xr.get("q_break", -9.0) - q)
        de = de * np.ones(n)

        # ---------- credibilidade e expectativas
        L = (cr["c0"] + cr["c_pb"] * pb_prev * 100 + cr["c_res"] * R / 10
             + cr["c_rate"] * float(sc.rate) * (1 - di / lr0)
             - cr["c_embi"] * (lembi - np.log(1000))
             - cr["c_peso_debt"] * np.maximum(0, dpeso - I0["d_peso_gdp"])
             - sw_c * swap_stock)
        cred = expit(L)
        cred_x = expit(L - cr.get("k_fx", 0.0) * dx)      # crença no câmbio anunciado
        cred_i = expit(L - cr.get("k_rate", 0.0) * di)    # crença na meta do BC
        anchor_fx = np.expm1(de) if t > 0 else pi_prev   # o crawl anunciado é a âncora
        if sc.rate:
            target = max(cr["target_floor"], cr["target_path_start"] * cr["target_decay"] ** t)
            pie = pi_prev + 0.5 * cred_x * (anchor_fx - pi_prev) + 0.5 * cred_i * (target - pi_prev)
        else:
            pie = pi_prev + cred_x * (anchor_fx - pi_prev)
        if t in inf.get("pie_override", {}):         # diagnóstico: expectativas exógenas (ex.: REM)
            pie = np.full(n, inf["pie_override"][t])

        # ---------- juros
        if sc.rate:
            i = pie + max(0.002, 0.008 + cr.get("rate_prem_slope", 0.0) * di)
        else:
            i = np.full(n, _actual_rate_tna(t, act) / 12)
        r = i - pie
        r_ann = 12 * r

        # ---------- fiscalização dos passivos do BCRA (comum)
        if t == fi["fiscalize_ql_month"]:
            dpeso = dpeso + ql
            ql_fiscalized = ql.copy()        # passivos já existentes: não muda o risco percebido
            ql = np.zeros(n)

        # ---------- fiscal
        spend = sum(s23[k] - cut[k] for k in CATS) - soe_saved
        pais = fi["pais_tax"] if t <= 12 else 0.0
        rev = (fi["revenue_base"] + pais + fi["revenue_gap"] * y
               + fi["olivera_tanzi"] * (I0["pi"] - pi_prev))
        pb = rev - spend
        dfx_gdp = dfx_usd / ex["gdp_usd_bn"] * np.exp(crk["debt_rer_weight"] * q)
        int_ext = fi["ext_interest"] * dfx_gdp / I0["d_fx_gdp"]
        int_dom = dpeso * (np.maximum(r_ann, 0) + fi["dom_spread_annual"]) * fi["dom_real_cost_share"]
        int_dom = int_dom + swap_stock * sw_prem          # prêmio extra (ou desconto) da dívida trocada
        overall = pb - int_ext - int_dom
        mkt = fi["market_financing"] * 1000 / np.exp(lembi)
        monetized = np.maximum(0, -overall - mkt)

        # ---------- setor externo (antes da emissão: compras do BCRA emitem)
        harvest = ex["tb_harvest_season"][month - 1]
        agri = ex["tb_agri_2024"] if t >= 4 else 0.0
        tb = (ex["tb_base"] + harvest + agri + ex["tb_rer"] * q + ex["tb_energy_trend"] * t
              - ex["tb_gap"] * y + sd(ex["sd_shock"]) * Z())
        leak = ex["cepo_leak"] * np.clip(b, 0, 1.0)
        flight = ex["flight_coef"] * np.maximum(0, ex["q_neutral"] - q) * (0.4 if t < 16 else 1.0)
        flight = flight + cr.get("flight_slope", 0.0) * dx      # dolarização por descrença no câmbio
        fx_serv = ex["fx_debt_service"].get(month, ex["fx_debt_service"]["other"])

        # troca de dívida
        swap_share = np.zeros(n)
        if sc.swap:
            auth = approved["debt_swap"]
            swap_share = np.where(auth, ds["flow_share"], ds["flow_share"] * ds["exec_only_share"])
        swapped = fx_serv * swap_share * sw_adh
        paid = fx_serv - swapped

        imf = 0.0
        if t in ex["imf_tranche"]:
            imf = np.where(pb >= ex["imf_pb_threshold"], ex["imf_tranche"][t], 0.0)

        # privatizações executadas neste mês
        proceeds = np.zeros(n)
        if sc.priv:
            ap = approved["privatization"]
            start = t_appr["privatization"] + pv["exec_lag"]
            selling = ap & (t >= start) & (t < start + pv["exec_months"])
            price = np.exp(-pv["price_embi_elast"] * np.maximum(0, lembi - np.log(600)))
            proceeds = np.where(selling, pv["full_value_usd_bn"] * scope["privatization"]
                                / pv["exec_months"] * price, 0.0)
            soe_saved = soe_saved + np.where(selling, pv["soe_transfer_savings"]
                                             * scope["privatization"] / pv["exec_months"], 0.0)

        purchases = np.maximum(0, tb - leak - flight)
        dR = tb - leak - flight - paid + imf + pv["fx_share"] * proceeds
        R = R + dR
        dfx_usd = dfx_usd - 0.6 * paid - swapped - proceeds + imf

        gdp_usd = ex["gdp_usd_bn"] * np.exp(-0.5 * q) * gdp_idx_prev / I0["gdp_index"]
        stock_swap = 0.0
        if sc.swap and t == 3:
            eff = np.where(approved["debt_swap"], 1.0, ds["exec_only_share"])
            stock_swap = ds["stock_swap_gdp"] * eff * sw_adh
            dfx_usd = dfx_usd - stock_swap * gdp_usd
        issuance = swapped / gdp_usd + stock_swap
        dpeso = dpeso + issuance
        swap_stock = swap_stock + issuance
        if sc.swap and sw_roll > 0:
            # na rolagem, parte dos detentores exige dólares (2019): sai de reservas, sai da dívida em pesos
            roll_out = swap_stock * sw_roll
            R = R - roll_out * gdp_usd
            swap_stock = swap_stock - roll_out
            dpeso = dpeso - roll_out
        # compras esterilizadas viram dívida doméstica
        purch_gdp = purchases / gdp_usd
        dpeso = dpeso + ex["sterilization"] * purch_gdp
        emit_purch = (1 - ex["sterilization"]) * purch_gdp

        # ---------- moeda
        qf = i * ql
        mu = (monetized / 12 + qf + emit_purch) / base
        excess = np.clip(mu - pie - inf["money_demand_semi"] * r, -0.10, 0.30)

        # ---------- brecha
        q_pre = q + de - pi_prev
        b_star = np.maximum(xr["brecha_floor"],
                            b_const - xr["brecha_rer"] * q_pre - xr["brecha_res"] * R
                            + 0.5 * np.maximum(excess, 0) + cr.get("brecha_slope", 0.0) * dx)
        if t >= xr["cepo_exit_month"]:
            b_star = b_star * 0.2              # unificação cambial (comum a todos)
        b_new = xr["brecha_rho"] * b + (1 - xr["brecha_rho"]) * b_star
        db = b_new - b
        b = b_new

        # ---------- inflação
        de_eff = inf["w_official"] * de + (1 - inf["w_official"]) * (de + db)
        pt_hist = [de_eff - np.log1p(pie)] + pt_hist[:-1]
        # repasse assimétrico: desvalorização acima da inflação esperada (beta_fx) vs. crawl abaixo dela,
        # que funciona como âncora (beta_fx_down); um coeficiente único ficava preso entre os dois
        beta_up = inf["beta_fx"] * max(0.0, 1 + cr.get("pt_slope", 0.0) * dx)
        passthrough = sum(w * (beta_up * np.maximum(h, 0) + inf["beta_fx_down"] * np.minimum(h, 0))
                          for w, h in zip(pt_w, pt_hist))
        reg = inf["reg_per_pp_subsidy"] * dcut["subsidies"] * 100
        cumreg = cumreg + reg
        pi = (inf["lambda_inertia"] * pi_prev + (1 - inf["lambda_inertia"]) * pie
              + passthrough
              + reg + inf["phi_money"] * excess + inf["gamma_gap"] * y
              + sd(inf["sd_shock"]) * Z())
        pi = np.maximum(pi, -0.01)

        lnE = lnE + de
        lnP = lnP + np.log1p(pi)
        q_prev = q
        q = lnE - lnP

        base = np.maximum(0.025, base * (1 + mu) / (1 + pi))
        ql = ql * (1 + i) / (1 + pi)

        # ---------- salários e renda
        omega = (inc["theta_index"] * np.log1p(pi_lag2) + (1 - inc["theta_index"]) * np.log1p(pie)
                 + inc["kappa_gap"] * y / 12
                 + inc["catchup"] * (-inc["rw_rer"] * q - lnrw_prev))   # alvo cai com câmbio real alto
        lnW = lnW + omega
        # salário real médio do mês: perda "dente de serra" entre reajustes ∝ inflação
        lnrw = lnW - lnP - inc["sawtooth"] * np.log1p(pi)
        dlnrw = lnrw - lnrw_prev

        # ---------- risco país (usa fundamentos correntes)
        dfx_gdp = dfx_usd / ex["gdp_usd_bn"] * np.exp(crk["debt_rer_weight"] * q)
        lembi_star = (crk["e0"] + crk["e_debt"] * (dfx_gdp - I0["d_fx_gdp"])
                      + crk["e_debt_peso"] * (dpeso - I0["d_peso_gdp"] - ql_fiscalized)
                      + sw_e * swap_stock
                      - crk["e_res"] * R / 10 - crk["e_pb"] * pb * 100
                      + crk["e_infl"] * 12 * np.log1p(pi) - crk["e_leg"] * leg)
        shock_ev = crk["events"].get(t, 0.0)
        vul = np.minimum(2.0, 1 + crk["event_vulnerability"] * np.maximum(0, -R))
        dl = (crk["kappa"] * (lembi_star - lembi) + shock_ev * vul
              + sd(crk["sd_shock"]) * Z())
        lembi = lembi + dl

        # ---------- atividade
        # hiato = componente cíclico + arrasto fiscal (decai devagar) + níveis
        F = ac["rho_fiscal"] * F - sum(fi["multipliers"][k] * dcut[k] for k in CATS)
        ycyc = ac["rho_y"] * ycyc + sd(ac["sd_shock"]) * Z()
        rate_drag = ac["rho_y"] * rate_drag + (1 - ac["rho_y"]) * ac["alpha_rate"] * np.clip(r_ann, 0, 0.5)
        crowd = ac["rho_y"] * crowd + ac["alpha_crowd"] * issuance
        y = (ycyc + F
             + ac["alpha_wage"] * lnrw
             + ac["alpha_rer"] * q
             - ac["alpha_conf"] * (lembi - np.log(I0["embi"]))
             - rate_drag - crowd
             - ac["alpha_high_infl"] * np.maximum(0, 12 * np.log1p(pi) - 1.0))
        lnYpot += ac["potential_growth_annual"] / 12
        lnYpot -= ac["capex_potential_drag"] * cut["capex"] / 12
        if t == 4:
            lnYpot += ac["agri_rebound"]
        gdp_idx = I0["gdp_index"] * np.exp(lnYpot + y - y0)

        # ---------- renda média e dos pobres
        emp = 1 + ac["okun"] * (y - y0)
        # até abr/24 a liquefação observada já está no corte de aposentadorias; erodimos só o excesso
        # de inflação sobre o caminho efetivo. Depois, indexação mensal com ~2 meses de defasagem.
        pi_obs = float(act.loc[act.t == t, "cpi_mom_pct"].iloc[0]) / 100
        infl_erode = np.log1p(pi) if t >= 4 else np.maximum(0, np.log1p(pi) - np.log1p(pi_obs))
        erosion = np.exp(-inc["benefit_lag"] * infl_erode)
        pen_idx = (1 - cut["pensions"] / s23["pensions"]) * erosion
        tt_idx = (1 + tt_boost * ramp - cut["targeted_transfers"] / s23["targeted_transfers"]) * erosion
        sm, sp = inc["shares_mean"], inc["shares_poor"]
        pub_cut = inc["payroll_wage_share"] * cut["payroll_operating"] / s23["payroll_operating"]
        emp = emp * (1 - inc["public_emp_share_mean"] * pub_cut)
        inc_mean = (sm["labor"] * np.exp(lnrw) * emp + sm["pensions"] * pen_idx
                    + sm["transfers"] * tt_idx + sm["other"] * gdp_idx / I0["gdp_index"])
        emp_poor = ((gdp_idx / I0["gdp_index"]) ** inc["poor_activity_elast"]
                    * (1 - inc["public_emp_share_poor"] * pub_cut))
        inc_poor = (sp["labor"] * np.exp(inc["poor_wage_elast"] * lnrw) * emp_poor
                    + sp["pensions"] * pen_idx
                    + sp["transfers"] * tt_idx)
        # linha (CBT) relativa ao IPC: alimentos reagem ao câmbio real; tarifas pesam menos na
        # cesta básica que no IPC, então o corte de subsídios sobe o IPC mais que a linha
        q_line = pov["rho_line"] * q_line + (1 - pov["rho_line"]) * q
        lnz = pov["zeta_rer"] * q_line - pov["eta_reg"] * cumreg
        poverty = norm.cdf(a0_pov + (lnz - np.log(inc_poor)) / pov["sigma"])

        # ---------- popularidade
        honey = 0.15 * np.exp(-t / 6)
        pop_star = np.clip(pop_p["p0"] + 0.1 * (1.0 - 12 * np.log1p(pi)) * 0.5
                           + pop_p["p_income"] * np.log(inc_mean) + honey, 0.15, 0.80)
        pop = pop + pop_p["speed"] * (pop_star - pop)

        # ---------- Congresso
        crisis = np.clip(12 * np.log1p(pi) / 3, 0, 1)
        for bl in bills:
            if sc.validation and bl == "privatization":
                hit = (~approved[bl]) & (t == fa["month"])
                approved[bl] |= hit
                t_appr[bl] = np.where(hit, t, t_appr[bl])
                scope[bl] = np.where(hit, fa["scope"], scope[bl])
                continue
            if t < 1:
                continue
            rad = lg["radicalness"][bl]
            h = expit(lg["h0"] + lg["h_coal"] * (lg["coalition_share"] - 0.30)
                      + lg["h_pop"] * (pop - 0.5) + lg["h_crisis"] * crisis
                      - lg["h_bundle"] * (nb - 1) - lg["h_gov"] * prov_cut_pp
                      - lg["h_rad"] * (rad - 1.0))
            pending = (~approved[bl]) & (t >= blocked_until[bl])
            event = pending & (rng.random(n) < h)
            fails = event & (~failed_once[bl]) & (rng.random(n) < lg["first_vote_fail_prob"])
            failed_once[bl] |= fails
            blocked_until[bl] = np.where(fails, t + lg["fail_delay"], blocked_until[bl])
            passed = event & ~fails
            m = expit(lg["m0"] + lg["m_coal"] * (lg["coalition_share"] - 0.30)
                      + lg["m_pop"] * (pop - 0.5) + lg["m_crisis"] * crisis
                      - lg["m_rad"] * (rad - 1.0))
            k = lg["scope_concentration"]
            s_draw = rng.beta(np.maximum(m * k, 1e-3), np.maximum((1 - m) * k, 1e-3))
            approved[bl] |= passed
            t_appr[bl] = np.where(passed, t, t_appr[bl])
            scope[bl] = np.where(passed, s_draw, scope[bl])

        leg = np.zeros(n)
        if sc.priv:
            leg += 0.7 * scope["privatization"] * approved["privatization"]
        if sc.swap:
            leg += 0.3 * approved["debt_swap"]

        # ---------- registra
        for k_, v_ in [("pi", pi), ("pie", pie), ("cred", cred), ("cred_x", cred_x), ("cred_i", cred_i), ("i", i), ("r_ann", r_ann),
                       ("q", q), ("brecha", b), ("reserves", R), ("embi", np.exp(lembi)),
                       ("y", y), ("gdp_idx", gdp_idx), ("rw", np.exp(lnrw)),
                       ("inc_mean", inc_mean), ("inc_poor", inc_poor), ("poverty", poverty),
                       ("pb", pb), ("overall", overall), ("dfx_gdp", dfx_gdp), ("dpeso", dpeso),
                       ("pop", pop), ("leg", leg), ("priv_proceeds", proceeds), ("mu", mu),
                       ("tb", tb), ("lnz", lnz)]:
            out[k_][:, t] = v_

        pi_lag2 = pi_prev
        pi_prev, pie_prev, pb_prev, lnrw_prev, gdp_idx_prev = pi, pie, pb, lnrw, gdp_idx

    if sc.priv:
        out["priv_t"] = t_appr["privatization"]
        out["priv_scope"] = scope["privatization"]
    if sc.swap:
        out["swap_auth_t"] = t_appr["debt_swap"]
    return out


# --------------------------------------------------------------------- métricas
def metrics(out: dict[str, np.ndarray]) -> pd.DataFrame:
    """Indicadores-resumo por simulação (linhas = simulações)."""
    pi = out["pi"]
    lp = np.log1p(pi)
    m = pd.DataFrame({
        "infl_2024": np.expm1(lp[:, 1:13].sum(1)) * 100,
        "infl_2025": np.expm1(lp[:, 13:25].sum(1)) * 100,
        "infl_mensal_dez25": pi[:, 24] * 100,
        "pib_2024": (out["gdp_idx"][:, 1:13].mean(1) / 100 - 1) * 100,
        "pib_2025": (out["gdp_idx"][:, 13:25].mean(1) / out["gdp_idx"][:, 1:13].mean(1) - 1) * 100,
        "pobreza_2024S1": out["poverty"][:, 1:7].mean(1) * 100,
        "pobreza_2024S2": out["poverty"][:, 7:13].mean(1) * 100,
        "pobreza_2025S1": out["poverty"][:, 13:19].mean(1) * 100,
        "pobreza_2025S2": out["poverty"][:, 19:25].mean(1) * 100,
        "renda_media_2024": out["inc_mean"][:, 1:13].mean(1) * 100,
        "renda_media_2025": out["inc_mean"][:, 13:25].mean(1) * 100,
        "renda_pobres_2025": out["inc_poor"][:, 13:25].mean(1) * 100,
        "embi_dez24": out["embi"][:, 12],
        "embi_dez25": out["embi"][:, 24],
        "embi_max": out["embi"].max(1),
        "reservas_dez25": out["reserves"][:, 24],
        "primario_2024": out["pb"][:, 1:13].mean(1) * 100,
        "divida_fx_pib_dez25": out["dfx_gdp"][:, 24] * 100,
        "divida_peso_pib_dez25": out["dpeso"][:, 24] * 100,
        "pobreza_media_24_25": out["poverty"][:, 1:25].mean(1) * 100,
        "cred_cambio_2024": out["cred_x"][:, 1:13].mean(1),
        "cred_cambio_2025": out["cred_x"][:, 13:25].mean(1),
        "cred_juros_2024": out["cred_i"][:, 1:13].mean(1),
        "cambio_real_min": out["q"][:, 1:].min(1),
        "priv_aprovada": (out["priv_t"] >= 0).astype(float),
        "priv_mes": np.where(out["priv_t"] >= 0, out["priv_t"], np.nan),
        "priv_escopo": np.where(out["priv_t"] >= 0, out["priv_scope"], np.nan),
        "priv_receita_usd": out["priv_proceeds"].sum(1),
    })
    return m
