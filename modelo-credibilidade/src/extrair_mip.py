"""Matriz insumo-produto: Leontief tipo I e II, demanda final por componente e multiplicadores.

Fontes (data/raw/ibge/):
- Matriz_de_Insumo_Produto_2015_Nivel_67.xls (IBGE): tabelas 03 (oferta e demanda da produção nacional a preço
  básico), 13 (matriz D de participação setorial), 14 (D·Bn) e 15 (Leontief).
- 68_tab2_2015.xls (TRU 2015, nível 68): valor adicionado, remunerações, valor da produção e ocupações por atividade.
- 12_tab1_2023.xls e 12_tab2_2023.xls (TRU 2023, nível 12): recursos e usos.

Saídas em data/processed/mip/: L_tipo1.npy, L_tipo2.npy (67 × 67), atividades_67.csv, demanda_final_2015.csv,
mip2015_multiplicadores_67.csv, mip2015_multiplicadores_setores.csv (12 grupos) e multiplicadores_tru12_2023.csv.

Uso: python -m src.extrair_mip
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "data" / "raw" / "ibge"
SAIDA = RAIZ / "data" / "processed" / "mip"
MIP = BRUTO / "Matriz_de_Insumo_Produto_2015_Nivel_67.xls"
log = logging.getLogger(__name__)

# premissas centrais do tipo II (famílias endógenas): propensão a consumir e impostos sobre a renda do trabalho
PROPENSAO, IMPOSTOS = 0.9, 0.15
COMPONENTES = {"exportacao": "Exportação", "governo": "Consumo do governo", "isflsf": "Consumo das  ISFLSF",
               "familias": "Consumo  das famílias", "fbcf": "Formação bruta de capital", "estoque": "Variação de estoque"}
GRUPOS = {1: "Agropecuária", 2: "Indústrias extrativas", 3: "Indústrias de transformação",
          4: "Eletricidade e gás, água, esgoto e resíduos", 5: "Construção", 6: "Comércio",
          7: "Transporte, armazenagem e correio", 8: "Informação e comunicação",
          9: "Atividades financeiras e de seguros", 10: "Atividades imobiliárias", 11: "Outras atividades de serviços",
          12: "Administração, defesa, saúde e educação públicas"}


def grupo_tru12(codigo: str) -> int:
    """Grupo da TRU nível 12 de uma atividade da MIP nível 67 (código de 4 dígitos, divisão CNAE 2.0)."""
    if codigo in ("8400", "8591", "8691"):
        return 12
    d = int(codigo[:2])
    if d in (55, 56):  # alojamento e alimentação
        return 11
    for lim, g in ((4, 1), (10, 2), (34, 3), (40, 4), (44, 5), (48, 6), (54, 7), (64, 8), (67, 9), (69, 10)):
        if d < lim:
            return g
    return 11


def _tabela(aba: str) -> pd.DataFrame:
    return pd.read_excel(MIP, sheet_name=aba, header=None)


def _codigos_cab(d: pd.DataFrame, linha: int = 3, col0: int = 2) -> list[str]:
    return [str(c).split("\n")[0].strip() for c in d.iloc[linha, col0:].tolist()]


def _bloco_quadrado(aba: str) -> tuple[list[str], list[str], np.ndarray]:
    """Matriz atividade × atividade (tabelas 14 e 15): códigos, descrições e valores."""
    d = _tabela(aba)
    linhas = d.iloc[5:, 0].astype(str).str.strip()
    ok = linhas.str.fullmatch(r"\d{4}")
    cod = linhas[ok].tolist()
    desc = d.iloc[5:, 1][ok].astype(str).str.strip().tolist()
    cab = _codigos_cab(d)
    M = d.iloc[5:, 2:2 + len(cab)][ok.values].astype(float).to_numpy()
    assert cab[:len(cod)] == cod, f"tabela {aba}: linhas e colunas fora de ordem"
    return cod, desc, M[:, :len(cod)]


def ler_mip() -> dict:
    cod, desc, L = _bloco_quadrado("15")
    _, _, A = _bloco_quadrado("14")
    # matriz D (atividade × produto) e demanda final da produção nacional por produto
    d13 = _tabela("13")
    linhas = d13.iloc[5:, 0].astype(str).str.strip()
    ok = linhas.str.fullmatch(r"\d{4}")
    prod_cab = [str(c).split("\n")[0].split(" ")[0].strip() for c in d13.iloc[3, 2:].tolist()]
    n_prod = sum(bool(pd.Series([p]).str.fullmatch(r"\d{5}").iloc[0]) for p in prod_cab)
    D = d13.iloc[5:, 2:2 + n_prod][ok.values].astype(float).to_numpy()
    d03 = _tabela("03")
    cab03 = [str(c).replace("\n", " ") for c in d03.iloc[3].tolist()]
    lin = d03.iloc[5:, 0].astype(str).str.strip()
    okp = lin.str.fullmatch(r"\d{5}")
    assert lin[okp].tolist() == prod_cab[:n_prod], "tabela 03: produtos fora da ordem da matriz D"
    f_prod = {}
    for chave, rotulo in COMPONENTES.items():
        j = next(k for k, c in enumerate(cab03) if c.startswith(rotulo))
        f_prod[chave] = d03.iloc[5:, j][okp.values].astype(float).to_numpy()
    f_set = {k: D @ v for k, v in f_prod.items()}
    # importações: coeficiente de insumos importados por atividade (soma das colunas de Bm, tabela 12) e parcela
    # importada da demanda final de cada componente (tabela 04 ÷ tabelas 03 + 04)
    d12 = _tabela("12")
    ok12 = d12.iloc[5:, 0].astype(str).str.strip().str.fullmatch(r"\d{5}")
    m_int = d12.iloc[5:, 2:2 + len(cod)][ok12.values].astype(float).to_numpy().sum(axis=0)
    d04 = _tabela("04")
    cab04 = [str(c).replace("\n", " ") for c in d04.iloc[3].tolist()]
    ok04 = d04.iloc[5:, 0].astype(str).str.strip().str.fullmatch(r"\d{5}")
    m_final = {}
    for chave, rotulo in COMPONENTES.items():
        j = next(k for k, c in enumerate(cab04) if c.startswith(rotulo))
        imp = d04.iloc[5:, j][ok04.values].astype(float).sum()
        m_final[chave] = imp / (imp + f_prod[chave].sum())
    return {"cod": cod, "desc": desc, "L": L, "A": A, "D": D, "f": f_set, "m_int": m_int, "m_final": m_final}


def ler_va_tru68() -> pd.DataFrame:
    """Componentes do valor adicionado e ocupações por atividade (TRU 2015 nível 68 agregada a 67 atividades)."""
    v = pd.read_excel(BRUTO / "68_tab2_2015.xls", sheet_name="VA", header=None)
    cod = [str(c).split("\n")[0].split(" ")[0].strip() for c in v.iloc[3, 1:-1].tolist()]
    nomes = {"va": "Valor adicionado bruto", "rem": "Remunerações", "sal": "Salários",
             "prev": "Previdência oficial", "vbp": "Valor da produção", "ocup": "Fator trabalho"}
    rot = v.iloc[:, 0].astype(str).str.strip()
    df = pd.DataFrame({k: v.iloc[rot.index[rot.str.startswith(n)][0], 1:-1].astype(float).to_numpy()
                       for k, n in nomes.items()}, index=cod)
    # a MIP nível 67 junta comércio e reparação de veículos (4500) com o comércio por atacado e varejo (4680)
    df.loc["4580"] = df.loc[["4500", "4680"]].sum()
    return df.drop(index=["4500", "4680"])


def tipo2(A: np.ndarray, rem_coef: np.ndarray, cons_coef: np.ndarray, propensao: float = PROPENSAO,
          impostos: float = IMPOSTOS) -> np.ndarray:
    """Leontief com as famílias endógenas: linha de renda do trabalho líquida e coluna de consumo."""
    n = A.shape[0]
    Ab = np.zeros((n + 1, n + 1))
    Ab[:n, :n] = A
    Ab[n, :n] = rem_coef * (1 - impostos)
    Ab[:n, n] = cons_coef * propensao
    return np.linalg.inv(np.eye(n + 1) - Ab)[:n, :n]


def multiplicadores(L: np.ndarray, L2: np.ndarray, coef: pd.DataFrame) -> pd.DataFrame:
    """Produção, emprego, renda e VA por unidade de demanda final (tipos I e II)."""
    out = pd.DataFrame(index=coef.index)
    out["prod_tipo1"] = L.sum(axis=0)
    out["prod_tipo2"] = L2.sum(axis=0)
    for k in ("va", "rem", "ocup"):
        c = coef[k].to_numpy()
        out[f"{k}_tipo1"] = c @ L
        out[f"{k}_tipo2"] = c @ L2
    return out


def agregar(mult: pd.DataFrame, peso: pd.Series, grupo: pd.Series) -> pd.DataFrame:
    """Multiplicadores dos 12 grupos: média ponderada pelo valor da produção de cada atividade."""
    m = mult.mul(peso, axis=0).groupby(grupo).sum().div(peso.groupby(grupo).sum(), axis=0)
    m.insert(0, "grupo_nome", [GRUPOS[g] for g in m.index])
    return m


def tru12_2023() -> pd.DataFrame:
    """Multiplicadores tipo I da TRU 2023 nível 12. Aproximação da MIP a partir da TRU: tecnologia baseada na
    atividade, consumo intermediário levado a preço básico pela razão oferta a preço básico ÷ oferta a preço de
    consumidor de cada produto, e importações retiradas na proporção da demanda interna."""
    t1 = pd.read_excel(BRUTO / "12_tab1_2023.xls", sheet_name=None, header=None)
    t2 = pd.read_excel(BRUTO / "12_tab2_2023.xls", sheet_name=None, header=None)
    num = lambda d, c0, c1: d.iloc[5:17, c0:c1].astype(float).to_numpy()  # noqa: E731
    V = num(t1["producao"], 2, 14).T  # atividade × produto
    importacao = num(t1["importacao"], 2, 3)[:, 0]
    of = t1["oferta"]
    preco_basico = num(of, 10, 11)[:, 0] / num(of, 2, 3)[:, 0]
    U = num(t2["CI"], 2, 14) * preco_basico[:, None]  # produto × atividade
    dem = t2["demanda"]
    dem_total, export = num(dem, 9, 10)[:, 0], num(dem, 2, 3)[:, 0]
    g = V.sum(axis=1)
    q = V.sum(axis=0)
    m = np.clip(importacao / np.maximum(dem_total * preco_basico - export, 1e-9), 0, 1)
    Bn = (1 - m)[:, None] * U / g[None, :]
    Dm = V / q[None, :]
    L = np.linalg.inv(np.eye(12) - Dm @ Bn)
    va = t2["VA"]
    rot = va.iloc[:, 0].astype(str).str.strip()
    ocup = va.iloc[rot.index[rot.str.startswith("Fator trabalho")][0], 1:13].astype(float).to_numpy()
    vbp = va.iloc[rot.index[rot.str.startswith("Valor da produção")][0], 1:13].astype(float).to_numpy()
    vab = va.iloc[rot.index[rot.str.startswith("Valor adicionado")][0], 1:13].astype(float).to_numpy()
    # a TRU 2023 publica a linha de ocupações zerada: o emprego de 2025 vem da PNAD Contínua (extrair_emprego.py)
    ocup = np.where(ocup > 0, ocup, np.nan)
    return pd.DataFrame({"grupo_nome": list(GRUPOS.values()), "prod_tipo1": L.sum(axis=0),
                         "ocup_tipo1": (ocup / vbp) @ L, "va_tipo1": (vab / vbp) @ L,
                         "vbp_2023": vbp, "va_2023": vab, "ocup_2023": ocup}, index=range(1, 13))


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    SAIDA.mkdir(parents=True, exist_ok=True)
    mip = ler_mip()
    va = ler_va_tru68().loc[mip["cod"]]
    coef = pd.DataFrame({k: va[k] / va["vbp"] for k in ("va", "rem", "sal", "prev", "ocup")}, index=mip["cod"])
    # cada R$ de renda disponível do trabalho vira PROPENSAO de consumo, na estrutura do consumo das famílias de 2015
    cons = mip["f"]["familias"]
    L2 = tipo2(mip["A"], coef["rem"].to_numpy(), cons / cons.sum())
    np.save(SAIDA / "L_tipo1.npy", mip["L"])
    np.save(SAIDA / "L_tipo2.npy", L2)
    np.save(SAIDA / "A_tecnico.npy", mip["A"])
    grupo = pd.Series([grupo_tru12(c) for c in mip["cod"]], index=mip["cod"])
    ativ = pd.DataFrame({"descricao": mip["desc"], "grupo": grupo, "vbp_2015": va["vbp"], "va_2015": va["va"],
                         "rem_2015": va["rem"], "sal_2015": va["sal"], "prev_2015": va["prev"],
                         "ocup_2015": va["ocup"]}, index=mip["cod"])
    ativ.index.name = "codigo"
    ativ.to_csv(SAIDA / "atividades_67.csv")
    f = pd.DataFrame(mip["f"], index=mip["cod"])
    f.index.name = "codigo"
    f.to_csv(SAIDA / "demanda_final_2015.csv")
    pd.DataFrame({"codigo": mip["cod"], "insumos_importados_por_vbp": mip["m_int"]}).to_csv(
        SAIDA / "importacoes_insumos_2015.csv", index=False)
    pd.Series(mip["m_final"], name="parcela_importada").rename_axis("componente").to_csv(
        SAIDA / "importacoes_demanda_final_2015.csv")
    mult = multiplicadores(mip["L"], L2, coef)
    mult.insert(0, "grupo", grupo)
    mult.insert(0, "descricao", mip["desc"])
    mult.index.name = "codigo"
    mult.to_csv(SAIDA / "mip2015_multiplicadores_67.csv")
    ag = agregar(mult.drop(columns=["descricao", "grupo"]), va["vbp"], grupo)
    ag.index.name = "grupo"
    ag.to_csv(SAIDA / "mip2015_multiplicadores_setores.csv")
    t12 = tru12_2023()
    t12.index.name = "grupo"
    t12.to_csv(SAIDA / "multiplicadores_tru12_2023.csv")
    log.info("transformação, produção tipo I: MIP 2015 = %.2f; TRU 2023 = %.2f",
             ag.loc[3, "prod_tipo1"], t12.loc[3, "prod_tipo1"])
    log.info("pronto: %s", SAIDA)


if __name__ == "__main__":
    main()
