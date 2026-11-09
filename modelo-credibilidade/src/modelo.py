"""Equações do modelo semiestrutural e simulação de um cenário.

A simulação é vetorizada: as adesões (λ_π, λ_fiscal) e os choques têm uma
dimensão de trajetórias (P,), de modo que uma única chamada roda várias adesões
e vários sorteios. Taxas em % a.a.; passo trimestral; razões em % do PIB.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from . import fiscal_valoracao, inflacao, politicas, rolagem

COMPONENTES = ("lft", "pre", "ipca", "fx")
# Guardas numéricas: evitam overflow em trajetórias que já romperam (π > pi_explosao) e serão truncadas.
GUARDAS = {"incons": 50.0, "prem": 30.0, "de": 50.0, "h": 20.0, "r_long": 40.0, "pi": 1e4}
COMP_PI = tuple(f"comp_{c}" for c in inflacao.COMPONENTES_PI)
VARIAVEIS = (
    "h", "g", "pi", "pi_e", "i", "i_taylor", "r_long", "prem", "de", "E", "R", "venda",
    "s", "s_estab", "incons", "d_gross", "d_net", "i_ef", "gamma", "Y",
    "w_lft", "w_pre", "w_ipca", "w_fx",
    "c_juros", "c_cresc", "c_prim", "c_res",
    "tp", "pi_fiscal", "vp", "lacuna", "fracao", "migracao", "r_real_lft",
    "alongado", "w_lft_meta", "lft_tesouro", "duracao", "erosao_total", "erosao_na", "de_tend",
) + COMP_PI
# decomposição da demanda (termos do trimestre na equação do hiato, antes da persistência a1):
# juro real longo, CAPEX, câmbio real, choque, fiscal fora do pacote e cada item do pacote (até MAX_ITENS)
MAX_ITENS = 10
DEMANDA = ("dem_juro", "dem_capex", "dem_cambio", "dem_choque", "dem_fiscal_resto") + tuple(
    f"dem_item{k}" for k in range(MAX_ITENS))
VARIAVEIS = VARIAVEIS + DEMANDA

# Parâmetros introduzidos na v2; preenchem calibrações antigas que não os têm.
PADROES_V2 = {
    "especificacao": "P1", "peso_fiscal_expect": 1.0, "b2_p2": 0.025, "b2_p3": 0.025, "theta": 0.5, "phi": 0.0, "delta_min": 0.5, "escala_vt": 1.0,
    "p2_p3": 0.15, "H_vp": 40, "dur_fx": 5.0, "r_long_neutro": 5.5, "omega": 0.0, "tau_tp": 6.0,
    "rolagem": True, "r_min_rolagem": 1.0, "banda_rolagem": 2.0, "monetizacao": False, "psi_monet": 1.0,
    "alongamento": False, "w_lft_alvo": 0.40, "T_along": 20, "s_ipca": 0.7,
    "prazo_lft_meses_padrao": 36.0, "pi_explosao": 50.0,
    # tendência da depreciação nominal (% a.a.; "pdj" = paridade descoberta: Selic − juro externo − prêmio)
    "de_tendencia": 0.0,
    # canal reservas → prêmio: κ_R × max(0, R_adequado − R)/R_adequado (p.p.); R_adequado None = R_min
    "kappa_R": 0.0, "R_adequado": None,
    # piso da defesa do câmbio na parada súbita (None = R_min); a venda programada respeita sempre R_min
    "R_min_defesa": None,
    # dependência do ciclo dos multiplicadores por item: m × (1 + γ · max(0, −hiato do trimestre anterior))
    "gamma_ciclo": 0.0,
    # efeito fiscal em nível dos itens do pacote: m · (medida_t − ρ_f · medida_{t−1}) no lugar de m · (−Δmedida);
    # rho_f None = a1, que torna o efeito direto sobre o hiato igual a m × medida em todo trimestre
    "fiscal_nivel": False, "rho_f": None,
}


# ---------------------------------------------------------------- calibração

def carregar_calibracao(caminho: str | Path, especificacao: str | None = None) -> dict:
    """Parâmetros efetivos: padrões do YAML, sobrescritos pelas estimativas aceitas, mais valores iniciais."""
    cfg = yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))
    if "iniciais" not in cfg:
        raise RuntimeError("calibracao.yaml sem bloco AUTO: rode `python run.py --atualizar-dados`")
    p = {**PADROES_V2, **cfg["parametros"]}
    fontes = {k: "padrão" for k in p}
    if cfg["estimacao"].get("usar_estimados"):
        for k, est in (cfg.get("estimados") or {}).items():
            if est.get("aceito"):
                p[k] = est["estimado"]
                fontes[k] = "estimado (OLS)"
    if especificacao:
        p["especificacao"] = especificacao
    p["fontes"] = fontes
    p["ini"] = cfg["iniciais"]
    p["criterios"] = cfg["criterios"]
    p["choques"] = cfg.get("choques")
    return preparar(p)


def p2_efetivo(p: dict) -> float:
    """Em P3 a lacuna fiscal já gera inflação: o prêmio usa p2 reduzido para não contar duas vezes."""
    return p["p2_p3"] if p["especificacao"] == "P3" else p["p2"]


def _taxas_componentes(i, i_pre_est, r_long_est, pi, i_ext, de_trim):
    de_anual = ((1 + de_trim / 100) ** 4 - 1) * 100
    return {
        "lft": i,
        "pre": i_pre_est,
        "ipca": ((1 + r_long_est / 100) * (1 + pi / 100) - 1) * 100,
        "fx": ((1 + i_ext / 100) * (1 + de_anual / 100) - 1) * 100,
    }


def s_estabilizador(i_ef, gamma, d):
    """Primário (% PIB) que estabiliza a dívida: ((1+i)/(1+γ) - 1) d."""
    return ((1 + i_ef / 100) / (1 + gamma / 100) - 1) * d


def term_premium(p: dict, t):
    """tp[t] = tp_lp + (tp_0 − tp_lp)·exp(−t/τ); sem τ (v1), constante em tp_0."""
    if not p.get("tau_tp"):
        return p["tp0"] + 0 * np.asarray(t, dtype=float)
    return p["tp_lp"] + (p["tp0"] - p["tp_lp"]) * np.exp(-np.asarray(t, dtype=float) / p["tau_tp"])


def preparar(p: dict) -> dict:
    """Constantes derivadas das condições iniciais (prêmio inicial, term premium, base fiscal)."""
    for k, v in PADROES_V2.items():
        p.setdefault(k, v)
    ini = p["ini"]
    faltando = [k for k, v in ini.items() if v is None]
    if faltando:
        raise RuntimeError(f"valores iniciais ausentes: {faltando}")
    w = np.array([ini["w_lft"], ini["w_pre"], ini["w_ipca"], ini["w_fx"]])
    p["w0"] = w / w.sum()
    p["w_oma0"] = ini.get("w_oma", 0.0) / w.sum()
    taxas = _taxas_componentes(ini["i0"], ini["i_pre_estoque0"], ini["r_long_estoque0"],
                               ini["pi0"], p["i_ext"], 0.0)
    p["i_ef0"] = float(sum(p["w0"][k] * taxas[c] for k, c in enumerate(COMPONENTES)))
    p["s_estab0"] = float(s_estabilizador(p["i_ef0"], ini["gamma0"], ini["d_gross0"]))
    F0 = p["p1"] * (ini["d_gross0"] - p["d_ref"]) + p2_efetivo(p) * (p["s_estab0"] - ini["s0"])
    # Canais do prêmio (v2.1): ω na Taylor, (1 − ω) no juro longo; na v1 o prêmio inteiro entrava nos dois.
    legado = bool(p.get("_legado_v1"))
    p["omega_ef"] = 1.0 if legado else p["omega"]
    p["peso_prem_longo"] = 1.0 if legado else 1 - p["omega"]
    p["nivel_prem_longo"] = p["p0"] if legado else 0.0
    p["prem0"] = max(p["prem_min"], p["p0"] + F0)
    # Juro neutro (v2.1): o juro real longo neutro é calibrado diretamente e o term premium de longo prazo
    # sai dele. p0 não entra no nível: o risco-país médio já está nos dois juros neutros.
    p["tp_lp"] = p["r_long_neutro"] - p["r_neutro_base"]
    # Term premium inicial: fecha a identidade de r_long no t0 com a Selic esperada pelo Focus.
    p["tp0"] = (ini["r_long0"] - (np.mean(ini["selic_focus_8t"]) - ini["pi_e0"])
                - p["peso_prem_longo"] * (p["prem0"] - p["p0"]) - p["nivel_prem_longo"])
    p["term_premium"] = p["tp0"]
    if p.get("_legado_v1"):
        # equações da v1 (só para o teste de regressão): r_long neutro = r_neutro + tp_0 + p0
        p["r_long_neutro"] = p["r_neutro_base"] + p["tp0"] + p["p0"]
    # Prazos (giro da LFT na rolagem; durações em anos para P3)
    p["giro_lft"] = 3 / ini.get("prazo_lft_meses", p["prazo_lft_meses_padrao"])
    p["dur_pre"] = ini.get("dur_pre_anos") or ini["prazo_pre_meses"] / 12
    p["dur_ipca"] = ini.get("dur_ipca_anos") or 0.7 * ini["prazo_ipca_meses"] / 12
    # Bloco fiscal do governo central (RTN), ajustado para bater com o primário do BCB.
    desp = {k: ini[f"rtn_{k}"] for k in ("prev", "pessoal", "outras_obrig", "fluxo", "disc")}
    fator = ini["rtn_desp_total"] / sum(desp.values())
    p["desp0"] = {k: v * fator for k, v in desp.items()}
    desp_total = sum(p["desp0"].values())
    rec_obs = ini["s_gc0"] + desp_total
    p["rec_base"] = rec_obs / (1 + p["eps_rec"] * ini["h0"] / 100)
    p["share_fluxo"] = p["desp0"]["fluxo"] / rec_obs
    p["limite0"] = desp_total
    p["s_outros"] = ini["s0"] - ini["s_gc0"]
    return p


def matriz_plano_s(s_path: np.ndarray, H: int) -> np.ndarray:
    """(T+1, H): primário anunciado para t+1..t+H visto de cada t, estendido com o último valor."""
    T = len(s_path) - 1
    ext = np.concatenate([s_path, np.full(H, s_path[-1])])
    return np.stack([ext[t + 1:t + 1 + H] for t in range(T + 1)])


# ---------------------------------------------------------------- simulação

def simular(p: dict, cen: dict, lam_pi, lam_fiscal=None, choques: np.ndarray | None = None,
            plano: dict | None = None, override: dict | None = None,
            guardar: tuple[str, ...] = VARIAVEIS) -> dict:
    """Simula o cenário `cen` para vetores de adesão λ_π e λ_fiscal (P,). λ_fiscal=None usa a diagonal.

    choques: (P, T, 4) com colunas (ε_h, ε_π, ε_e, ε_prem); None = determinístico.
    plano: {'F': fundamentos anunciados, 'i': Selic anunciada (T+9,), 's_mat': primário anunciado (T+1, H)}.
    override: trilhas históricas {'i', 's', 'de'} (T+1,) para validação.
    Trajetórias com π acima de `pi_explosao` são encerradas: valores posteriores à ruptura viram NaN e o
    trimestre de ruptura sai em 'ruptura' (−1 = sem ruptura).
    """
    ini = p["ini"]
    T = cen["T"]
    espec = p["especificacao"]
    lam_pi = np.atleast_1d(np.asarray(lam_pi, dtype=float))
    if lam_fiscal is None:
        lam_f = lam_pi
    else:
        lam_f = np.broadcast_to(np.asarray(lam_fiscal, dtype=float), lam_pi.shape)
    P = lam_pi.size
    # λ endógeno (opcional): revisão anual pela regra p["dinamica_lambda"] (ver atualizar_lambda)
    din = p.get("dinamica_lambda")
    if din:
        lam_pi = lam_pi.astype(float).copy()
        lam_f = np.array(lam_f, dtype=float, copy=True)
        LAM = {"lam_pi": np.full((P, T + 1), np.nan), "lam_f": np.full((P, T + 1), np.nan)}
        LAM["lam_pi"][:, 0], LAM["lam_f"][:, 0] = lam_pi, lam_f
        buf_s, buf_s_plano, buf_pi = [], [], []
    if choques is None:
        choques = np.zeros((P, T, 4))
    override = override or {}
    H = int(p["H_vp"])
    if plano is None:
        plano = {"F": p["prem0"] - p["p0"], "i": np.full(T + 9, ini["i0"])}
    if "s_mat" not in plano:
        plano = {**plano, "s_mat": np.full((T + 1, H), ini["s0"])}
    i_anun = plano["i"]
    media_anun = np.array([i_anun[t:t + 8].mean() for t in range(T + 1)])
    tp = term_premium(p, np.arange(T + 1))
    p2 = p2_efetivo(p)
    G = GUARDAS
    g_pot = p.get("g_potencial") or ini["g_potencial"]
    zeros_T = np.zeros(T + 1)
    choque_de, choque_prem, defesa = (cen.get(k, zeros_T) for k in ("choque_de", "choque_prem", "defesa"))

    X = {v: np.full((P, T + 1), np.nan) for v in VARIAVEIS}
    um = np.ones(P)
    iniciais = {
        "h": ini["h0"], "g": ini["g0"], "pi": ini["pi0"], "pi_e": ini["pi_e0"], "i": ini["i0"],
        "i_taylor": ini["i0"], "r_long": ini["r_long0"], "prem": p["prem0"], "de": ini["de_ult4"][-1],
        "E": ini["E0"], "R": ini["R0"], "venda": 0.0, "s": ini["s0"], "s_estab": p["s_estab0"], "incons": 0.0,
        "d_gross": ini["d_gross0"], "d_net": ini["d_net0"], "i_ef": p["i_ef0"], "gamma": ini["gamma0"],
        "Y": ini["Y0"], "c_juros": 0.0, "c_cresc": 0.0, "c_prim": 0.0, "c_res": 0.0, "tp": tp[0],
        "pi_fiscal": 0.0, "migracao": 0.0, "r_real_lft": ini["i0"] - ini["pi_e0"],
        "alongado": 0.0, "w_lft_meta": p["w0"][0], "lft_tesouro": ini["d_gross0"] * (p["w0"][0] - p["w_oma0"]),
        "duracao": fiscal_valoracao.duracao(*p["w0"], p["dur_pre"], p["dur_ipca"], p["dur_fx"]),
        "erosao_total": 0.0, "erosao_na": 0.0,
    }
    for v, x in iniciais.items():
        X[v][:, 0] = x
    for k, c in enumerate(COMPONENTES):
        X[f"w_{c}"][:, 0] = p["w0"][k]

    d_k = {c: ini["d_gross0"] * p["w0"][k] * um for k, c in enumerate(COMPONENTES)}
    d_oma = ini["d_gross0"] * p["w_oma0"] * um
    w_emissao = dict(zip(COMPONENTES, p["w0"]))
    i_pre_est = ini["i_pre_estoque0"] * um
    r_long_est = ini["r_long_estoque0"] * um
    giro_pre = 1 / (ini["prazo_pre_meses"] / 3)
    giro_ipca = 1 / (ini["prazo_ipca_meses"] / 3)
    L = (ini["d_net0"] + 100 * ini["R0"] * ini["E0"] / ini["Y0"]) * um  # passivo líquido ex-reservas
    de_hist = [np.full(P, x) for x in ini["de_ult4"]]
    buf_ief = [p["i_ef0"] * um] * 4
    buf_gamma = [ini["gamma0"] * um] * 4
    buf_g = [ini["g0"] * um] * 4
    # Fiscal (% PIB)
    prev, pessoal, outras = (p["desp0"][k] * um for k in ("prev", "pessoal", "outras_obrig"))
    limite = p["limite0"] * um
    s_estr_ant = (p["rec_base"] - p["limite0"] + p["s_outros"]) * um
    # P3: lacuna inicial (precificada na fração 1 − φ) e referência ao longo da trajetória anunciada
    p3 = espec == "P3"
    sem_fiscal = p.get("_plano_sem_fiscal", False)  # o plano anunciado supõe credibilidade: sem inflação fiscal
    if p3:
        vp0 = fiscal_valoracao.valor_presente(plano["s_mat"][0], ini["s0"] * um, lam_f, ini["r_long0"] * um,
                                              g_pot, p["delta_min"], p["escala_vt"], p["r_long_neutro"])
        lacuna0 = ini["d_net0"] - vp0
        fracao0 = fiscal_valoracao.fracao_nao_lastreada(lacuna0, ini["d_net0"])
        ref_plano = plano.get("fracao_ref")
        X["vp"][:, 0], X["lacuna"][:, 0], X["fracao"][:, 0] = vp0, lacuna0, fracao0
    pi_fiscal_ant = np.zeros(P)
    pi_monet = np.zeros(P)
    R_adeq = p["R_adequado"] or p["R_min"]
    pdj = p["de_tendencia"] == "pdj"
    tend_fixa = 0.0 if pdj else ((1 + float(p["de_tendencia"]) / 100) ** 0.25 - 1) * 100
    ruptura = np.full(P, -1)
    # itens do pacote com multiplicador próprio (None = a3); sem itens, o impulso inteiro usa a3
    itens = cen.get("itens", [])
    assert len(itens) <= MAX_ITENS
    m_itens = [p["a3"] if it.get("multiplicador") is None else float(it["multiplicador"]) for it in itens]

    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for t in range(1, T + 1):
            eh, epi, ee, eprem = (choques[:, t - 1, j] for j in range(4))
            g_ant = X["g"][:, t - 1]
            # --- fiscal estrutural (regras de indexação e arcabouço)
            cresc = lambda real: (1 + real / 400) / (1 + g_ant / 400)  # noqa: E731
            prev = prev * cresc(p["g_salario_minimo"] + p["veg_previdencia"])
            pessoal = pessoal * cresc(p["g_pessoal"])
            outras = outras * cresc(p["g_outras_obrig"])
            rec_estr = p["rec_base"] + cen["medidas_receita"][t]
            fluxo = p["share_fluxo"] * rec_estr
            g_rec = np.mean(buf_g, axis=0)
            lim_real = np.clip(p["limite_frac_receita"] * g_rec, p["limite_min"], p["limite_max"])
            limite = limite * cresc(lim_real)
            obrig = prev + pessoal + outras + fluxo
            disc = np.maximum(p["disc_min"], limite - obrig)
            despesa = obrig + disc - cen["medidas_despesa"][t]
            s_estr = rec_estr - despesa + p["s_outros"]
            impulso = -(s_estr - s_estr_ant)
            s_estr_ant = s_estr
            if "impulso" in override:  # validação: impulso do primário estrutural observado
                impulso = override["impulso"][t] * um

            # --- demanda agregada
            r_long_ant = X["r_long"][:, t - 1]
            capex = cen["capex_ppp"][t] * (1 - p["a6"] * np.maximum(0, r_long_ant - p["r_long_neutro"]))
            de_real_ant = X["de"][:, t - 1] - (X["pi"][:, t - 1] - p["pi_ext"]) / 4
            # impulso de cada item: −Δ(medida em vigor); o restante do impulso (regras do arcabouço, efeitos de
            # segunda ordem do pacote) fica com a3. Com todos os multiplicadores = a3 e γ = 0, reproduz a3 · impulso
            ciclo = 1 + p["gamma_ciclo"] * np.maximum(0, -X["h"][:, t - 1])
            imp_itens = [-(it["trilha"][t] - it["trilha"][t - 1]) * um for it in itens]
            if p["fiscal_nivel"]:
                rho_f = p["a1"] if p["rho_f"] is None else p["rho_f"]
                dem_itens = [-m * ciclo * (it["trilha"][t] - rho_f * it["trilha"][t - 1]) * um
                             for m, it in zip(m_itens, itens)]
            else:
                dem_itens = [m * ciclo * imp for m, imp in zip(m_itens, imp_itens)]
            dem_resto = p["a3"] * (impulso - sum(imp_itens, np.zeros(P)))
            dem = {"dem_juro": -p["a2"] * (r_long_ant - p["r_long_neutro"]), "dem_capex": p["a4"] * capex,
                   "dem_cambio": p["a5"] * de_real_ant, "dem_choque": eh, "dem_fiscal_resto": dem_resto,
                   **{f"dem_item{k}": (dem_itens[k] if k < len(itens) else np.zeros(P)) for k in range(MAX_ITENS)}}
            h = p["a1"] * X["h"][:, t - 1] + sum(dem[k] for k in DEMANDA)
            h = np.clip(h, -G["h"], G["h"])
            g = g_pot + (h - X["h"][:, t - 1]) * 4
            s = s_estr + p["rec_base"] * p["eps_rec"] * h / 100
            if "s" in override:
                s = override["s"][t] * um

            # --- estabilizador (médias móveis de 4 trimestres, defasadas)
            s_estab = s_estabilizador(np.mean(buf_ief, axis=0), np.mean(buf_gamma, axis=0),
                                      X["d_gross"][:, t - 1])
            F_corr = p["p1"] * (X["d_gross"][:, t - 1] - p["d_ref"]) + p2 * (s_estab - s)

            # --- bloco de política: ponto fixo entre Taylor, expectativas (λ_π) e prêmio (λ_fiscal)
            pi_ant = X["pi"][:, t - 1]
            # P3: quem não acredita na meta incorpora a inflação fiscal passada às expectativas (peso ajustável)
            extra_fiscal = p["peso_fiscal_expect"] * (1 - lam_pi) * pi_fiscal_ant if p3 else 0.0
            pi_e = lam_pi * p["pi_meta"] + (1 - lam_pi) * pi_ant + extra_fiscal
            prem = X["prem"][:, t - 1]
            # reservas abaixo do nível adequado (no fim do trimestre anterior) encarecem o prêmio
            prem_reservas = p["kappa_R"] * np.maximum(0, R_adeq - X["R"][:, t - 1]) / R_adeq
            for _ in range(6):
                alvo = (p["r_neutro_base"] + p["omega_ef"] * (prem - p["p0"]) + pi_e
                        + p["phi_pi"] * (pi_ant - p["pi_meta"]) + p["phi_h"] * X["h"][:, t - 1])
                i_tay = p["rho"] * X["i_taylor"][:, t - 1] + (1 - p["rho"]) * alvo
                if "i" in override:
                    i = override["i"][t] * um
                else:
                    i = politicas.selic(cen["regra"], i_tay, cen["i_exog"][t], cen["delta"][t], p["i_min"])
                incons = np.minimum(np.maximum(0, i_tay - i) + p["mu"] * np.maximum(0, s_estab - s), G["incons"])
                pi_e = lam_pi * p["pi_meta"] + (1 - lam_pi) * (pi_ant + p["kappa"] * incons) + extra_fiscal
                pi_e = np.clip(pi_e, p["pi_min"], G["pi"])
                prem = (p["p0"] + lam_f * plano["F"] + (1 - lam_f) * (F_corr + p["p3"] * incons) + eprem
                        + choque_prem[t] + prem_reservas)
                prem = np.clip(prem, p["prem_min"], G["prem"])

            # --- reservas
            R_ant = X["R"][:, t - 1]
            R_rend = R_ant * (1 + p["rend_reservas"] / 400)
            disponivel = np.maximum(0, R_rend - p["R_min"])
            # venda programada limitada por R_min; defesa do câmbio na parada súbita limitada por R_min_defesa
            venda_prog = np.minimum(cen["venda_reservas"][t], disponivel)
            piso_def = p["R_min"] if p["R_min_defesa"] is None else p["R_min_defesa"]
            venda = venda_prog + np.minimum(defesa[t], np.maximum(0, R_rend - piso_def - venda_prog))
            R = R_ant * (1 + p["rend_reservas"] / 400) - venda

            # --- câmbio (fuga por desconfiança fiscal)
            pib_usd = X["Y"][:, t - 1] / X["E"][:, t - 1]
            c3_ef = p["c3"] * (R / ini["R0"]) ** p["eta"]
            de = (-p["c1"] * (i - X["i"][:, t - 1]) + p["c2"] * (prem - X["prem"][:, t - 1])
                  - c3_ef * 100 * venda / pib_usd + (1 - lam_f) * p["c4"] * incons + ee)
            # parada súbita: depreciação exógena; o salto do prêmio já deprecia via c2, então a parte exógena
            # desconta c2 × salto para que o impacto conjunto seja choque_de
            salto = max(choque_prem[t] - choque_prem[t - 1], 0.0)
            de = de + choque_de[t] - (p["c2"] * salto if choque_de[t] else 0.0)
            de = np.clip(de, -G["de"], G["de"])
            if "de" in override:
                de = override["de"][t] * um
            # tendência: só valoriza o câmbio (reservas, dívida cambial); o repasse e o câmbio real da demanda
            # usam o componente cíclico `de`, porque a tendência é antecipada e consistente com a meta
            if pdj:
                de_tend = (((1 + (i - prem) / 100) / (1 + p["i_ext"] / 100)) ** 0.25 - 1) * 100
            else:
                de_tend = tend_fixa * um
            de_tot = ((1 + de / 100) * (1 + de_tend / 100) - 1) * 100
            E = X["E"][:, t - 1] * (1 + de_tot / 100)
            de_hist = de_hist[1:] + [de]
            de12 = (np.prod([1 + x / 100 for x in de_hist], axis=0) - 1) * 100

            # --- P3: valor presente dos superávits esperados e inflação fiscal
            if p3:
                vp = fiscal_valoracao.valor_presente(plano["s_mat"][t], s, lam_f, r_long_ant, g_pot,
                                                     p["delta_min"], p["escala_vt"], p["r_long_neutro"])
                lacuna = X["d_net"][:, t - 1] - vp
                fracao = fiscal_valoracao.fracao_nao_lastreada(lacuna, X["d_net"][:, t - 1])
                dur = fiscal_valoracao.duracao(*(X[f"w_{c}"][:, t - 1] for c in COMPONENTES),
                                               p["dur_pre"], p["dur_ipca"], p["dur_fx"])
                ref = None if ref_plano is None else ref_plano[t] - ref_plano[0] + fracao0
                bruto = fiscal_valoracao.inflacao_fiscal(fracao, fracao0, dur, p["theta"], p["phi"], ref)
                pi_fiscal = np.zeros(P) if sem_fiscal else 0.5 * bruto + 0.5 * pi_fiscal_ant
            else:
                vp = lacuna = fracao = np.full(P, np.nan)
                pi_fiscal = np.zeros(P)

            # --- inflação (módulo da especificação)
            estado = {"pi_ant": pi_ant, "pi_e": pi_e, "h_ant": X["h"][:, t - 1], "de12": de12,
                      "pi_fiscal": pi_fiscal, "pi_monet": pi_monet}
            pi, comp = inflacao.inflacao(espec, estado, p, epi)
            pi = np.clip(pi, p["pi_min"], G["pi"])
            pi_fiscal_ant = pi_fiscal

            # --- juro real longo: Selic anunciada (peso λ_π) vs. Selic atual constante (peso 1 − λ_π)
            esperada = lam_pi * media_anun[t] + (1 - lam_pi) * i
            r_long = esperada - pi_e + tp[t] + p["peso_prem_longo"] * (prem - p["p0"]) + p["nivel_prem_longo"]
            r_long = np.clip(r_long, -G["r_long"], G["r_long"])

            # --- restrição de rolagem (antes do custo efetivo)
            r_real_lft = i - pi_e
            d_ant = X["d_gross"][:, t - 1]
            if p["rolagem"]:
                migr = rolagem.migracao(d_k["lft"], d_oma, i, pi_e, p["giro_lft"], p["r_min_rolagem"],
                                        p["banda_rolagem"])
                d_k, r_long_est = rolagem.aplicar(d_k, r_long_est, r_long, migr, p["monetizacao"])
            else:
                migr = np.zeros(P)
            if p["monetizacao"]:
                pi_monet = p["psi_monet"] * 100 * migr / d_ant  # entra na inflação do trimestre seguinte
                base = d_ant - migr                             # o estoque monetizado sai da dívida
            else:
                base = d_ant

            # --- dívida por componente
            gamma = ((1 + g / 100) * (1 + pi / 100) - 1) * 100
            gq = (1 + gamma / 100) ** 0.25
            taxas = _taxas_componentes(i, i_pre_est, r_long_est, pi, p["i_ext"], de_tot)
            fator = {c: (1 + taxas[c] / 100) ** 0.25 for c in COMPONENTES}
            Y = X["Y"][:, t - 1] * gq
            res_brl = 100 * venda * E / Y
            juros = sum(d_k[c] * (fator[c] - 1) for c in COMPONENTES) / gq
            # erosão da dívida não indexada (LFT, prefixados, cambial) pela inflação; a parte não antecipada
            # compara a inflação com a embutida no custo de cada título (LFT e cambial: π_e; prefixados: a do estoque)
            pi_pre_emb = ((1 + i_pre_est / 100) / (1 + r_long_est / 100) - 1) * 100
            erosao_total = (d_k["lft"] + d_k["pre"] + d_k["fx"]) * pi / 400 / gq
            erosao_na = ((d_k["lft"] + d_k["fx"]) * (pi - pi_e) + d_k["pre"] * (pi - pi_pre_emb)) / 400 / gq
            F_tot = sum(d_k[c] * fator[c] for c in COMPONENTES) / base
            i_ef = (F_tot ** 4 - 1) * 100
            for c in COMPONENTES:
                d_k[c] = d_k[c] * fator[c] / gq + w_emissao[c] * (-s / 4) - (res_brl if c == "lft" else 0)
            # compromissadas são parte da LFT: não podem exceder o estoque de LFT (resgates por superávit e
            # migrações reduzem a LFT do Tesouro primeiro)
            d_oma = np.minimum(np.maximum(d_oma * fator["lft"] / gq - res_brl, 0), np.maximum(d_k["lft"], 0))
            d = sum(d_k.values())
            L = (L - (migr if p["monetizacao"] else 0)) * F_tot / gq - s / 4 - res_brl
            d_net = L - 100 * R * E / Y
            i_pre_est = (1 - giro_pre) * i_pre_est + giro_pre * (r_long + pi_e)
            r_long_est = (1 - giro_ipca) * r_long_est + giro_ipca * r_long

            # --- alongamento (fim do trimestre, depois da emissão): a LFT do Tesouro acima da meta migra para
            # NTN-B (s_ipca) e prefixados (1 − s_ipca) às taxas correntes; as compromissadas não migram. A restrição
            # de rolagem do trimestre seguinte atua sobre a LFT que restar.
            w_meta = p["w0"][0] - (p["w0"][0] - p["w_lft_alvo"]) * min(1.0, t / p["T_along"])
            alongado = np.zeros(P)
            if p["alongamento"]:
                excesso = d_k["lft"] - w_meta * d
                alongado = np.clip(excesso, 0, np.maximum(d_k["lft"] - d_oma, 0))
                para_ipca = p["s_ipca"] * alongado
                para_pre = alongado - para_ipca
                novo_ipca, novo_pre = d_k["ipca"] + para_ipca, d_k["pre"] + para_pre
                r_long_est = np.where(novo_ipca > 0, (d_k["ipca"] * r_long_est + para_ipca * r_long)
                                      / np.where(novo_ipca > 0, novo_ipca, 1), r_long_est)
                i_pre_est = np.where(novo_pre > 0, (d_k["pre"] * i_pre_est + para_pre * (r_long + pi_e))
                                     / np.where(novo_pre > 0, novo_pre, 1), i_pre_est)
                d_k = {**d_k, "lft": d_k["lft"] - alongado, "ipca": novo_ipca, "pre": novo_pre}

            buf_ief = buf_ief[1:] + [i_ef]
            buf_gamma = buf_gamma[1:] + [gamma]
            buf_g = buf_g[1:] + [g]

            nova = (ruptura < 0) & (pi > p["pi_explosao"])
            ruptura[nova] = t
            morto = (ruptura >= 0) & (ruptura < t)
            valores = {
                "h": h, "g": g, "pi": pi, "pi_e": pi_e, "i": i, "i_taylor": i_tay, "r_long": r_long,
                "prem": prem, "de": de, "de_tend": de_tend, "E": E, "R": R, "venda": venda, "s": s, "s_estab": s_estab,
                "incons": incons, "d_gross": d, "d_net": d_net, "i_ef": i_ef, "gamma": gamma, "Y": Y,
                # decomposição: juros + crescimento + primário + reservas (+ monetização) = Δd
                "c_juros": juros, "c_cresc": -base * (gq - 1) / gq, "c_prim": -s / 4 * um,
                "c_res": -res_brl - (migr if p["monetizacao"] else 0),
                "tp": tp[t] * um, "pi_fiscal": pi_fiscal, "vp": vp, "lacuna": lacuna, "fracao": fracao,
                "migracao": migr, "r_real_lft": r_real_lft,
                "alongado": alongado, "w_lft_meta": w_meta * um, "lft_tesouro": d_k["lft"] - d_oma,
                "duracao": fiscal_valoracao.duracao(*(d_k[c] / d for c in COMPONENTES), p["dur_pre"], p["dur_ipca"],
                                                    p["dur_fx"]),
                "erosao_total": erosao_total, "erosao_na": erosao_na,
                **{f"w_{c}": d_k[c] / d for c in COMPONENTES},
                **{f"comp_{k}": v * um for k, v in comp.items()},
                **dem,
            }
            if din:
                buf_s.append(s * um)
                buf_s_plano.append(float(plano["s_mat"][t - 1, 0]))
                buf_pi.append(pi)
                if t % int(din.get("periodo", 4)) == 0:
                    lam_pi, lam_f = atualizar_lambda(din, lam_pi, lam_f, np.mean(buf_pi, axis=0),
                                                     np.mean(buf_s, axis=0) - np.mean(buf_s_plano), p["pi_meta"])
                    buf_s, buf_s_plano, buf_pi = [], [], []
                LAM["lam_pi"][:, t], LAM["lam_f"][:, t] = lam_pi, lam_f
            for nome in guardar:
                X[nome][:, t] = np.where(morto, np.nan, valores[nome])
            # estados lidos no trimestre seguinte precisam existir mesmo quando não são guardados
            for nome in ("h", "g", "pi", "i", "i_taylor", "r_long", "prem", "de", "E", "R", "Y", "d_gross",
                         "d_net", "w_lft", "w_pre", "w_ipca", "w_fx"):
                if nome not in guardar:
                    X[nome][:, t] = valores[nome]

    saida = {k: X[k] for k in guardar}
    saida["ruptura"] = ruptura
    if din:
        saida.update(LAM)
    return saida


def atualizar_lambda(din: dict, lam_pi, lam_f, pi_ano, gap_s, pi_meta):
    """Revisão das credibilidades ao fim de cada período (padrão: 4 trimestres).

    g_π = tol − |π média do ano − meta| (> 0: inflação dentro do intervalo; < 0: fora)
    g_f = primário médio do ano − primário anunciado no plano (p.p. do PIB)
    Δλ_π = b_pi_pos·max(g_π, 0) + b_pi_neg·min(g_π, 0) + b_cruzado·min(g_f, 0)
    Δλ_f = b_f_pos·max(g_f, 0) + b_f_neg·min(g_f, 0)
    Coeficientes estimados/calibrados em lambda_dinamico_estimacao.py.
    """
    g_pi = din.get("tol", 1.5) - np.abs(pi_ano - pi_meta)
    g_pi = np.where(np.isfinite(g_pi), g_pi, -din.get("tol", 1.5))
    g_f = np.where(np.isfinite(gap_s), gap_s, 0.0)
    d_pi = (din["b_pi_pos"] * np.maximum(g_pi, 0) + din["b_pi_neg"] * np.minimum(g_pi, 0)
            + din.get("b_cruzado", 0.0) * np.minimum(g_f, 0))
    d_f = din["b_f_pos"] * np.maximum(g_f, 0) + din["b_f_neg"] * np.minimum(g_f, 0)
    lo, hi = din.get("min", 0.0), din.get("max", 1.0)
    return np.clip(lam_pi + d_pi, lo, hi), np.clip(lam_f + d_f, lo, hi)


def plano_anunciado(p: dict, cen: dict, iteracoes: int = 4) -> dict:
    """Trajetória ANUNCIADA: o próprio cenário simulado com adesão total e sem choques.

    Itera porque o prêmio planejado depende do fim da trajetória anunciada, que por sua vez
    depende do prêmio. Devolve F (fundamentos ao fim do horizonte), a Selic anunciada e o
    primário anunciado (matriz usada pelo valor presente de P3).
    """
    T = cen["T"]
    H = int(p["H_vp"])
    if cen["regra"] == "taylor":
        i_path = np.concatenate([[p["ini"]["i0"]], np.interp(np.arange(1, T + 1), [0, 8, T],
                                                              [p["ini"]["i0"], p["ini"]["selic_focus_8t"][-1],
                                                               p["r_neutro_base"] + p["pi_meta"]])])
    else:
        i_path = cen["i_exog"].copy()
    plano = {"F": p["prem0"] - p["p0"], "i": np.concatenate([i_path, np.full(8, i_path[-1])])}
    # o anúncio não antecipa a parada súbita
    cen = {**cen, **{k: np.zeros(T + 1) for k in ("choque_de", "choque_prem", "defesa")}}
    q = {**p, "_plano_sem_fiscal": True,  # o anúncio supõe credibilidade total: sem inflação fiscal
         "dinamica_lambda": None}         # e credibilidade fixa
    for _ in range(iteracoes):
        tr = simular(q, cen, 1.0, plano=plano, guardar=("d_gross", "s", "s_estab", "i", "fracao"))
        F = (p["p1"] * (tr["d_gross"][0, -1] - p["d_ref"])
             + p2_efetivo(p) * (tr["s_estab"][0, -1] - tr["s"][0, -1]))
        i_sim = tr["i"][0]
        plano = {"F": float(F), "i": np.concatenate([i_sim, np.full(8, i_sim[-1])]),
                 "s_mat": matriz_plano_s(tr["s"][0], H)}
    if p["especificacao"] == "P3":
        # fração não lastreada ao longo da trajetória anunciada, avaliada com o s_mat final
        tr = simular(q, cen, 1.0, plano=plano, guardar=("fracao",))
        plano["fracao_ref"] = tr["fracao"][0]
    return plano
