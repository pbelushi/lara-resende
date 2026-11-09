"""Canal institucional: três regras fiscais como choques de credibilidade (estudo de evento).

Eventos (anúncio e aprovação):
- Lei de Responsabilidade Fiscal (LC 101/2000): projeto enviado em abril de 1999; sancionada em 4/5/2000.
- Teto de gastos (EC 95/2016): anunciado em 24/5/2016; PEC enviada em 15/6/2016; promulgada em 15/12/2016.
- Novo arcabouço fiscal (LC 200/2023): apresentado em 30/3/2023; sancionado em 30/8/2023.

Medidas, em janelas mensais em torno de cada data:
- risco país: EMBI+ Brasil (data/raw/embi_brasil_mensal.csv; Ipeadata), com o índice do dólar amplo (FRED
  DTWEXB/DTWEXBGS) como controle de condições globais;
- Focus: primário esperado para o ano seguinte, dívida líquida esperada para o ano seguinte e distância entre o
  IPCA esperado para o ano seguinte e a meta;
- λ do modelo: λ_π e λ_fiscal ajustados (validação 2D, P2) em janelas trimestrais antes e depois do anúncio (teto
  e arcabouço; para a LRF faltam dívida bruta, NTN-B e primário trimestral no painel).

Uso: python -m src.regras_fiscais_eventos
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import modelo
from .credibilidade_focus import METAS
from .credibilidades_separadas import RAIZ
from .lambda_fundamentos_validacao import G, grades_de_erro, preparar_episodios
from .lambda_fundamentos_estimacao import SAIDA as S_F

RAW = RAIZ / "data" / "raw"
SAIDA = S_F.parent / "regras_fiscais"
EVENTOS = {
    "LRF": {"anuncio": "1999-04-01", "aprovacao": "2000-05-01"},
    "Teto de gastos": {"anuncio": "2016-05-01", "aprovacao": "2016-12-01"},
    "Arcabouço": {"anuncio": "2023-03-01", "aprovacao": "2023-08-01"},
}
# janelas trimestrais para o λ do modelo (fim de trimestre; o t0 fica fora do ajuste)
JANELAS = {
    "Teto de gastos": {"antes": ("2015-03-31", "2016-03-31"), "depois": ("2016-06-30", "2017-12-31"),
                       "depois, até dez/16": ("2016-03-31", "2016-12-31")},
    "Arcabouço": {"antes": ("2022-03-31", "2023-03-31"), "depois": ("2023-03-31", "2024-06-30"),
                  "depois, até dez/23": ("2023-03-31", "2023-12-31"), "2024": ("2023-12-31", "2024-12-31")},
}
METAS_ANTIGAS = {1999: 8.0, 2000: 6.0, 2001: 4.0, 2002: 3.5, 2003: 4.0, 2004: 5.5}
DEFAS = [-6, -3, -1, 0, 1, 3, 6, 12]


def serie_mensal() -> pd.DataFrame:
    embi = pd.read_csv(RAW / "embi_brasil_mensal.csv", parse_dates=["data"])
    embi = embi.set_index(embi["data"].dt.to_period("M").dt.to_timestamp())["embi_bp"]
    usd = pd.concat([pd.read_csv(RAW / f, index_col=0, parse_dates=True).iloc[:, 0]
                     for f in ("fred_DTWEXB.csv", "fred_DTWEXBGS.csv")])
    usd = pd.to_numeric(usd, errors="coerce").resample("MS").mean()
    a = pd.read_csv(RAW / "focus_anuais_historico.csv", parse_dates=["Data"])
    a["mes"] = a["Data"].dt.to_period("M").dt.to_timestamp()
    a["h"] = a["DataReferencia"].astype(int) - a["Data"].dt.year
    prox = a[a["h"] == 1].groupby(["Indicador", "mes"])["Mediana"].mean().unstack(0)
    d = pd.DataFrame({"embi": embi, "dolar_amplo": usd,
                      "primario_esperado_t1": prox.get("Resultado primário"),
                      "dlsp_esperada_t1": prox.get("Dívida líquida do setor público"),
                      "ipca_esperado_t1": prox.get("IPCA")})
    metas = {**METAS_ANTIGAS, **{k: v[0] for k, v in METAS.items()}}
    d["meta_t1"] = [metas.get(t.year + 1, np.nan) for t in d.index]
    d["ipca_t1_menos_meta"] = d["ipca_esperado_t1"] - d["meta_t1"]
    return d


def tabela_evento(d: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for ev, datas in EVENTOS.items():
        for marco, dt in datas.items():
            t0 = pd.Timestamp(dt)
            for k in DEFAS:
                t = t0 + pd.DateOffset(months=k)
                linhas.append({"evento": ev, "marco": marco, "mes_relativo": k, "mes": t.strftime("%Y-%m"),
                               **{c: (float(d[c].get(t)) if pd.notna(d[c].get(t, np.nan)) else np.nan)
                                  for c in ["embi", "dolar_amplo", "primario_esperado_t1", "dlsp_esperada_t1",
                                            "ipca_t1_menos_meta"]}})
    return pd.DataFrame(linhas)


def variacoes(t: pd.DataFrame) -> pd.DataFrame:
    """Variação de −1 a +6 e de −1 a +12 meses em torno de cada marco."""
    out = []
    for (ev, marco), g in t.groupby(["evento", "marco"], sort=False):
        g = g.set_index("mes_relativo")
        lin = {"evento": ev, "marco": marco}
        for c in ["embi", "dolar_amplo", "primario_esperado_t1", "dlsp_esperada_t1", "ipca_t1_menos_meta"]:
            for k in (6, 12):
                lin[f"d_{c}_{k}m"] = g.loc[k, c] - g.loc[-1, c]
            if c == "embi":
                lin["d_embi_6m_pct"] = 100 * (g.loc[6, c] / g.loc[-1, c] - 1)
        out.append(lin)
    return pd.DataFrame(out)


def lambda_modelo() -> pd.DataFrame:
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    linhas = []
    for ev, jan in JANELAS.items():
        eps = preparar_episodios(p, "P2", {f"{ev} | {k}": v for k, v in jan.items()})
        erros = grades_de_erro(eps, None)
        for e, x in zip(eps, erros):
            j = np.unravel_index(np.nanargmin(x), x.shape)
            ok = x <= 1.05 * np.nanmin(x)
            lp_ok, lf_ok = np.where(ok)
            linhas.append({"evento": ev, "janela": e["nome"].split(" | ")[1], "lambda_pi": G[j[0]],
                           "lambda_f": G[j[1]], "erro": float(x[j]),
                           "faixa_lambda_pi": f"{G[lp_ok.min()]:.2f}–{G[lp_ok.max()]:.2f}",
                           "faixa_lambda_f": f"{G[lf_ok.min()]:.2f}–{G[lf_ok.max()]:.2f}"})
    return pd.DataFrame(linhas)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    d = serie_mensal()
    t = tabela_evento(d)
    v = variacoes(t)
    lam = lambda_modelo()
    t.to_csv(SAIDA / "eventos_janelas.csv", index=False)
    v.to_csv(SAIDA / "eventos_variacoes.csv", index=False)
    lam.to_csv(SAIDA / "eventos_lambda_modelo.csv", index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(t.round(2).to_string(index=False))
    print(v.round(2).T.to_string())
    print(lam.to_string(index=False))


if __name__ == "__main__":
    main()
