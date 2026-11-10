# turquia-ajuste

Terceiro caso do projeto de credibilidade (Brasil, Argentina, Turquia): o que a Turquia poderia ter feito em
setembro de 2021, quando o governo decidiu forçar a queda dos juros com a inflação em 19% e a credibilidade abalada.

- `PYTHONPATH=src python -m turmodel.calibrate`: calibra o modelo mensal na trajetória observada (set/2021–set/2026),
  em duas variantes de inércia (o peso dos contratos anuais não é identificado pelos dados).
- `PYTHONPATH=src python -m turmodel.search`: busca aleatória de 6.000 políticas alternativas, nas duas variantes.
- `PYTHONPATH=src python -m turmodel.report`: sensibilidade e figura.

Dados em `data/` (ver `data/LEIAME.md`: parte das séries é aproximada e precisa ser conferida). Resultados e
limitações em `outputs/relatorio.md`. Edite `config/params.yaml`, nunca os `params_calibrated_*.yaml`.
