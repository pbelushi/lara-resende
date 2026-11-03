"""Coleta e tratamento dos dados públicos; preenche automaticamente calibracao.yaml.

Fontes: BCB/SGS (REST + webservice de metadados para validar nomes), BCB/Focus
(API Olinda via python-bcb), Tesouro Direto (taxas de NTN-B) e Tesouro (RTN).
Cada série é baixada de forma independente: uma falha é registrada e não
interrompe as demais.
"""
from __future__ import annotations

import html
import io
import logging
import re
import time
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yaml
from scipy import sparse
from scipy.sparse.linalg import spsolve

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
PROC = RAIZ / "data" / "processed"
MARCADOR_AUTO = "# >>> AUTO"
INICIO_HIST = "2000-01-01"

log = logging.getLogger(__name__)

# nome -> (código SGS, termos que devem constar no nome oficial, agregação trimestral)
SERIES_SGS = {
    "meta_selic": (432, ["meta selic"], "fim"),
    "selic": (4189, ["selic", "anualizada"], "media"),
    "ipca_m": (433, ["ipca"], "ipca12"),
    "dbgg": (13762, ["divida bruta do governo geral", "% pib"], "fim"),
    "dlsp": (4513, ["divida liquida do setor publico", "% pib", "consolidado"], "fim"),
    "reservas": (3546, ["reservas internacionais"], "fim"),
    "cambio": (1, ["cambio", "dolar"], "media"),
    "nfsp_prim_spc": (5793, ["resultado primario", "setor publico consolidado", "12 meses"], "fim"),
    "nfsp_prim_gc": (5783, ["resultado primario", "governo federal e banco central", "12 meses"], "fim"),
    "pib_12m": (4382, ["pib acumulado dos ultimos 12 meses"], "fim"),
    "pib_real": (22109, ["pib trimestral", "dessazonalizados"], "fim"),
    "part_cambio": (10622, ["participacao por indexador", "cambio"], "fim"),
    "part_tr": (10623, ["participacao por indexador", "tr"], "fim"),
    "part_igpm": (10624, ["participacao por indexador", "igp-m"], "fim"),
    "part_igpdi": (10625, ["participacao por indexador", "igp-di"], "fim"),
    "part_ipca": (10626, ["participacao por indexador", "ipc-a"], "fim"),
    "part_inpc": (10627, ["participacao por indexador", "inpc"], "fim"),
    "part_selic": (10628, ["participacao por indexador", "selic"], "fim"),
    "part_pre": (10629, ["participacao por indexador", "prefixado"], "fim"),
    "part_tjlp": (10630, ["participacao por indexador", "tjlp"], "fim"),
    "part_outros": (10631, ["participacao por indexador", "outros"], "fim"),
    "part_oma": (10632, ["participacao por indexador", "mercado aberto"], "fim"),
    "prazo_ltn": (10613, ["prazo", "ltn"], "fim"),
    "prazo_ntnb": (10608, ["prazo", "ntn-b"], "fim"),
    "prazo_lft": (10614, ["prazo medio", "lft"], "fim"),
}

# coluna do painel -> série bruta de origem (para registrar a data real da última observação)
ORIGEM = {
    "meta_selic": "meta_selic", "ipca12": "ipca_m", "dbgg": "dbgg", "dlsp": "dlsp", "reservas_bi": "reservas",
    "cambio": "cambio", "pib_12m_bi": "pib_12m", "s_spc": "nfsp_prim_spc", "s_gc": "nfsp_prim_gc",
    "gamma": "pib_12m", "h": "pib_real", "g_12m": "pib_real", "g_tend": "pib_real", "w_lft": "part_selic",
    "w_pre": "part_pre", "w_ipca": "part_ipca", "w_fx": "part_cambio", "w_oma": "part_oma",
    "prazo_ltn": "prazo_ltn", "prazo_ntnb": "prazo_ntnb", "prazo_lft": "prazo_lft",
    "pi_e": "focus_ipca12m", "ntnb10": "ntnb", "ntnb5": "ntnb",
}

URL_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{c}/dados"
URL_SGS_WS = "https://www3.bcb.gov.br/wssgs/services/FachadaWSSGS"
URL_CKAN = "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id={id}"
CKAN_TD = "taxas-dos-titulos-ofertados-pelo-tesouro-direto"
CKAN_RTN = "resultado-do-tesouro-nacional"


def normalizar(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", txt.lower()).strip()


# ---------------------------------------------------------------- SGS

def nome_sgs(codigo: int) -> str | None:
    """Nome oficial da série no webservice de metadados do SGS."""
    corpo = (
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:pub="http://publico.ws.casosdeuso.sgs.pec.bcb.gov.br"><soapenv:Body>'
        f"<pub:getUltimoValorXML><codigoSerie>{codigo}</codigoSerie></pub:getUltimoValorXML>"
        "</soapenv:Body></soapenv:Envelope>"
    )
    r = requests.post(URL_SGS_WS, data=corpo.encode(), timeout=60,
                      headers={"Content-Type": "text/xml;charset=UTF-8", "SOAPAction": '""'})
    r.raise_for_status()
    try:
        texto = r.content.decode("utf-8")
    except UnicodeDecodeError:
        texto = r.content.decode("latin-1")
    m = re.search(r"<NOME>(.*?)</NOME>", html.unescape(texto), re.S)
    return m.group(1).strip() if m else None


def validar_codigos(series: dict = SERIES_SGS) -> pd.DataFrame:
    """Testa se cada código existe e se o nome oficial contém os termos esperados."""
    linhas = []
    for nome, (codigo, termos, _) in series.items():
        try:
            oficial = nome_sgs(codigo)
            ok = oficial is not None and all(t in normalizar(oficial) for t in termos)
            erro = "" if ok else "nome não confere" if oficial else "série inexistente"
        except Exception as e:  # noqa: BLE001 - registrar e seguir
            oficial, ok, erro = None, False, str(e)
        if not ok:
            log.error("SGS %s (%s): %s", codigo, nome, erro)
        linhas.append({"serie": nome, "codigo": codigo, "nome_oficial": oficial, "ok": ok, "erro": erro})
    return pd.DataFrame(linhas)


def _get_json_retentando(url: str, params: dict, tentativas: int = 4) -> list:
    """A API do SGS falha de forma intermitente; um bloco vazio só é aceito com status 404."""
    for k in range(tentativas):
        try:
            r = requests.get(url, params=params, timeout=120)
            if r.status_code == 404:
                return []
            if r.status_code == 200 and r.text.strip().startswith("["):
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2 * (k + 1))
    raise ConnectionError(f"falha após {tentativas} tentativas: {url} {params}")


def baixar_sgs(codigo: int, inicio: str = INICIO_HIST, offline: bool = False) -> pd.Series:
    """Baixa a série em blocos de 5 anos (limite da API para séries diárias) e guarda em data/raw."""
    arq = RAW / f"sgs_{codigo}.csv"
    if offline and arq.exists():
        return pd.read_csv(arq, index_col=0, parse_dates=True).iloc[:, 0]
    partes = []
    ini = pd.Timestamp(inicio)
    hoje = pd.Timestamp(date.today())
    while ini <= hoje:
        fim = min(ini + pd.DateOffset(years=5) - pd.DateOffset(days=1), hoje)
        params = {"formato": "json", "dataInicial": ini.strftime("%d/%m/%Y"),
                  "dataFinal": fim.strftime("%d/%m/%Y")}
        partes.extend(_get_json_retentando(URL_SGS.format(c=codigo), params))
        ini = fim + pd.DateOffset(days=1)
    if not partes:
        raise ValueError(f"SGS {codigo}: nenhum dado retornado")
    df = pd.DataFrame(partes)
    s = pd.Series(pd.to_numeric(df["valor"], errors="coerce").values,
                  index=pd.to_datetime(df["data"], dayfirst=True), name=str(codigo))
    s = s[~s.index.duplicated()].sort_index().dropna()
    s.to_csv(arq)
    return s


def trimestralizar(s: pd.Series, metodo: str) -> pd.Series:
    if metodo == "ipca12":
        s = ((1 + s / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
        metodo = "fim"
    q = s.resample("QE")
    return (q.mean() if metodo == "media" else q.last()).dropna()


# ---------------------------------------------------------------- Focus

INDICADORES_FOCUS_ANUAIS = ["Selic", "PIB Total", "Câmbio", "IPCA", "Resultado primário",
                            "Dívida líquida do setor público"]


def baixar_focus(offline: bool = False) -> dict:
    """Medianas do Focus: IPCA 12m à frente e o histórico das expectativas anuais.

    O histórico anual permite usar a pesquisa vigente no t0 (e não a mais recente) e montar,
    na validação de P3, o primário que o mercado esperava em cada data.
    """
    arq = RAW / "focus_ipca12m.csv"
    arq_anual = RAW / "focus_anuais_historico.csv"
    if offline and arq.exists() and arq_anual.exists():
        ipca = pd.read_csv(arq, index_col=0, parse_dates=True).iloc[:, 0]
        anuais = pd.read_csv(arq_anual, parse_dates=["Data"])
    else:
        from bcb import Expectativas

        em = Expectativas()
        ep = em.get_endpoint("ExpectativasMercadoInflacao12Meses")
        df = (ep.query().filter(ep.Indicador == "IPCA", ep.Suavizada == "S", ep.baseCalculo == 0)
              .select(ep.Data, ep.Mediana).collect())
        ipca = df.set_index(pd.to_datetime(df["Data"]))["Mediana"].sort_index()
        ipca.to_csv(arq)
        ep = em.get_endpoint("ExpectativasMercadoAnuais")
        partes = []
        for ind in INDICADORES_FOCUS_ANUAIS:
            d = (ep.query().filter(ep.Indicador == ind, ep.baseCalculo == 0)
                 .select(ep.Indicador, ep.Data, ep.DataReferencia, ep.Mediana).collect())
            partes.append(d)
        anuais = pd.concat(partes)
        anuais["Data"] = pd.to_datetime(anuais["Data"])
        anuais.to_csv(arq_anual, index=False)
    anuais["DataReferencia"] = anuais["DataReferencia"].astype(int)
    return {"ipca12m": ipca, "anuais": anuais}


def pesquisa_focus(anuais: pd.DataFrame, indicador: str, ate: pd.Timestamp) -> pd.Series:
    """Medianas por ano de referência na última pesquisa até a data `ate`."""
    d = anuais[(anuais["Indicador"] == indicador) & (anuais["Data"] <= ate)]
    if d.empty:
        return pd.Series(dtype=float)
    d = d[d["Data"] == d["Data"].max()]
    return d.set_index("DataReferencia")["Mediana"].astype(float).sort_index()


def fim_ultimo_trimestre_fechado(hoje: date | None = None) -> pd.Timestamp:
    hoje = pd.Timestamp(hoje or date.today())
    return (hoje.to_period("Q").start_time - pd.Timedelta(days=1)).normalize()


# ---------------------------------------------------------------- Tesouro

def _url_ckan(pacote: str, filtro) -> str:
    r = requests.get(URL_CKAN.format(id=pacote), timeout=60)
    r.raise_for_status()
    for rec in r.json()["result"]["resources"]:
        if filtro(rec):
            return rec["url"]
    raise ValueError(f"recurso não encontrado em {pacote}")


TIPOS_TD = {"tesouro ipca+": "ntnb", "tesouro ipca+ com juros semestrais": "ntnb",
            "tesouro prefixado": "pre", "tesouro prefixado com juros semestrais": "pre"}


def baixar_tesouro_direto(offline: bool = False) -> pd.DataFrame:
    """Taxas (compra, manhã) de NTN-B e prefixados por data e vencimento, do Tesouro Direto."""
    arq = RAW / "tesouro_direto_taxas.csv"
    if offline and arq.exists():
        return pd.read_csv(arq, parse_dates=["base", "venc"])
    url = _url_ckan(CKAN_TD, lambda r: str(r.get("format", "")).upper() == "CSV"
                    and "preco" in normalizar(r["name"] + r["url"]).replace(" ", ""))
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    td = pd.read_csv(io.BytesIO(r.content), sep=";", decimal=",", encoding="latin-1")
    td.columns = [normalizar(c) for c in td.columns]
    td["classe"] = td["tipo titulo"].map(normalizar).map(TIPOS_TD)
    td = td[td["classe"].notna()]
    td = pd.DataFrame({"classe": td["classe"], "base": pd.to_datetime(td["data base"], dayfirst=True),
                       "venc": pd.to_datetime(td["data vencimento"], dayfirst=True),
                       "taxa": pd.to_numeric(td["taxa compra manha"], errors="coerce")})
    td = td[td["taxa"] > 0]
    td.to_csv(arq, index=False)
    return td


def baixar_ntnb(offline: bool = False) -> pd.DataFrame:
    """Taxa real das NTN-B com prazo mais próximo de 5 e 10 anos, por dia."""
    td = baixar_tesouro_direto(offline)
    td = td[td["classe"] == "ntnb"].copy()
    td["anos"] = (td["venc"] - td["base"]).dt.days / 365.25
    saida = {}
    for alvo in (5, 10):
        idx = (td.assign(dist=(td["anos"] - alvo).abs()).groupby("base")["dist"].idxmin())
        saida[f"ntnb{alvo}"] = td.loc[idx].set_index("base")["taxa"]
    return pd.DataFrame(saida).sort_index()


# ---------------------------------------------------------------- duração de Macaulay

CKAN_ESTOQUE = "estoque-da-divida-publica-federal"
CUPOM_ANUAL = {"NTN-B": 0.06, "NTN-F": 0.10, "LTN": 0.0, "NTN-B Principal": 0.0}


def baixar_estoque_dpf(offline: bool = False) -> pd.DataFrame:
    """Estoque da DPF por título e vencimento (Tesouro Transparente), R$."""
    arq = RAW / "estoque_dpf.csv"
    if offline and arq.exists():
        return pd.read_csv(arq, parse_dates=["mes", "venc"])
    url = _url_ckan(CKAN_ESTOQUE, lambda r: str(r.get("format", "")).upper() == "CSV")
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    e = pd.read_csv(io.BytesIO(r.content), sep=";", decimal=",", encoding="latin-1")
    e.columns = [normalizar(c) for c in e.columns]
    titulo = e["titulo/contrato"].astype(str).str.strip()
    out = pd.DataFrame({
        "titulo": titulo.str.rsplit(" ", n=1).str[0],
        "venc": pd.to_datetime(e["vencimento do titulo/contrato"], dayfirst=True, errors="coerce"),
        "valor": pd.to_numeric(e["valor do estoque"], errors="coerce"),
        "mes": pd.to_datetime(e["mes do estoque"], format="%m/%Y", errors="coerce"),
        "classe": e["classe da carteira"].astype(str),
        "tipo": e["tipo de divida"].astype(str).map(normalizar),
    })
    out = out[out["venc"].notna()]
    out.to_csv(arq, index=False)
    return out


def macaulay(t_venc: float, cupom_anual: float, taxa: float) -> float:
    """Duração de Macaulay (anos) de um título com cupons semestrais, descontado à taxa anual `taxa` (%)."""
    if t_venc <= 0:
        return 0.0
    c = (1 + cupom_anual) ** 0.5 - 1 if cupom_anual else 0.0
    tempos = np.arange(t_venc, 0, -0.5)[::-1] if c else np.array([t_venc])
    fluxos = np.full(tempos.size, c)
    fluxos[-1] += 1
    vp = fluxos / (1 + taxa / 100) ** tempos
    return float((tempos * vp).sum() / vp.sum())


def duracoes_macaulay(estoque: pd.DataFrame, td: pd.DataFrame, ate: pd.Timestamp) -> dict:
    """Duração de Macaulay e prazo médio ponderados pelo estoque, por classe (NTN-B; prefixados LTN + NTN-F).

    Cada título é descontado pela taxa do Tesouro Direto da mesma classe com vencimento mais próximo.
    """
    mes = estoque.loc[estoque["mes"] <= ate, "mes"].max()
    e = estoque[estoque["mes"] == mes].groupby(["titulo", "venc"], as_index=False)["valor"].sum()
    data_ref = mes + pd.offsets.MonthEnd(0)
    tdm = td[td["base"] <= data_ref]
    tdm = tdm[tdm["base"] == tdm["base"].max()]
    saida = {"duracao_mes_estoque": mes.strftime("%Y-%m"), "duracao_data_taxas": tdm["base"].max().strftime("%Y-%m-%d")}
    for classe, titulos in (("ipca", ("NTN-B", "NTN-B Principal")), ("pre", ("LTN", "NTN-F"))):
        sub = e[e["titulo"].isin(titulos) & (e["venc"] > data_ref)].copy()
        curva = tdm[tdm["classe"] == ("ntnb" if classe == "ipca" else "pre")]
        sub["t"] = (sub["venc"] - data_ref).dt.days / 365.25
        taxas = []
        for v in sub["venc"]:
            k = (curva["venc"] - v).abs().idxmin()
            taxas.append(curva.loc[k, "taxa"])
        sub["taxa"] = taxas
        sub["dur"] = [macaulay(t, CUPOM_ANUAL[ti], tx) for t, ti, tx in zip(sub["t"], sub["titulo"], sub["taxa"])]
        w = sub["valor"] / sub["valor"].sum()
        saida[f"dur_{classe}_anos"] = float((w * sub["dur"]).sum())
        saida[f"prazo_{classe}_estoque_anos"] = float((w * sub["t"]).sum())
    return saida


def decomposicao_lft(estoque: pd.DataFrame, ate: pd.Timestamp) -> dict:
    """Participação da LFT do Tesouro em mercado na DPMFi em mercado (Tesouro Transparente)."""
    mes = estoque.loc[estoque["mes"] <= ate, "mes"].max()
    e = estoque[(estoque["mes"] == mes) & (estoque["classe"] == "Mercado") & estoque["tipo"].str.contains("interna")]
    return {"mes": mes.strftime("%Y-%m"),
            "lft_mercado_share": float(e.loc[e["titulo"] == "LFT", "valor"].sum() / e["valor"].sum())}


# rótulo normalizado (início da linha) -> nome
LINHAS_RTN = {
    "3. receita liquida": "rec_liq",
    "4. despesa total": "desp_total",
    "4.1 beneficios previdenciarios": "prev",
    "4.2 pessoal e encargos sociais": "pessoal",
    "4.3 outras despesas obrigatorias": "outras_obrig",
    "4.4.1 obrigatorias com controle de fluxo": "fluxo",
    "4.4.2 despesas discricionarias": "disc",
}


def baixar_rtn(offline: bool = False) -> pd.DataFrame:
    """Tabela 1.1 do RTN (R$ milhões correntes, mensal) para as linhas usadas no bloco fiscal."""
    arq = RAW / "rtn_tabela_1_1.csv"
    if offline and arq.exists():
        return pd.read_csv(arq, index_col=0, parse_dates=True)
    url = _url_ckan(CKAN_RTN, lambda r: str(r.get("format", "")).upper() == "XLSX"
                    and "serie" in normalizar(r["name"]))
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    bruto = pd.read_excel(io.BytesIO(r.content), sheet_name="1.1", header=None)
    lin_cab = bruto.index[bruto.iloc[:, 0].astype(str).map(normalizar) == "discriminacao"][0]
    datas = pd.to_datetime(bruto.iloc[lin_cab, 1:], errors="coerce")
    saida = {}
    for _, linha in bruto.iloc[lin_cab + 1:].iterrows():
        rot = normalizar(str(linha.iloc[0]))
        for prefixo, nome in LINHAS_RTN.items():
            if rot.startswith(prefixo) and nome not in saida:
                saida[nome] = pd.to_numeric(linha.iloc[1:], errors="coerce").values
    df = pd.DataFrame(saida, index=datas.values).loc[lambda d: d.index.notna()].sort_index()
    df.to_csv(arq)
    return df


# ---------------------------------------------------------------- tratamento

def filtro_hp(y: pd.Series, lamb: float = 1600.0) -> pd.Series:
    n = len(y)
    e = np.ones(n)
    D = sparse.spdiags([e, -2 * e, e], [0, 1, 2], n - 2, n)
    tendencia = spsolve(sparse.csc_matrix(sparse.eye(n) + lamb * D.T @ D), y.values)
    return pd.Series(tendencia, index=y.index)


def montar_painel(offline: bool = False) -> tuple[pd.DataFrame, dict, list[str]]:
    """Baixa tudo, trimestraliza e devolve (painel trimestral, dados auxiliares, erros)."""
    RAW.mkdir(parents=True, exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)
    erros: list[str] = []
    fim = fim_ultimo_trimestre_fechado()
    corta = lambda s: s[s.index <= fim]  # noqa: E731 - t0 = último trimestre fechado
    ultima_obs: dict = {}
    q = {}
    for nome, (codigo, _, metodo) in SERIES_SGS.items():
        try:
            bruto = corta(baixar_sgs(codigo, offline=offline))
            ultima_obs[nome] = bruto.index[-1].strftime("%Y-%m-%d")
            q[nome] = trimestralizar(bruto, metodo)
        except Exception as e:  # noqa: BLE001
            erros.append(f"SGS {codigo} ({nome}): {e}")
            log.error(erros[-1])
    painel = pd.DataFrame(q)
    painel = painel.rename(columns={"ipca_m": "ipca12"})

    aux: dict = {"fim_t0": fim, "ultima_obs": ultima_obs}
    try:
        focus = baixar_focus(offline)
        ipca12m = corta(focus["ipca12m"])
        painel["pi_e"] = ipca12m.resample("QE").mean()
        ultima_obs["focus_ipca12m"] = ipca12m.index[-1].strftime("%Y-%m-%d")
        aux["focus_anuais"] = focus["anuais"]
    except Exception as e:  # noqa: BLE001
        erros.append(f"Focus: {e}")
        log.error(erros[-1])
    try:
        ntnb = corta(baixar_ntnb(offline))
        ultima_obs["ntnb"] = ntnb.index[-1].strftime("%Y-%m-%d")
        painel = painel.join(ntnb.resample("QE").mean(), how="left")
    except Exception as e:  # noqa: BLE001
        erros.append(f"Tesouro Direto (NTN-B): {e}")
        log.error(erros[-1])
    try:
        aux["duracoes"] = duracoes_macaulay(baixar_estoque_dpf(offline), baixar_tesouro_direto(offline), fim)
    except Exception as e:  # noqa: BLE001
        erros.append(f"Estoque da DPF / duração de Macaulay: {e}")
        log.error(erros[-1])
    try:
        aux["rtn"] = baixar_rtn(offline)
    except Exception as e:  # noqa: BLE001
        erros.append(f"RTN: {e}")
        log.error(erros[-1])

    painel = painel[(painel.index >= INICIO_HIST) & (painel.index <= fim)]
    # Unidades e sinais: primário positivo = superávit; reservas e PIB em bilhões.
    painel["s_spc"] = -painel["nfsp_prim_spc"]
    painel["s_gc"] = -painel["nfsp_prim_gc"]
    painel["reservas_bi"] = painel["reservas"] / 1e3
    painel["pib_12m_bi"] = painel["pib_12m"] / 1e3
    # Hiato (HP) e crescimento real anualizado
    lpib = np.log(painel["pib_real"].dropna())
    tend = filtro_hp(lpib)
    painel["h"] = 100 * (lpib - tend)
    painel["g"] = 100 * (np.exp(4 * lpib.diff()) - 1)
    painel["g_tend"] = 100 * (np.exp(4 * tend.diff()) - 1)
    painel["g_12m"] = 100 * (np.exp(lpib.diff(4)) - 1)
    # Câmbio: depreciação trimestral e em 12 meses (%)
    painel["de"] = 100 * painel["cambio"].pct_change(fill_method=None)
    painel["de12"] = 100 * painel["cambio"].pct_change(4, fill_method=None)
    # Deflator implícito (PIB nominal 12m vs real 12m) e crescimento nominal
    painel["gamma"] = 100 * painel["pib_12m"].pct_change(4, fill_method=None)
    # Composição da dívida (DPMFi, custódia explicitando operações de mercado aberto)
    lft = painel["part_selic"] + painel["part_oma"]
    pre = painel["part_pre"] + painel["part_tr"].fillna(0) + painel["part_tjlp"].fillna(0) + painel["part_outros"].fillna(0)
    ipca = painel["part_ipca"] + painel["part_igpm"].fillna(0) + painel["part_igpdi"].fillna(0) + painel["part_inpc"].fillna(0)
    fx = painel["part_cambio"]
    tot = lft + pre + ipca + fx
    painel["w_lft"], painel["w_pre"], painel["w_ipca"], painel["w_fx"] = lft / tot, pre / tot, ipca / tot, fx / tot
    painel["w_oma"] = painel["part_oma"] / tot
    painel.index.name = "trimestre"
    painel.to_csv(PROC / "trimestral.csv")
    return painel, aux, erros


def ultimo(painel: pd.DataFrame, col: str):
    s = painel[col].dropna() if col in painel else pd.Series(dtype=float)
    if s.empty:
        return None, None
    return float(s.iloc[-1]), s.index[-1].strftime("%Y-%m-%d")


def trajetoria_focus_selic(selic_anual: pd.Series, i0: float, data_base: pd.Timestamp, n: int = 8) -> list[float]:
    """Selic esperada nos próximos n trimestres, interpolando entre i0 e as medianas de fim de ano."""
    sel = selic_anual[selic_anual.index >= data_base.year]
    pontos_t = [data_base] + [pd.Timestamp(f"{a}-12-31") for a in sel.index]
    pontos_v = [i0] + list(sel.values)
    futuro = [data_base + pd.offsets.QuarterEnd(k) for k in range(1, n + 1)]
    x = np.array([p.toordinal() for p in pontos_t])
    return [float(np.interp(f.toordinal(), x, pontos_v)) for f in futuro]


def condicoes_iniciais(painel: pd.DataFrame, aux: dict) -> tuple[dict, list[str]]:
    """Valores iniciais = última observação disponível de cada variável."""
    ini: dict = {}
    datas: dict = {}
    pend: list[str] = []
    mapa = {
        "i0": "meta_selic", "pi0": "ipca12", "pi_e0": "pi_e", "h0": "h", "g0": "g_12m",
        "g_potencial": "g_tend", "d_gross0": "dbgg", "d_net0": "dlsp", "R0": "reservas_bi",
        "E0": "cambio", "Y0": "pib_12m_bi", "s0": "s_spc", "s_gc0": "s_gc", "gamma0": "gamma",
        "w_lft": "w_lft", "w_pre": "w_pre", "w_ipca": "w_ipca", "w_fx": "w_fx", "w_oma": "w_oma",
        "prazo_pre_meses": "prazo_ltn", "prazo_ipca_meses": "prazo_ntnb", "prazo_lft_meses": "prazo_lft",
        "r_long0": "ntnb10", "r_long5_0": "ntnb5",
    }
    ultima_obs = aux.get("ultima_obs", {})
    for chave, col in mapa.items():
        v, d = ultimo(painel, col)
        if v is None:
            pend.append(f"{chave} ({col}) sem dados")
        ini[chave] = v
        # data real da última observação usada (não o rótulo do trimestre)
        datas[chave] = ultima_obs.get(ORIGEM.get(col, ""), d) if d == painel.index[-1].strftime("%Y-%m-%d") else d
    if ini.get("g_potencial") is not None:
        # média da tendência HP nos últimos 5 anos (o ponto final do filtro é ruidoso)
        ini["g_potencial"] = float(painel["g_tend"].dropna().iloc[-20:].mean())
    ini["i_pre_estoque0"] = float(painel["selic"].dropna().iloc[-8:].mean())
    ini["r_long_estoque0"] = float(painel["ntnb10"].dropna().iloc[-28:].mean()) if "ntnb10" in painel else None
    ini["de_ult4"] = [float(x) for x in painel["de"].dropna().iloc[-4:]]
    # Referência empírica do juro real longo (não usada como padrão)
    if "ntnb10" in painel:
        nt = painel["ntnb10"].dropna()
        ini["ntnb10_media_2017_2019"] = float(nt.loc["2017":"2019"].mean())
        ini["ntnb10_media_amostra"] = float(nt.mean())
        ini["ntnb10_amostra_inicio"] = nt.index[0].strftime("%Y-%m")
    # Duração de Macaulay (estoque por vencimento); alternativa: fator × prazo médio
    if "duracoes" in aux:
        ini.update(aux["duracoes"])
        ini["duracao_metodo"] = "Macaulay (estoque da DPF por vencimento, taxas do Tesouro Direto)"
    elif ini.get("prazo_ipca_meses") is not None:
        ini["dur_ipca_anos"] = 0.7 * ini["prazo_ipca_meses"] / 12
        ini["dur_pre_anos"] = 1.0 * ini["prazo_pre_meses"] / 12
        ini["duracao_metodo"] = "aproximação: 0,7 × prazo médio (NTN-B) e 1,0 × prazo médio (LTN)"
        pend.append("Duração de Macaulay indisponível: usada a aproximação fator × prazo médio")
    data_base = painel.index[-1]
    ini["data_base"] = data_base.strftime("%Y-%m-%d")
    ini["trimestre_base"] = f"{data_base.year}T{data_base.quarter}"
    selic_anual = pesquisa_focus(aux["focus_anuais"], "Selic", data_base) if "focus_anuais" in aux else pd.Series()
    if not selic_anual.empty and ini["i0"] is not None:
        ini["selic_focus_8t"] = trajetoria_focus_selic(selic_anual, ini["i0"], data_base)
        anu = aux["focus_anuais"]
        ini["focus_data_pesquisa"] = anu.loc[anu["Data"] <= data_base, "Data"].max().strftime("%Y-%m-%d")
        for ind, chave in (("Resultado primário", "focus_primario"), ("Dívida líquida do setor público", "focus_dlsp")):
            serie = pesquisa_focus(anu, ind, data_base)
            ini[chave] = {int(a): float(v) for a, v in serie.items()}
    else:
        ini["selic_focus_8t"] = [ini["i0"]] * 8
        pend.append("Focus Selic indisponível: trajetória esperada = Selic atual")
    # Bloco fiscal (governo central, RTN, % do PIB em 12 meses)
    if "rtn" in aux:
        rtn = aux["rtn"].rolling(12).sum()
        pib_m = pib_mensal()
        comum = rtn.index.intersection(pib_m.index)
        comum = comum[comum <= data_base]
        fim = comum[-1]
        for nome in LINHAS_RTN.values():
            if nome in rtn:
                ini[f"rtn_{nome}"] = float(100 * rtn.loc[fim, nome] / pib_m.loc[fim])
        ini["rtn_data"] = fim.strftime("%Y-%m-%d")
        datas["rtn"] = ini["rtn_data"]
    else:
        pend.append("RTN indisponível")
    ini["datas_observacao"] = datas
    for chave, d in datas.items():
        if d is not None and (data_base - pd.Timestamp(d)).days > 200:
            pend.append(f"{chave}: última observação em {d}, defasada em relação a {ini['data_base']}")
    return ini, pend


def pib_mensal() -> pd.Series:
    s = pd.read_csv(RAW / f"sgs_{SERIES_SGS['pib_12m'][0]}.csv", index_col=0, parse_dates=True).iloc[:, 0]
    return s.groupby(s.index.to_period("M")).last().to_timestamp()


# ---------------------------------------------------------------- estimação

def _ols(y: pd.Series, X: pd.DataFrame):
    df = pd.concat([y, X], axis=1).dropna()
    yy, XX = df.iloc[:, 0].values, df.iloc[:, 1:].values
    beta, *_ = np.linalg.lstsq(XX, yy, rcond=None)
    resid = yy - XX @ beta
    return dict(zip(X.columns, beta)), pd.Series(resid, index=df.index), len(df)


def estimar(painel: pd.DataFrame, cfg_est: dict) -> tuple[dict, dict]:
    """OLS de IS, Phillips e câmbio. Devolve (estimativas com diagnóstico, matriz de covariância dos choques)."""
    p = painel[painel.index >= cfg_est["amostra_inicio"]].copy()
    p = p[~((p.index >= cfg_est["excluir_inicio"]) & (p.index <= cfg_est["excluir_fim"]))]
    full = painel
    lag = lambda c: full[c].shift(1).reindex(p.index)  # noqa: E731
    out: dict = {}
    res = {}
    # IS: h = a1 h(-1) - a2 (r_long(-1) - média) + c
    rl = full["ntnb10"]
    X = pd.DataFrame({"a1": lag("h"), "a2": -(rl.shift(1) - rl.mean()).reindex(p.index), "c": 1.0})
    b, res["h"], n = _ols(p["h"], X)
    out["is"] = {"a1": b["a1"], "a2": b["a2"], "n": n}
    # Phillips: pi - pi_e = b1 (pi(-1) - pi_e) + b2 h(-1) + b3 de12
    y = p["ipca12"] - p["pi_e"]
    X = pd.DataFrame({"b1": lag("ipca12") - p["pi_e"], "b2": lag("h"), "b3": p["de12"]})
    b, res["pi"], n = _ols(y, X)
    out["phillips"] = {"b1": b["b1"], "b2": b["b2"], "b3": b["b3"], "n": n}
    # Câmbio: de = -c1 Δi + c2 Δprem_proxy + c ; prem_proxy = NTN-B 10a - (Selic - pi_e)
    prem_proxy = full["ntnb10"] - (full["selic"] - full["pi_e"])
    X = pd.DataFrame({"c1": -full["selic"].diff().reindex(p.index),
                      "c2": prem_proxy.diff().reindex(p.index), "c": 1.0})
    b, res["e"], n = _ols(p["de"], X)
    out["cambio"] = {"c1": b["c1"], "c2": b["c2"], "n": n}
    # Choque de prêmio: resíduo de AR(1) da proxy
    X = pd.DataFrame({"rho": prem_proxy.shift(1).reindex(p.index), "c": 1.0})
    _, res["prem"], _ = _ols(prem_proxy.reindex(p.index), X)
    R = pd.DataFrame(res).dropna()
    cov = {"nomes": ["eps_h", "eps_pi", "eps_e", "eps_prem"], "n": len(R),
           "matriz": [[float(x) for x in linha] for linha in R[["h", "pi", "e", "prem"]].cov().values]}
    # Aceitação: estimativa dentro da faixa de teste
    aceitos = {}
    for bloco in ("is", "phillips", "cambio"):
        for k, v in out[bloco].items():
            if k == "n":
                continue
            lo, hi = cfg_est["faixas"][k]
            aceitos[k] = {"estimado": float(v), "aceito": bool(lo <= v <= hi)}
    return aceitos, cov


# ---------------------------------------------------------------- YAML

def escrever_auto(caminho: Path, auto: dict) -> None:
    texto = caminho.read_text(encoding="utf-8")
    topo = texto.split(MARCADOR_AUTO)[0].rstrip() + "\n\n"
    corpo = yaml.safe_dump(auto, allow_unicode=True, sort_keys=False, default_flow_style=None, width=120)
    caminho.write_text(topo + MARCADOR_AUTO + " (gerado por src/dados.py; não editar abaixo desta linha)\n" + corpo,
                       encoding="utf-8")


def atualizar(caminho_calib: Path, offline: bool = False) -> dict:
    """Executa a coleta completa e reescreve o bloco AUTO de calibracao.yaml."""
    cfg = yaml.safe_load(caminho_calib.read_text(encoding="utf-8"))
    validacao = validar_codigos() if not offline else pd.DataFrame()
    painel, aux, erros = montar_painel(offline)
    ini, pend = condicoes_iniciais(painel, aux)
    estimados, cov = estimar(painel, cfg["estimacao"])
    auto = {
        "gerado_em": date.today().isoformat(),
        "iniciais": ini,
        "estimados": estimados,
        "choques": cov,
        "validacao_sgs": validacao.to_dict("records") if not validacao.empty else "não executada (offline)",
        "erros_coleta": erros + pend,
    }
    escrever_auto(caminho_calib, auto)
    return auto


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    atualizar(RAIZ / "config" / "calibracao.yaml")
