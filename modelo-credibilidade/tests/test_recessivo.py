"""Testes do módulo recessivo (seção 7 de modelo_credibilidade_fiscal_efeito_recessivo.md)."""
import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from src import modelo, recessivo

RAIZ = Path(__file__).resolve().parents[1]
MIPD = RAIZ / "data" / "processed" / "mip"
pytestmark = pytest.mark.skipif(not (MIPD / "L_tipo1.npy").exists(),
                                reason="rode python -m src.extrair_mip e python -m src.extrair_emprego")


@pytest.fixture(scope="module")
def base():
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    return p, cfg


def test_multiplicador_referencia():
    m = pd.read_csv(MIPD / "mip2015_multiplicadores_setores.csv").set_index("grupo")
    assert m.loc[3, "prod_tipo1"] == pytest.approx(2.16, abs=0.005)


def test_choque_nulo_setorial():
    mat = recessivo.Matriz()
    nT = 41
    dC = {"dem_juro": np.zeros(nT), "item:governo": np.zeros(nT)}
    st = recessivo.setorial(dC, np.zeros(nT), mat)
    for k in ("dVA", "dX", "emp1", "emp2_bruto"):
        assert np.allclose(st[k], 0)


def test_reconciliacao_va():
    mat = recessivo.Matriz()
    rng = np.random.default_rng(1)
    nT = 41
    dC = {"dem_juro": rng.normal(0, 0.5, nT), "item:governo": rng.normal(0, 0.2, nT),
          "dem_cambio": rng.normal(0, 0.1, nT)}
    dh = sum(dC.values()) + rng.normal(0, 0.05, nT)
    st = recessivo.setorial(dC, dh, mat)
    alvo = dh / 100 * mat.va_total
    assert np.allclose(st["dVA"].sum(axis=1), alvo, rtol=1e-3, atol=1e-6)


def test_multiplicadores_iguais_a3_reproduzem(base):
    p, cfg = base
    q = recessivo.preparar_espec(p, "P1", {"fiscal_nivel": False})  # forma de impulso, a do modelo principal
    pac = recessivo.pacote("pacote_base", cfg["horizonte"])
    for it in pac:
        it["multiplicador"] = q["a3"]
    ch = np.zeros((1, cfg["horizonte"], 4))
    novo = recessivo.simular(q, cfg, "A", [0.7], ch, pac)
    antigo = recessivo.simular(q, cfg, "A", [0.7], ch, None)  # pacote de cenarios.yaml com a3 único
    for v in ("h", "pi", "d_net"):
        assert np.allclose(novo[v], antigo[v], atol=1e-10)


def test_calibracao_rho_f(base):
    """Efeito em nível: o multiplicador acumulado direto em 8 trimestres é o multiplicador do item (e também em 4 e
    16, porque ρ_f = a1 faz o efeito direto igual a m × medida em todo trimestre)."""
    p, cfg = base
    mult = recessivo.multiplicadores_efetivos(p, cfg)
    for H in (4, 8, 16):
        assert np.allclose(mult[f"direto_{H}"], mult["m"], atol=1e-10)
    # a forma de impulso não satisfaz a calibração (acumulado em 8 trimestres ≈ 0,5 m)
    q = recessivo.preparar_espec(p, "P1", {"fiscal_nivel": False})
    T = cfg["horizonte"]
    degrau = np.where(np.arange(T + 1) >= 1, 1.0, 0.0)
    pac = [{"nome": "x", "chave": "x", "tipo": "despesa", "canal": "governo", "multiplicador": 1.0, "trilha": degrau}]
    tr = recessivo.simular(q, cfg, "A", [0.7], np.zeros((1, T, 4)), pac)
    d8 = -recessivo.componentes_hiato(tr, q, tr["itens"])["item:governo"][0, 0, 1:9].sum() / 8
    assert d8 < 0.6


def test_total_ocupados_pnad():
    meta = json.loads((MIPD / "pnad_meta.json").read_text(encoding="utf-8"))
    pc = pd.read_csv(MIPD / "pnad_coeficientes.csv")
    assert pc["ocupados_2025_mil"].sum() == pytest.approx(meta["ocupados_pnad_2025_mil"], rel=0.01)


def test_composicoes_mesmo_total():
    T = 40
    tot = {c: sum(it["trilha"] for it in recessivo.pacote(c, T)) for c in recessivo.CONF["composicoes"]}
    ref = tot["pacote_base"]
    assert ref[-1] == pytest.approx(2.7)
    for c, x in tot.items():
        assert np.allclose(x, ref), c


def test_mesma_seed_mesmos_resultados(base):
    p, cfg = base
    q = recessivo.preparar_espec(p, "P2")
    from src import varredura
    ch = varredura.sortear_choques(p, 20, cfg["horizonte"], 42)
    pac = recessivo.pacote("pacote_base", cfg["horizonte"])
    a = recessivo.simular(q, copy.deepcopy(cfg), "C", [0.5], ch, pac)
    ch2 = varredura.sortear_choques(p, 20, cfg["horizonte"], 42)
    b = recessivo.simular(q, copy.deepcopy(cfg), "C", [0.5], ch2, pac)
    assert np.array_equal(np.nan_to_num(a["h"]), np.nan_to_num(b["h"]))
