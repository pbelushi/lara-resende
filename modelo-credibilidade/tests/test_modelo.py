"""Testes da seção 9 (v1 e v2). Usam a calibração em config/ (requer o bloco AUTO preenchido)."""
from __future__ import annotations

import copy
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from src import consistencia, dados, fiscal_valoracao, metricas, modelo, politicas, rolagem, varredura

RAIZ = Path(__file__).resolve().parents[1]
CALIB = RAIZ / "config" / "calibracao.yaml"
DADOS = Path(__file__).resolve().parent / "dados"


@pytest.fixture(scope="module")
def p():
    if "iniciais" not in yaml.safe_load(CALIB.read_text(encoding="utf-8")):
        pytest.skip("calibracao.yaml sem bloco AUTO; rode `python run.py --atualizar-dados`")
    return modelo.carregar_calibracao(CALIB)


@pytest.fixture(scope="module")
def cfg():
    return yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=["P1", "P3"])
def p_espec(request, p):
    return modelo.preparar({**copy.deepcopy(p), "especificacao": request.param})


@pytest.fixture(scope="module")
def cens(p, cfg):
    return varredura.preparar_cenarios(p, cfg)


def _sim(p, c, lam, choques=None, lam_f=None):
    return modelo.simular(p, c["cen"], lam, lam_f, choques=choques, plano=c["plano"])


# ---------------------------------------------------------------- v1

def test_identidade_contabil(p_espec, cfg):
    cens = varredura.preparar_cenarios(p_espec, cfg)
    choques = varredura.sortear_choques(p_espec, 20, cfg["horizonte"], seed=1)
    for c in cens.values():
        tr = _sim(p_espec, c, np.full(20, 0.5), choques)
        soma = tr["c_juros"] + tr["c_cresc"] + tr["c_prim"] + tr["c_res"]
        np.testing.assert_allclose(soma[:, 1:], np.diff(tr["d_gross"], axis=1), atol=1e-10)


def test_identidade_contabil_monetizacao(p, cfg):
    q = modelo.preparar({**copy.deepcopy(p), "monetizacao": True, "r_min_rolagem": 8.0})
    c = varredura.preparar_cenarios(q, cfg, ["B"])["B"]
    tr = _sim(q, c, np.linspace(0, 1, 5))
    assert np.nansum(tr["migracao"]) > 0
    soma = tr["c_juros"] + tr["c_cresc"] + tr["c_prim"] + tr["c_res"]
    np.testing.assert_allclose(soma[:, 1:], np.diff(tr["d_gross"], axis=1), atol=1e-10)


def test_pesos_somam_um(p_espec, cfg):
    for c in varredura.preparar_cenarios(p_espec, cfg).values():
        tr = _sim(p_espec, c, np.linspace(0, 1, 11))
        soma = tr["w_lft"] + tr["w_pre"] + tr["w_ipca"] + tr["w_fx"]
        m = np.isfinite(soma)
        np.testing.assert_allclose(soma[m], 1.0, atol=1e-12)


def test_caso_de_controle(p, cfg):
    """Sem choques, sem medidas, Selic constante e dívida toda pós-fixada: d' = d (1+i)/(1+γ) − s, trimestral."""
    q = copy.deepcopy(p)
    for k, w in zip(("w_lft", "w_pre", "w_ipca", "w_fx"), (1.0, 0.0, 0.0, 0.0)):
        q["ini"][k] = w
    q["rolagem"] = False
    q = modelo.preparar(q)
    cen = politicas.montar_cenario("B", cfg, q["ini"]["i0"])
    T = cen["T"]
    cen["venda_reservas"] = np.zeros(T + 1)
    i_const, s_const = 10.0, 1.0
    # λ = 1: expectativas ancoradas, sem ruptura inflacionária que truncaria a trajetória
    tr = modelo.simular(q, cen, 1.0, override={"i": np.full(T + 1, i_const), "s": np.full(T + 1, s_const)})
    assert tr["ruptura"][0] < 0
    d, gamma = tr["d_gross"][0], tr["gamma"][0]
    esperado = d[:-1] * ((1 + i_const / 100) / (1 + gamma[1:] / 100)) ** 0.25 - s_const / 4
    np.testing.assert_allclose(d[1:], esperado, rtol=1e-12)
    np.testing.assert_allclose(tr["i_ef"][0, 1:], i_const, rtol=1e-10)


def test_monotonicidade(p, cens):
    """prem não crescente e P_sucesso não decrescente em λ: avisa se violado, sem falhar."""
    grade = np.linspace(0, 1, 21)
    for chave, c in cens.items():
        tr = _sim(p, c, grade)
        viol = int((np.diff(tr["prem"][:, 1:], axis=0) > 1e-9).any(axis=0).sum())
        if viol:
            warnings.warn(f"cenário {chave}: prem cresce com λ em {viol} trimestre(s)")
    choques = varredura.sortear_choques(p, 100, 40, seed=7)
    mc = varredura.diagonal(p, cens, grade, choques)
    for chave, m in mc.groupby("cenario"):
        quedas = metricas.violacoes_monotonia(m["p_sucesso"].values, tolerancia=0.02)
        if quedas:
            warnings.warn(f"cenário {chave}: P_sucesso cai com λ em {quedas} ponto(s)")


def test_reservas(p, cfg):
    cen = politicas.montar_cenario("B", cfg, p["ini"]["i0"])
    cen["venda_reservas"] = np.full(cen["T"] + 1, 100.0)  # venda agressiva para forçar o piso
    choques = varredura.sortear_choques(p, 50, cen["T"], seed=3)
    plano = modelo.plano_anunciado(p, cen)
    tr = modelo.simular(p, cen, np.full(50, 0.5), choques=choques, plano=plano)
    R = tr["R"][np.isfinite(tr["R"])]
    assert (R >= 0).all()
    assert (R >= p["R_min"] - 1e-9).all()
    assert np.nansum(tr["venda"][:, 1:], axis=1).max() > 0


def test_reprodutibilidade(p, cens):
    grade = np.array([0.2, 0.5, 0.8])
    a = varredura.diagonal(p, cens, grade, varredura.sortear_choques(p, 50, 40, seed=42))
    b = varredura.diagonal(p, cens, grade, varredura.sortear_choques(p, 50, 40, seed=42))
    assert a.equals(b)


def test_lambda_star_intervalos():
    grade = np.round(np.linspace(0, 1, 11), 2)
    ok = np.array([0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1], dtype=bool)
    r = metricas.lambda_star_det(grade, ok)
    assert r["lambda_star"] == 0.2 and not r["monotonico"]
    assert r["intervalos"] == [(0.2, 0.3), (0.6, 1.0)]


# ---------------------------------------------------------------- v2

def test_diagonal_reproduz_v1():
    """P1, sem rolagem, δ e term premium constantes, calibração congelada: bate com a v1 até a ruptura."""
    p1 = modelo.carregar_calibracao(DADOS / "calibracao_v1.yaml", "P1")
    p1.update(rolagem=False, tau_tp=None, _legado_v1=True)
    p1 = modelo.preparar(p1)
    cfg1 = yaml.safe_load((DADOS / "cenarios_v1.yaml").read_text(encoding="utf-8"))
    ref = np.load(DADOS / "v1_referencia.npz")
    for k, c in varredura.preparar_cenarios(p1, cfg1).items():
        assert c["plano"]["F"] == pytest.approx(float(ref[f"{k}_F"]), abs=1e-12)
        tr = modelo.simular(p1, c["cen"], ref["grade"], ref["grade"], plano=c["plano"])
        for v in ("d_gross", "pi", "i", "prem", "r_long", "h", "s", "E", "R", "d_net"):
            m = np.isfinite(tr[v])
            np.testing.assert_allclose(tr[v][m], ref[f"{k}_{v}"][m], atol=1e-8, err_msg=f"{k}/{v}")


def test_p3_lacuna_nula():
    d_net = np.array([60.0, 70.0, 80.0])
    vp = d_net.copy()  # VP = d_net em todo t
    fr = fiscal_valoracao.fracao_nao_lastreada(d_net - vp, d_net)
    pi_f = fiscal_valoracao.inflacao_fiscal(fr, fr, dur=np.full(3, 2.0), theta=0.5, phi=0.0)
    np.testing.assert_allclose(pi_f, 0.0)


def test_p3_plano_crivel_sem_inflacao_fiscal(p, cfg):
    """Com λ = 1 e sem choques, a trajetória é a anunciada: não há revisão e pi_fiscal = 0."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P3"})
    for c in varredura.preparar_cenarios(q, cfg).values():
        tr = _sim(q, c, np.array([1.0]))
        np.testing.assert_allclose(tr["pi_fiscal"][0, 1:], 0.0, atol=1e-9)


def test_p3_sinal():
    """Mais superávit anunciado, com λ_fiscal = 1, eleva o VP e reduz a inflação fiscal."""
    um = np.ones(1)
    args = dict(s_corr=um * 0.0, lam_fiscal=um, r_desc=um * 6.0, g_esp=2.5, delta_min=0.5)
    vp_baixo = fiscal_valoracao.valor_presente(np.full(40, 1.0), **args)
    vp_alto = fiscal_valoracao.valor_presente(np.full(40, 2.0), **args)
    assert vp_alto > vp_baixo
    fr0 = fiscal_valoracao.fracao_nao_lastreada(70 - vp_baixo, 70.0)
    f = lambda vp: fiscal_valoracao.inflacao_fiscal(  # noqa: E731
        fiscal_valoracao.fracao_nao_lastreada(70 - vp, 70.0), fr0, 2 * um, 0.5, 0.0)
    assert f(vp_alto) < f(vp_baixo)


def test_p3_duracao():
    """Mesma lacuna, dívida mais curta: inflação fiscal maior por trimestre."""
    kw = dict(fracao=np.array([0.3]), fracao0=np.array([0.1]), theta=0.5, phi=0.0)
    curta = fiscal_valoracao.inflacao_fiscal(dur=np.array([1.0]), **kw)
    longa = fiscal_valoracao.inflacao_fiscal(dur=np.array([4.0]), **kw)
    assert curta > longa > 0
    d_curta = fiscal_valoracao.duracao(0.8, 0.1, 0.1, 0.0, 2.0, 7.0, 5.0)
    d_longa = fiscal_valoracao.duracao(0.2, 0.3, 0.5, 0.0, 2.0, 7.0, 5.0)
    assert d_curta < d_longa


def test_p3_valor_terminal_finito():
    r = np.array([-5.0, 0.0, 2.5, 2.6, 3.0, 10.0])
    for escala in (1.0, 100.0):
        vp = fiscal_valoracao.valor_presente(np.full(40, 2.0), np.full(r.size, -1.0), np.full(r.size, 0.5), r,
                                             g_esp=2.5, delta_min=0.5, escala_vt=escala)
        assert np.isfinite(vp).all()


def test_rolagem():
    d_k = {"lft": np.array([50.0]), "pre": np.array([15.0]), "ipca": np.array([15.0]), "fx": np.array([0.1])}
    migr = rolagem.migracao(d_k["lft"], np.array([10.0]), i=np.array([4.0]), pi_e=np.array([4.0]),
                            giro_lft=0.1, r_min=1.0, banda=2.0)
    assert migr[0] == pytest.approx(40 * 0.1 * 0.5)
    novo, _ = rolagem.aplicar(d_k, np.array([5.0]), np.array([6.0]), migr, monetizar=False)
    assert novo["lft"][0] == pytest.approx(50 - migr[0])
    assert novo["ipca"][0] == pytest.approx(15 + migr[0])
    assert sum(v[0] for v in novo.values()) == pytest.approx(sum(v[0] for v in d_k.values()))
    sem = rolagem.migracao(d_k["lft"], np.array([10.0]), np.array([8.0]), np.array([4.0]), 0.1, 1.0, 2.0)
    assert sem[0] == 0


def test_explosao(p, cfg):
    """Trajetória com π > 50% é encerrada (NaN depois da ruptura) e conta como falha."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1"})
    c = varredura.preparar_cenarios(q, cfg, ["B"])["B"]
    tr = _sim(q, c, np.array([0.0, 1.0]))
    t = tr["ruptura"][0]
    assert t > 0
    assert tr["pi"][0, t] > q["pi_explosao"]
    assert np.isnan(tr["pi"][0, t + 1:]).all()
    ok, det = metricas.sucesso(tr, q)
    assert not ok[0] and not det["inflacao_explosiva"][0]


def test_delta_decrescente(p, cfg):
    c = varredura.preparar_cenarios(p, cfg, ["C"])["C"]
    cen = c["cen"]
    fim = cfg["cenarios"]["C"]["T_corte"] + cfg["cenarios"]["C"]["T_delta"]
    assert cen["delta"][fim + 1:].max() == 0
    tr = _sim(p, c, np.linspace(0, 1, 11))
    i, it = tr["i"][:, fim + 1:], tr["i_taylor"][:, fim + 1:]
    m = np.isfinite(i)
    assert (i[m] >= it[m] - 1e-9).all()
    assert (i[m] >= cfg["cenarios"]["C"]["i_alvo"] - 1e-9).all()


def test_dimensoes_lambda(p, cens):
    """λ_fiscal só entra no prêmio, na fuga cambial e em P3; λ_π só nas expectativas e na Selic esperada."""
    c = cens["B"]
    a = _sim(p, c, np.array([0.5]), lam_f=np.array([0.2]))
    b = _sim(p, c, np.array([0.5]), lam_f=np.array([0.9]))
    assert not np.allclose(a["prem"][0, 1:], b["prem"][0, 1:])


# ---------------------------------------------------------------- v2.1

def _estacionario(p, cfg, omega, delta_prem):
    """Selic no neutro (Taylor de estado estacionário), inflação na meta, prêmio = p0 + delta_prem, sem choques."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1", "omega": omega, "rolagem": False})
    cen = politicas.montar_cenario("B", cfg, q["ini"]["i0"])
    T = cen["T"]
    i_ss = q["r_neutro_base"] + omega * delta_prem + q["pi_meta"]
    plano = {"F": float(delta_prem), "i": np.full(T + 9, i_ss)}  # λ_fiscal = 1: prem = p0 + F
    tr = modelo.simular(q, cen, 1.0, plano=plano, override={"i": np.full(T + 1, i_ss)})
    return q, tr


@pytest.mark.parametrize("omega", [0.0, 0.5, 1.0])
def test_estado_estacionario(p, cfg, omega):
    q, tr = _estacionario(p, cfg, omega, 0.0)
    assert tr["r_long"][0, -1] == pytest.approx(q["r_long_neutro"], abs=0.05)


@pytest.mark.parametrize("omega", [0.0, 0.5, 1.0])
def test_sem_dupla_contagem(p, cfg, omega):
    """+1 p.p. de prêmio eleva o juro longo de estado estacionário em 1 p.p. (pela Selic ou pela curva)."""
    _, base = _estacionario(p, cfg, omega, 0.0)
    _, alto = _estacionario(p, cfg, omega, 1.0)
    assert alto["r_long"][0, -1] - base["r_long"][0, -1] == pytest.approx(1.0, abs=0.05)


def test_tp_lp_derivado(p, cfg):
    exp = yaml.safe_load((RAIZ / "config" / "experimentos.yaml").read_text(encoding="utf-8"))
    for espec in ("P1", "P3"):
        for nome, var in exp["variantes"].items():
            r = varredura.aplicar_variante(p, espec, var, list(cfg["cenarios"]))
            if r is None:
                continue
            q = r[0]
            assert q["tp_lp"] == pytest.approx(q["r_long_neutro"] - q["r_neutro_base"]), nome
    a = varredura.aplicar_variante(p, "P1", exp["variantes"]["base"], ["A"])[0]
    n = varredura.aplicar_variante(p, "P1", exp["variantes"]["neutro_45"], ["A"])[0]
    assert n["tp_lp"] == pytest.approx(a["tp_lp"])  # neutro_45 muda o nível, não a inclinação


def test_parametro_unico(p, cfg):
    """IS, VP de P3 e checagem de consistência usam o mesmo r_long_neutro."""
    saidas = {}
    for rl in (4.5, 6.5):
        q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P3", "r_long_neutro": rl})
        c = varredura.preparar_cenarios(q, cfg, ["A"])["A"]
        tr = _sim(q, c, np.array([0.5]))
        vp = fiscal_valoracao.valor_presente(np.full(40, 2.0), np.zeros(1), np.ones(1), np.full(1, 6.0),
                                             q["ini"]["g_potencial"], q["delta_min"], 1.0, q["r_long_neutro"])
        saidas[rl] = (tr["h"][0, 1], vp[0], consistencia.linha(p, cfg, rl, 0.0)["s_estab_bruta"])
    h45, vp45, se45 = saidas[4.5]
    h65, vp65, se65 = saidas[6.5]
    assert h45 < h65          # IS: juro longo neutro mais alto torna a mesma taxa menos contracionista
    assert vp45 > vp65        # VP: desconto terminal maior reduz o valor presente
    assert se45 < se65        # consistência: estabilizador maior com juro neutro maior


def test_duracao_macaulay():
    """Duração de Macaulay da NTN-B (cupom 6% a.a.) é menor que o prazo; LTN (zero cupom) é igual ao prazo."""
    assert dados.macaulay(10.0, 0.06, 6.0) < 10.0
    assert dados.macaulay(3.0, 0.0, 12.0) == pytest.approx(3.0)


def test_duracao_estoque(p):
    ini = p["ini"]
    if "prazo_ipca_estoque_anos" not in ini:
        pytest.skip("duração de Macaulay não calculada nesta calibração")
    assert ini["dur_ipca_anos"] < ini["prazo_ipca_estoque_anos"]


def test_portao_qualidade(p, cfg):
    """Com o pacote fiscal zerado, A não estabiliza com λ = 1 e o aviso aparece."""
    c = copy.deepcopy(cfg)
    for m in c["pacote_fiscal"]:
        m["impacto_final"] = 0.0
    port = consistencia.portao(p, c)
    assert not port["A_estabiliza"]
    assert port["aviso"] == consistencia.AVISO_PORTAO
    assert port["pacote_adicional"] > 0


# ---------------------------------------------------------------- v2.2

from src import bootstrap, estimacao  # noqa: E402


def test_bootstrap_identidade_reproduz_pontual():
    rng = np.random.default_rng(0)
    grade = np.round(np.linspace(0, 1, 11), 2)
    okA = rng.random((11, 200)) < np.linspace(0.1, 0.95, 11)[:, None]
    okC = rng.random((11, 200)) < np.linspace(0.05, 0.9, 11)[:, None]
    idx = bootstrap.indices(200, 1, seed=1, identidade=True)
    r = bootstrap.diagonal(okA, okC, grade, idx)
    assert r["ic_lo_80"] == pytest.approx(r["delta_80"]) and r["ic_hi_80"] == pytest.approx(r["delta_80"])
    assert r["ic_lo_50"] == pytest.approx(r["delta_50"])
    supA = rng.random((5, 5, 100)) < 0.85
    a = bootstrap.area(supA, supA, bootstrap.indices(100, 1, 1, identidade=True))
    assert a["ic_lo"] == pytest.approx(a["delta_area"]) == pytest.approx(0.0)


def test_bootstrap_indices_pareados():
    """Os mesmos índices valem para todos os cenários: com sucesso idêntico em A e C, Δ = 0 em toda réplica."""
    rng = np.random.default_rng(3)
    grade = np.round(np.linspace(0, 1, 11), 2)
    ok = rng.random((11, 300)) < np.linspace(0.2, 0.95, 11)[:, None]
    r = bootstrap.diagonal(ok, ok.copy(), grade, bootstrap.indices(300, 200, seed=5))
    assert r["ic_lo_80"] == 0 and r["ic_hi_80"] == 0 and r["frac_C_supera_80"] == 0


def test_bootstrap_seed_reproduz():
    rng = np.random.default_rng(4)
    grade = np.round(np.linspace(0, 1, 11), 2)
    okA, okC = (rng.random((11, 300)) < np.linspace(0.2, 0.95, 11)[:, None] for _ in range(2))
    a = bootstrap.diagonal(okA, okC, grade, bootstrap.indices(300, 100, seed=9))
    b = bootstrap.diagonal(okA, okC, grade, bootstrap.indices(300, 100, seed=9))
    assert a == b
    assert bootstrap.ordem_com_empate("A > C > B", True) == "A ≈ C > B"
    assert bootstrap.ordem_com_empate("C > A > B", False) == "C > A > B"


def _along(p, cfg, **kw):
    q = modelo.preparar({**copy.deepcopy(p), "alongamento": True, "w_lft_alvo": 0.40, "T_along": 20,
                         "s_ipca": 0.7, **kw})
    c = varredura.preparar_cenarios(q, cfg, ["A"])["A"]
    return q, c, _sim(q, c, np.array([0.3, 0.9]))


def test_alongamento_pesos_e_teto(p, cfg):
    q, _, tr = _along(p, cfg)
    soma = tr["w_lft"] + tr["w_pre"] + tr["w_ipca"] + tr["w_fx"]
    np.testing.assert_allclose(soma[np.isfinite(soma)], 1.0, atol=1e-12)
    w, meta = tr["w_lft"][:, 1:], tr["w_lft_meta"][:, 1:]
    m = np.isfinite(w)
    assert (w[m] <= meta[m] + 1e-12).all()


def test_alongamento_duracao_aumenta(p, cfg):
    q, _, tr = _along(p, cfg)
    dur = tr["duracao"][1, :q["T_along"] + 1]
    assert dur[-1] > dur[0] + 0.5
    assert (np.diff(dur) > -0.05).all()


def test_alongamento_p3_plano_crivel(p, cfg):
    """φ = 0, λ = 1, sem choques: com alongamento, P3 continua sem inflação fiscal."""
    q = modelo.preparar({**copy.deepcopy(p), "especificacao": "P3", "alongamento": True})
    for c in varredura.preparar_cenarios(q, cfg).values():
        tr = _sim(q, c, np.array([1.0]))
        np.testing.assert_allclose(tr["pi_fiscal"][0, 1:], 0.0, atol=1e-9)


def test_alongamento_rolagem_sem_sobreposicao(p, cfg):
    """Juro real abaixo do piso e alongamento ativos: as migrações nunca somam mais que a LFT do Tesouro."""
    q, c, _ = _along(p, cfg, r_min_rolagem=7.0)  # piso acima do juro real de equilíbrio: rolagem e alongamento ativos
    tr = modelo.simular(q, c["cen"], np.array([0.5]), plano=c["plano"])
    assert np.nansum(tr["migracao"]) > 0 and np.nansum(tr["alongado"]) > 0
    lft_tes = tr["lft_tesouro"][0]
    assert (lft_tes[np.isfinite(lft_tes)] >= -1e-9).all()      # nunca migra além do estoque existente
    # a rolagem do trimestre t atua sobre o que o alongamento de t−1 deixou
    assert (tr["migracao"][0, 1:] <= lft_tes[:-1] + 1e-9).all()


def test_calibracao_b3_reproduz_alvo(p, cfg):
    for espec in ("P1", "P3"):
        b3, _ = estimacao.calibrar_b3(p, espec, 0.09, cfg)
        assert estimacao.erpt_modelo(p, espec, b3, cfg)[4] == pytest.approx(0.09, abs=0.01)


def test_recuperacao_omega():
    """Taylor simulada com ψ conhecido: o NLS recupera ψ dentro do IC de 95%."""
    rng = np.random.default_rng(11)
    n, rho, c, fp, fh, psi = 400, 0.85, 9.0, 1.5, 0.5, 0.4
    gap = np.cumsum(rng.normal(0, 0.2, n)) * 0.3
    h = np.cumsum(rng.normal(0, 0.3, n)) * 0.2
    prem = 3 + np.cumsum(rng.normal(0, 0.15, n)) * 0.5
    i = np.empty(n)
    i[0] = c
    for t in range(1, n):
        i[t] = rho * i[t - 1] + (1 - rho) * (c + fp * gap[t] + fh * h[t - 1] + psi * (prem[t - 1] - prem.mean())) \
               + rng.normal(0, 0.1)
    df = pd.DataFrame({"i": i, "i_l1": np.r_[np.nan, i[:-1]], "gap": gap, "h_l1": np.r_[np.nan, h[:-1]],
                       "prem_l1": np.r_[np.nan, prem[:-1]]}, index=pd.date_range("2000-01-01", periods=n, freq="MS"))
    r = estimacao.taylor_nls(df)
    assert r["ic_tipo"] == "limitado" and r["ic_lo"] <= psi <= r["ic_hi"]
    assert r["psi_nls"] == pytest.approx(r["psi"], abs=1e-3)  # NLS e forma linear coincidem


def test_fieller_e_classificacao():
    """Fieller: limitado com denominador significativo; ilimitado quando 1 − ρ não é significativo."""
    lim = estimacao.fieller(b=0.10, d=0.20, Vbb=0.02 ** 2, Vdd=0.02 ** 2, Vbd=0.0)
    assert lim["ic_tipo"] == "limitado" and lim["ic_lo"] < 0.5 < lim["ic_hi"]
    ilim = estimacao.fieller(b=0.10, d=0.02, Vbb=0.03 ** 2, Vdd=0.02 ** 2, Vbd=0.0)
    assert ilim["ic_tipo"] != "limitado"
    base = {"ic_tipo": "limitado", "psi": 0.5}
    assert estimacao.classificar_omega({**ilim, "psi": 5.0}) == "nao_identificado"
    assert estimacao.classificar_omega({**base, "ic_lo": -1, "ic_hi": 2, "ic_contem_0": True,
                                        "ic_contem_1": True}) == "nao_informativo"
    assert estimacao.classificar_omega({**base, "psi": 3.0, "ic_lo": 1.5, "ic_hi": 4, "ic_contem_0": False,
                                        "ic_contem_1": False}) == "erro_especificacao"
    assert estimacao.classificar_omega({**base, "ic_lo": 0.2, "ic_hi": 0.8, "ic_contem_0": False,
                                        "ic_contem_1": False}) == "identificado"


def test_recuperacao_erpt():
    """Preços simulados com repasse conhecido (10% no mês, 5% no seguinte): a LP recupera ERPT_12 ≈ 15%."""
    rng = np.random.default_rng(12)
    n = 400
    idx = pd.date_range("1990-01-01", periods=n, freq="MS")
    de = rng.normal(0, 3, n)
    pi = 0.4 + 0.10 * de + 0.05 * np.r_[0, de[:-1]] + rng.normal(0, 0.2, n)
    m = pd.DataFrame({"pi_m": pi, "p_ipca": np.cumsum(pi), "e": np.cumsum(de), "de": de,
                      "hiato": rng.normal(0, 1, n), "desvio_focus": rng.normal(0, 0.5, n), "dicbr": rng.normal(0, 2, n),
                      "d2020": 0.0, "ddolar": de * 0.5 + rng.normal(0, 1, n), "dvix": rng.normal(0, 5, n)}, index=idx)
    r = estimacao.lp(m, 12)
    ic = estimacao.erpt_bootstrap(m, [12], B=100)
    assert ic.loc[12, "lo"] <= 0.15 <= ic.loc[12, "hi"]
    assert r["erpt"] == pytest.approx(0.15, abs=0.05)


def test_validacao_codigos_estimacao():
    """Todos os códigos usados na estimação existem e conferem com o nome oficial (falha explícita se não)."""
    try:
        v = estimacao.validar()
    except RuntimeError as e:
        pytest.fail(str(e))
    except Exception as e:  # noqa: BLE001 - sem rede: não é falha do código
        pytest.skip(f"sem acesso ao webservice do SGS: {e}")
    assert v["ok"].all()


def test_c_sem_piso(p, cfg):
    """Teto durante o corte (Taylor − δ ≤ i ≤ Taylor, i ≤ trajetória salvo o limite de δ); depois, i = Taylor."""
    cen = politicas.montar_cenario("C", cfg, p["ini"]["i0"], ajustes={"politica_monetaria": "condicionada_sem_piso"})
    plano = modelo.plano_anunciado(p, cen)
    tr = modelo.simular(p, cen, np.linspace(0, 1, 11), plano=plano)
    i, tay = tr["i"][:, 1:], tr["i_taylor"][:, 1:]
    delta, exog = cen["delta"][1:], cen["i_exog"][1:]
    m = np.isfinite(i)
    assert (i[m] <= np.maximum(tay, p["i_min"])[m] + 1e-9).all()
    assert (i[m] >= (tay - delta)[m] - 1e-9).all()
    assert ((i <= np.maximum(exog, tay - delta) + 1e-9) | ~m).all()
    fim = cfg["cenarios"]["C"]["T_corte"] + cfg["cenarios"]["C"]["T_delta"]
    np.testing.assert_allclose(i[:, fim:][m[:, fim:]], np.maximum(tay, p["i_min"])[:, fim:][m[:, fim:]], atol=1e-9)
    assert (i[:, fim:][m[:, fim:]] < cfg["cenarios"]["C"]["i_alvo"]).any()  # sem piso de 7,5%


def test_criterio_banda_simetrica(p):
    """Deflação no fim passa no critério de teto, mas não na banda simétrica [meta − 1,5; meta + 1,5]."""
    T = 41
    d = np.tile(np.linspace(80, 75, T), (3, 1))
    pi = np.vstack([np.full(T, -1.0), np.full(T, 3.0), np.full(T, 5.0)])
    tr = {"d_gross": d, "pi": pi, "R": np.full((3, T), 400.0), "ruptura": np.full(3, -1)}
    ok_teto, _ = metricas.sucesso(tr, p)
    ok_banda, det = metricas.sucesso(tr, p, bilateral=True)
    assert list(ok_teto) == [True, True, False]
    assert list(ok_banda) == [False, True, False]
    assert not det["inflacao"][0]


def test_parada_subita(p, cfg):
    """Choque não antecipado: plano igual ao do cenário sem choque; depreciação ≈ 30% no impacto; a venda programada
    respeita R_min e a defesa (≤ US$ 50 bi) pode rompê-lo."""
    sem = varredura.preparar_cenarios(p, cfg, ["A"], {"venda_reservas": [25] * 4})["A"]
    com = varredura.preparar_cenarios(p, cfg, ["A"], {"venda_reservas": [25] * 4, "choque_t": 8})["A"]
    np.testing.assert_allclose(sem["plano"]["i"], com["plano"]["i"])
    assert sem["plano"]["F"] == pytest.approx(com["plano"]["F"])
    t_sem = modelo.simular(p, sem["cen"], np.array([1.0]), plano=sem["plano"])
    t_com = modelo.simular(p, com["cen"], np.array([1.0]), plano=com["plano"])
    np.testing.assert_allclose(t_sem["d_gross"][0, :8], t_com["d_gross"][0, :8])  # idênticos antes do choque
    assert t_com["de"][0, 8] > 20  # 30% menos o efeito da defesa
    assert (t_sem["R"][0] >= p["R_min"] - 1e-9).all()
    assert (t_com["R"][0] >= p["R_min"] - 50 - 1e-9).all()
    assert t_com["venda"][0, 8] + t_com["venda"][0, 9] <= 50 + 1e-9


def test_criterio_divida_liquida(p):
    """O critério líquido usa a DLSP: dívida bruta estável com líquida subindo falha só no líquido."""
    T = 41
    tr = {"d_gross": np.tile(np.linspace(80, 76, T), (1, 1)), "d_net": np.tile(np.linspace(70, 80, T), (1, 1)),
          "pi": np.full((1, T), 3.0), "R": np.full((1, T), 400.0), "ruptura": np.full(1, -1)}
    assert metricas.sucesso(tr, p)[0][0]
    assert not metricas.sucesso(tr, p, divida="liquida")[0][0]
    todas = metricas.sucesso_todas(tr, p)
    assert set(todas) == {"", "_bil", "_liq", "_liq_bil"} and todas[""][0] and not todas["_liq"][0]


def test_tendencia_cambio(p, cfg):
    """A tendência só valoriza o câmbio: com 1% a.a. o câmbio sobe ~1% a.a. a mais, a DLSP cai pelas reservas e a
    inflação não muda; na paridade descoberta a tendência é (Selic − prêmio) contra o juro externo."""
    q0 = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1"})
    q1 = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1", "de_tendencia": 1.0})
    qu = modelo.preparar({**copy.deepcopy(p), "especificacao": "P1", "de_tendencia": "pdj"})
    c = varredura.preparar_cenarios(q0, cfg, ["A"])["A"]
    g = ("E", "pi", "d_net", "de_tend", "i", "prem")
    t0, t1, tu = (modelo.simular(q, c["cen"], 1.0, plano=c["plano"], guardar=g) for q in (q0, q1, qu))
    T = t0["E"].shape[1] - 1
    razao = (t1["E"][0, -1] / t1["E"][0, 0]) / (t0["E"][0, -1] / t0["E"][0, 0])
    assert razao == pytest.approx(1.01 ** (T / 4), rel=1e-6)
    np.testing.assert_allclose(t1["pi"], t0["pi"])
    assert t1["d_net"][0, -1] < t0["d_net"][0, -1]
    esperado = (((1 + (tu["i"][0, 1:] - tu["prem"][0, 1:]) / 100) / (1 + q0["i_ext"] / 100)) ** 0.25 - 1) * 100
    np.testing.assert_allclose(tu["de_tend"][0, 1:], esperado)


def test_canal_reservas_premio(p, cfg):
    """κ_R só age com reservas abaixo do nível adequado: inerte com R_adequado = R_min (padrão) e ativo, com prêmio
    maior, quando R_adequado = reservas iniciais e o cenário vende reservas."""
    base = {**copy.deepcopy(p), "especificacao": "P1"}
    aj = {"venda_reservas": [25, 25, 25, 25]}
    q0 = modelo.preparar(dict(base))
    c = varredura.preparar_cenarios(q0, cfg, ["A"], aj)["A"]
    t0 = modelo.simular(q0, c["cen"], 0.7, plano=c["plano"], guardar=("prem", "R"))
    qi = modelo.preparar({**base, "kappa_R": 5.0})
    ti = modelo.simular(qi, c["cen"], 0.7, plano=c["plano"], guardar=("prem", "R"))
    np.testing.assert_allclose(ti["prem"], t0["prem"])
    qa = modelo.preparar({**base, "kappa_R": 5.0, "R_adequado": p["ini"]["R0"]})
    ta = modelo.simular(qa, c["cen"], 0.7, plano=c["plano"], guardar=("prem", "R"))
    assert (ta["prem"][0, 2:6] > t0["prem"][0, 2:6]).all()
