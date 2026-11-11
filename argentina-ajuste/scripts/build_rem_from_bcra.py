"""Monta data/rem_medianas.csv a partir da planilha histórica do REM (BCRA).

Fonte: https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/relevamiento-expectativas-mercado-historico.xlsx
(cópia em data/raw/, baixada em 11/11/2026), aba "Base de Datos Completa", medianas. Substitui a versão montada a
partir dos relatórios mensais e da imprensa (data/rem_medianas_v1_imprensa.csv), com a qual as medianas coincidem
(diferença máxima de 0,04 p.p. na inflação e de 0,8 peso no câmbio, por arredondamento), salvo a inflação de jan/24
na pesquisa de nov/23 (19,0 na planilha, 19,7 na imprensa).

Colunas: infl_cur/next/next2 = inflação mensal esperada para o mês da pesquisa e os dois seguintes; infl_12m =
inflação em 12 meses esperada para 12 meses à frente; fx_next = câmbio médio esperado no mês seguinte; fx_dec =
câmbio médio esperado em dezembro (do ano seguinte, se a pesquisa é de dezembro).

Uso: python scripts/build_rem_from_bcra.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "raw" / "relevamiento-expectativas-mercado-historico.xlsx"
URL = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/relevamiento-expectativas-mercado-historico.xlsx"
MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
IPC = "Precios minoristas (IPC nivel general; INDEC)"
FX = "Tipo de cambio nominal"


def _lab(p):
    return f"{MES[p.month - 1]}-{str(p.year)[2:]}"


def _serie(g, var, ref):
    s = g[(g.Variable == var) & (g.Referencia == ref)]
    return s.assign(per=pd.to_datetime(s["Período"]).dt.to_period("M")).set_index("per").Mediana


def main():
    d = pd.read_excel(XLSX, "Base de Datos Completa", header=1)
    d.columns = [str(c).strip() for c in d.columns]
    d["f"] = pd.to_datetime(d["Fecha de pronóstico"])
    d = d[(d.f >= "2023-11-01") & (d.f < "2026-01-01")]
    rows = []
    for f, g in d.groupby("f"):
        m = pd.Period(f, "M")
        ipc, fx = _serie(g, IPC, "var. % mensual"), _serie(g, FX, "$/USD")
        ia = g[(g.Variable == IPC) & (g.Referencia == f"var. % i.a.; {_lab(m + 12)}")].Mediana
        decy = m.year + (1 if m.month == 12 else 0)
        fxd = g[(g.Variable == FX) & (g.Referencia == f"$/USD; dic-{str(decy)[2:]}")].Mediana
        fxd = fxd.iloc[0] if len(fxd) else fx.get(pd.Period(f"{decy}-12", "M"), np.nan)
        rows.append(dict(survey_month=str(m), infl_cur=ipc.get(m, np.nan), infl_next=ipc.get(m + 1, np.nan),
                         infl_next2=ipc.get(m + 2, np.nan), infl_12m=ia.iloc[0] if len(ia) else np.nan,
                         fx_cur=np.nan, fx_next=fx.get(m + 1, np.nan), fx_dec=fxd, fx_dec_month=f"{decy}-12",
                         source_url=URL, notes=f"Pesquisa de {f:%d/%m/%Y}; medianas da planilha histórica do BCRA."))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "data" / "rem_medianas.csv", index=False, float_format="%.4g")
    print(out.drop(columns=["source_url", "notes"]).to_string(index=False))


if __name__ == "__main__":
    main()
