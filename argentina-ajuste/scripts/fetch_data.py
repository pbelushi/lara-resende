"""
Atualiza/confere os dados com APIs oficiais argentinas.

Este script NÃO rodou no ambiente onde o projeto foi montado (sem acesso de rede
a esses domínios). Rode-o localmente; ele só baixa e salva em data/raw/ — a
decisão de substituir valores em data/actuals_monthly.csv é sua.

  python scripts/fetch_data.py search "precios al consumidor nivel general"
  python scripts/fetch_data.py series <ID_DA_SERIE> [<ID> ...]
  python scripts/fetch_data.py bcra            # lista variáveis monetárias do BCRA

APIs:
  - Series de Tiempo (datos.gob.ar): https://apis.datos.gob.ar/series/api/
    use o endpoint /search para achar os IDs (IPC, EMAE, resultado fiscal...).
  - BCRA Estadísticas: https://api.bcra.gob.ar/estadisticas/  (versão pode mudar;
    confira a documentação vigente).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
SERIES_API = "https://apis.datos.gob.ar/series/api"
BCRA_API = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias"


def search(q: str) -> None:
    r = requests.get(f"{SERIES_API}/search/", params={"q": q, "limit": 20}, timeout=30)
    r.raise_for_status()
    for d in r.json().get("data", []):
        f = d.get("field", {})
        print(f"{f.get('id'):40s} {f.get('frequency', ''):5s} {f.get('description', '')[:90]}")


def series(ids: list[str]) -> None:
    r = requests.get(f"{SERIES_API}/series/", timeout=60,
                     params={"ids": ",".join(ids), "start_date": "2022-01-01", "format": "csv"})
    r.raise_for_status()
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / f"series_{'_'.join(i.replace('.', '-') for i in ids)[:80]}.csv"
    out.write_text(r.text)
    print(pd.read_csv(out).tail(30).to_string(index=False))
    print(f"\nsalvo em {out}")


def bcra() -> None:
    r = requests.get(BCRA_API, timeout=30)
    r.raise_for_status()
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "bcra_variaveis.json").write_text(json.dumps(r.json(), ensure_ascii=False, indent=1))
    for v in r.json().get("results", [])[:80]:
        print(v.get("idVariable"), "-", v.get("descripcion"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    cmd, args = sys.argv[1], sys.argv[2:]
    {"search": lambda: search(" ".join(args)), "series": lambda: series(args), "bcra": bcra}[cmd]()
