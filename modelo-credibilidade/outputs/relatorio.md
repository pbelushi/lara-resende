# Relatório: credibilidade, Selic e estabilização da dívida

Gerado em 2026-11-02 11:29 · trimestre-base 2026T4 (a coluna Data indica o trimestre da última observação) · Monte Carlo com N = 1000 por (cenário, λ), semente 42.

## Ordenação por robustez à desconfiança

Critério: menor λ\*₈₀ (adesão mínima para P(sucesso) ≥ 80%); desempate por λ\*₅₀ e λ\* determinístico.

| Posição | Cenário | λ\* determinístico | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| 1 | A. Ortodoxo | 0.08 | 0.34 | 0.71 | 88% | [0.08, 1.00] |
| 2 | C. Lara Resende condicionado | 0.57 | 0.48 | 1.00 | 80% | [0.57, 1.00] |
| 3 | B. Lara Resende puro | 0.77 | não atinge | não atinge | 16% | [0.77, 0.84] |

**Mais robusto: A. Ortodoxo**, que atinge 80% de probabilidade de sucesso com adesão a partir de λ = 0.71.

### Avisos de monotonicidade

- B. Lara Resende puro: sucesso determinístico **não monotônico** em λ; intervalos [0.77, 0.84].

## Critérios que mais falharam

Fração das simulações estocásticas que violam cada critério, na média da grade de λ (e em λ = 0,5).

| Cenário | dívida ainda subindo no fim | dívida acima da tolerância | inflação acima do teto | reservas abaixo do piso |
|---|---|---|---|---|
| A. Ortodoxo | 15% (7%) | 21% (1%) | 24% (25%) | 0% (0%) |
| B. Lara Resende puro | 15% (2%) | 17% (4%) | 78% (98%) | 0% (0%) |
| C. Lara Resende condicionado | 25% (4%) | 24% (1%) | 40% (45%) | 0% (0%) |

## Validação qualitativa (seção 10)

Selic, primário e depreciação cambial seguem o observado; λ escolhido por menor erro normalizado (RMSE/desvio-padrão) de inflação e NTN-B 10 anos.

| Episódio | λ de melhor ajuste | Erro mín. | Erro λ = 0 | Erro λ = 1 |
|---|---|---|---|---|
| 2016–2019: âncora fiscal e queda da Selic | 0.90 | 2.36 | 64.44 | 2.42 |
| 2020–2022: Selic a 2%, expansão fiscal e aperto | 0.90 | 3.99 | 8.51 | 4.00 |

Leitura: o episódio 2016–2019 é bem reproduzido com adesão alta. No episódio 2020–2022 nenhum λ reproduz o pico de inflação de 2021–2022, que teve forte componente de choques de oferta e de commodities ausentes do modelo; o λ de melhor ajuste desse episódio não deve ser lido como estimativa de credibilidade.

## Premissas

### Condições iniciais (última observação)

| Variável | Valor | Data |
|---|---|---|
| Meta Selic (% a.a.) | 13.75 | 2026-12-31 |
| IPCA 12m (%) | 4.58 | 2026-09-30 |
| Focus IPCA 12m à frente (%) | 4.52 | 2026-12-31 |
| Hiato do produto (HP, %) | -0.42 | 2026-06-30 |
| Crescimento potencial (tendência HP, % a.a.) | 2.86 | 2026-06-30 |
| Dívida bruta do governo geral (% PIB) | 82.93 | 2026-09-30 |
| DLSP (% PIB) | 69.98 | 2026-09-30 |
| Reservas (US$ bi) | 362.82 | 2026-09-30 |
| Câmbio (R$/US$, média do trimestre) | 5.13 | 2026-12-31 |
| Primário do setor público consolidado, 12m (% PIB) | -0.52 | 2026-09-30 |
| NTN-B ~10 anos (% a.a.) | 7.12 | 2026-12-31 |
| Composição da dívida: LFT+compromissadas / pré / índices de preço / câmbio | 59% / 19% / 22% / 0.0% | 2026-09-30 |

### Constantes derivadas

- Custo nominal efetivo inicial da dívida: 13.16% a.a.; primário estabilizador inicial: 4.77% do PIB.
- Prêmio inicial: 3.47 p.p.; term premium calibrado para fechar a identidade do juro longo no t0: -3.33 p.p. (negativo porque a Selic esperada para os próximos 8 trimestres está acima da taxa real longa: a curva real está invertida).
- Juro real longo neutro implícito: 3.17% a.a.
- Receita líquida estrutural do governo central: 18.90% do PIB (RTN de 2026-07, ajustada ao primário do BCB).

### Parâmetros

| Parâmetro | Valor | Fonte |
|---|---|---|
| a1 | 0.777 | estimado (OLS) |
| a2 | 0.182 | estimado (OLS) |
| a3 | 0.4 | padrão |
| a4 | 0.8 | padrão |
| a5 | 0.03 | padrão |
| a6 | 0.1 | padrão |
| b1 | 0.6 | padrão |
| b2 | 0.153 | estimado (OLS) |
| b3 | 0.06 | padrão |
| rho | 0.8 | padrão |
| phi_pi | 1.5 | padrão |
| phi_h | 0.5 | padrão |
| r_neutro_base | 5 | padrão |
| kappa | 0.5 | padrão |
| mu | 0.25 | padrão |
| p0 | 1.5 | padrão |
| p1 | 0.03 | padrão |
| p2 | 0.3 | padrão |
| p3 | 0.3 | padrão |
| d_ref | 70 | padrão |
| c1 | 1 | padrão |
| c2 | 3.72 | estimado (OLS) |
| c3 | 2 | padrão |
| c4 | 0.5 | padrão |
| eta | 1 | padrão |
| R_min | 250 | padrão |

Estimativas OLS rejeitadas (fora da faixa de teste ou sinal errado; usado o padrão): b1 = 0.820, b3 = 0.012, c1 = -3.036.

### Cenários

- Pacote fiscal (A e C), total de 2.7% do PIB ao fim das rampas: Extinção programada de renúncias (sunset) (1.2% PIB, receita); Limite para emendas (0.3% PIB, despesa); Revisão de subsídios (0.4% PIB, despesa); Nova regra dos pisos (inflação + componente real per capita) (0.8% PIB, despesa).
- B e C: Selic exógena até 7.5% em 6 trimestres; venda de reservas 100 US$ bi em 4 trimestres; C com tolerância δ = 1.0 p.p. em relação à Taylor.
- Critérios de sucesso: inclinação da dívida ≤ 0 nos últimos 8 trimestres, dívida final ≤ inicial + 5.0 p.p., inflação média final ≤ 4.5%, reservas ≥ US$ 250 bi.

## Limitações

- λ é **exógeno e constante**. Na prática a credibilidade evolui com o histórico da política. Extensão sugerida: λ[t] = λ[t−1] + ν (sucesso_parcial[t] − 0,5).
- O modelo é semiestrutural e reduzido; não captura equilíbrio geral, distribuição de renda nem a composição setorial do investimento.
- Os resultados dependem da calibração do prêmio de risco (p1 a p3) e do repasse cambial (b3). O mapa de sensibilidade (`6_sensibilidade`) mostra essa dependência e deve ser apresentado junto com o gráfico principal.
- O cenário B não inclui reação fiscal endógena; uma variante com regra de resposta do primário à dívida testaria se um ajuste reativo, em vez de anunciado, resolve o problema.
- Choques de oferta e de commodities não estão modelados (ver validação 2020–2022).
- O índice de inconsistência é medido em p.p. (sem a divisão por 100 da especificação), com p3 e μ recalibrados; ver README.
- O piso de reservas (R_min) é ilustrativo e deve ser alinhado à última avaliação ARA do FMI.
