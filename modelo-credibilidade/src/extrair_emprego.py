"""Coeficientes de emprego e renda: MIP/TRU 2015 e atualização para 2025 com a PNAD Contínua e as Contas Trimestrais.

Saídas em data/processed/mip/:
- emprego_renda_67.csv, emprego_renda_setores.csv (12 grupos), emprego_renda_tru12.csv: coeficientes por R$ milhão
  de produção (ocupações, remunerações, salários, contribuições) e multiplicadores de emprego e renda (tipos I e II).
- sensibilidade_tipo2.csv: multiplicadores tipo II para a grade de propensão a consumir × impostos.
- pnad_coeficientes.csv: ocupados (PNAD, média de 2025), formalidade (Censo 2022, calibrada à PNAD), rendimento
  habitual e coeficiente de emprego de 2025 por grupo da TRU; sidra_tabelas.csv registra as tabelas usadas.
- elasticidades_cnt.csv: sensibilidade do valor adicionado de cada grupo (CNT) ao hiato, ao juro real longo, ao
  câmbio real e ao IC-Br; okun.csv: coeficiente de Okun (PNAD, 2012–2026).

Cada tabela do SIDRA é validada pelo nome e pela variável no metadado antes do uso.
Uso: python -m src.extrair_emprego [--offline]
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from src import extrair_mip

RAIZ = Path(__file__).resolve().parent.parent
MIPD = RAIZ / "data" / "processed" / "mip"
CACHE = RAIZ / "data" / "raw" / "sidra"
API = "https://servicodados.ibge.gov.br/api/v3/agregados"
log = logging.getLogger(__name__)

# tabela: (trechos que o nome tem de conter, variável, trecho do nome da variável, classificação)
TABELAS = {
    5434: (["ocupadas", "grupamentos de atividades"], 4090, "ocupadas", 888),
    5442: (["rendimento médio mensal real", "grupamentos de atividade"], 5932, "habitualmente recebido", 888),
    4097: (["ocupadas", "posição na ocupação e categoria do emprego"], 4090, "ocupadas", 11913),
    4093: (["informalidade"], 12466, "taxa de informalidade", None),
    4099: (["taxas de desocupação"], 4099, "taxa de desocupação", None),
    10262: (["posição na ocupação e categoria do emprego", "seção de atividade"], 4090, "ocupadas", None),
    1846: (["preços correntes"], 585, "preços correntes", 11255),
    1621: (["índice de volume trimestral com ajuste sazonal"], 584, "ajuste sazonal", 11255),
}

# grupamentos da PNAD (classificação 888) → atividades da MIP nível 67; indústria geral = extrativa + utilidades
# (a transformação vem separada) e mal definidas são redistribuídas na proporção dos demais
PNAD_67 = {
    "47947": ["0191", "0192", "0280"],
    "60031": None,  # transformação: atividades do grupo 3
    "IND_RESTO": ["0580", "0680", "0791", "0792", "3500", "3680"],
    "47949": ["4180"],
    "47950": ["4580"],
    "56622": ["4900", "5000", "5100", "5280"],
    "56623": ["5500", "5600"],
    "56624": ["5800", "5980", "6100", "6280", "6480", "6800", "6980", "7180", "7380", "7700", "7880", "8000"],
    "60032": ["8400", "8591", "8592", "8691", "8692"],
    "56627": ["9080", "9480"],
    "56628": ["9700"],
}
# seções da CNAE no Censo 2022 (classificação 11805) → atividades da MIP nível 67
CENSO_67 = {
    "12640": "01", "12641": "02", "12642": "03", "12643": ["3500"], "12644": ["3680"], "95377": "05",
    "12645": "06", "12646": "07", "95379": ["5500", "5600"], "12647": "08", "12648": "09", "9205": "10",
    "12649": ["6980", "7180", "7380"], "12650": ["7700", "7880", "8000"], "95383": ["8400"],
    "95384": ["8591", "8592"], "12651": ["8691", "8692"], "12652": ["9080"], "12653": ["9480"], "95387": ["9700"],
}
# categorias-folha da posição na ocupação no Censo 2022 (classificação 11913) consideradas formais
FORMAIS = {"31722", "79367", "79369", "79370", "79372", "79375", "45934", "45936"}
INFORMAIS = {"31723", "79368", "79373", "79376", "45935", "45937", "31731"}
# setores da CNT (classificação 11255) → grupos da TRU nível 12
CNT_12 = {"90687": 1, "90692": 2, "90693": 3, "90695": 4, "90694": 5, "90697": 6, "90698": 7, "90699": 8,
          "90700": 9, "90702": 10, "90701": 11, "90703": 12}
# IRPF 2026 (Lei 15.270/2025): tabela mensal e redução que zera o imposto até R$ 5.000 e decresce até R$ 7.350
TABELA_IR = [(2428.80, 0.0, 0.0), (2826.65, 0.075, 182.16), (3751.05, 0.15, 394.16), (4664.68, 0.225, 675.49),
             (np.inf, 0.275, 908.73)]


# ---------------------------------------------------------------- SIDRA

def metadado(t: int) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    arq = CACHE / f"meta_{t}.json"
    if not arq.exists():
        arq.write_text(json.dumps(requests.get(f"{API}/{t}/metadados", timeout=120).json(), ensure_ascii=False),
                       encoding="utf-8")
    return json.loads(arq.read_text(encoding="utf-8"))


def validar(t: int) -> dict:
    """Confere nome da tabela e da variável no metadado; devolve o registro da tabela usada."""
    trechos, var, trecho_var, _ = TABELAS[t]
    m = metadado(t)
    nome = m["nome"].lower()
    assert all(x in nome for x in trechos), f"tabela {t} não confere: {m['nome']}"
    v = next(x for x in m["variaveis"] if x["id"] == var)
    assert trecho_var in v["nome"].lower(), f"variável {var} da tabela {t} não confere: {v['nome']}"
    return {"tabela": t, "nome": m["nome"], "variavel": var, "nome_variavel": v["nome"], "unidade": v["unidade"],
            "periodicidade": m["periodicidade"]["frequencia"]}


def baixar(t: int, classif: str | None = None, periodos: str = "all", offline: bool = False) -> pd.DataFrame:
    """Valores (período × categoria) de uma tabela do SIDRA, com cache em data/raw/sidra."""
    var = TABELAS[t][1]
    arq = CACHE / f"sidra_{t}{'_' + classif.split('[')[0] if classif else ''}.csv"
    if offline or arq.exists():
        return pd.read_csv(arq, dtype={"categoria": str})
    url = f"{API}/{t}/periodos/{periodos}/variaveis/{var}?localidades=N1[all]"
    if classif:
        url += f"&classificacao={classif}"
    r = requests.get(url, timeout=300).json()
    linhas = []
    for res in r[0]["resultados"]:
        cats = res["classificacoes"]
        cat = "|".join(next(iter(c["categoria"])) for c in cats) if cats else "total"
        for per, val in res["series"][0]["serie"].items():
            linhas.append({"periodo": per, "categoria": cat, "valor": pd.to_numeric(val, errors="coerce")})
    df = pd.DataFrame(linhas)
    df.to_csv(arq, index=False)
    return df


def serie_trimestral(df: pd.DataFrame) -> pd.DataFrame:
    w = df.pivot_table(index="periodo", columns="categoria", values="valor")
    w.index = pd.PeriodIndex([f"{p[:4]}Q{int(p[4:])}" for p in w.index.astype(str)], freq="Q").to_timestamp("Q")
    return w.sort_index()


# ---------------------------------------------------------------- 2015 (MIP/TRU)

def coeficientes_2015() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame]:
    ativ = pd.read_csv(MIPD / "atividades_67.csv", dtype={"codigo": str}).set_index("codigo")
    L = np.load(MIPD / "L_tipo1.npy")
    L2 = np.load(MIPD / "L_tipo2.npy")
    f = pd.read_csv(MIPD / "demanda_final_2015.csv", dtype={"codigo": str}).set_index("codigo")
    return ativ, L, L2, f


def emprego_renda(ativ, L, L2) -> pd.DataFrame:
    vbp = ativ["vbp_2015"]
    c = pd.DataFrame({"ocup_por_milhao": ativ["ocup_2015"] / vbp, "rem_por_vbp": ativ["rem_2015"] / vbp,
                      "sal_por_vbp": ativ["sal_2015"] / vbp, "prev_por_rem": ativ["prev_2015"] / ativ["rem_2015"],
                      "va_por_vbp": ativ["va_2015"] / vbp}, index=ativ.index)
    for k, col in (("emprego", "ocup_por_milhao"), ("renda", "rem_por_vbp")):
        x = c[col].to_numpy()
        c[f"mult_{k}_tipo1"] = x @ L
        c[f"mult_{k}_tipo2"] = x @ L2
        # multiplicador "tipo" (efeito total ÷ efeito direto)
        c[f"razao_{k}_tipo1"] = c[f"mult_{k}_tipo1"] / x
        c[f"razao_{k}_tipo2"] = c[f"mult_{k}_tipo2"] / x
    c.insert(0, "grupo", ativ["grupo"])
    c.insert(0, "descricao", ativ["descricao"])
    return c


def agregar_12(ativ: pd.DataFrame, er: pd.DataFrame) -> pd.DataFrame:
    g = ativ["grupo"]
    soma = ativ[["vbp_2015", "va_2015", "rem_2015", "sal_2015", "prev_2015", "ocup_2015"]].groupby(g).sum()
    out = pd.DataFrame({"grupo_nome": [extrair_mip.GRUPOS[k] for k in soma.index],
                        "ocup_por_milhao": soma["ocup_2015"] / soma["vbp_2015"],
                        "rem_por_vbp": soma["rem_2015"] / soma["vbp_2015"],
                        "sal_por_vbp": soma["sal_2015"] / soma["vbp_2015"],
                        "prev_por_rem": soma["prev_2015"] / soma["rem_2015"]}, index=soma.index)
    w = ativ["vbp_2015"]
    for col in [c for c in er.columns if c.startswith("mult_")]:
        out[col] = (er[col] * w).groupby(g).sum() / w.groupby(g).sum()
    return out.join(soma)


def sensibilidade_tipo2(ativ, f) -> pd.DataFrame:
    A = np.load(MIPD / "A_tecnico.npy")
    rem = (ativ["rem_2015"] / ativ["vbp_2015"]).to_numpy()
    ocup = (ativ["ocup_2015"] / ativ["vbp_2015"]).to_numpy()
    cons = f["familias"].to_numpy()
    peso = f.sum(axis=1).clip(lower=0).to_numpy()
    peso = peso / peso.sum()
    linhas = []
    for c in (0.8, 0.9, 1.0):
        for tx in (0.10, 0.15, 0.20):
            L2 = extrair_mip.tipo2(A, rem, cons / cons.sum(), c, tx)
            linhas.append({"propensao": c, "impostos": tx, "prod_tipo2_medio": float(L2.sum(axis=0) @ peso),
                           "emprego_tipo2_medio": float((ocup @ L2) @ peso),
                           "central": c == extrair_mip.PROPENSAO and tx == extrair_mip.IMPOSTOS})
    L = np.load(MIPD / "L_tipo1.npy")
    linhas.append({"propensao": np.nan, "impostos": np.nan, "prod_tipo2_medio": float(L.sum(axis=0) @ peso),
                   "emprego_tipo2_medio": float((ocup @ L) @ peso), "central": False, "nota": "tipo I"})
    return pd.DataFrame(linhas)


def tru12() -> pd.DataFrame:
    """VBP e VA da TRU 2023 nível 12. A TRU 2023 publica zeradas as ocupações e os componentes da renda
    (remunerações, salários, contribuições): os coeficientes de renda ficam em NaN e vêm da TRU 2015."""
    v = pd.read_excel(extrair_mip.BRUTO / "12_tab2_2023.xls", sheet_name="VA", header=None)
    rot = v.iloc[:, 0].astype(str).str.strip()
    def lin(s):
        x = v.iloc[rot.index[rot.str.startswith(s)][0], 1:13].astype(float).to_numpy()
        return np.where(x > 0, x, np.nan)
    vbp, rem, sal, prev, va = (lin(s) for s in ("Valor da produção", "Remunerações", "Salários",
                                                "Previdência oficial", "Valor adicionado"))
    return pd.DataFrame({"grupo_nome": list(extrair_mip.GRUPOS.values()), "vbp_2023": vbp, "va_2023": va,
                         "rem_2023": rem, "rem_por_vbp": rem / vbp, "sal_por_vbp": sal / vbp,
                         "prev_por_rem": prev / rem}, index=range(1, 13))


# ---------------------------------------------------------------- 2025 (PNAD, Censo, CNT)

def ocupados_67(ativ: pd.DataFrame, pnad: pd.Series) -> pd.Series:
    """Ocupados de 2025 (PNAD) distribuídos pelas 67 atividades na proporção das ocupações da TRU 2015."""
    o15 = ativ["ocup_2015"]
    grupos = {k: (v if v is not None else ativ.index[ativ["grupo"] == 3].tolist()) for k, v in PNAD_67.items()}
    tot = {k: pnad[k] for k in grupos if k in pnad}
    tot["IND_RESTO"] = pnad["47948"] - pnad["60031"]
    soma = sum(tot.values())
    fator = pnad["47946"] / soma  # mal definidas: redistribuídas na proporção dos demais
    out = pd.Series(0.0, index=ativ.index)
    for k, cods in grupos.items():
        out[cods] = tot[k] * fator * o15[cods] / o15[cods].sum()
    return out


def formalidade_67(ativ: pd.DataFrame, censo: pd.DataFrame, inf_pnad: float) -> tuple[pd.Series, float]:
    """Fração formal por atividade: estrutura do Censo 2022, calibrada à taxa de informalidade da PNAD de 2025."""
    c = censo.copy()
    c[["pos", "secao"]] = c["categoria"].str.split("|", expand=True)
    piv = c.pivot_table(index="secao", columns="pos", values="valor", aggfunc="sum")
    form = piv[[k for k in FORMAIS if k in piv]].sum(axis=1)
    inf = piv[[k for k in INFORMAIS if k in piv]].sum(axis=1)
    frac = (form / (form + inf)).to_dict()
    out = pd.Series(np.nan, index=ativ.index)
    for sec, alvo in CENSO_67.items():
        cods = alvo if isinstance(alvo, list) else ativ.index[ativ["grupo"] == int(alvo)].tolist()
        out[cods] = frac[sec]
    inf_censo = float(inf.sum() / (form.sum() + inf.sum()))
    # razão de chances constante: preserva a ordem entre setores e acerta a informalidade total da PNAD
    odds = out / (1 - out) * ((1 - inf_pnad) / inf_pnad) / ((1 - inf_censo) / inf_censo)
    return odds / (1 + odds), inf_censo


def ir_efetivo(renda_mensal: float) -> float:
    """Alíquota efetiva do IRPF 2026 sobre o rendimento mensal médio do setor (sem deduções além da redução)."""
    faixa = next(f for f in TABELA_IR if renda_mensal <= f[0])
    imposto = max(0.0, renda_mensal * faixa[1] - faixa[2])
    if renda_mensal <= 5000:
        imposto = 0.0
    elif renda_mensal <= 7350:
        imposto = max(0.0, imposto - (978.62 - 0.133145 * renda_mensal))
    return imposto / renda_mensal


def okun(desoc: pd.Series, hiato: pd.Series) -> dict:
    """Δ₄ desocupação = c + β Δ₄ hiato (diferenças de 4 trimestres removem a sazonalidade da PNAD)."""
    d = pd.DataFrame({"u": desoc, "h": hiato}).dropna()
    y = d["u"].diff(4).dropna()
    x = d["h"].diff(4).reindex(y.index)
    X = np.column_stack([np.ones(len(x)), x])
    b, *_ = np.linalg.lstsq(X, y.to_numpy(), rcond=None)
    res = y.to_numpy() - X @ b
    # erro-padrão HAC (Newey-West, 4 defasagens), porque as diferenças de 4 trimestres se sobrepõem
    n, k = X.shape
    u = X * res[:, None]
    S = u.T @ u
    for lag in range(1, 5):
        w = 1 - lag / 5
        G = u[lag:].T @ u[:-lag]
        S += w * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(XtXi @ S @ XtXi))
    return {"beta": b[1], "ep": se[1], "ic_lo": b[1] - 1.96 * se[1], "ic_hi": b[1] + 1.96 * se[1],
            "const": b[0], "n": n, "inicio": str(y.index[0].date()), "fim": str(y.index[-1].date())}


def elasticidades(va_vol: pd.DataFrame, painel: pd.DataFrame, icbr: pd.Series) -> pd.DataFrame:
    """Crescimento trimestral anualizado do VA de cada grupo (CNT, com ajuste sazonal) sobre a variação do hiato,
    do juro real longo, do câmbio real e do IC-Br em US$, 2004–2026."""
    X = pd.DataFrame(index=painel.index)
    X["dh"] = painel["h"].diff()
    X["dr_long"] = painel["ntnb10"].diff()
    X["de_real"] = 100 * np.log(painel["cambio"]).diff() - (painel["ipca12"] - 2.5) / 4
    X["dicbr"] = 100 * np.log(icbr.reindex(painel.index)).diff()
    linhas = []
    for cat, g in CNT_12.items():
        y = 400 * np.log(va_vol[cat]).diff()
        d = pd.concat([y.rename("y"), X], axis=1).loc["2004":].dropna()
        A = np.column_stack([np.ones(len(d)), d[["dh", "dr_long", "de_real", "dicbr"]].to_numpy()])
        b, *_ = np.linalg.lstsq(A, d["y"].to_numpy(), rcond=None)
        res = d["y"].to_numpy() - A @ b
        se = np.sqrt(np.diag(np.linalg.inv(A.T @ A)) * res.var(ddof=A.shape[1]))
        linhas.append({"grupo": g, "grupo_nome": extrair_mip.GRUPOS[g], "n": len(d),
                       **{f"b_{k}": v for k, v in zip(("const", "hiato", "r_long", "cambio_real", "icbr"), b)},
                       **{f"ep_{k}": v for k, v in zip(("const", "hiato", "r_long", "cambio_real", "icbr"), se)}})
    return pd.DataFrame(linhas).set_index("grupo")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ativ, L, L2, f = coeficientes_2015()
    er = emprego_renda(ativ, L, L2)
    er.to_csv(MIPD / "emprego_renda_67.csv")
    er12 = agregar_12(ativ, er)
    er12.index.name = "grupo"
    er12.to_csv(MIPD / "emprego_renda_setores.csv")
    t12 = tru12()
    t12.index.name = "grupo"
    t12.to_csv(MIPD / "emprego_renda_tru12.csv")
    sensibilidade_tipo2(ativ, f).to_csv(MIPD / "sensibilidade_tipo2.csv", index=False)

    reg = [validar(t) for t in TABELAS]
    pd.DataFrame(reg).to_csv(MIPD / "sidra_tabelas.csv", index=False)
    anos25 = "|".join(f"2025{q:02d}" for q in range(1, 5))
    pn = baixar(5434, "888[all]", offline=a.offline)
    pn25 = pn[pn["periodo"].astype(str).str.startswith("2025")].groupby("categoria")["valor"].mean()
    rd = baixar(5442, "888[all]", offline=a.offline)
    rd25 = rd[rd["periodo"].astype(str).str.startswith("2025")].groupby("categoria")["valor"].mean()
    inf = baixar(4093, None, offline=a.offline)
    inf25 = float(inf[inf["periodo"].astype(str).str.startswith("2025")]["valor"].mean()) / 100
    censo = baixar(10262, "11913[all]|11805[all]", periodos="2022", offline=a.offline)
    cnt_cor = serie_trimestral(baixar(1846, "11255[all]", offline=a.offline))
    cnt_vol = serie_trimestral(baixar(1621, "11255[all]", offline=a.offline))
    desoc = serie_trimestral(baixar(4099, None, offline=a.offline))["total"]

    o25 = ocupados_67(ativ, pn25)
    fr25, inf_censo = formalidade_67(ativ, censo, inf25)
    g = ativ["grupo"]
    # VBP de 2025 = VBP da TRU 2023 × (VA corrente de 2025 ÷ VA corrente de 2023), por grupo
    va_ano = cnt_cor.groupby(cnt_cor.index.year).sum()
    cresc = pd.Series({gr: va_ano.loc[2025, cat] / va_ano.loc[2023, cat] for cat, gr in CNT_12.items()})
    vbp25 = t12["vbp_2023"] * cresc
    # rendimento habitual por grupo: o grupamento da PNAD de cada atividade, ponderado pelos ocupados
    rend_cat = {}
    for k, cods in PNAD_67.items():
        cods = cods if cods is not None else ativ.index[g == 3].tolist()
        chave = "60031" if k == "60031" else ("47948" if k == "IND_RESTO" else k)
        for c in cods:
            rend_cat[c] = rd25[chave]
    rend67 = pd.Series(rend_cat).reindex(ativ.index)
    ocup12 = o25.groupby(g).sum()
    pc = pd.DataFrame({
        "grupo_nome": [extrair_mip.GRUPOS[k] for k in ocup12.index],
        "ocupados_2025_mil": ocup12, "ocupados_2015_mil": ativ["ocup_2015"].groupby(g).sum() / 1000,
        "fracao_formal": (fr25 * o25).groupby(g).sum() / ocup12,
        "rendimento_medio_mensal": (rend67 * o25).groupby(g).sum() / ocup12,
        "vbp_2025_milhoes": vbp25,
        "coef_emprego_2025": ocup12 * 1000 / vbp25, "coef_emprego_2015": er12["ocup_por_milhao"],
    })
    pc["ir_efetivo"] = pc["rendimento_medio_mensal"].map(ir_efetivo)
    pc["prev_por_rem"] = er12["prev_por_rem"]  # TRU 2015: a TRU 2023 não publica os componentes da renda
    pc["var_coef_nominal_pct"] = 100 * (pc["coef_emprego_2025"] / pc["coef_emprego_2015"] - 1)
    # em termos reais: VBP de 2025 a preços de 2015 pelo deflator implícito do VA de cada grupo (CNT)
    vol_ano = cnt_vol.groupby(cnt_vol.index.year).mean()
    defl = pd.Series({gr: (va_ano.loc[2025, c] / va_ano.loc[2015, c]) / (vol_ano.loc[2025, c] / vol_ano.loc[2015, c])
                      for c, gr in CNT_12.items()})
    pc["deflator_2025_2015"] = defl
    pc["var_coef_real_pct"] = 100 * (pc["coef_emprego_2025"] * defl / pc["coef_emprego_2015"] - 1)
    # multiplicadores de emprego atualizados (coeficiente de 2025 a preços de 2015) e ordem relativa dos setores
    fator = (pc["coef_emprego_2025"] * defl / pc["coef_emprego_2015"]).reindex(g).to_numpy()
    oc = (ativ["ocup_2015"] / ativ["vbp_2015"]).to_numpy() * fator
    w = ativ["vbp_2015"]
    for tipo, M in (("tipo1", L), ("tipo2", L2)):
        m67 = pd.Series(oc @ M, index=ativ.index)
        pc[f"mult_emprego_{tipo}_2025"] = (m67 * w).groupby(g).sum() / w.groupby(g).sum()
        pc[f"mult_emprego_{tipo}_2015"] = er12[f"mult_emprego_{tipo}"]
        pc[f"spearman_{tipo}"] = pc[f"mult_emprego_{tipo}_2025"].rank().corr(pc[f"mult_emprego_{tipo}_2015"].rank())
    pc.index.name = "grupo"
    pc.attrs = {}
    pc.to_csv(MIPD / "pnad_coeficientes.csv")
    pd.DataFrame({"codigo": ativ.index, "ocupados_2025_mil": o25.values, "fracao_formal": fr25.values,
                  "rendimento_medio_mensal": rend67.values}).to_csv(MIPD / "pnad_67.csv", index=False)
    meta = {"informalidade_pnad_2025": inf25, "informalidade_censo_2022": inf_censo,
            "ocupados_pnad_2025_mil": float(pn25["47946"]), "ocupados_distribuidos_mil": float(o25.sum())}
    (MIPD / "pnad_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    painel = pd.read_csv(RAIZ / "data" / "processed" / "trimestral.csv", parse_dates=["trimestre"]).set_index(
        "trimestre")
    sgs = pd.read_csv(RAIZ / "data" / "raw" / "sgs_29042.csv", parse_dates=["data"])  # IC-Br em US$, mensal
    icbr = sgs.set_index("data").iloc[:, -1].astype(float).resample("QE").mean()
    elasticidades(cnt_vol, painel, icbr).to_csv(MIPD / "elasticidades_cnt.csv")
    pd.DataFrame([okun(desoc, painel["h"])]).to_csv(MIPD / "okun.csv", index=False)
    log.info("ocupados 2025: PNAD %.0f mil; distribuídos %.0f mil; informalidade PNAD %.1f%%, Censo %.1f%%",
             pn25["47946"], o25.sum(), 100 * inf25, 100 * inf_censo)
    log.info("pronto: %s", MIPD)


if __name__ == "__main__":
    main()
