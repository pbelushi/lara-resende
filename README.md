# Modelo de credibilidade fiscal: Selic, reservas e ajuste fiscal no Brasil

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23934618.svg)](https://doi.org/10.5281/zenodo.23934618)

Modelo semiestrutural trimestral que compara três estratégias de estabilização para o Brasil e mede **quanta
adesão do mercado (credibilidade) cada uma exige** para estabilizar a dívida pública com a inflação controlada.

| Estratégia | Política |
|---|---|
| A. Ortodoxa | Pacote fiscal e Selic pela regra de Taylor |
| B. Lara Resende puro | Corte exógeno da Selic e venda de reservas, sem ajuste fiscal |
| C. Condicionada | Pacote fiscal, corte da Selic limitado pela regra de Taylor e venda de reservas |

*English summary.* Quarterly semi-structural model of Brazil comparing three stabilization strategies by the
degree of market credibility each requires to stabilize public debt while keeping inflation under control. It
includes three inflation theories (hybrid and flat Phillips curves, fiscal theory of the price level), Monte Carlo
simulation with paired bootstrap, historical validation, a reserves and sudden-stop analysis, and a recessionary
module (item-level fiscal multipliers, 2015 input-output matrix, employment). Code and reports are in Portuguese.

## Conteúdo

```
docs/especificacoes/     especificações de cada versão (v1, v2, v2.1, v2.2) e do módulo recessivo
modelo-credibilidade/    código, configuração, testes, dados e resultados (README próprio, com as escolhas
                         de implementação)
  config/                parâmetros (calibracao.yaml), cenários, experimentos, módulo recessivo
  src/                   modelo, coleta de dados, estimação, varredura, bootstrap, reservas, módulo recessivo
  tests/                 testes (pytest)
  data/raw/              dados brutos baixados (ver data/README.md)
  data/processed/        painel trimestral e matriz insumo-produto processada
  outputs/               resultados: v1 (raiz), v2/, v2_1/, v2_2/ (versão final), com relatórios .md e gráficos
CITATION.cff, .zenodo.json   metadados de citação e de depósito
LICENSE                  licença MIT
```

Relatórios da versão final:

- `modelo-credibilidade/outputs/v2_2/relatorio.md`: rodada principal (ordenamento, bootstrap, superfície,
  validação, alongamento, reservas).
- `modelo-credibilidade/outputs/v2_2/reservas_choque/relatorio_reservas_choque.md`: carregamento das reservas,
  parada súbita e sensibilidade de c3 e R_min.
- `modelo-credibilidade/outputs/v2_2/recessivo/relatorio_recessivo.md`: efeito recessivo (PIB, composição do
  pacote, setores, emprego, validação em 2015–2016); a versão com o efeito fiscal pelo impulso está em
  `relatorio_recessivo_impulso.md`.

Os resultados de `outputs/` (v1), `outputs/v2/` e `outputs/v2_1/` foram gerados por versões anteriores do código e
ficam como registro; o código atual reproduz os de `outputs/v2_2/`.

## Como reproduzir

Requisitos: Python 3.13 (testado em 3.13.7) e os pacotes de `modelo-credibilidade/requirements.txt`.

```bash
cd modelo-credibilidade
pip install -r requirements.txt
python -m pytest -q                                   # 57 testes

# rodada principal (≈ 40 min com 8 núcleos)
python run.py --mc 1000 --seed 42 --superficie --boot-r 1000 --est-b 300

# reservas e parada súbita (≈ 1 h 30)
python -m src.reservas_choque --N 1000 --R 1000

# módulo recessivo (≈ 10 min)
python -m src.extrair_mip
python -m src.extrair_emprego
python -m src.recessivo --N 1000 --R 1000
python -m src.recessivo_relatorio
```

A calibração usada está gravada em `config/calibracao.yaml` (bloco AUTO, com t0 = 2026T3). **Não rode
`--atualizar-dados` para reproduzir os resultados publicados**: essa opção baixa os dados mais recentes e reescreve a
calibração. Os únicos dados que faltam no depósito (EMBI+ e VIX, ver abaixo) são baixados automaticamente na
estimação de ω; o EMBI+ é uma série encerrada em jul/2024, de modo que a estimação não muda.

Sementes: choques de Monte Carlo com seed 42; bootstrap pareado com seed 2026. A mesma semente gera os mesmos
resultados (teste `test_mesma_seed_mesmos_resultados`).

## Dados

Fontes públicas: Banco Central do Brasil (SGS e Focus), Tesouro Nacional (Tesouro Direto, Tesouro Transparente,
RTN), IBGE (MIP 2015, TRUs 2015 e 2023, SIDRA: PNAD Contínua, Contas Nacionais Trimestrais e Censo 2022) e FRED
(dólar amplo). A lista completa, com as tabelas e os termos de uso, está em `modelo-credibilidade/data/README.md`.

Dois insumos não estão no depósito porque os provedores restringem a redistribuição: o EMBI+ Brasil (J.P. Morgan,
via Ipeadata, série JPM366_EMBI366) e o VIX (Cboe, via FRED, série VIXCLS). O código os baixa das fontes originais
quando ausentes (`src/estimacao.py`).

## Licença

MIT (arquivo `LICENSE`) para o código, a documentação, os relatórios e os resultados derivados. Os dados brutos de
terceiros em `modelo-credibilidade/data/raw/` continuam sujeitos aos termos de uso de cada provedor (ver
`modelo-credibilidade/data/README.md`).

## Como citar

Use o DOI do Zenodo (metadados também em `CITATION.cff`):

> Silva, Paulo Roberto (2026). *Modelo de credibilidade fiscal: Selic, reservas e ajuste fiscal no Brasil*
> (versão 1.0.0) [software]. Zenodo. https://doi.org/10.5281/zenodo.23934618
