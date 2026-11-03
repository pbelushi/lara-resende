# Relatório v2: credibilidade, teoria da inflação e estabilização da dívida

Gerado em 2026-11-02 13:34 · t0 = 2026T3 (último trimestre fechado, 2026-09-30) · Monte Carlo N = 1000 por (especificação, variante, cenário, λ), semente 42, mesmos choques em todos os experimentos.

## 1. Ordenamento por especificação (variante base)

Critério: menor λ\*₈₀ na diagonal λ_π = λ_fiscal; desempate por λ\*₅₀, λ\* determinístico e P(sucesso) máxima.

### P1 · Phillips híbrida

Ordem: **C > A > B**

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | não atinge | não atinge | não atinge | 16% | 0% | nenhum |
| B. Lara Resende puro | não atinge | não atinge | não atinge | 1% | 99% | nenhum |
| C. Lara Resende condicionado | 0,33 | 0,66 | não atinge | 77% | 0% | [0,33 – 1,00] |

### P2 · Phillips achatada

Ordem: **C > A > B**

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | não atinge | não atinge | não atinge | 3% | 0% | nenhum |
| B. Lara Resende puro | não atinge | não atinge | não atinge | 1% | 99% | nenhum |
| C. Lara Resende condicionado | 0,36 | 0,65 | não atinge | 77% | 0% | [0,36 – 1,00] |

### P3 · Fechamento fiscal (FTPL)

Ordem: **C > A > B**

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | não atinge | não atinge | não atinge | 19% | 0% | nenhum |
| B. Lara Resende puro | não atinge | não atinge | não atinge | 2% | 0% | nenhum |
| C. Lara Resende condicionado | 0,76 | 0,80 | 0,91 | 86% | 0% | [0,76 – 1,00] |

Critérios que mais falharam (média da grade de λ; explosivas sobre o total, demais entre as não explosivas):

| Especificação | Cenário | inflação explosiva (>20%) | dívida ainda subindo | dívida acima da tolerância | inflação acima do teto | reservas abaixo do piso |
|---|---|---|---|---|---|---|
| P1 | A | 2% | 55% | 87% | 17% | 0% |
| P1 | B | 65% | 25% | 24% | 14% | 0% |
| P1 | C | 2% | 54% | 47% | 19% | 0% |
| P2 | A | 11% | 57% | 86% | 25% | 0% |
| P2 | B | 63% | 26% | 26% | 16% | 0% |
| P2 | C | 9% | 46% | 39% | 26% | 0% |
| P3 | A | 0% | 75% | 95% | 0% | 0% |
| P3 | B | 28% | 68% | 59% | 4% | 0% |
| P3 | C | 1% | 73% | 76% | 0% | 0% |

## 2. Robustez do ordenamento

Nas três especificações (variante base): P1: C > A > B; P2: C > A > B; P3: C > A > B. **O ordenamento é o mesmo nas três: a conclusão é robusta à teoria de inflação.**

Gráfico `12_ordenamento_variantes`. Ordem por variante (1º → 3º):

| Variante | Descrição | P1 | P2 | P3 |
|---|---|---|---|---|
| base (obrigatória) | calibração padrão | C > A > B | C > A > B | C > A > B |
| neutro_45 (obrigatória) | r_neutro = 4,5 (7,5% é neutra) | A > C > B | C > A > B | A > C > B |
| inercia_alta (obrigatória) | b1 = 0,82 (estimado) | C > A > B | C > A > B | — |
| repasse_est (obrigatória) | b3 = 0,012 (estimado) | C > A > B | C > A > B | C > A > B |
| C_lento (obrigatória) | C com corte em 12 trimestres | C > A > B | C > A > B | C > A > B |
| C_sem_tolerancia (obrigatória) | C com δ0 = 0 | C > A > B | C > A > B | C > A > B |
| p2_zero | P3 com p2 = 0 | — | — | C > A > B |
| p2_integral | P3 com p2 integral (0,3) | — | — | C > A > B |
| vt_perpetuidade | P3 com valor terminal 100·s/(r−g) | — | — | C > A > B |
| tp_050 | tp_lp = 0,5 | C > A > B | C > A > B | C > A > B |
| tp_100 | tp_lp = 1,0 | C > A > B | C > A > B | C > A > B |
| rolagem_0 | r_min_rolagem = 0 | C > A > B | C > A > B | C > A > B |
| rolagem_2 | r_min_rolagem = 2,0 | C > A > B | C > A > B | C > A > B |

Variantes obrigatórias que alteram o ordenamento da base: neutro_45 em P1 (A > C > B); neutro_45 em P3 (A > C > B).

Teto de inflação em meta + 2,0 p.p. (variante base): P1: C > A > B; P2: C > A > B; P3: C > A > B (mesmo ordenamento).

## 3. Área de sucesso na superfície λ_π × λ_fiscal

Fração do quadrado [0,1]² com P(sucesso) ≥ 80% (grade 21 × 21, N = 300 por ponto). Maior área = mais robusto às duas formas de desconfiança.

| Variante | Cenário | P1 | P2 | P3 |
|---|---|---|---|---|
| base | A. Ortodoxo | 0% | 0% | 0% |
| base | B. Lara Resende puro | 0% | 0% | 0% |
| base | C. Lara Resende condicionado | 0% | 0% | 2% |
| neutro_45 | A. Ortodoxo | 2% | 1% | 11% |
| neutro_45 | B. Lara Resende puro | 0% | 0% | 0% |
| neutro_45 | C. Lara Resende condicionado | 2% | 5% | 10% |

Gráficos `10_superficie_base` e `10_superficie_neutro_45`.

## 4. Validação e especificação de referência

Selic, primário e depreciação cambial observados; em P3, primário anunciado = mediana do Focus em cada data. Erro = RMSE/desvio-padrão de inflação + NTN-B 10 anos.

| Especificação | Episódio | λ de melhor ajuste | θ (P3) | Erro mín. | Erro λ = 0 | Erro λ = 1 | Erro P3 com θ = 0,5 | Pico obs. / sim. | Reproduz o pico de 2021–22? |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 2016–2019: âncora fiscal e queda da Selic | 1,00 | — | 1,61 | 38,37 | 1,61 | — | — | — |
| P1 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,15 | — | 3,78 | 9,54 | 6,12 | — | 11,9 / 7,5 | não |
| P2 | 2016–2019: âncora fiscal e queda da Selic | 1,00 | — | 1,44 | 40,36 | 1,44 | — | — | — |
| P2 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,30 | — | 3,74 | 23,22 | 5,90 | — | 11,9 / 8,6 | não |
| P3 | 2016–2019: âncora fiscal e queda da Selic | 1,00 | 0,25 | 2,10 | 40,93 | 2,10 | 2,21 | — | — |
| P3 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 1,00 | 0,25 | 6,69 | 29,28 | 6,69 | 6,99 | 11,9 / 2,1 | não |

Erro combinado: P1 = 5,39; P2 = 5,18; P3 = 8,79. **Especificação de referência: P2 · Phillips achatada** (ordem: C > A > B).
Nenhuma especificação reproduz o pico de 2021–22: o pico tem componente de oferta e commodities não modelado.
Sobreajuste: P3 tem θ como parâmetro livre a mais; ver a coluna de erro com θ fixo em 0,5.

## 5. Premissas e limitações

### Condições iniciais

| Variável | Valor | Data real da última observação |
|---|---|---|
| Meta Selic (% a.a.) | 13,75 | 2026-09-30 |
| IPCA 12m (%) | 4,58 | 2026-09-01 |
| Focus IPCA 12m à frente (%) | 4,37 | 2026-09-30 |
| Hiato do produto (HP, %) | -0,42 | 2026-06-30 |
| Crescimento potencial (% a.a.) | 2,86 | 2026-06-30 |
| Dívida bruta do governo geral (% PIB) | 82,93 | 2026-09-01 |
| DLSP (% PIB) | 69,98 | 2026-09-01 |
| Reservas (US$ bi) | 362,82 | 2026-09-01 |
| Câmbio (R$/US$, média do trimestre) | 5,14 | 2026-09-30 |
| Primário do setor público, 12m (% PIB) | -0,52 | 2026-09-01 |
| NTN-B ~10 anos (% a.a.) | 7,75 | 2026-09-30 |
| NTN-B ~5 anos (% a.a.) | 8,06 | 2026-09-30 |

Focus na pesquisa de 2026-09-30: primário 2026: -0,41, 2027: -0,40, 2028: -0,29, 2029: -0,15, 2030: -0,05; DLSP 2026: 70,0, 2027: 73,8, 2028: 76,5, 2029: 79,1, 2030: 81,3 (% PIB).

### Juros e term premium

- Term premium inicial (fecha a identidade do juro longo em t0): -3,52 p.p.; converge para tp_lp = 0,75 p.p. com τ = 6 trimestres.
- Checagem (ANBIMA indisponível sem credenciais): inclinação NTN-B 10a − 5a em t0 = -0,31 p.p. (Tesouro Direto).
- Juro real longo neutro implícito: r_neutro = 5,0 → 7,25% a.a. (+2,25 p.p. sobre o curto neutro = tp_lp + p0); r_neutro = 4,5 → 6,75% a.a. (+2,25 p.p. sobre o curto neutro = tp_lp + p0). Com meta de 3,0%, a Selic de 7,5% é neutra só com r_neutro = 4,5.
- Restrição de rolagem: LFT com juro real abaixo de 1,0% migra para NTN-B (giro 8,3%/trimestre, banda 2,0 p.p.).
- Repressão financeira (trimestres com juro real da LFT < 0, trajetória determinística em λ = 0,5): P1/A: 0; P1/B: 18; P1/C: 0; P2/A: 0; P2/B: 32; P2/C: 0; P3/A: 0; P3/B: 0; P3/C: 0.

### Parâmetros-chave

| Parâmetro | Valor | Fonte |
|---|---|---|
| a1 | 0,777 | estimado (OLS) |
| a2 | 0,182 | estimado (OLS) |
| b1 | 0,6 | padrão |
| b2 | 0,153 | estimado (OLS) |
| b3 | 0,06 | padrão |
| b2_p2 | 0,025 | padrão |
| b2_p3 | 0,025 | padrão |
| theta | 0,5 | padrão |
| phi | 0 | padrão |
| delta_min | 0,5 | padrão |
| p2 | 0,3 | padrão |
| p2_p3 | 0,15 | padrão |
| p3 | 0,3 | padrão |
| kappa | 0,5 | padrão |
| mu | 0,25 | padrão |
| r_neutro_base | 5 | padrão |
| tp_lp | 0,75 | padrão |
| tau_tp | 6 | padrão |
| r_min_rolagem | 1 | padrão |
| R_min | 250 | padrão |

### Cenários

- Pacote fiscal (A e C): 2,7% do PIB ao fim das rampas.
- B e C: Selic exógena até 7,5% em 6 trimestres; venda de US$ 100 bi em reservas. C: tolerância δ0 = 1,0 p.p. que cai a zero em 8 trimestres após o corte.
- Sucesso: dívida com inclinação ≤ 0 nos últimos 8 trimestres e final ≤ inicial + 5 p.p.; inflação média final ≤ 4,5%; inflação ≤ 20% em todos os trimestres; reservas ≥ US$ 250 bi. Trajetórias com inflação acima de 50% são encerradas.

### Limitações

- λ_π e λ_fiscal são exógenos e constantes. Extensão sugerida: credibilidade adaptativa, λ[t] = λ[t−1] + ν (sucesso_parcial[t] − 0,5), separadamente para cada dimensão.
- P3 é uma versão reduzida da FTPL: não resolve um equilíbrio com expectativas racionais; a lacuna é absorvida por inflação na proporção θ, e θ é calibrado, não derivado.
- φ = 0 (a lacuna inicial já está precificada) é uma hipótese forte; com φ > 0 todos os cenários começam com pressão inflacionária adicional (ver sensibilidade de P3).
- A restrição de rolagem é uma regra de comportamento, não um modelo de demanda por títulos.
- O modelo continua semiestrutural e sem choques de oferta e de commodities.
- Os resultados de P1 e P2 dependem de b1 e b3; os de P3, de θ, Δ_min e da duração da dívida (gráficos `6_sensibilidade_*`).
- O piso de reservas (R_min) é ilustrativo e deve ser alinhado à métrica ARA do FMI.
- Duração da dívida: prazos médios de LTN e NTN-B do SGS (mesma base do RMD); a duração da NTN-B é aproximada pelo prazo médio, o que superestima a duração e atenua a inflação fiscal em P3.
- Inflação fiscal (P3): a lacuna entra como fração da dívida líquida e é medida contra a trajetória anunciada (com λ = 1 e sem choques, não há inflação fiscal); o valor terminal segue a fórmula literal s/max(r − g, Δ_min), e a perpetuidade 100·s/(r − g) é a variante `vt_perpetuidade` (ver README).
- O teto de inflação não tem piso: trajetórias deflacionárias (limitadas a −5% a.a.) contam como inflação controlada; o critério de dívida costuma reprová-las.
