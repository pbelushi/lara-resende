# Dados do experimento turco

- `mensal.csv`: IPCA turco em 12 meses (OCDE via FRED, série CPALTT01TRM659N, até abr/2025; out/2025–set/2026 de
  global-rates.com; out/2026 de tradingeconomics.com; mai–set/2025 de memória do TurkStat, a conferir); câmbio médio
  mensal USD/TRY (FRED, CCUSMA02TRM618N); reservas brutas sem ouro (FMI via FRED, TRESEGTRM052N); taxa básica (repo de
  uma semana, fim de mês, montada a partir das decisões do TCMB; conferida contra a taxa interbancária da OCDE/FRED,
  IRSTCI01TRM156N). A variação mensal do IPCA é obtida encadeando o índice a partir das variações mensais de 2020;
  as de 2021 assim obtidas batem com as divulgadas pelo TurkStat.
- `anual.csv`: crescimento do PIB (tabela da Wikipedia, com base no TurkStat); primário do governo central e dívida
  bruta em % do PIB são APROXIMADOS (memória de relatórios do Tesouro turco e do FMI), a conferir.
- `reservas_liquidas_ancoras.csv`: reservas líquidas descontados os swaps, em pontos selecionados; APROXIMADAS.
- `salario_minimo.csv`: reajustes do salário mínimo líquido (decisões oficiais), de memória; a conferir.

O shell da sessão não alcança as fontes; as séries do FRED foram lidas por WebFetch e transcritas. Conferir antes
de publicar.
