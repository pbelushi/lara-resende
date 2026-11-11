# Fontes dos dados de calibração e validação

Levantadas em 06/11/2026. Antes de usar em texto publicado, confira cada número na
fonte primária (INDEC, BCRA, Secretaría de Hacienda) — `scripts/fetch_data.py`
ajuda a puxar as séries oficiais.

| Dado | Valor | Fonte |
|---|---|---|
| Inflação 2023 / 2024 / 2025 (dez/dez) | 211,4% / 117,8% / 31,5% | BCRA, Informe al Congreso 2023; INDEC (via Mercopress, El Cronista) |
| Inflação mensal dez/23, nov/24, dez/24, dez/25 | 25,5% / 2,4% / 2,7% / 2,8% | BCRA; INDEC (via Diario de Cuyo, El Cronista) |
| Inflação mensal demais meses | ver `actuals_monthly.csv` | INDEC — conferidos em 11/11/2026: os 12 meses de 2024 e de 2025 batem com as séries publicadas (2025 mês a mês em iProfesional, "Inflación INDEC 2025"); produto 117,7% e 31,5% |
| Pobreza 2º sem 23 / 1º sem 24 / 2º sem 24 / 1º sem 25 / 2º sem 25 | 41,7 / 52,9 / 38,1 / 31,6 / 28,2 | INDEC-EPH (via El Litoral, Diario de Cuyo, La Voz de San Justo, C5N) |
| PIB 2023 / 2024 / 2025 | −1,6% / −1,7% (rev.) / +4,4% | INDEC (via iProfesional, El Cronista). Atenção: 2024 aparece como −1,3%, −1,7% e −1,8% conforme a revisão |
| Resultado primário SPN 2023 / 2024 | −2,9% / +1,8% do PIB | Ministerio de Economía (via El Cronista, Diario de Cuba) |
| Ajuste fiscal 2024 | ~4,7 p.p. do PIB | IARAF (via La Nación PY) |
| Gasto primário 2023 → 2025 e composição do corte | 19,58% → 14,82% do PIB; subsídios 1,32, províncias 0,40, obra pública 0,65 p.p. | Ministerio de Economía (via LM Neuquén); aposentadorias ≈22% do corte de 2024 (El Cronista) |
| Reservas líquidas nov/23 e dez/24 | ≈ −US$10,5 bi e ≈ −US$10 bi | Outlier, PPI, Eco Go (via Bloomberg Línea, iProfesional, El Marplatense) |
| Risco país (fim de mês) jul–out/25, dez/25 | 730, 829, 1.222, 657; ~570 | USAL, Indicadores de Coyuntura nov/25 e dez/25 |
| Risco país dez/23, jun/24, dez/24 | ~1.900, ~1.450, ~640 | aproximados de cobertura de imprensa. Em 11/11/2026: fechamento de 2024 em 635 pb (El Economista, "2024 fue un año superlativo para los activos argentinos"), 5 pb abaixo do alvo; dez/23 (1.907) e jun/24 ainda sem confirmação na série EMBI do JP Morgan |
| Lei Bases | enviada dez/23; Ómnibus derrotada fev/24; aprovada 27/06/24; privatizações 41 → 6–8 empresas | El Cronista, El Economista, Bloomberg Línea, A24 |
| Salário real registrado privado, CBT/IPC, EMAE dessaz. (mensal, dez/23–dez/25) | `relative_prices_wages.csv` (nov/23 = 100; EMAE com 2023 = 100) | INDEC via API Series de Tiempo (datos.gob.ar), baixado em 06/11/2026: IDs 149.1_SOR_PRIADO_OCTU_0_25, 150.1_CSTA_BATAL_0_D_20, 148.3_INIVELNAL_DICI_M_26, 143.3_NO_PR_2004_A_31; brutos em `raw/oficiais_cbt_salarios_emae.csv`. EMAE dessaz. dá PIB 2024 de −1,37% |
| Dívida pública 2023 | 91% (IIF) a 118% (Latinfocus) do PIB, conforme câmbio de conversão | Infobae |

Parâmetros comportamentais (multiplicadores, repasse, sensibilidades) não são dados:
são calibrados (`argmodel.calibrate`) ou fixados com base em literatura, e estão
justificados linha a linha em `config/params.yaml`.

## REM (BCRA) — `rem_medianas.csv`

Medianas do Relevamiento de Expectativas de Mercado, pesquisas de nov/23 a dez/25 (inflação do mês, dos dois seguintes,
12 meses; câmbio médio mensal esperado do mês seguinte e de dezembro). Montado em nov/2026 a partir dos relatórios e PDFs
mensais do BCRA (https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp) e, para os
meses sem tabela legível, da imprensa (El Cronista, Ámbito, La Nación, Bloomberg Línea, C5N e outros), com conferência
cruzada pela revisão que cada relatório informa ("+0,3 p.p. respecto del REM previo"). Fonte por linha em `source_url`;
dúvidas em `notes` (ex.: set/25 sem inflação do mês seguinte por fontes divergentes). **Conferir**: substituir pela planilha
histórica do BCRA (historico-relevamiento-expectativas-mercado.xlsx) quando baixada localmente.
