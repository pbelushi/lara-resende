# Relatório v2.1: credibilidade, teoria da inflação e estabilização da dívida

Gerado em 2026-11-02 14:17 · t0 = 2026T3 (último trimestre fechado, 2026-09-30) · Monte Carlo N = 1000 por (especificação, variante, cenário, λ), semente 42, mesmos choques em todos os experimentos.

## 0. Checagem de consistência

Trajetória determinística, P1, λ = 1. Custo real efetivo em estado estacionário = composição final de A, com LFT ao juro curto neutro e NTN-B, prefixados e cambial ao juro longo neutro. Primário estabilizador = (r − g)/(1 + g) × dívida inicial, com g = 2,86% a.a. Folga = primário final (média dos últimos 8 trimestres) − estabilizador da dívida bruta.

| r_long neutro | ω | r neutro curto | tp_lp | Custo real efetivo | Estabilizador bruta | Estabilizador líquida | Primário final A / B / C | Folga A / B / C | A estabiliza? |
|---|---|---|---|---|---|---|---|---|---|
| 4,5 | 0,0 | 5,0 | -0,50 | 4,80 | 1,57 | 1,32 | 3,52 / 0,87 / 3,59 | 1,95 / -0,69 / 2,02 | sim |
| 4,5 | 0,5 | 5,0 | -0,50 | 4,79 | 1,56 | 1,31 | 3,47 / 1,04 / 3,69 | 1,91 / -0,52 / 2,13 | sim |
| 4,5 | 1,0 | 5,0 | -0,50 | 4,79 | 1,56 | 1,32 | 3,65 / 1,13 / 3,66 | 2,09 / -0,43 / 2,10 | sim |
| 5,5 | 0,0 | 5,0 | 0,50 | 5,21 | 1,89 | 1,60 | 3,51 / 0,80 / 3,57 | 1,62 / -1,09 / 1,68 | sim |
| 5,5 | 0,5 | 5,0 | 0,50 | 5,21 | 1,90 | 1,60 | 3,45 / 1,02 / 3,68 | 1,55 / -0,88 / 1,78 | sim |
| 5,5 | 1,0 | 5,0 | 0,50 | 5,21 | 1,89 | 1,60 | 3,62 / 1,13 / 3,66 | 1,72 / -0,76 / 1,77 | sim |
| 6,5 | 0,0 | 5,0 | 1,50 | 5,64 | 2,24 | 1,89 | 3,49 / 0,71 / 3,56 | 1,25 / -1,53 / 1,31 | sim |
| 6,5 | 0,5 | 5,0 | 1,50 | 5,66 | 2,26 | 1,91 | 3,42 / 1,00 / 3,66 | 1,16 / -1,26 / 1,40 | sim |
| 6,5 | 1,0 | 5,0 | 1,50 | 5,65 | 2,25 | 1,90 | 3,58 / 1,13 / 3,66 | 1,33 / -1,12 / 1,42 | sim |

Portão de qualidade (calibração base): A estabiliza a dívida com adesão total; o ranking abaixo compara robustez relativa.
Referência empírica (não usada como padrão): NTN-B 10 anos real média de 4,57% em 2017–2019 e 6,11% desde 2004-12.

## 1. Ordenamento por especificação (variante base)

Critério: menor λ\*₈₀ na diagonal λ_π = λ_fiscal; desempate por λ\*₅₀, λ\* determinístico e P(sucesso) máxima.

### P1 · Phillips híbrida

Ordem: **A > C > B**

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | 0,07 | 0,42 | 0,84 | 84% | 0% | [0,07 – 1,00] |
| B. Lara Resende puro | 0,72 | não atinge | não atinge | 5% | 89% | [0,72 – 0,72] |
| C. Lara Resende condicionado | 0,09 | 0,50 | 0,85 | 87% | 0% | [0,09 – 1,00] |

### P2 · Phillips achatada

Ordem: **A > C > B**

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | 0,26 | 0,42 | 0,79 | 87% | 0% | [0,26 – 1,00] |
| B. Lara Resende puro | 0,70 | não atinge | não atinge | 4% | 87% | [0,70 – 0,70] |
| C. Lara Resende condicionado | 0,17 | 0,46 | 0,82 | 88% | 0% | [0,17 – 1,00] |

### P3 · Fechamento fiscal (FTPL)

Ordem: **A > C > B**

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | 0,62 | 0,62 | 0,68 | 97% | 0% | [0,62 – 1,00] |
| B. Lara Resende puro | não atinge | não atinge | não atinge | 4% | 0% | nenhum |
| C. Lara Resende condicionado | 0,65 | 0,67 | 0,75 | 98% | 0% | [0,65 – 1,00] |

Critérios que mais falharam (média da grade de λ; explosivas sobre o total, demais entre as não explosivas):

| Especificação | Cenário | inflação explosiva (>20%) | dívida ainda subindo | dívida acima da tolerância | inflação acima do teto | reservas abaixo do piso |
|---|---|---|---|---|---|---|
| P1 | A | 0% | 25% | 23% | 22% | 0% |
| P1 | B | 58% | 27% | 29% | 15% | 0% |
| P1 | C | 0% | 38% | 30% | 19% | 0% |
| P2 | A | 4% | 24% | 26% | 25% | 0% |
| P2 | B | 56% | 27% | 29% | 16% | 0% |
| P2 | C | 4% | 32% | 25% | 26% | 0% |
| P3 | A | 1% | 50% | 60% | 0% | 0% |
| P3 | B | 25% | 70% | 62% | 1% | 0% |
| P3 | C | 2% | 48% | 64% | 1% | 0% |

## 2. Ordenamento por juro real longo neutro

Resultado central da v2.1: o juro neutro decide entre A e C. Ordem e λ\*₈₀ (λ\*₅₀ entre parênteses) de cada cenário.

| Especificação | r_long neutro | Ordem | λ\*₈₀ A | λ\*₈₀ B | λ\*₈₀ C |
|---|---|---|---|---|---|
| P1 | 4,5 | A > C > B | 0,76 (0,33) | não atinge (não atinge) | 0,79 (0,45) |
| P1 | 5,5 | A > C > B | 0,84 (0,42) | não atinge (não atinge) | 0,85 (0,50) |
| P1 | 6,5 | C > A > B | 0,99 (0,52) | não atinge (não atinge) | 0,97 (0,57) |
| P2 | 4,5 | A > C > B | 0,71 (0,36) | não atinge (não atinge) | 0,73 (0,41) |
| P2 | 5,5 | A > C > B | 0,79 (0,42) | não atinge (não atinge) | 0,82 (0,46) |
| P2 | 6,5 | A > C > B | 0,93 (0,51) | não atinge (não atinge) | 0,94 (0,54) |
| P3 | 4,5 | A > C > B | 0,64 (0,58) | não atinge (não atinge) | 0,66 (0,60) |
| P3 | 5,5 | A > C > B | 0,68 (0,62) | não atinge (não atinge) | 0,75 (0,67) |
| P3 | 6,5 | A > C > B | 0,72 (0,66) | não atinge (não atinge) | 0,83 (0,73) |

## 3. Robustez do ordenamento por variante

Nas três especificações (variante base): P1: A > C > B; P2: A > C > B; P3: A > C > B. **O ordenamento é o mesmo nas três: a conclusão é robusta à teoria de inflação.**

Gráfico `12_ordenamento_variantes`. Ordem por variante (1º → 3º):

| Variante | Descrição | P1 | P2 | P3 |
|---|---|---|---|---|
| base (obrigatória) | r_long_neutro = 5,5; ω = 0 | A > C > B | A > C > B | A > C > B |
| rlong_45 (obrigatória) | r_long_neutro = 4,5 | A > C > B | A > C > B | A > C > B |
| rlong_65 (obrigatória) | r_long_neutro = 6,5 | C > A > B | A > C > B | A > C > B |
| neutro_45 (obrigatória) | r_neutro = 4,5 e r_long_neutro = 5,0 (mesmo tp_lp) | A > C > B | A > C > B | A > C > B |
| omega_05 (obrigatória) | ω = 0,5 | A > C > B | C > A > B | A > C > B |
| omega_1 (obrigatória) | ω = 1 (todo o prêmio pela Taylor) | A > C > B | C > A > B | A > C > B |
| inercia_alta (obrigatória) | b1 = 0,82 (estimado) | A > C > B | A > C > B | — |
| repasse_est (obrigatória) | b3 = 0,012 (estimado) | C > A > B | C > A > B | A > C > B |
| C_lento (obrigatória) | C com corte em 12 trimestres | A > C > B | A > C > B | A > C > B |
| C_sem_tolerancia (obrigatória) | C com δ0 = 0 | A > C > B | A > C > B | A > C > B |
| phi_025 (obrigatória) | P3 com φ = 0,25 | — | — | B > A > C † |
| phi_05 (obrigatória) | P3 com φ = 0,5 | — | — | A > B > C † |
| rolagem_0 | r_min_rolagem = 0 | A > C > B | A > C > B | A > C > B |
| rolagem_2 | r_min_rolagem = 2,0 | A > C > B | A > C > B | A > C > B |
| p2_zero | P3 com p2 = 0 | — | — | A > C > B |
| p2_integral | P3 com p2 integral (0,3) | — | — | A > C > B |
| vt_perpetuidade | P3 com valor terminal 100·s/(r−g) | — | — | C > A > B |

† Nenhum cenário atinge P(sucesso) ≥ 50% nesta variante: a ordem vem só do desempate pela probabilidade máxima e compara graus de fracasso, não robustez relativa.

Variantes obrigatórias que alteram o ordenamento da base (excluídas as marcadas com †): rlong_65 em P1 (C > A > B); repasse_est em P1 (C > A > B); omega_05 em P2 (C > A > B); omega_1 em P2 (C > A > B); repasse_est em P2 (C > A > B).

Teto de inflação em meta + 2,0 p.p. (variante base): P1: A > C > B; P2: A > C > B; P3: A > C > B (mesmo ordenamento).

## 4. Área de sucesso na superfície λ_π × λ_fiscal

Fração do quadrado [0,1]² com P(sucesso) ≥ 80% (grade 21 × 21, N = 300 por ponto). Maior área = mais robusto às duas formas de desconfiança.

| Variante | Cenário | P1 | P2 | P3 |
|---|---|---|---|---|
| base | A. Ortodoxo | 12% | 17% | 20% |
| base | B. Lara Resende puro | 0% | 0% | 0% |
| base | C. Lara Resende condicionado | 10% | 12% | 15% |
| neutro_45 | A. Ortodoxo | 23% | 31% | 28% |
| neutro_45 | B. Lara Resende puro | 0% | 0% | 0% |
| neutro_45 | C. Lara Resende condicionado | 14% | 18% | 22% |
| rlong_45 | A. Ortodoxo | 22% | 28% | 26% |
| rlong_45 | B. Lara Resende puro | 0% | 0% | 0% |
| rlong_45 | C. Lara Resende condicionado | 17% | 22% | 21% |
| rlong_65 | A. Ortodoxo | 0% | 1% | 14% |
| rlong_65 | B. Lara Resende puro | 0% | 0% | 0% |
| rlong_65 | C. Lara Resende condicionado | 0% | 1% | 8% |

Gráficos `10_superficie_base`, `10_superficie_neutro_45`, `10_superficie_rlong_45`, `10_superficie_rlong_65`.

## 5. Validação e especificação de referência

Selic, primário e depreciação cambial observados; em P3, primário anunciado = mediana do Focus em cada data. Erro = RMSE/desvio-padrão de inflação + NTN-B 10 anos.

| Especificação | Episódio | λ de melhor ajuste | θ (P3) | Erro mín. | Erro λ = 0 | Erro λ = 1 | Erro P3 com θ = 0,5 | Pico obs. / sim. | Reproduz o pico de 2021–22? |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 2016–2019: âncora fiscal e queda da Selic | 0,90 | — | 1,91 | 35,90 | 1,95 | — | — | — |
| P1 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,10 | — | 4,48 | 4,65 | 5,24 | — | 11,9 / 5,3 | não |
| P2 | 2016–2019: âncora fiscal e queda da Selic | 0,95 | — | 1,76 | 39,00 | 1,78 | — | — | — |
| P2 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,40 | — | 4,02 | 15,01 | 4,99 | — | 11,9 / 6,5 | não |
| P3 | 2016–2019: âncora fiscal e queda da Selic | 1,00 | 0,25 | 2,17 | 31,08 | 2,17 | 2,26 | — | — |
| P3 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,30 | 0,00 | 4,01 | 26,61 | 5,45 | 5,99 | 11,9 / 9,1 | sim |

Erro combinado: P1 = 6,39; P2 = 5,78; P3 = 6,17. **Especificação de referência: P2 · Phillips achatada** (ordem: A > C > B).
P3 reproduz o pico de 2021–22 e P1 não, mas com θ = 0, isto é, sem o canal fiscal: a reprodução vem da ausência de inércia própria (a inflação segue as expectativas), não da lacuna fiscal. Não é evidência a favor da leitura fiscal da inflação recente.
Sobreajuste: P3 tem θ como parâmetro livre a mais; ver a coluna de erro com θ fixo em 0,5.
Em parte dos episódios o melhor ajuste de P3 tem θ = 0: nos dados brasileiros, o canal fiscal não melhora o ajuste e P3 se reduz a uma Phillips achatada sem inércia.

## 6. Premissas e limitações

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

### Juros, prêmio e term premium

- Juro real curto neutro 5,0% e juro real longo neutro 5,5% (calibrado diretamente; grade 4,5 / 5,5 / 6,5); tp_lp derivado = 0,50 p.p. O prêmio médio p0 = 1,5 não entra no nível de nenhum dos dois juros.
- Desvios do prêmio: fração ω = 0,0 pela Taylor e 1 − ω pelo juro longo (variantes ω = 0,5 e 1).
- Term premium inicial (fecha a identidade do juro longo em t0): -2,02 p.p.; converge para tp_lp com τ = 6 trimestres.
- Checagem (ANBIMA indisponível sem credenciais): inclinação NTN-B 10a − 5a em t0 = -0,31 p.p. (Tesouro Direto).
- Com meta de 3,0%, a Selic de 7,5% é neutra só com r_neutro = 4,5 (variante neutro_45).
- Duração da dívida (Macaulay (estoque da DPF por vencimento, taxas do Tesouro Direto)): NTN-B 7,3 anos (prazo médio do estoque 12,5); prefixados 2,4 anos (prazo 2,9); LFT 0,25 ano. Estoque de 2026-08.
- Restrição de rolagem: LFT com juro real abaixo de 1,0% migra para NTN-B (giro 8,3%/trimestre, banda 2,0 p.p.).

Repressão financeira: fração do tempo com juro real da LFT abaixo de zero (trajetória determinística):

| Especificação | Cenário | λ = 0,3 | λ = 0,5 | λ = 0,9 |
|---|---|---|---|---|
| P1 | A | 0% | 0% | 0% |
| P1 | B | 69% | 58% | 0% |
| P1 | C | 0% | 0% | 0% |
| P2 | A | 0% | 0% | 0% |
| P2 | B | 69% | 68% | 0% |
| P2 | C | 0% | 0% | 0% |
| P3 | A | 0% | 0% | 0% |
| P3 | B | 40% | 0% | 0% |
| P3 | C | 0% | 0% | 0% |

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
| r_long_neutro | 5,5 | padrão |
| tp_lp | 0,5 | padrão |
| omega | 0 | padrão |
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
- φ = 0 (a lacuna inicial já está precificada) é uma hipótese forte; com φ > 0 todos os cenários começam com pressão inflacionária adicional (variantes phi_025 e phi_05 na seção 3).
- A restrição de rolagem é uma regra de comportamento, não um modelo de demanda por títulos.
- O modelo continua semiestrutural e sem choques de oferta e de commodities.
- Os resultados de P1 e P2 dependem de b1 e b3; os de P3, de θ, Δ_min e da duração da dívida (gráficos `6_sensibilidade_*`).
- O piso de reservas (R_min) é ilustrativo e deve ser alinhado à métrica ARA do FMI.
- Duração de Macaulay calculada com taxas do Tesouro Direto do vértice mais próximo (não ANBIMA) e com o estoque total da DPMFi (mercado e carteira do BC).
- O VP de P3 desconta o horizonte explícito ao juro longo corrente e o valor terminal ao juro longo neutro.
- Inflação fiscal (P3): a lacuna entra como fração da dívida líquida e é medida contra a trajetória anunciada (com λ = 1 e sem choques, não há inflação fiscal); o valor terminal segue a fórmula literal s/max(r − g, Δ_min), e a perpetuidade 100·s/(r − g) é a variante `vt_perpetuidade` (ver README).
- O teto de inflação não tem piso: trajetórias deflacionárias (limitadas a −5% a.a.) contam como inflação controlada; o critério de dívida costuma reprová-las.
