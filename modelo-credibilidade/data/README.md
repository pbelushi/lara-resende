# Dados

Dados baixados entre 2 e 3 de novembro de 2026 (t0 do modelo = 2026T3). Os arquivos em `raw/` são os insumos
originais de cada provedor, sem alteração; `processed/` contém o painel trimestral e a matriz insumo-produto
processada, gerados pelo código a partir de `raw/`. Os dados brutos de terceiros continuam sujeitos aos termos de
uso de cada provedor; cite a fonte original ao reutilizá-los.

## Arquivos e fontes

| Arquivo em `raw/` | Conteúdo | Fonte | Gerado por |
|---|---|---|---|
| `sgs_<código>.csv` | Selic, IPCA, dívida bruta e líquida, reservas, câmbio, primário, PIB, composição e prazos da DPMFi, IC-Br, meta de inflação (códigos em `src/dados.py` e `src/estimacao.py`) | Banco Central do Brasil, Sistema Gerenciador de Séries Temporais (api.bcb.gov.br) | `run.py --atualizar-dados` |
| `focus_ipca12m.csv`, `focus_anuais_historico.csv` | Expectativas de mercado (IPCA 12 meses; projeções anuais) | Banco Central do Brasil, Focus (API Olinda) | `run.py --atualizar-dados` |
| `tesouro_direto_taxas.csv`, `tesouro_direto_ntnb.csv` | Taxas dos títulos ofertados no Tesouro Direto | Tesouro Nacional, Tesouro Transparente (CKAN) | `run.py --atualizar-dados` |
| `estoque_dpf.csv` | Estoque da Dívida Pública Federal por título e vencimento | Tesouro Nacional, Tesouro Transparente | `run.py --atualizar-dados` |
| `rtn_tabela_1_1.csv` | Resultado do Tesouro Nacional, tabela 1.1 | Tesouro Nacional, Tesouro Transparente | `run.py --atualizar-dados` |
| `fred_DTWEXBGS.csv`, `fred_DTWEXB.csv` | Índice amplo do dólar (proxy do DXY) | Board of Governors of the Federal Reserve System, via FRED (Federal Reserve Bank of St. Louis) | `src/estimacao.py` |
| `ibge/Matriz_de_Insumo_Produto_2015_Nivel_67.xls` | Matriz insumo-produto 2015, nível 67 | IBGE, Sistema de Contas Nacionais | download manual (ftp.ibge.gov.br) |
| `ibge/nivel_68_2010_2015_xls.zip`, `ibge/68_tab1_2015.xls`, `ibge/68_tab2_2015.xls` | Tabelas de Recursos e Usos 2010–2015, nível 68 | IBGE, Sistema de Contas Nacionais | download manual |
| `ibge/12_tab1_2023.xls`, `ibge/12_tab2_2023.xls` | Tabelas de Recursos e Usos 2023, nível 12 | IBGE, Sistema de Contas Nacionais (ftp.ibge.gov.br/Contas_Nacionais/Sistema_de_Contas_Nacionais/2023) | download manual |
| `sidra/` | PNAD Contínua (tabelas 5434, 5442, 4093, 4097, 4099), Contas Nacionais Trimestrais (1846, 1621) e Censo 2022 (10262), com os metadados usados na validação de cada tabela | IBGE, SIDRA (servicodados.ibge.gov.br) | `src/extrair_emprego.py` |

## Fora do depósito

| Arquivo | Conteúdo | Fonte | Motivo |
|---|---|---|---|
| `ipea_JPM366_EMBI366.csv` | EMBI+ Brasil (pontos-base) | J.P. Morgan, via Ipeadata (série JPM366_EMBI366, encerrada em jul/2024) | Índice proprietário: redistribuição sujeita aos termos da J.P. Morgan |
| `fred_VIXCLS.csv` | VIX | Cboe Global Markets, via FRED (série VIXCLS) | Série com direitos da Cboe |

Os dois são baixados automaticamente das fontes originais na primeira execução que precisar deles
(`src/estimacao.py`, funções `_ipea` e `_fred`) e ficam em `raw/`, fora do controle de versão (`.gitignore`).

## Processados

| Arquivo | Conteúdo | Gerado por |
|---|---|---|
| `processed/trimestral.csv` | Painel trimestral 2000–2026 usado na calibração e na validação | `run.py --atualizar-dados` |
| `processed/mip/` | Leontief tipo I e II, demanda final por componente, multiplicadores (67 atividades, 12 grupos, TRU 2023), coeficientes de emprego e renda de 2015 e 2025, elasticidades setoriais, lei de Okun | `src/extrair_mip.py`, `src/extrair_emprego.py` |
