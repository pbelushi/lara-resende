# CLAUDE.md — projeto argentina-ajuste

Experimento contrafactual sobre o ajuste argentino 2023–2025. Leia o README antes de mudar algo.

## Comandos
- `python run_all.py` — pipeline completo (calibração → 48 cenários → sensibilidade → gráficos)
- `PYTHONPATH=src python -m argmodel.calibrate` — só calibração; imprime ajuste item a item
- `PYTHONPATH=src python -m argmodel.experiment` — só o grid
- `PYTHONPATH=src python -m argmodel.sensitivity`
- `python scripts/fetch_data.py search "<termo>"` — achar séries oficiais (datos.gob.ar)

## Regras de trabalho
- **Edite `config/params.yaml`, nunca `params_calibrated.yaml`** (é regenerado).
- **Toda mudança no modelo exige recalibrar e conferir `outputs/calibracao_ajuste.csv`.**
  Se o ajuste piorar (pobreza fora de ±2 p.p., inflação anual fora de ±6 p.p., PIB fora de
  ±1,5 p.p.), a mudança está errada ou precisa de justificativa explícita.
- Unidades: taxas mensais em decimal; câmbio e preços em log. Ao somar inflação em
  log, use `np.log1p(pi)` — já houve um bug de unidade na equação de salários.
- Um parâmetro que a calibração leva ao limite ou a zero provavelmente não é
  identificado: fixe com base em literatura e adicione à `sensitivity.py`, não aceite o zero.
- Depois de qualquer mudança, rode um cenário extremo (ex.: `Scenario(dev=True)`) e
  confira se renda e pobreza andam na direção economicamente esperada.
- `phi_money` (canal monetário) e `beta_fx` (repasse do salto) são as hipóteses das quais
  mais depende a conclusão sobre "câmbio competitivo + juros"; não apresente esse
  resultado sem a faixa da sensibilidade.
- O repasse é assimétrico (`beta_fx` para o salto, `beta_fx_down` para o crawl abaixo da
  inflação esperada). Não volte a um coeficiente único: ele ficava preso no piso.
- Duas pobrezas (2º sem/24 e 2º sem/25) estão 0,1 p.p. fora de ±2, por causa do canal de
  aluguéis e serviços que falta na linha. Não reponderar a calibração para escondê-las.
- A troca de dívida tem adesão do mercado (`debt_swap.lambda_fiscal`, `lambda_pi`; 0,75 = calibração). `python -m argmodel.lambda_swap` roda a grade. O modelo não tem corrida descontínua contra a dívida em pesos: não conclua que a troca "nunca piora" o risco país.
- Credibilidade das âncoras: `credibility.lambda_fx` e `lambda_rate` (0,75 = calibração). O `cred` do modelo é uma âncora efetiva, não a credibilidade das pesquisas: o REM dá ~0 e, imposto ao modelo, leva a inflação de 2024 a 254%. Não ponha o REM no mapa de λ como se fosse a mesma unidade.
- O crawl é abandonado se o câmbio real cair abaixo de `exchange.q_break` (−0,15). Se mudar o modelo, confira que o gatilho continua sem disparar no caminho calibrado.

- λ endógeno (v2): `credibility.dinamica` (desligada por padrão; `on: true` liga). `PYTHONPATH=src python -m argmodel.dinamico` recalibra com a regra, roda os 48 cenários, as trajetórias de λ, o mapa de λ inicial e a sensibilidade (simétrica, metade, dobro); saídas em `outputs/v2_lambda_endogeno/`. Coeficientes transportados do Brasil em unidades de tolerância, truncados em −4 tolerâncias (suporte da estimação).

## Extensões sugeridas
- Substituir os valores mensais marcados "conferir" em `data/` pelas séries oficiais.
- Reação endógena de política (abandono da regra de câmbio se inflação > X).
- Composição alternativa de `baixo_multiplicador` com restrição de viabilidade política
  por categoria (governadores, sindicatos).
- Horizonte até 2026 com a nova composição do Congresso pós-legislativas.
