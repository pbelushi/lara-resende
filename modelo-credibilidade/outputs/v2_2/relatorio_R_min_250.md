# Relatório v2.2: credibilidade, teoria da inflação e estabilização da dívida

Gerado em 2026-11-02 20:22 · t0 = 2026T3 (último trimestre fechado, 2026-09-30) · Monte Carlo N = 1000 por (especificação, variante, cenário, λ), semente 42, mesmos choques em todos os experimentos.

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

## 1. Parâmetros estimados

### Repasse cambial (b3)

Projeções locais mensais (2004–2026): repasse acumulado ERPT_h = β_h/δ_h (preço e câmbio na mesma janela), controles de 12 defasagens da inflação, hiato e desvio do Focus em relação à meta (ambos defasados) e variação do IC-Br em US$; dummy de 2020. IC de 95% por bootstrap em blocos de 12 meses. IV: depreciação instrumentada pela variação do dólar amplo e do VIX.

| Método | Índice | Amostra | ERPT 3m | ERPT 6m | ERPT 12m [IC 95%] | ERPT 24m | F 1º estágio (12m) |
|---|---|---|---|---|---|---|---|
| LP OLS | ipca | completa (dummy 2020) | 4% | 7% | 10% [1%; 33%] | 13% | — |
| LP OLS | ipca | sem 2020 | 5% | 8% | 12% [3%; 42%] | 12% | — |
| LP OLS | ipca | 2004–2015 | 6% | 4% | 0% [-63%; 71%] | 1% | — |
| LP OLS | ipca | 2016–2026 | 1% | 4% | 6% [-159%; 52%] | 45% | — |
| LP IV | ipca | completa (dummy 2020) | 6% | 6% | 9% [-31%; 48%] | 5% | 46,8 |
| LP IV | ipca | sem 2020 | 6% | 7% | 11% [-95%; 57%] | -1% | 45,7 |
| LP OLS | ipca_comerc | completa (dummy 2020) | 6% | 10% | 20% [5%; 65%] | 22% | — |
| LP OLS | ipca_livres | completa (dummy 2020) | 3% | 6% | 11% [-0%; 34%] | 12% | — |

Referência da v1 (regressão trimestral, coeficiente da depreciação em 12 meses): 0,012.
**Estimativa principal: LP IV**, ERPT em 12 meses = 9% [-31%; 48%]; F do primeiro estágio = 46,8 (instrumentos fortes: IV é a estimativa principal).

Calibração de b3 por impulso-resposta (choque de 10% de depreciação, Selic fixa, λ = 0,5): b3 tal que o repasse simulado em 4 trimestres = ERPT_12; conferência em 2 e 8 trimestres contra ERPT_6 e ERPT_24.

| Especificação | b3 pontual | b3 (IC inferior) | b3 (IC superior) | Modelo 2t / LP 6m | Modelo 4t / LP 12m | Modelo 8t / LP 24m |
|---|---|---|---|---|---|---|
| P1 | 0,0451 | 0,0000 | 0,2399 | 3% / 6% | 9% / 9% | 18% / 5% |
| P2 | 0,0464 | 0,0000 | 0,2411 | 3% / 6% | 9% / 9% | 17% / 5% |
| P3 | 0,0769 | 0,0000 | 0,3467 | 4% / 6% | 9% / 9% | 4% / 5% |
b3 (IC inferior) = 0 em P1, P2, P3: o limite inferior do IC de ERPT_12 (-31%) é menor que o repasse que o modelo já gera com b3 = 0 (via expectativas e inércia); como b3 negativo não tem interpretação, o parâmetro foi fixado em 0 nesse limite.
Em P1, P2, o modelo repassa 18%, 17% em 8 trimestres, contra 5% estimado em 24 meses: a inércia acumula o repasse além do que os dados mostram, mesmo com o ajuste exato em 4 trimestres.

### Fração do prêmio que passa pela Selic (ω)

Regra de Taylor mensal com prêmio, 2005-01 a 2024-08 (o EMBI+ foi descontinuado em jul/2024; não há CDS público por API). Unidade conferida: o Ipeadata publica o EMBI+ em pontos-base (média de 267 bp em 2005–2024, de 136 a 688); o painel divide por 100 e usa p.p. (média 2,67).
ψ = b_curto/(1 − ρ) é o efeito de longo prazo de 1 p.p. de prêmio sobre a Selic, além do canal das expectativas. IC de 95% de ψ pelo método de Fieller (não pelo método delta): quando 1 − ρ não é significativamente diferente de zero, o conjunto é ilimitado. A estimativa não é cortada em [0, 1].

| Amostra | Método | n | ρ (EP) | Coef. curto prazo do prêmio (EP) | ψ | IC 95% de Fieller | Classificação |
|---|---|---|---|---|---|---|---|
| completa | NLS | 236 | 0,967 (0,012) | 0,140 (0,071) | 4,23 | [0,02; 13,48] | identificado, mas com estimativa pontual fora de [0, 1] |
| completa | 2SLS/GMM | 233 | 0,967 (0,011) | 0,097 (0,091) | 2,94 | [-3,78; 10,11] | não informativo para o modelo (IC limitado, mas contém 0 e 1) |
| 2005–2015 | NLS | 132 | 0,976 (0,018) | 0,159 (0,080) | 6,74 | (−∞; -2,82] ∪ [0,51; ∞) | não identificado (IC ilimitado: 1 − ρ não é significativamente diferente de zero) |
| 2005–2015 | 2SLS/GMM | 129 | 0,983 (0,019) | 0,064 (0,119) | 3,65 | (−∞; ∞) | não identificado (IC ilimitado: 1 − ρ não é significativamente diferente de zero) |
| 2016–2024 | NLS | 104 | 0,915 (0,019) | 0,091 (0,098) | 1,07 | [-1,22; 4,08] | não informativo para o modelo (IC limitado, mas contém 0 e 1) |
| 2016–2024 | 2SLS/GMM | 101 | 0,920 (0,019) | 0,205 (0,121) | 2,56 | [-0,33; 8,95] | não informativo para o modelo (IC limitado, mas contém 0 e 1) |
| pré-autonomia (até fev/2021) | NLS | 194 | 0,986 (0,008) | 0,076 (0,062) | 5,57 | (−∞; -68,22] ∪ [-4,12; ∞) | não identificado (IC ilimitado: 1 − ρ não é significativamente diferente de zero) |
| pré-autonomia (até fev/2021) | 2SLS/GMM | 191 | 0,987 (0,007) | 0,007 (0,084) | 0,56 | (−∞; ∞) | não identificado (IC ilimitado: 1 − ρ não é significativamente diferente de zero) |
| pós-autonomia (mar/2021–) | NLS | 42 | 0,906 (0,027) | 0,274 (0,178) | 2,91 | [-0,55; 13,91] | não informativo para o modelo (IC limitado, mas contém 0 e 1) |
| pós-autonomia (mar/2021–) | 2SLS/GMM | 39 | 0,991 (0,083) | 1,295 (0,607) | 149,05 | (−∞; -15,93] ∪ [0,63; ∞) | não identificado (IC ilimitado: 1 − ρ não é significativamente diferente de zero) |

**Estimativa principal (NLS, amostra completa): ψ = 4,23, IC de Fieller [0,02; 13,48] — identificado, mas com estimativa pontual fora de [0, 1].**
- **Magnitude:** não identificada; o intervalo vai de 0,02 a 13,48 e a estimativa pontual (4,23) cai fora da faixa admissível, então ω não é calibrado pelos dados.
- **Sinal:** há evidência fraca, só por NLS na amostra completa (1 de 10 regressões), de que ω é positivo. Por isso, as variantes ω = 0,5 e ω = 1 aparecem no relatório com o mesmo destaque da base (ω = 0), e não como sensibilidade secundária.

Como o ponto está fora do domínio que o modelo admite e o intervalo, embora limitado, vai de praticamente zero a mais de dez, sem discriminar entre os valores da grade, ω **não é usado** no modelo: a variante `estimada` usa ω = 0 (o mesmo da base) com o b3 estimado, não há variantes estimada_omega_* e a incerteza sobre ω fica representada pela grade {0; 0,5; 1} (variantes base, omega_05 e omega_1).
Nenhuma regressão tem IC limitado e inteiramente fora de [0, 1]. As estimativas pontuais acima de 1 e os ρ próximos de 1 (Selic muito persistente) são compatíveis com variável omitida que move prêmio e Selic juntos (2008, 2015–16, 2020), mas os dados não permitem afirmar erro de especificação.

Verificação cruzada pelo juro longo (2005-01 a 2024-07, n = 235): Δ NTN-B10 = a + b·Δprêmio + c·ΔSelic esperada, b = 0,62 (EP 0,06; IC 95% [0,50; 0,73]). O modelo implica b ≈ 1 − ω; ψ + b = 4,84.
**A soma ψ + b não é informativa**, porque ψ não está identificado com precisão útil: qualquer valor de ψ no intervalo é compatível com os dados, e a soma herda essa indeterminação. Isoladamente, b é preciso: se o modelo valesse, implicaria ω ≈ 1 − b = 0,38 [0,27; 0,50], isto é, cerca de 62% do prêmio chegando ao juro longo. Esse valor é uma leitura indireta, condicionada à estrutura do modelo, e não substitui a estimação direta de ω; não é usado como calibração.

Ordenamento A × C na variante `estimada` (ao lado da base):

| Especificação | Base | Estimada | Δλ*₈₀ estimada [IC 95%] | Leitura |
|---|---|---|---|---|
| P1 | A ≈ C > B | A ≈ C > B | 0,01 [-0,03; 0,05] | empate estatístico |
| P2 | A ≈ C > B | A ≈ C > B | 0,00 [-0,03; 0,05] | empate estatístico |
| P3 | A > C > B | A > C > B | 0,08 [0,07; 0,10] | vantagem significativa de A |

## 2. Critério de inflação: só teto × banda simétrica

Só teto: inflação média dos últimos 8 trimestres ≤ 4,5%. Banda simétrica: entre 1,5% e 4,5% (intervalo de tolerância da meta). Os demais critérios são os mesmos. Ordens com "A ≈ C" quando o IC de 95% de Δλ\*₈₀ (bootstrap pareado da mesma métrica) contém zero.

| Variante | P1 teto | P1 banda | P2 teto | P2 banda | P3 teto | P3 banda |
|---|---|---|---|---|---|---|
| base | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |
| estimada | A ≈ C > B | C > A > B | A ≈ C > B | C > A > B | A > C > B | C > A > B |
| omega_038 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |
| omega_05 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |
| omega_1 | A > C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |
| theta_025 | — | — | — | — | A > C > B | C > A > B |
| theta_0 | — | — | — | — | C > A > B | C > A > B |
| pe_fiscal_05 | — | — | — | — | A > C > B | C > A > B |
| pe_fiscal_0 | — | — | — | — | A > C > B | C > A > B |
| neutro_45 | A > C > B | A ≈ C > B | A > C > B | A ≈ C > B | A > C > B | C > A > B |
| rlong_45 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |
| rlong_65 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |
| inercia_alta | A ≈ C > B | A ≈ C > B † | A ≈ C > B | A ≈ C > B | — | — |
| repasse_est | A ≈ C > B | C > A > B | A ≈ C > B | C > A > B | A > C > B | C > A > B |
| C_lento | A > C > B | A ≈ C > B | A > C > B | A ≈ C > B | A > C > B | C > A > B |
| C_sem_tolerancia | A ≈ C > B | A ≈ C > B | A > C > B | A ≈ C > B | A > C > B | C > A > B |
| C_piso_corte | C > A > B | A ≈ C > B | C > A > B | A ≈ C > B | C > A > B | C > A > B |
| C_sem_piso | C > A > B | A ≈ C > B | C > A > B | A ≈ C > B | C > A > B | C > A > B |
| A_reservas | A > C > B | A > C > B | A > C > B | A > C > B | A > C > B | C > A > B |
| along_20 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B |

Com a banda simétrica, nenhum cenário chega a 80% em boa parte das variantes de P1 e P2; por isso o ordenamento também é reportado nos limiares de 70% e 50% ("A ≈ C" pelo bootstrap do mesmo limiar):

| Variante | P1 80% | P1 70% | P1 50% | P2 80% | P2 70% | P2 50% | P3 80% | P3 70% | P3 50% |
|---|---|---|---|---|---|---|---|---|---|
| base | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |
| estimada | C > A > B | A ≈ C > B | A ≈ C > B | C > A > B | A ≈ C > B | C > A > B | C > A > B | C > A > B | C > A > B |
| omega_038 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |
| omega_05 | A ≈ C > B | C > A > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |
| omega_1 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B | C > A > B |
| theta_025 | — | — | — | — | — | — | C > A > B | C > A > B | C > A > B |
| theta_0 | — | — | — | — | — | — | C > A > B | C > A > B | C > A > B |
| pe_fiscal_05 | — | — | — | — | — | — | C > A > B | C > A > B | C > A > B |
| pe_fiscal_0 | — | — | — | — | — | — | C > A > B | C > A > B | C > A > B |
| neutro_45 | A ≈ C > B | A ≈ C > B | A > C > B | A ≈ C > B | A ≈ C > B | A > C > B | C > A > B | C > A > B | C > A > B |
| rlong_45 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |
| rlong_65 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |
| inercia_alta | A ≈ C > B † | A ≈ C > B † | A ≈ C > B † | A ≈ C > B | A ≈ C > B | A ≈ C > B | — | — | — |
| repasse_est | C > A > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B | C > A > B | C > A > B | C > A > B |
| C_lento | A ≈ C > B | A ≈ C > B | A > C > B | A ≈ C > B | A > C > B | A > C > B | C > A > B | C > A > B | C > A > B |
| C_sem_tolerancia | A ≈ C > B | A ≈ C > B | A > C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |
| C_piso_corte | A ≈ C > B | C > A > B | C > A > B | A ≈ C > B | C > A > B | C > A > B | C > A > B | C > A > B | A ≈ C > B |
| C_sem_piso | A ≈ C > B | C > A > B | C > A > B | A ≈ C > B | C > A > B | C > A > B | C > A > B | C > A > B | A ≈ C > B |
| A_reservas | A > C > B | A > C > B | A > C > B | A > C > B | A > C > B | A > C > B | C > A > B | C > A > B | C > A > B |
| along_20 | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | A ≈ C > B | C > A > B | C > A > B | C > A > B |

Δλ\* (C − A) com a banda, por limiar [IC 95%]:

| Especificação | Variante | 80% | 70% | 50% |
|---|---|---|---|---|
| P1 | base | 0,00 [-0,05; 0,00] ⚠ | -0,01 [-0,04; 0,02] | 0,02 [0,00; 0,05] |
| P1 | estimada | -0,06 [-0,12; -0,03] | -0,02 [-0,04; 0,01] | 0,00 [-0,02; 0,03] |
| P1 | C_sem_piso | -0,03 [-0,10; 0,00] ⚠ | -0,06 [-0,09; -0,04] | -0,06 [-0,08; -0,04] |
| P1 | C_piso_corte | -0,02 [-0,07; 0,00] ⚠ | -0,04 [-0,07; -0,02] | -0,06 [-0,08; -0,03] |
| P2 | base | 0,00 [-0,04; 0,00] ⚠ | 0,01 [-0,03; 0,02] | 0,00 [-0,03; 0,01] |
| P2 | estimada | -0,04 [-0,08; -0,01] | -0,02 [-0,04; 0,01] | -0,04 [-0,05; -0,01] |
| P2 | C_sem_piso | -0,02 [-0,06; 0,00] ⚠ | -0,03 [-0,07; -0,02] | -0,07 [-0,09; -0,04] |
| P2 | C_piso_corte | -0,02 [-0,06; 0,00] ⚠ | -0,04 [-0,06; -0,02] | -0,06 [-0,09; -0,04] |
| P3 | base | -0,05 [-0,07; -0,05] | -0,09 [-0,10; -0,07] | -0,15 [-0,16; -0,14] |
| P3 | estimada | -0,05 [-0,07; -0,04] | -0,07 [-0,09; -0,06] | -0,15 [-0,16; -0,13] |
| P3 | C_sem_piso | -0,02 [-0,03; -0,01] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| P3 | C_piso_corte | -0,02 [-0,03; -0,01] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |

Δλ\*₈₀ = λ\*₈₀(C) − λ\*₈₀(A) [IC 95%] e P(sucesso) máxima de A e C, com cada critério:

| Especificação | Variante | Δλ\*₈₀ teto | Δλ\*₈₀ banda | P máx. A teto → banda | P máx. C teto → banda |
|---|---|---|---|---|---|
| P1 | base | 0,01 [-0,05; 0,05] | 0,00 [-0,05; 0,00] ⚠ | 84% → 77% | 87% → 79% |
| P1 | estimada | 0,01 [-0,03; 0,05] | -0,06 [-0,12; -0,03] | 88% → 83% | 92% → 86% |
| P1 | omega_038 | 0,02 [-0,04; 0,06] | -0,01 [-0,07; 0,00] ⚠ | 86% → 78% | 88% → 81% |
| P1 | C_sem_piso | -0,08 [-0,13; -0,04] | -0,03 [-0,10; 0,00] ⚠ | 84% → 77% | 88% → 81% |
| P2 | base | 0,03 [-0,01; 0,07] | 0,00 [-0,04; 0,00] ⚠ | 87% → 78% | 88% → 79% |
| P2 | estimada | 0,00 [-0,03; 0,05] | -0,04 [-0,08; -0,01] | 90% → 85% | 92% → 86% |
| P2 | omega_038 | -0,01 [-0,04; 0,05] | 0,00 [-0,05; 0,00] ⚠ | 87% → 79% | 89% → 80% |
| P2 | C_sem_piso | -0,08 [-0,12; -0,05] | -0,02 [-0,06; 0,00] ⚠ | 87% → 78% | 89% → 81% |
| P3 | base | 0,07 [0,06; 0,09] | -0,05 [-0,07; -0,05] | 97% → 91% | 98% → 96% |
| P3 | estimada | 0,08 [0,07; 0,10] | -0,05 [-0,07; -0,04] | 97% → 90% | 96% → 94% |
| P3 | omega_038 | 0,07 [0,05; 0,08] | -0,06 [-0,07; -0,05] | 97% → 91% | 98% → 96% |
| P3 | theta_025 | 0,16 [0,14; 0,17] | -0,04 [-0,05; -0,03] | 99% → 96% | 99% → 98% |
| P3 | theta_0 | -0,04 [-0,05; -0,02] | -0,03 [-0,04; -0,01] | 96% → 96% | 99% → 98% |
| P3 | pe_fiscal_05 | 0,10 [0,08; 0,11] | -0,06 [-0,07; -0,05] | 98% → 91% | 98% → 96% |
| P3 | pe_fiscal_0 | 0,13 [0,11; 0,14] | -0,06 [-0,06; -0,04] | 98% → 91% | 98% → 96% |
| P3 | C_sem_piso | -0,08 [-0,09; -0,07] | -0,02 [-0,03; -0,01] | 97% → 91% | 99% → 96% |

Fração dos sucessos (critério de teto) com inflação média final abaixo de 1,5%, ponderada por P(sucesso) ao longo da grade de λ (variante base): P1: A 23%, C 13%; P2: A 23%, C 13%; P3: A 62%, C 17%.
- **P1:** empate com o teto, empate com a banda; o ranking não depende do piso de inflação.
- **P2:** empate com o teto, empate com a banda; o ranking não depende do piso de inflação.
- **P3:** vantagem de A com o teto, vantagem de C com a banda. **O ranking muda com a banda: a vantagem de A era em parte artificial**, sustentada por trajetórias com inflação abaixo da meta.

Área de sucesso (≥ 80%) na superfície, banda simétrica: P1/base/A: 0%; P1/base/B: 0%; P1/base/C: 0%; P1/C_sem_piso/C: 0%; P1/A_reservas/A: 0%; P2/base/A: 0%; P2/base/B: 0%; P2/base/C: 0%; P2/C_sem_piso/C: 0%; P2/A_reservas/A: 0%; P3/base/A: 2%; P3/base/B: 0%; P3/base/C: 7%; P3/C_sem_piso/C: 4%; P3/A_reservas/A: 4%.

## 3. Ordenamento por especificação (variante base e estimada; critério de teto)

Critério: menor λ\*₈₀ na diagonal λ_π = λ_fiscal; desempate por λ\*₅₀, λ\* determinístico e P(sucesso) máxima. Ordem estrita entre A e C só quando o IC de 95% de Δλ\*₈₀ (bootstrap pareado, R = 1000) exclui zero; caso contrário, "A ≈ C".

### P1 · Phillips híbrida

Base: **A ≈ C > B** — Δλ\*₈₀ = 0,01 [-0,05; 0,05], Δλ\*₅₀ = 0,08 [0,06; 0,12], C supera A em 33% das réplicas: empate estatístico.
Estimada: **A ≈ C > B** — Δλ\*₈₀ = 0,01 [-0,03; 0,05]: empate estatístico.

Grade de ω (mesmo destaque da base, porque ω não é calibrado pelos dados):

| ω | Variante | Ordem | λ\*₈₀ A | λ\*₈₀ C | λ\*₈₀ B | Δλ\*₈₀ (C − A) [IC 95%] | Leitura |
|---|---|---|---|---|---|---|---|
| 0 | base | A ≈ C > B | 0,84 | 0,85 | não atinge | 0,01 [-0,05; 0,05] | empate estatístico |
| 0,38 (1 − b) | omega_038 | A ≈ C > B | 0,81 | 0,83 | não atinge | 0,02 [-0,04; 0,06] | empate estatístico |
| 0,5 | omega_05 | A ≈ C > B | 0,81 | 0,82 | não atinge | 0,01 [-0,04; 0,05] | empate estatístico |
| 1 | omega_1 | A > C > B | 0,82 | 0,87 | não atinge | 0,05 [0,01; 0,07] | vantagem significativa de A |

Variante base em detalhe:

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | 0,07 | 0,42 | 0,84 | 84% | 0% | [0,07 – 1,00] |
| B. Lara Resende puro | 0,72 | não atinge | não atinge | 5% | 89% | [0,72 – 0,72] |
| C. Lara Resende condicionado | 0,09 | 0,50 | 0,85 | 87% | 0% | [0,09 – 1,00] |

### P2 · Phillips achatada

Base: **A ≈ C > B** — Δλ\*₈₀ = 0,03 [-0,01; 0,07], Δλ\*₅₀ = 0,04 [0,02; 0,06], C supera A em 8% das réplicas: empate estatístico.
Estimada: **A ≈ C > B** — Δλ\*₈₀ = 0,00 [-0,03; 0,05]: empate estatístico.

Grade de ω (mesmo destaque da base, porque ω não é calibrado pelos dados):

| ω | Variante | Ordem | λ\*₈₀ A | λ\*₈₀ C | λ\*₈₀ B | Δλ\*₈₀ (C − A) [IC 95%] | Leitura |
|---|---|---|---|---|---|---|---|
| 0 | base | A ≈ C > B | 0,79 | 0,82 | não atinge | 0,03 [-0,01; 0,07] | empate estatístico |
| 0,38 (1 − b) | omega_038 | A ≈ C > B | 0,79 | 0,78 | não atinge | -0,01 [-0,04; 0,05] | empate estatístico |
| 0,5 | omega_05 | A ≈ C > B | 0,78 | 0,78 | não atinge | 0,00 [-0,04; 0,04] | empate estatístico |
| 1 | omega_1 | A ≈ C > B | 0,79 | 0,78 | não atinge | -0,01 [-0,04; 0,04] | empate estatístico |

Variante base em detalhe:

| Cenário | λ\* det. | λ\*₅₀ | λ\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |
|---|---|---|---|---|---|---|
| A. Ortodoxo | 0,26 | 0,42 | 0,79 | 87% | 0% | [0,26 – 1,00] |
| B. Lara Resende puro | 0,70 | não atinge | não atinge | 4% | 87% | [0,70 – 0,70] |
| C. Lara Resende condicionado | 0,17 | 0,46 | 0,82 | 88% | 0% | [0,17 – 1,00] |

### P3 · Fechamento fiscal (FTPL)

Base: **A > C > B** — Δλ\*₈₀ = 0,07 [0,06; 0,09], Δλ\*₅₀ = 0,05 [0,05; 0,05], C supera A em 0% das réplicas: vantagem significativa de A.
Estimada: **A > C > B** — Δλ\*₈₀ = 0,08 [0,07; 0,10]: vantagem significativa de A.

Grade de ω (mesmo destaque da base, porque ω não é calibrado pelos dados):

| ω | Variante | Ordem | λ\*₈₀ A | λ\*₈₀ C | λ\*₈₀ B | Δλ\*₈₀ (C − A) [IC 95%] | Leitura |
|---|---|---|---|---|---|---|---|
| 0 | base | A > C > B | 0,68 | 0,75 | não atinge | 0,07 [0,06; 0,09] | vantagem significativa de A |
| 0,38 (1 − b) | omega_038 | A > C > B | 0,68 | 0,75 | não atinge | 0,07 [0,05; 0,08] | vantagem significativa de A |
| 0,5 | omega_05 | A > C > B | 0,68 | 0,74 | não atinge | 0,06 [0,05; 0,08] | vantagem significativa de A |
| 1 | omega_1 | A > C > B | 0,69 | 0,73 | não atinge | 0,04 [0,03; 0,06] | vantagem significativa de A |

θ (fração da lacuna absorvida por inflação): base θ = 0,5; θ = 0,25, o melhor ajuste da validação 2016–2019; e θ = 0, o melhor ajuste de 2020–2022, em que P3 vira uma Phillips achatada sem inércia e serve de limite inferior para o canal fiscal. As três linhas cobrem o intervalo sustentado pelos dados.

| θ | Variante | Ordem | λ\*₈₀ A | λ\*₈₀ C | λ\*₈₀ B | Δλ\*₈₀ (C − A) [IC 95%] | Leitura |
|---|---|---|---|---|---|---|---|
| 0,5 | base | A > C > B | 0,68 | 0,75 | não atinge | 0,07 [0,06; 0,09] | vantagem significativa de A |
| 0,25 | theta_025 | A > C > B | 0,53 | 0,69 | não atinge | 0,16 [0,14; 0,17] | vantagem significativa de A |
| 0 | theta_0 | C > A > B | 0,49 | 0,45 | não atinge | -0,04 [-0,05; -0,02] | vantagem significativa de C |

Variante base em detalhe:

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

## 4. Ordenamento por juro real longo neutro (r_long_neutro = 4,5; 5,5; 6,5)

Ordem e λ\*₈₀ (λ\*₅₀ entre parênteses) de cada cenário em cada valor da grade; "A ≈ C" quando o IC de 95% de Δλ\*₈₀ do bootstrap pareado contém zero.

| Especificação | r_long neutro | Ordem | λ\*₈₀ A | λ\*₈₀ B | λ\*₈₀ C |
|---|---|---|---|---|---|
| P1 | 4,5 | A ≈ C > B | 0,76 (0,33) | não atinge (não atinge) | 0,79 (0,45) |
| P1 | 5,5 | A ≈ C > B | 0,84 (0,42) | não atinge (não atinge) | 0,85 (0,50) |
| P1 | 6,5 | A ≈ C > B | 0,99 (0,52) | não atinge (não atinge) | 0,97 (0,57) |
| P2 | 4,5 | A ≈ C > B | 0,71 (0,36) | não atinge (não atinge) | 0,73 (0,41) |
| P2 | 5,5 | A ≈ C > B | 0,79 (0,42) | não atinge (não atinge) | 0,82 (0,46) |
| P2 | 6,5 | A ≈ C > B | 0,93 (0,51) | não atinge (não atinge) | 0,94 (0,54) |
| P3 | 4,5 | A > C > B | 0,64 (0,58) | não atinge (não atinge) | 0,66 (0,60) |
| P3 | 5,5 | A > C > B | 0,68 (0,62) | não atinge (não atinge) | 0,75 (0,67) |
| P3 | 6,5 | A > C > B | 0,72 (0,66) | não atinge (não atinge) | 0,83 (0,73) |

**O juro neutro muda os níveis de λ\* (todos sobem com r_long_neutro), mas não o ordenamento:** em nenhuma especificação C passa à frente de A ao longo da grade.

## 5. Robustez do ordenamento por variante

Nas três especificações (variante base): P1: A ≈ C > B; P2: A ≈ C > B; P3: A > C > B. **Nenhuma especificação inverte o ordenamento: A e C empatam em P1, P2 e A fica significativamente à frente em P3; B é o último em todas.**

Gráfico `12_ordenamento_variantes`. Ordem por variante (1º → 3º):

| Variante | Descrição | P1 | P2 | P3 |
|---|---|---|---|---|
| base (obrigatória) | r_long_neutro = 5,5; ω = 0 | A ≈ C > B | A ≈ C > B | A > C > B |
| rlong_45 (obrigatória) | r_long_neutro = 4,5 | A ≈ C > B | A ≈ C > B | A > C > B |
| rlong_65 (obrigatória) | r_long_neutro = 6,5 | A ≈ C > B | A ≈ C > B | A > C > B |
| neutro_45 (obrigatória) | r_neutro = 4,5 e r_long_neutro = 5,0 (mesmo tp_lp) | A > C > B | A > C > B | A > C > B |
| omega_05 (obrigatória) | ω = 0,5 | A ≈ C > B | A ≈ C > B | A > C > B |
| omega_1 (obrigatória) | ω = 1 (todo o prêmio pela Taylor) | A > C > B | A ≈ C > B | A > C > B |
| inercia_alta (obrigatória) | b1 = 0,82 (estimado) | A ≈ C > B | A ≈ C > B | — |
| repasse_est (obrigatória) | b3 = 0,012 (estimado) | A ≈ C > B | A ≈ C > B | A > C > B |
| C_lento (obrigatória) | C com corte em 12 trimestres | A > C > B | A > C > B | A > C > B |
| C_sem_tolerancia (obrigatória) | C com δ0 = 0 | A ≈ C > B | A > C > B | A > C > B |
| C_sem_piso | C com a trajetória como teto (Taylor − δ ≤ i ≤ Taylor); sem piso de 7,5% após T_corte + T_δ | C > A > B | C > A > B | C > A > B |
| A_reservas | A com a mesma venda de US$ 100 bi em reservas | A > C > B | A > C > B | A > C > B |
| C_piso_corte | C com piso de 7,5% só durante o corte (sem piso após T_corte + T_δ) | C > A > B | C > A > B | C > A > B |
| C_sem_piso_inercia | C_sem_piso com b1 = 0,82 (comparado com A sob a mesma inércia) | A ≈ C > B | A ≈ C > B | — |
| phi_025 (obrigatória) | P3 com φ = 0,25 | — | — | B > A ≈ C † |
| phi_05 (obrigatória) | P3 com φ = 0,5 | — | — | A > B > C † |
| theta_025 (obrigatória) | P3 com θ = 0,25 (validação 2016–2019) | — | — | A > C > B |
| theta_0 (obrigatória) | P3 com θ = 0 (validação 2020–2022: Phillips achatada sem inércia) | — | — | C > A > B |
| pe_fiscal_0 | P3 sem inflação fiscal nas expectativas | — | — | A > C > B |
| pe_fiscal_05 | P3 com peso 0,5 da inflação fiscal nas expectativas | — | — | A > C > B |
| rolagem_0 | r_min_rolagem = 0 | A ≈ C > B | A ≈ C > B | A > C > B |
| rolagem_2 | r_min_rolagem = 2,0 | A ≈ C > B | A ≈ C > B | A > C > B |
| p2_zero | P3 com p2 = 0 | — | — | A > C > B |
| p2_integral | P3 com p2 integral (0,3) | — | — | A > C > B |
| vt_perpetuidade | P3 com valor terminal 100·s/(r−g) | — | — | C > A > B |
| along_20 | alongamento: LFT + compromissadas ≤ 40% em 20 trimestres, 70% para NTN-B | A ≈ C > B | A ≈ C > B | A > C > B |
| estimada | b3 estimado; ω = 0 (ω não identificado) | A ≈ C > B | A ≈ C > B | A > C > B |
| estimada_b3_baixo | b3 no limite inferior do IC | A ≈ C > B | A ≈ C > B | A > C > B |
| estimada_b3_alto | b3 no limite superior do IC | A ≈ C > B † | A ≈ C > B | A ≈ C > B |
| omega_038 (obrigatória) | ω = 0,38 = 1 − b (verificação cruzada pelo juro longo) | A ≈ C > B | A ≈ C > B | A > C > B |
| C_sem_piso_b3_alto | C_sem_piso com b3 no limite superior do IC (comparado com A sob o mesmo b3) | A ≈ C > B | A ≈ C > B | A ≈ C > B |

† Nenhum cenário atinge P(sucesso) ≥ 50% nesta variante: a ordem vem só do desempate pela probabilidade máxima e compara graus de fracasso, não robustez relativa. "A ≈ C": IC de 95% de Δλ\*₈₀ contém zero (empate estatístico na diagonal); ⚠: mais de 20% das réplicas censuradas (λ\* não atingido), resultado pouco confiável. Variantes de alongamento com φ > 0 na seção 8.

Bootstrap pareado por variante (gráfico `13_bootstrap_delta`): Δλ\*₈₀ = λ\*₈₀(C) − λ\*₈₀(A); negativo = C exige menos adesão.

| Especificação | Variante | λ\*₈₀ A | λ\*₈₀ C | Δλ\*₈₀ [IC 95%] | C supera A | Censura A / C | Leitura |
|---|---|---|---|---|---|---|---|
| P1 | base | 0,84 | 0,85 | 0,01 [-0,05; 0,05] | 33% | 0% / 0% | empate estatístico |
| P1 | rlong_45 | 0,76 | 0,79 | 0,03 [-0,01; 0,06] | 7% | 0% / 0% | empate estatístico |
| P1 | rlong_65 | 0,99 | 0,97 | -0,02 [-0,04; 0,02] ⚠ | 60% | 37% / 13% | empate estatístico |
| P1 | neutro_45 | 0,73 | 0,79 | 0,06 [0,02; 0,10] | 0% | 0% / 0% | vantagem significativa de A |
| P1 | omega_05 | 0,81 | 0,82 | 0,01 [-0,04; 0,05] | 26% | 0% / 0% | empate estatístico |
| P1 | omega_1 | 0,82 | 0,87 | 0,05 [0,01; 0,07] | 0% | 0% / 0% | vantagem significativa de A |
| P1 | inercia_alta | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P1 | repasse_est | 0,62 | 0,60 | -0,02 [-0,05; 0,03] | 67% | 0% / 0% | empate estatístico |
| P1 | C_lento | 0,84 | 0,92 | 0,08 [0,02; 0,12] | 0% | 0% / 0% | vantagem significativa de A |
| P1 | C_sem_tolerancia | 0,84 | 0,87 | 0,03 [-0,03; 0,07] | 18% | 0% / 0% | empate estatístico |
| P1 | C_sem_piso | 0,84 | 0,76 | -0,08 [-0,13; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | C_piso_corte | 0,84 | 0,73 | -0,11 [-0,16; -0,09] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | C_sem_piso_inercia | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P1 | rolagem_0 | 0,84 | 0,85 | 0,01 [-0,05; 0,05] | 33% | 0% / 0% | empate estatístico |
| P1 | rolagem_2 | 0,84 | 0,85 | 0,01 [-0,06; 0,05] | 33% | 0% / 0% | empate estatístico |
| P1 | along_20 | 0,83 | 0,82 | -0,01 [-0,06; 0,02] | 73% | 0% / 0% | empate estatístico |
| P1 | C_sem_piso_choque2 | 0,79 | 0,74 | -0,05 [-0,11; -0,03] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | C_sem_piso_choque3 | 0,75 | 0,69 | -0,06 [-0,12; -0,01] | 99% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_c3_05 | 0,84 | 0,76 | -0,08 [-0,13; -0,03] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_c3_1 | 0,84 | 0,76 | -0,08 [-0,13; -0,03] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_c3_4 | 0,84 | 0,75 | -0,09 [-0,13; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_rmin_200 | 0,84 | 0,76 | -0,08 [-0,13; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_rmin_300 | 0,84 | 0,77 | -0,07 [-0,11; -0,02] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_rend_2 | 0,84 | 0,76 | -0,08 [-0,13; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | sens_C_sem_piso_rend_6 | 0,84 | 0,76 | -0,08 [-0,13; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P1 | estimada | 0,71 | 0,72 | 0,01 [-0,03; 0,05] | 23% | 0% / 0% | empate estatístico |
| P1 | estimada_b3_baixo | 0,66 | 0,64 | -0,02 [-0,04; 0,02] | 76% | 0% / 0% | empate estatístico |
| P1 | estimada_b3_alto | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P1 | omega_038 | 0,81 | 0,83 | 0,02 [-0,04; 0,06] | 24% | 0% / 0% | empate estatístico |
| P1 | C_sem_piso_b3_alto | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P2 | base | 0,79 | 0,82 | 0,03 [-0,01; 0,07] | 8% | 0% / 0% | empate estatístico |
| P2 | rlong_45 | 0,71 | 0,73 | 0,02 [0,00; 0,07] | 1% | 0% / 0% | empate estatístico |
| P2 | rlong_65 | 0,93 | 0,94 | 0,01 [-0,05; 0,05] | 39% | 4% / 0% | empate estatístico |
| P2 | neutro_45 | 0,67 | 0,75 | 0,08 [0,05; 0,12] | 0% | 0% / 0% | vantagem significativa de A |
| P2 | omega_05 | 0,78 | 0,78 | 0,00 [-0,04; 0,04] | 47% | 0% / 0% | empate estatístico |
| P2 | omega_1 | 0,79 | 0,78 | -0,01 [-0,04; 0,04] | 45% | 0% / 0% | empate estatístico |
| P2 | inercia_alta | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P2 | repasse_est | 0,56 | 0,55 | -0,01 [-0,04; 0,01] | 71% | 0% / 0% | empate estatístico |
| P2 | C_lento | 0,79 | 0,87 | 0,08 [0,05; 0,14] | 0% | 0% / 0% | vantagem significativa de A |
| P2 | C_sem_tolerancia | 0,79 | 0,84 | 0,05 [0,01; 0,09] | 0% | 0% / 0% | vantagem significativa de A |
| P2 | C_sem_piso | 0,79 | 0,71 | -0,08 [-0,12; -0,05] | 100% | 0% / 0% | vantagem significativa de C |
| P2 | C_piso_corte | 0,79 | 0,71 | -0,08 [-0,11; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P2 | C_sem_piso_inercia | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P2 | rolagem_0 | 0,79 | 0,82 | 0,03 [-0,01; 0,07] | 8% | 0% / 0% | empate estatístico |
| P2 | rolagem_2 | 0,79 | 0,82 | 0,03 [-0,01; 0,07] | 8% | 0% / 0% | empate estatístico |
| P2 | along_20 | 0,78 | 0,77 | -0,01 [-0,06; 0,03] | 50% | 0% / 0% | empate estatístico |
| P2 | C_sem_piso_choque2 | 0,78 | 0,70 | -0,08 [-0,11; -0,03] | 100% | 0% / 0% | vantagem significativa de C |
| P2 | C_sem_piso_choque3 | 0,77 | 0,70 | -0,07 [-0,11; -0,04] | 100% | 0% / 0% | vantagem significativa de C |
| P2 | estimada | 0,70 | 0,70 | 0,00 [-0,03; 0,05] | 18% | 0% / 0% | empate estatístico |
| P2 | estimada_b3_baixo | 0,56 | 0,56 | 0,00 [-0,03; 0,02] | 51% | 0% / 0% | empate estatístico |
| P2 | estimada_b3_alto | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P2 | omega_038 | 0,79 | 0,78 | -0,01 [-0,04; 0,05] | 37% | 0% / 0% | empate estatístico |
| P2 | C_sem_piso_b3_alto | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | base | 0,68 | 0,75 | 0,07 [0,06; 0,09] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | rlong_45 | 0,64 | 0,66 | 0,02 [0,01; 0,04] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | rlong_65 | 0,72 | 0,83 | 0,11 [0,10; 0,13] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | neutro_45 | 0,62 | 0,65 | 0,03 [0,02; 0,04] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | omega_05 | 0,68 | 0,74 | 0,06 [0,05; 0,08] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | omega_1 | 0,69 | 0,73 | 0,04 [0,03; 0,06] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | repasse_est | 0,68 | 0,74 | 0,06 [0,05; 0,08] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | C_lento | 0,68 | 0,78 | 0,10 [0,09; 0,12] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | C_sem_tolerancia | 0,68 | 0,77 | 0,09 [0,08; 0,11] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | C_sem_piso | 0,68 | 0,60 | -0,08 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | C_piso_corte | 0,68 | 0,59 | -0,09 [-0,10; -0,08] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | phi_025 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | phi_05 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | theta_025 | 0,53 | 0,69 | 0,16 [0,14; 0,17] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | theta_0 | 0,49 | 0,45 | -0,04 [-0,05; -0,02] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | pe_fiscal_0 | 0,61 | 0,74 | 0,13 [0,11; 0,14] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | pe_fiscal_05 | 0,65 | 0,75 | 0,10 [0,08; 0,11] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | rolagem_0 | 0,69 | 0,75 | 0,06 [0,05; 0,08] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | rolagem_2 | 0,64 | 0,75 | 0,11 [0,09; 0,12] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | p2_zero | 0,69 | 0,78 | 0,09 [0,08; 0,10] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | p2_integral | 0,66 | 0,71 | 0,05 [0,04; 0,07] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | vt_perpetuidade | 0,90 | 0,82 | -0,08 [-0,09; -0,06] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | along_20 | 0,65 | 0,73 | 0,08 [0,07; 0,10] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | phi_025_along_20 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | phi_05_along_20 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | phi_025_along_12 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | phi_025_along_28 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | phi_025_along_pre | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | phi_025_along_50 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | C_sem_piso_choque2 | 0,67 | 0,60 | -0,07 [-0,08; -0,06] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | C_sem_piso_choque3 | 0,67 | 0,60 | -0,07 [-0,08; -0,06] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_c3_05 | 0,68 | 0,60 | -0,08 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_c3_1 | 0,68 | 0,60 | -0,08 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_c3_4 | 0,68 | 0,60 | -0,08 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_rmin_200 | 0,68 | 0,60 | -0,08 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_rmin_300 | 0,68 | 0,61 | -0,07 [-0,07; -0,05] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_rend_2 | 0,66 | 0,59 | -0,07 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | sens_C_sem_piso_rend_6 | 0,69 | 0,61 | -0,08 [-0,09; -0,07] | 100% | 0% / 0% | vantagem significativa de C |
| P3 | estimada | 0,68 | 0,76 | 0,08 [0,07; 0,10] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | estimada_b3_baixo | 0,68 | 0,74 | 0,06 [0,05; 0,08] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | estimada_b3_alto | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | 0% | 100% / 100% | empate estatístico |
| P3 | omega_038 | 0,68 | 0,75 | 0,07 [0,05; 0,08] | 0% | 0% / 0% | vantagem significativa de A |
| P3 | C_sem_piso_b3_alto | não atinge | 0,69 | -0,32 [-0,38; 0,00] ⚠ | 71% | 100% / 29% | empate estatístico |

Variantes obrigatórias que alteram o ordenamento da base (excluídas as marcadas com †): neutro_45 em P1 (A > C > B); omega_1 em P1 (A > C > B); C_lento em P1 (A > C > B); neutro_45 em P2 (A > C > B); C_lento em P2 (A > C > B); C_sem_tolerancia em P2 (A > C > B); theta_0 em P3 (C > A > B).

Teto de inflação em meta + 2,0 p.p. (variante base): P1: A > C > B; P2: A > C > B; P3: A > C > B (o ordenamento muda com o teto).
Com o teto mais folgado, A vence em todas as especificações: o critério de inflação deixa de restringir, o de dívida passa a dominar, e C perde nele (dívida ainda subindo no fim, média da grade de λ: P1: A 25%, C 38%; P2: A 24%, C 32%; P3: A 50%, C 48%). Ver o diagnóstico de C abaixo.

### Diagnóstico: dívida de C no fim do horizonte (P1 base, λ = 0,9)

Medianas de 1000 trajetórias nos últimos 12 trimestres (gráfico `18_diagnostico_C`). δ de C chega a zero no trimestre 14; depois disso, i_C = max(7,5; Taylor).

| Trimestre | Selic A | Taylor A | Dívida A | Selic C | Taylor C | Dívida C | C no piso de 7,5% acima da Taylor |
|---|---|---|---|---|---|---|---|
| 29 | 8,62 | 8,62 | 83,4 | 8,63 | 8,63 | 78,7 | 26% |
| 30 | 8,63 | 8,63 | 83,1 | 8,65 | 8,65 | 78,3 | 26% |
| 31 | 8,56 | 8,56 | 82,8 | 8,60 | 8,60 | 78,1 | 26% |
| 32 | 8,48 | 8,48 | 82,6 | 8,53 | 8,53 | 77,7 | 28% |
| 33 | 8,46 | 8,46 | 82,1 | 8,51 | 8,51 | 77,4 | 30% |
| 34 | 8,41 | 8,41 | 81,8 | 8,47 | 8,47 | 76,9 | 33% |
| 35 | 8,31 | 8,31 | 81,4 | 8,38 | 8,38 | 76,6 | 32% |
| 36 | 8,21 | 8,21 | 81,1 | 8,31 | 8,31 | 76,3 | 33% |
| 37 | 8,19 | 8,19 | 80,7 | 8,27 | 8,27 | 75,8 | 34% |
| 38 | 8,23 | 8,23 | 80,4 | 8,32 | 8,32 | 75,4 | 36% |
| 39 | 8,07 | 8,07 | 80,0 | 8,20 | 8,20 | 75,1 | 36% |
| 40 | 8,03 | 8,03 | 79,6 | 8,18 | 8,18 | 74,7 | 36% |

Dívida ainda subindo nos últimos 8 trimestres: A 8%, C 6%. Entre as trajetórias de C com dívida subindo, a Selic média dos últimos 8 trimestres é 8,62% contra 8,71% nas demais; a Taylor, 7,67% contra 8,30%; o piso de 7,5% fica acima da Taylor em 45% dos trimestres finais das trajetórias que sobem.

**Há aperto tardio em nível em C:** depois que δ zera, o piso de 7,5% fica acima da Taylor em 34% dos trimestres finais, e a Selic média de C nos últimos 8 trimestres é 8,71% contra 8,20% em A. Em λ = 0,9, porém, ele não explica a dívida ainda subindo: só 6% das trajetórias de C sobem no fim, contra 8% de A.

Fração das trajetórias com dívida ainda subindo no fim, por λ (P1 base, N = 1.000):

| λ | 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | 0,7 | 0,8 | 0,9 | média da grade |
|---|---|---|---|---|---|---|---|---|---|
| A | 39% | 34% | 27% | 20% | 16% | 12% | 10% | 8% | 25% |
| C | 70% | 57% | 44% | 32% | 22% | 15% | 9% | 6% | 38% |
Os 38% de C (contra 25% de A) são a média sobre toda a grade de λ; a diferença se concentra nos λ em que a coluna de C excede a de A, e não no fim do horizonte com adesão alta.

### Testes do C_sem_piso

Δλ\*₈₀ = λ\*₈₀(alternativa) − λ\*₈₀(referência), bootstrap pareado com os mesmos choques; negativo = a alternativa exige menos adesão.

| Teste | Especificação | Referência | Alternativa | λ\*₈₀ ref. | λ\*₈₀ alt. | Δλ\*₈₀ [IC 95%] | Δλ\*₅₀ [IC 95%] | Leitura (80%) |
|---|---|---|---|---|---|---|---|---|
| 1. A_reservas × C_sem_piso | P1 | A_reservas/A | C_sem_piso/C | 0,79 | 0,76 | -0,03 [-0,05; 0,00] | 0,01 [-0,01; 0,02] | empate estatístico |
| 1. Valor das reservas em A (A × A_reservas) | P1 | base/A | A_reservas/A | 0,84 | 0,79 | -0,05 [-0,10; -0,02] | -0,13 [-0,14; -0,10] | alternativa exige menos adesão |
| 1. A_reservas × C base | P1 | A_reservas/A | base/C | 0,79 | 0,85 | 0,06 [0,03; 0,10] | 0,21 [0,18; 0,24] | referência exige menos adesão |
| 2. Piso no fim (C base × C_piso_corte) | P1 | base/C | C_piso_corte/C | 0,85 | 0,73 | -0,12 [-0,16; -0,10] | -0,21 [-0,24; -0,19] | alternativa exige menos adesão |
| 2. Teto no corte (C_piso_corte × C_sem_piso) | P1 | C_piso_corte/C | C_sem_piso/C | 0,73 | 0,76 | 0,03 [0,01; 0,07] | 0,01 [-0,01; 0,02] | referência exige menos adesão |
| 2. A × C_piso_corte | P1 | base/A | C_piso_corte/C | 0,84 | 0,73 | -0,11 [-0,16; -0,09] | -0,13 [-0,14; -0,11] | alternativa exige menos adesão |
| 4. Estresse b1 = 0,82: A × C_sem_piso | P1 | inercia_alta/A | C_sem_piso_inercia/C | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | -0,23 [-0,27; -0,20] | empate estatístico |
| 4. Estresse b3 alto: A × C_sem_piso | P1 | estimada_b3_alto/A | C_sem_piso_b3_alto/C | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | -0,24 [-0,31; -0,10] | empate estatístico |
| 1. A_reservas × C_sem_piso | P2 | A_reservas/A | C_sem_piso/C | 0,72 | 0,71 | -0,01 [-0,03; 0,00] | 0,03 [0,02; 0,04] | empate estatístico |
| 1. Valor das reservas em A (A × A_reservas) | P2 | base/A | A_reservas/A | 0,79 | 0,72 | -0,07 [-0,10; -0,03] | -0,14 [-0,16; -0,13] | alternativa exige menos adesão |
| 1. A_reservas × C base | P2 | A_reservas/A | base/C | 0,72 | 0,82 | 0,10 [0,06; 0,13] | 0,18 [0,16; 0,21] | referência exige menos adesão |
| 2. Piso no fim (C base × C_piso_corte) | P2 | base/C | C_piso_corte/C | 0,82 | 0,71 | -0,11 [-0,14; -0,06] | -0,15 [-0,17; -0,13] | alternativa exige menos adesão |
| 2. Teto no corte (C_piso_corte × C_sem_piso) | P2 | C_piso_corte/C | C_sem_piso/C | 0,71 | 0,71 | 0,00 [-0,02; 0,00] | 0,00 [-0,01; 0,00] | empate estatístico |
| 2. A × C_piso_corte | P2 | base/A | C_piso_corte/C | 0,79 | 0,71 | -0,08 [-0,11; -0,04] | -0,11 [-0,12; -0,10] | alternativa exige menos adesão |
| 4. Estresse b1 = 0,82: A × C_sem_piso | P2 | inercia_alta/A | C_sem_piso_inercia/C | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | -0,18 [-0,20; -0,16] | empate estatístico |
| 4. Estresse b3 alto: A × C_sem_piso | P2 | estimada_b3_alto/A | C_sem_piso_b3_alto/C | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | -0,27 [-0,33; -0,16] | empate estatístico |
| 1. A_reservas × C_sem_piso | P3 | A_reservas/A | C_sem_piso/C | 0,61 | 0,60 | -0,01 [-0,01; 0,00] | -0,02 [-0,02; -0,01] | empate estatístico |
| 1. Valor das reservas em A (A × A_reservas) | P3 | base/A | A_reservas/A | 0,68 | 0,61 | -0,07 [-0,08; -0,06] | -0,08 [-0,09; -0,08] | alternativa exige menos adesão |
| 1. A_reservas × C base | P3 | A_reservas/A | base/C | 0,61 | 0,75 | 0,14 [0,14; 0,15] | 0,13 [0,13; 0,14] | referência exige menos adesão |
| 2. Piso no fim (C base × C_piso_corte) | P3 | base/C | C_piso_corte/C | 0,75 | 0,59 | -0,16 [-0,17; -0,15] | -0,14 [-0,15; -0,14] | alternativa exige menos adesão |
| 2. Teto no corte (C_piso_corte × C_sem_piso) | P3 | C_piso_corte/C | C_sem_piso/C | 0,59 | 0,60 | 0,01 [0,00; 0,02] | -0,01 [-0,01; 0,00] | empate estatístico |
| 2. A × C_piso_corte | P3 | base/A | C_piso_corte/C | 0,68 | 0,59 | -0,09 [-0,10; -0,08] | -0,09 [-0,10; -0,09] | alternativa exige menos adesão |
| 4. Estresse b3 alto: A × C_sem_piso | P3 | estimada_b3_alto/A | C_sem_piso_b3_alto/C | não atinge | 0,69 | -0,32 [-0,38; 0,00] ⚠ | -0,16 [-0,17; -0,15] | empate estatístico |

Os mesmos testes com o critério de banda simétrica (1,5%–4,5%):

| Teste | Especificação | λ\*₈₀ ref. | λ\*₈₀ alt. | Δλ\*₈₀ [IC 95%] | Leitura (80%) |
|---|---|---|---|---|---|
| 1. A_reservas × C_sem_piso | P1 | não atinge | 0,98 | -0,03 [-0,06; 0,00] ⚠ | empate estatístico |
| 1. Valor das reservas em A (A × A_reservas) | P1 | não atinge | não atinge | 0,00 [-0,06; 0,00] ⚠ | empate estatístico |
| 1. A_reservas × C base | P1 | não atinge | não atinge | 0,00 [-0,01; 0,03] ⚠ | empate estatístico |
| 2. Piso no fim (C base × C_piso_corte) | P1 | não atinge | 0,99 | -0,02 [-0,05; 0,00] ⚠ | empate estatístico |
| 2. Teto no corte (C_piso_corte × C_sem_piso) | P1 | 0,99 | 0,98 | -0,01 [-0,04; 0,02] ⚠ | empate estatístico |
| 2. A × C_piso_corte | P1 | não atinge | 0,99 | -0,02 [-0,07; 0,00] ⚠ | empate estatístico |
| 4. Estresse b1 = 0,82: A × C_sem_piso | P1 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | empate estatístico |
| 4. Estresse b3 alto: A × C_sem_piso | P1 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | empate estatístico |
| 1. A_reservas × C_sem_piso | P2 | 1,00 | 0,99 | -0,01 [-0,02; 0,00] ⚠ | empate estatístico |
| 1. Valor das reservas em A (A × A_reservas) | P2 | não atinge | 1,00 | -0,01 [-0,05; 0,00] ⚠ | empate estatístico |
| 1. A_reservas × C base | P2 | 1,00 | não atinge | 0,01 [0,00; 0,03] ⚠ | empate estatístico |
| 2. Piso no fim (C base × C_piso_corte) | P2 | não atinge | 0,99 | -0,02 [-0,04; 0,00] ⚠ | empate estatístico |
| 2. Teto no corte (C_piso_corte × C_sem_piso) | P2 | 0,99 | 0,99 | 0,00 [-0,01; 0,00] ⚠ | empate estatístico |
| 2. A × C_piso_corte | P2 | não atinge | 0,99 | -0,02 [-0,06; 0,00] ⚠ | empate estatístico |
| 4. Estresse b1 = 0,82: A × C_sem_piso | P2 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | empate estatístico |
| 4. Estresse b3 alto: A × C_sem_piso | P2 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | empate estatístico |
| 1. A_reservas × C_sem_piso | P3 | 0,90 | 0,90 | 0,00 [0,00; 0,01] | empate estatístico |
| 1. Valor das reservas em A (A × A_reservas) | P3 | 0,92 | 0,90 | -0,02 [-0,03; -0,01] | alternativa exige menos adesão |
| 1. A_reservas × C base | P3 | 0,90 | 0,87 | -0,03 [-0,05; -0,03] | alternativa exige menos adesão |
| 2. Piso no fim (C base × C_piso_corte) | P3 | 0,87 | 0,90 | 0,03 [0,03; 0,05] | referência exige menos adesão |
| 2. Teto no corte (C_piso_corte × C_sem_piso) | P3 | 0,90 | 0,90 | 0,00 [0,00; 0,01] | empate estatístico |
| 2. A × C_piso_corte | P3 | 0,92 | 0,90 | -0,02 [-0,03; -0,01] | alternativa exige menos adesão |
| 4. Estresse b3 alto: A × C_sem_piso | P3 | não atinge | não atinge | 0,00 [0,00; 0,00] ⚠ | empate estatístico |

**Teste 1 (reservas):** A_reservas empata com C_sem_piso em todas as especificações: a vantagem vem das reservas, que podem ser acrescentadas ao caminho ortodoxo.

**Teste 2 (decomposição):** de C base para C_sem_piso, a parte atribuída a tirar o piso no fim é P1: -0,12; P2: -0,11; P3: -0,16 e a parte atribuída a trocar o piso pelo teto durante o corte é P1: 0,03; P2: 0,00; P3: 0,01 (Δλ\*₈₀).

**Teste 3 (superfície λ_π × λ_fiscal):** ΔÁrea = Área(referência) − Área(alternativa).

| Comparação | Especificação | Área ref. | Área alt. | ΔÁrea [IC 95%] | Leitura |
|---|---|---|---|---|---|
| 3. A base × C_sem_piso (teto) | P1 | 12% | 20% | -8,4 p.p. [-16,1; -1,8] | alternativa mais robusta |
| 3. A_reservas × C_sem_piso (teto) | P1 | 19% | 20% | -0,7 p.p. [-6,3; 2,0] | empate estatístico |
| 3. A base × A_reservas (teto) | P1 | 12% | 19% | -7,7 p.p. [-12,0; -2,7] | alternativa mais robusta |
| 3. A base × C_sem_piso (teto) | P2 | 17% | 27% | -10,2 p.p. [-15,9; -3,2] | alternativa mais robusta |
| 3. A_reservas × C_sem_piso (teto) | P2 | 25% | 27% | -2,0 p.p. [-4,3; 0,2] | empate estatístico |
| 3. A base × A_reservas (teto) | P2 | 17% | 25% | -8,2 p.p. [-13,6; -2,5] | alternativa mais robusta |
| 3. A base × C_sem_piso (teto) | P3 | 20% | 32% | -12,0 p.p. [-13,6; -10,7] | alternativa mais robusta |
| 3. A_reservas × C_sem_piso (teto) | P3 | 32% | 32% | -0,9 p.p. [-2,0; -0,5] | alternativa mais robusta |
| 3. A base × A_reservas (teto) | P3 | 20% | 32% | -11,1 p.p. [-12,2; -9,5] | alternativa mais robusta |
| 3. A base × C_sem_piso (banda) | P1 | 0% | 0% | 0,0 p.p. [-2,0; 0,0] | empate estatístico |
| 3. A_reservas × C_sem_piso (banda) | P1 | 0% | 0% | 0,0 p.p. [-1,6; 0,0] | empate estatístico |
| 3. A base × A_reservas (banda) | P1 | 0% | 0% | 0,0 p.p. [-1,1; 0,0] | empate estatístico |
| 3. A base × C_sem_piso (banda) | P2 | 0% | 0% | 0,0 p.p. [-2,0; 0,0] | empate estatístico |
| 3. A_reservas × C_sem_piso (banda) | P2 | 0% | 0% | 0,0 p.p. [-0,5; 0,0] | empate estatístico |
| 3. A base × A_reservas (banda) | P2 | 0% | 0% | 0,0 p.p. [-1,1; 0,0] | empate estatístico |
| 3. A base × C_sem_piso (banda) | P3 | 2% | 4% | -1,1 p.p. [-1,6; -0,7] | alternativa mais robusta |
| 3. A_reservas × C_sem_piso (banda) | P3 | 4% | 4% | 0,0 p.p. [0,0; 0,5] | empate estatístico |
| 3. A base × A_reservas (banda) | P3 | 2% | 4% | -1,1 p.p. [-1,8; -0,7] | alternativa mais robusta |

**Teste 4 (grade fina de θ em P3):** Δλ\*₈₀ contra A, com os dois critérios de inflação (gráfico `theta_fino/19_theta_fino`).

| θ | C − A (teto) | C_sem_piso − A (teto) | C − A (banda) | C_sem_piso − A (banda) |
|---|---|---|---|---|
| 0,00 | -0,04 [-0,05; -0,02] | -0,10 [-0,11; -0,08] | -0,03 [-0,04; -0,01] | -0,06 [-0,07; -0,04] |
| 0,05 | 0,20 [0,18; 0,22] | -0,04 [-0,06; -0,04] | -0,01 [-0,02; 0,00] | -0,01 [-0,03; -0,01] |
| 0,10 | 0,21 [0,19; 0,23] | -0,06 [-0,07; -0,05] | -0,02 [-0,04; -0,02] | -0,01 [-0,02; -0,01] |
| 0,15 | 0,19 [0,18; 0,21] | -0,07 [-0,07; -0,05] | -0,04 [-0,05; -0,03] | -0,02 [-0,02; -0,01] |
| 0,20 | 0,17 [0,16; 0,19] | -0,07 [-0,07; -0,06] | -0,04 [-0,05; -0,03] | -0,01 [-0,02; -0,01] |
| 0,25 | 0,16 [0,14; 0,17] | -0,06 [-0,08; -0,06] | -0,04 [-0,05; -0,03] | -0,01 [-0,02; 0,00] |
| 0,50 | 0,07 [0,06; 0,09] | -0,08 [-0,09; -0,07] | -0,05 [-0,07; -0,05] | -0,02 [-0,03; -0,01] |

### Critério de dívida: bruta × líquida (A, A_reservas e C_sem_piso)

Dívida líquida: inclinação da DLSP ≤ 0 nos últimos 8 trimestres e DLSP final ≤ inicial + 5 p.p.; inflação e reservas como no critério correspondente. A venda de reservas reduz a dívida bruta (resgata compromissadas), mas não a líquida no ato da venda: a comparação separa o efeito contábil do econômico. Ordem pelo λ\* do limiar (1º = menor adesão necessária); "≈" quando o bootstrap pareado não distingue vizinhos; † quando nenhum dos três atinge o limiar.

| Especificação | Limiar | Dívida bruta, teto | Dívida bruta, banda | Dívida líquida, teto | Dívida líquida, banda |
|---|---|---|---|---|---|
| P1 | 80% | C_sem_piso ≈ A_reservas > A | C_sem_piso ≈ A_reservas ≈ A | C_sem_piso ≈ A_reservas ≈ A | C_sem_piso ≈ A_reservas ≈ A † |
| P1 | 70% | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas > A | C_sem_piso > A_reservas > A | C_sem_piso > A_reservas > A |
| P1 | 50% | A_reservas ≈ C_sem_piso > A | C_sem_piso ≈ A_reservas > A | C_sem_piso ≈ A_reservas > A | C_sem_piso > A_reservas > A |
| P2 | 80% | C_sem_piso ≈ A_reservas > A | C_sem_piso ≈ A_reservas ≈ A | C_sem_piso ≈ A_reservas ≈ A | C_sem_piso ≈ A_reservas ≈ A † |
| P2 | 70% | C_sem_piso ≈ A_reservas > A | C_sem_piso ≈ A_reservas > A | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas > A |
| P2 | 50% | A_reservas > C_sem_piso > A | C_sem_piso ≈ A_reservas > A | C_sem_piso ≈ A_reservas > A | C_sem_piso > A_reservas > A |
| P3 | 80% | C_sem_piso ≈ A_reservas > A | C_sem_piso ≈ A_reservas > A | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas > A |
| P3 | 70% | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas > A | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas > A |
| P3 | 50% | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas ≈ A | C_sem_piso > A_reservas > A | C_sem_piso ≈ A_reservas > A |

λ\*₇₀ de cada estratégia (não atinge = sem 70% de sucesso em nenhum λ):

| Especificação | Estratégia | bruta, teto | bruta, banda | líquida, teto | líquida, banda |
|---|---|---|---|---|---|
| P1 | A | 0,62 | 0,86 | não atinge | não atinge |
| P1 | A_reservas | 0,55 | 0,82 | 0,71 | 0,91 |
| P1 | C_sem_piso | 0,53 | 0,80 | 0,66 | 0,86 |
| P2 | A | 0,58 | 0,83 | 0,99 | não atinge |
| P2 | A_reservas | 0,51 | 0,80 | 0,62 | 0,87 |
| P2 | C_sem_piso | 0,51 | 0,80 | 0,59 | 0,85 |
| P3 | A | 0,65 | 0,90 | 0,65 | 0,96 |
| P3 | A_reservas | 0,57 | 0,88 | 0,61 | 0,89 |
| P3 | C_sem_piso | 0,55 | 0,88 | 0,59 | 0,89 |


### Parada súbita: custo de cauda da venda de reservas

Choque não antecipado no ano 2 (trimestre 8) ou 3 (trimestre 12): depreciação de 30% no trimestre e prêmio de risco +3 p.p., com decaimento de 20% por trimestre; o BC defende o câmbio com até US$ 50 bi de reservas, limitado pelo piso R_min. Quem vendeu US$ 100 bi antes (A_reservas, C_sem_piso) chega ao choque com cerca de US$ 26 bi acima do piso; A, com cerca de US$ 110 bi. Δλ\* = λ\*(alternativa) − λ\*(referência), bootstrap pareado; o "custo do choque" compara cada cenário com ele mesmo sem choque.

Critério de inflação: só teto (limiares 80% e 70%).

| Comparação | Especificação | Δλ\*80 [IC 95%] | Δλ\*70 [IC 95%] | Leitura (80%) |
|---|---|---|---|---|
| ano 2: custo do choque para A | P1 | -0,05 [-0,07; -0,03] | -0,04 [-0,07; -0,02] | alternativa exige menos adesão |
| ano 2: custo do choque para A_reservas | P1 | -0,03 [-0,05; -0,02] | -0,04 [-0,06; -0,03] | alternativa exige menos adesão |
| ano 2: custo do choque para C_sem_piso | P1 | -0,02 [-0,05; -0,01] | -0,05 [-0,07; -0,03] | alternativa exige menos adesão |
| ano 2: A × A_reservas sob choque | P1 | -0,03 [-0,08; -0,01] | -0,07 [-0,09; -0,05] | alternativa exige menos adesão |
| ano 2: A × C_sem_piso sob choque | P1 | -0,05 [-0,11; -0,03] | -0,10 [-0,12; -0,07] | alternativa exige menos adesão |
| ano 2: A_reservas × C_sem_piso sob choque | P1 | -0,02 [-0,05; 0,00] | -0,03 [-0,05; -0,01] | empate estatístico |
| ano 3: custo do choque para A | P1 | -0,09 [-0,11; -0,06] | -0,06 [-0,09; -0,03] | alternativa exige menos adesão |
| ano 3: custo do choque para A_reservas | P1 | -0,07 [-0,09; -0,05] | -0,09 [-0,11; -0,06] | alternativa exige menos adesão |
| ano 3: custo do choque para C_sem_piso | P1 | -0,07 [-0,10; -0,04] | -0,08 [-0,11; -0,06] | alternativa exige menos adesão |
| ano 3: A × A_reservas sob choque | P1 | -0,03 [-0,09; 0,00] | -0,10 [-0,12; -0,07] | empate estatístico |
| ano 3: A × C_sem_piso sob choque | P1 | -0,06 [-0,12; -0,01] | -0,11 [-0,13; -0,10] | alternativa exige menos adesão |
| ano 3: A_reservas × C_sem_piso sob choque | P1 | -0,03 [-0,06; 0,00] | -0,01 [-0,04; -0,01] | empate estatístico |
| ano 2: custo do choque para A | P2 | -0,01 [-0,03; 0,00] | 0,01 [-0,01; 0,01] | empate estatístico |
| ano 2: custo do choque para A_reservas | P2 | 0,00 [-0,02; 0,01] | 0,01 [-0,01; 0,04] | empate estatístico |
| ano 2: custo do choque para C_sem_piso | P2 | -0,01 [-0,02; 0,02] | 0,01 [0,00; 0,03] | empate estatístico |
| ano 2: A × A_reservas sob choque | P2 | -0,06 [-0,08; -0,02] | -0,07 [-0,09; -0,05] | alternativa exige menos adesão |
| ano 2: A × C_sem_piso sob choque | P2 | -0,08 [-0,11; -0,03] | -0,07 [-0,09; -0,06] | alternativa exige menos adesão |
| ano 2: A_reservas × C_sem_piso sob choque | P2 | -0,02 [-0,03; 0,00] | 0,00 [-0,02; 0,00] | empate estatístico |
| ano 3: custo do choque para A | P2 | -0,02 [-0,04; -0,01] | 0,01 [-0,02; 0,02] | alternativa exige menos adesão |
| ano 3: custo do choque para A_reservas | P2 | -0,01 [-0,03; 0,00] | 0,00 [-0,01; 0,02] | empate estatístico |
| ano 3: custo do choque para C_sem_piso | P2 | -0,01 [-0,03; 0,01] | 0,00 [-0,01; 0,02] | empate estatístico |
| ano 3: A × A_reservas sob choque | P2 | -0,06 [-0,09; -0,03] | -0,08 [-0,10; -0,06] | alternativa exige menos adesão |
| ano 3: A × C_sem_piso sob choque | P2 | -0,07 [-0,11; -0,04] | -0,08 [-0,10; -0,06] | alternativa exige menos adesão |
| ano 3: A_reservas × C_sem_piso sob choque | P2 | -0,01 [-0,03; 0,00] | 0,00 [-0,01; 0,00] | empate estatístico |
| ano 2: custo do choque para A | P3 | -0,01 [-0,02; 0,00] | -0,01 [-0,02; -0,01] | empate estatístico |
| ano 2: custo do choque para A_reservas | P3 | -0,01 [-0,01; 0,00] | -0,01 [-0,01; 0,00] | empate estatístico |
| ano 2: custo do choque para C_sem_piso | P3 | 0,00 [-0,01; 0,00] | 0,00 [-0,01; 0,01] | empate estatístico |
| ano 2: A × A_reservas sob choque | P3 | -0,07 [-0,07; -0,05] | -0,08 [-0,09; -0,07] | alternativa exige menos adesão |
| ano 2: A × C_sem_piso sob choque | P3 | -0,07 [-0,08; -0,06] | -0,09 [-0,10; -0,08] | alternativa exige menos adesão |
| ano 2: A_reservas × C_sem_piso sob choque | P3 | 0,00 [-0,01; 0,00] | -0,01 [-0,02; 0,00] | empate estatístico |
| ano 3: custo do choque para A | P3 | -0,01 [-0,02; 0,00] | -0,01 [-0,02; -0,01] | empate estatístico |
| ano 3: custo do choque para A_reservas | P3 | 0,00 [-0,01; 0,01] | -0,01 [-0,01; 0,00] | empate estatístico |
| ano 3: custo do choque para C_sem_piso | P3 | 0,00 [-0,01; 0,01] | 0,00 [-0,01; 0,01] | empate estatístico |
| ano 3: A × A_reservas sob choque | P3 | -0,06 [-0,07; -0,05] | -0,08 [-0,08; -0,07] | alternativa exige menos adesão |
| ano 3: A × C_sem_piso sob choque | P3 | -0,07 [-0,08; -0,06] | -0,09 [-0,09; -0,07] | alternativa exige menos adesão |
| ano 3: A_reservas × C_sem_piso sob choque | P3 | -0,01 [-0,01; 0,00] | -0,01 [-0,01; 0,00] | empate estatístico |

Custo de cauda (diferença das diferenças: custo do choque do cenário − custo do choque de A; positivo = o cenário sofre mais):

| Comparação | Especificação | 80% [IC 95%] | 70% [IC 95%] |
|---|---|---|---|
| ano 2: custo do choque, A_reservas − A | P1 | 0,02 [-0,01; 0,04] | 0,00 [-0,03; 0,02] |
| ano 2: custo do choque, C_sem_piso − A | P1 | 0,03 [-0,01; 0,04] | -0,01 [-0,03; 0,02] |
| ano 3: custo do choque, A_reservas − A | P1 | 0,02 [-0,01; 0,05] | -0,03 [-0,06; 0,00] |
| ano 3: custo do choque, C_sem_piso − A | P1 | 0,02 [-0,02; 0,05] | -0,02 [-0,05; 0,00] |
| ano 2: custo do choque, A_reservas − A | P2 | 0,01 [-0,01; 0,03] | 0,00 [-0,01; 0,04] |
| ano 2: custo do choque, C_sem_piso − A | P2 | 0,00 [-0,01; 0,03] | 0,00 [-0,01; 0,03] |
| ano 3: custo do choque, A_reservas − A | P2 | 0,01 [-0,02; 0,03] | -0,01 [-0,02; 0,03] |
| ano 3: custo do choque, C_sem_piso − A | P2 | 0,01 [-0,02; 0,03] | -0,01 [-0,02; 0,03] |
| ano 2: custo do choque, A_reservas − A | P3 | 0,00 [0,00; 0,02] | 0,00 [0,00; 0,02] |
| ano 2: custo do choque, C_sem_piso − A | P3 | 0,01 [0,00; 0,02] | 0,01 [0,00; 0,02] |
| ano 3: custo do choque, A_reservas − A | P3 | 0,01 [-0,01; 0,02] | 0,00 [0,00; 0,02] |
| ano 3: custo do choque, C_sem_piso − A | P3 | 0,01 [0,00; 0,02] | 0,01 [0,00; 0,03] |

**Não há custo de cauda significativo da venda de reservas** neste critério: A_reservas não sofre com o choque significativamente mais que A. Ressalva: no modelo, o nível de reservas só afeta o câmbio pela eficácia da intervenção (c3); não há canal de reservas para o prêmio de risco.

Critério de inflação: banda simétrica (limiares 70% e 50%).

| Comparação | Especificação | Δλ\*70 [IC 95%] | Δλ\*50 [IC 95%] | Leitura (70%) |
|---|---|---|---|---|
| ano 2: custo do choque para A | P1 | 0,00 [-0,02; 0,01] | -0,01 [-0,02; 0,01] | empate estatístico |
| ano 2: custo do choque para A_reservas | P1 | 0,00 [-0,02; 0,02] | 0,00 [-0,02; 0,01] | empate estatístico |
| ano 2: custo do choque para C_sem_piso | P1 | 0,00 [-0,02; 0,01] | 0,00 [-0,03; 0,01] | empate estatístico |
| ano 2: A × A_reservas sob choque | P1 | -0,04 [-0,06; -0,02] | -0,04 [-0,06; -0,03] | alternativa exige menos adesão |
| ano 2: A × C_sem_piso sob choque | P1 | -0,06 [-0,09; -0,04] | -0,05 [-0,08; -0,04] | alternativa exige menos adesão |
| ano 2: A_reservas × C_sem_piso sob choque | P1 | -0,02 [-0,04; 0,00] | -0,01 [-0,03; 0,00] | empate estatístico |
| ano 3: custo do choque para A | P1 | 0,00 [-0,03; 0,02] | -0,01 [-0,03; 0,02] | empate estatístico |
| ano 3: custo do choque para A_reservas | P1 | -0,01 [-0,03; 0,02] | -0,02 [-0,04; 0,01] | empate estatístico |
| ano 3: custo do choque para C_sem_piso | P1 | -0,01 [-0,03; 0,01] | -0,03 [-0,05; 0,00] | empate estatístico |
| ano 3: A × A_reservas sob choque | P1 | -0,05 [-0,07; -0,02] | -0,06 [-0,09; -0,04] | alternativa exige menos adesão |
| ano 3: A × C_sem_piso sob choque | P1 | -0,07 [-0,10; -0,04] | -0,08 [-0,10; -0,05] | alternativa exige menos adesão |
| ano 3: A_reservas × C_sem_piso sob choque | P1 | -0,02 [-0,04; -0,01] | -0,02 [-0,04; 0,00] | alternativa exige menos adesão |
| ano 2: custo do choque para A | P2 | 0,00 [-0,02; 0,01] | 0,01 [0,00; 0,02] | empate estatístico |
| ano 2: custo do choque para A_reservas | P2 | 0,00 [-0,02; 0,01] | 0,01 [0,00; 0,03] | empate estatístico |
| ano 2: custo do choque para C_sem_piso | P2 | -0,01 [-0,02; 0,01] | 0,01 [0,00; 0,02] | empate estatístico |
| ano 2: A × A_reservas sob choque | P2 | -0,03 [-0,06; -0,02] | -0,06 [-0,09; -0,04] | alternativa exige menos adesão |
| ano 2: A × C_sem_piso sob choque | P2 | -0,04 [-0,07; -0,02] | -0,07 [-0,09; -0,04] | alternativa exige menos adesão |
| ano 2: A_reservas × C_sem_piso sob choque | P2 | -0,01 [-0,02; 0,00] | -0,01 [-0,02; 0,00] | empate estatístico |
| ano 3: custo do choque para A | P2 | 0,01 [-0,02; 0,02] | 0,01 [0,00; 0,02] | empate estatístico |
| ano 3: custo do choque para A_reservas | P2 | 0,00 [-0,02; 0,01] | 0,01 [-0,01; 0,02] | empate estatístico |
| ano 3: custo do choque para C_sem_piso | P2 | -0,02 [-0,03; 0,01] | 0,01 [-0,01; 0,02] | empate estatístico |
| ano 3: A × A_reservas sob choque | P2 | -0,04 [-0,07; -0,02] | -0,06 [-0,09; -0,04] | alternativa exige menos adesão |
| ano 3: A × C_sem_piso sob choque | P2 | -0,06 [-0,08; -0,03] | -0,07 [-0,09; -0,05] | alternativa exige menos adesão |
| ano 3: A_reservas × C_sem_piso sob choque | P2 | -0,02 [-0,03; 0,00] | -0,01 [-0,01; 0,01] | empate estatístico |
| ano 2: custo do choque para A | P3 | 0,00 [-0,01; 0,00] | 0,00 [-0,01; 0,00] | empate estatístico |
| ano 2: custo do choque para A_reservas | P3 | -0,01 [-0,01; 0,00] | -0,01 [-0,01; 0,00] | empate estatístico |
| ano 2: custo do choque para C_sem_piso | P3 | 0,00 [-0,01; 0,00] | 0,00 [-0,01; 0,00] | empate estatístico |
| ano 2: A × A_reservas sob choque | P3 | -0,03 [-0,03; -0,01] | -0,02 [-0,02; -0,01] | alternativa exige menos adesão |
| ano 2: A × C_sem_piso sob choque | P3 | -0,02 [-0,02; -0,01] | -0,01 [-0,02; -0,01] | alternativa exige menos adesão |
| ano 2: A_reservas × C_sem_piso sob choque | P3 | 0,01 [0,00; 0,01] | 0,01 [0,00; 0,01] | empate estatístico |
| ano 3: custo do choque para A | P3 | 0,00 [-0,01; 0,00] | -0,01 [-0,01; 0,00] | empate estatístico |
| ano 3: custo do choque para A_reservas | P3 | 0,00 [-0,01; 0,00] | -0,01 [-0,01; 0,00] | empate estatístico |
| ano 3: custo do choque para C_sem_piso | P3 | 0,00 [-0,01; 0,00] | -0,01 [-0,01; 0,00] | empate estatístico |
| ano 3: A × A_reservas sob choque | P3 | -0,02 [-0,03; -0,01] | -0,01 [-0,02; -0,01] | alternativa exige menos adesão |
| ano 3: A × C_sem_piso sob choque | P3 | -0,02 [-0,03; -0,01] | -0,01 [-0,02; -0,01] | alternativa exige menos adesão |
| ano 3: A_reservas × C_sem_piso sob choque | P3 | 0,00 [0,00; 0,01] | 0,00 [0,00; 0,01] | empate estatístico |

Custo de cauda (diferença das diferenças: custo do choque do cenário − custo do choque de A; positivo = o cenário sofre mais):

| Comparação | Especificação | 70% [IC 95%] | 50% [IC 95%] |
|---|---|---|---|
| ano 2: custo do choque, A_reservas − A | P1 | 0,00 [-0,02; 0,03] | 0,01 [-0,02; 0,02] |
| ano 2: custo do choque, C_sem_piso − A | P1 | 0,00 [-0,02; 0,02] | 0,01 [-0,02; 0,02] |
| ano 3: custo do choque, A_reservas − A | P1 | -0,01 [-0,03; 0,03] | -0,01 [-0,04; 0,02] |
| ano 3: custo do choque, C_sem_piso − A | P1 | -0,01 [-0,03; 0,03] | -0,02 [-0,04; 0,01] |
| ano 2: custo do choque, A_reservas − A | P2 | 0,00 [-0,02; 0,02] | 0,00 [-0,01; 0,02] |
| ano 2: custo do choque, C_sem_piso − A | P2 | -0,01 [-0,02; 0,02] | 0,00 [-0,01; 0,02] |
| ano 3: custo do choque, A_reservas − A | P2 | -0,01 [-0,03; 0,02] | 0,00 [-0,02; 0,02] |
| ano 3: custo do choque, C_sem_piso − A | P2 | -0,03 [-0,03; 0,02] | 0,00 [-0,02; 0,01] |
| ano 2: custo do choque, A_reservas − A | P3 | -0,01 [-0,01; 0,01] | -0,01 [-0,01; 0,00] |
| ano 2: custo do choque, C_sem_piso − A | P3 | 0,00 [-0,01; 0,01] | 0,00 [-0,01; 0,00] |
| ano 3: custo do choque, A_reservas − A | P3 | 0,00 [-0,01; 0,01] | 0,00 [-0,01; 0,00] |
| ano 3: custo do choque, C_sem_piso − A | P3 | 0,00 [-0,01; 0,01] | 0,00 [-0,01; 0,00] |

**Não há custo de cauda significativo da venda de reservas** neste critério: A_reservas não sofre com o choque significativamente mais que A. Ressalva: no modelo, o nível de reservas só afeta o câmbio pela eficácia da intervenção (c3); não há canal de reservas para o prêmio de risco.


### Sensibilidade dos parâmetros das reservas (P1 e P3)

Padrões: c3 = 2 (efeito da intervenção sobre o câmbio), R_min = US$ 250 bi, rendimento das reservas = 4% a.a. (contra o custo das compromissadas à Selic). Δλ\* = λ\*(alternativa) − λ\*(referência), bootstrap pareado.

| Parâmetro | Comparação | Especificação | Teto 80% | Banda 70% | Banda 50% |
|---|---|---|---|---|---|
| c3 = 0,5 | A × A_reservas | P1 | -0,05 [-0,10; -0,02] | -0,04 [-0,07; -0,02] | -0,04 [-0,06; -0,03] |
| c3 = 0,5 | A × C_sem_piso | P1 | -0,08 [-0,13; -0,03] | -0,06 [-0,09; -0,03] | -0,05 [-0,08; -0,04] |
| c3 = 0,5 | A_reservas × C_sem_piso | P1 | -0,03 [-0,05; 0,01] | -0,02 [-0,04; -0,01] | -0,01 [-0,02; 0,00] |
| c3 = 1 | A × A_reservas | P1 | -0,05 [-0,10; -0,02] | -0,04 [-0,07; -0,02] | -0,05 [-0,07; -0,03] |
| c3 = 1 | A × C_sem_piso | P1 | -0,08 [-0,13; -0,03] | -0,06 [-0,09; -0,03] | -0,06 [-0,08; -0,04] |
| c3 = 1 | A_reservas × C_sem_piso | P1 | -0,03 [-0,05; 0,00] | -0,02 [-0,04; 0,00] | -0,01 [-0,03; 0,00] |
| c3 = 4 | A × A_reservas | P1 | -0,06 [-0,10; -0,02] | -0,04 [-0,07; -0,02] | -0,05 [-0,07; -0,03] |
| c3 = 4 | A × C_sem_piso | P1 | -0,09 [-0,13; -0,04] | -0,06 [-0,09; -0,04] | -0,07 [-0,09; -0,04] |
| c3 = 4 | A_reservas × C_sem_piso | P1 | -0,03 [-0,05; 0,01] | -0,02 [-0,04; 0,00] | -0,02 [-0,02; 0,00] |
| rendimento das reservas = 2% | A × A_reservas | P1 | -0,05 [-0,10; -0,02] | -0,04 [-0,07; -0,02] | -0,05 [-0,07; -0,03] |
| rendimento das reservas = 2% | A × C_sem_piso | P1 | -0,08 [-0,13; -0,04] | -0,06 [-0,09; -0,04] | -0,06 [-0,08; -0,04] |
| rendimento das reservas = 2% | A_reservas × C_sem_piso | P1 | -0,03 [-0,05; 0,00] | -0,02 [-0,04; 0,00] | -0,01 [-0,03; 0,00] |
| rendimento das reservas = 6% | A × A_reservas | P1 | -0,05 [-0,10; -0,02] | -0,04 [-0,07; -0,02] | -0,05 [-0,07; -0,03] |
| rendimento das reservas = 6% | A × C_sem_piso | P1 | -0,08 [-0,13; -0,04] | -0,06 [-0,09; -0,04] | -0,06 [-0,08; -0,04] |
| rendimento das reservas = 6% | A_reservas × C_sem_piso | P1 | -0,03 [-0,05; 0,00] | -0,02 [-0,04; 0,00] | -0,01 [-0,03; 0,00] |
| R_min = US$ 200 bi | A × A_reservas | P1 | -0,05 [-0,10; -0,02] | -0,04 [-0,07; -0,02] | -0,05 [-0,07; -0,03] |
| R_min = US$ 200 bi | A × C_sem_piso | P1 | -0,08 [-0,13; -0,04] | -0,06 [-0,09; -0,04] | -0,06 [-0,08; -0,04] |
| R_min = US$ 200 bi | A_reservas × C_sem_piso | P1 | -0,03 [-0,05; 0,00] | -0,02 [-0,04; 0,00] | -0,01 [-0,03; 0,00] |
| R_min = US$ 300 bi | A × A_reservas | P1 | -0,05 [-0,08; -0,02] | -0,03 [-0,06; -0,01] | -0,04 [-0,06; -0,02] |
| R_min = US$ 300 bi | A × C_sem_piso | P1 | -0,07 [-0,11; -0,02] | -0,05 [-0,08; -0,03] | -0,05 [-0,07; -0,03] |
| R_min = US$ 300 bi | A_reservas × C_sem_piso | P1 | -0,02 [-0,05; 0,01] | -0,02 [-0,04; -0,01] | -0,01 [-0,02; 0,00] |
| c3 = 0,5 | A × A_reservas | P3 | -0,07 [-0,08; -0,06] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| c3 = 0,5 | A × C_sem_piso | P3 | -0,08 [-0,09; -0,07] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| c3 = 0,5 | A_reservas × C_sem_piso | P3 | -0,01 [-0,01; 0,00] | 0,00 [0,00; 0,01] | 0,00 [0,00; 0,01] |
| c3 = 1 | A × A_reservas | P3 | -0,07 [-0,08; -0,06] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| c3 = 1 | A × C_sem_piso | P3 | -0,08 [-0,09; -0,07] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| c3 = 1 | A_reservas × C_sem_piso | P3 | -0,01 [-0,01; 0,00] | 0,00 [0,00; 0,01] | 0,00 [0,00; 0,01] |
| c3 = 4 | A × A_reservas | P3 | -0,08 [-0,08; -0,06] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| c3 = 4 | A × C_sem_piso | P3 | -0,08 [-0,09; -0,07] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| c3 = 4 | A_reservas × C_sem_piso | P3 | 0,00 [-0,01; 0,00] | 0,00 [-0,01; 0,00] | 0,00 [0,00; 0,01] |
| rendimento das reservas = 2% | A × A_reservas | P3 | -0,07 [-0,08; -0,06] | -0,01 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| rendimento das reservas = 2% | A × C_sem_piso | P3 | -0,07 [-0,09; -0,07] | -0,01 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| rendimento das reservas = 2% | A_reservas × C_sem_piso | P3 | 0,00 [-0,01; 0,00] | 0,00 [0,00; 0,00] | 0,00 [0,00; 0,01] |
| rendimento das reservas = 6% | A × A_reservas | P3 | -0,07 [-0,09; -0,07] | -0,02 [-0,03; -0,01] | -0,01 [-0,01; 0,00] |
| rendimento das reservas = 6% | A × C_sem_piso | P3 | -0,08 [-0,09; -0,07] | -0,01 [-0,03; -0,01] | -0,01 [-0,01; 0,00] |
| rendimento das reservas = 6% | A_reservas × C_sem_piso | P3 | -0,01 [-0,01; 0,00] | 0,01 [0,00; 0,01] | 0,00 [0,00; 0,01] |
| R_min = US$ 200 bi | A × A_reservas | P3 | -0,07 [-0,08; -0,06] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| R_min = US$ 200 bi | A × C_sem_piso | P3 | -0,08 [-0,09; -0,07] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| R_min = US$ 200 bi | A_reservas × C_sem_piso | P3 | -0,01 [-0,01; 0,00] | 0,00 [0,00; 0,01] | 0,00 [0,00; 0,01] |
| R_min = US$ 300 bi | A × A_reservas | P3 | -0,06 [-0,06; -0,05] | -0,02 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| R_min = US$ 300 bi | A × C_sem_piso | P3 | -0,07 [-0,07; -0,05] | -0,01 [-0,02; -0,01] | -0,01 [-0,01; 0,00] |
| R_min = US$ 300 bi | A_reservas × C_sem_piso | P3 | -0,01 [-0,01; 0,00] | 0,01 [0,00; 0,01] | 0,00 [0,00; 0,01] |

Nota: a venda de reservas reduz as compromissadas e, com elas, a dívida bruta, que é a variável do critério de dívida; a dívida líquida não muda no ato da venda. Parte da vantagem de vender reservas no critério de dívida bruta é, portanto, contábil; o custo de carregamento (rendimento das reservas abaixo da Selic) aparece ao longo do tempo.


## 6. Área de sucesso na superfície λ_π × λ_fiscal

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
| estimada | A. Ortodoxo | 25% | 29% | 20% |
| estimada | B. Lara Resende puro | 0% | 0% | 0% |
| estimada | C. Lara Resende condicionado | 22% | 25% | 13% |
| C_sem_piso | A. Ortodoxo | — | — | — |
| C_sem_piso | B. Lara Resende puro | — | — | — |
| C_sem_piso | C. Lara Resende condicionado | 20% | 27% | 32% |
| A_reservas | A. Ortodoxo | 19% | 25% | 32% |
| A_reservas | B. Lara Resende puro | — | — | — |
| A_reservas | C. Lara Resende condicionado | — | — | — |

Gráficos `10_superficie_base`, `10_superficie_neutro_45`, `10_superficie_rlong_45`, `10_superficie_rlong_65`, `10_superficie_estimada`, `10_superficie_C_sem_piso`, `10_superficie_A_reservas`.

Bootstrap pareado da área (ΔÁrea = Área(A) − Área(C)):

| Especificação | Variante | Área A | Área C | ΔÁrea [IC 95%] | C supera A | Leitura |
|---|---|---|---|---|---|---|
| P1 | base | 12% | 10% | 2,0 p.p. [-4,5; 9,8] | 26% | empate estatístico |
| P1 | neutro_45 | 23% | 14% | 9,1 p.p. [4,3; 16,6] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P1 | rlong_45 | 22% | 17% | 5,4 p.p. [1,6; 11,3] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P1 | rlong_65 | 0% | 0% | 0,0 p.p. [-2,0; 2,9] | 29% | empate estatístico |
| P1 | estimada | 25% | 22% | 3,2 p.p. [-6,6; 11,8] | 20% | empate estatístico |
| P2 | base | 17% | 12% | 4,8 p.p. [-3,6; 15,7] | 14% | empate estatístico |
| P2 | neutro_45 | 31% | 18% | 12,9 p.p. [2,5; 20,2] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P2 | rlong_45 | 28% | 22% | 6,1 p.p. [-1,1; 13,8] | 4% | empate estatístico |
| P2 | rlong_65 | 1% | 1% | 0,7 p.p. [-1,1; 9,8] | 20% | empate estatístico |
| P2 | estimada | 29% | 25% | 4,3 p.p. [-3,2; 11,1] | 17% | empate estatístico |
| P3 | base | 20% | 15% | 5,9 p.p. [3,9; 7,3] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P3 | neutro_45 | 28% | 22% | 6,1 p.p. [4,8; 7,7] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P3 | rlong_45 | 26% | 21% | 5,2 p.p. [4,1; 6,8] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P3 | rlong_65 | 14% | 8% | 6,1 p.p. [4,1; 7,3] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |
| P3 | estimada | 20% | 13% | 6,8 p.p. [5,0; 8,8] | 0% | A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal |

## 7. Validação e especificação de referência

Selic, primário e depreciação cambial observados; em P3, primário anunciado = mediana do Focus em cada data. Erro = RMSE/desvio-padrão de inflação + NTN-B 10 anos.

| Especificação | Episódio | λ de melhor ajuste | θ (P3) | Erro mín. | Erro λ = 0 | Erro λ = 1 | Erro P3 com θ = 0,5 | Pico obs. / sim. | Reproduz o pico de 2021–22? |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 2016–2019: âncora fiscal e queda da Selic | 0,90 | — | 1,91 | 35,90 | 1,95 | — | — | — |
| P1 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,10 | — | 4,48 | 4,65 | 5,24 | — | 11,9 / 5,3 | não |
| P2 | 2016–2019: âncora fiscal e queda da Selic | 0,95 | — | 1,76 | 39,00 | 1,78 | — | — | — |
| P2 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,40 | — | 4,02 | 15,01 | 4,99 | — | 11,9 / 6,5 | não |
| P3 | 2016–2019: âncora fiscal e queda da Selic | 1,00 | 0,25 | 2,17 | 31,08 | 2,17 | 2,26 | — | — |
| P3 | 2020–2022: Selic a 2%, expansão fiscal e aperto | 0,30 | 0,00 | 4,01 | 26,61 | 5,45 | 5,99 | 11,9 / 9,1 | sim |

Erro combinado: P1 = 6,39; P2 = 5,78; P3 = 6,17. **Especificação de referência: P2 · Phillips achatada** (ordem: A ≈ C > B).
P3 reproduz o pico de 2021–22 e P1 não, mas com θ = 0, isto é, sem o canal fiscal: a reprodução vem da ausência de inércia própria (a inflação segue as expectativas), não da lacuna fiscal. Não é evidência a favor da leitura fiscal da inflação recente.
Sobreajuste: P3 tem θ como parâmetro livre a mais; ver a coluna de erro com θ fixo em 0,5.
Em parte dos episódios o melhor ajuste de P3 tem θ = 0: nos dados brasileiros, o canal fiscal não melhora o ajuste e P3 se reduz a uma Phillips achatada sem inércia.

## 8. Alongamento da dívida

Decomposição em t0 (SGS, composição da DPMFi com operações de mercado aberto): LFT + compromissadas = 59%, das quais LFT do Tesouro = 47% e compromissadas do BCB = 12% (SGS 10632). Conferência no estoque do Tesouro (2026-08): LFT = 55% da DPMFi em mercado.
O alongamento reduz só a LFT do Tesouro; a meta de 40% para o total é alcançável (o piso é a fatia de compromissadas, 12%). Fatia mínima de LFT atingida (P3, λ = 0,9, cenário A): 34%.

| Especificação | φ | Alongamento | Cenário | P(sucesso) máx. | λ\*₅₀ | λ\*₈₀ | Explosiva | Dívida ↑ | Dívida > tol. | Inflação > teto |
|---|---|---|---|---|---|---|---|---|---|---|
| P3 | 0,00 | sem | A | 97% | 0,62 | 0,68 | 1% | 50% | 60% | 0% |
| P3 | 0,00 | sem | B | 4% | não atinge | não atinge | 25% | 70% | 62% | 1% |
| P3 | 0,00 | sem | C | 98% | 0,67 | 0,75 | 2% | 48% | 64% | 1% |
| P3 | 0,25 | sem † | A | 0% | não atinge | não atinge | 64% | 20% | 17% | 36% |
| P3 | 0,25 | sem † | B | 31% | não atinge | não atinge | 59% | 1% | 0% | 37% |
| P3 | 0,25 | sem † | C | 0% | não atinge | não atinge | 62% | 17% | 9% | 38% |
| P3 | 0,50 | sem † | A | 0% | não atinge | não atinge | 86% | 9% | 3% | 14% |
| P3 | 0,50 | sem † | B | 0% | não atinge | não atinge | 80% | 0% | 0% | 20% |
| P3 | 0,50 | sem † | C | 0% | não atinge | não atinge | 83% | 8% | 0% | 17% |
| P3 | 0,00 | along_20 | A | 94% | 0,59 | 0,65 | 1% | 49% | 58% | 0% |
| P3 | 0,00 | along_20 | B | 4% | não atinge | não atinge | 26% | 70% | 61% | 2% |
| P3 | 0,00 | along_20 | C | 98% | 0,65 | 0,73 | 2% | 50% | 61% | 1% |
| P3 | 0,25 | along_20 † | A | 3% | não atinge | não atinge | 48% | 23% | 24% | 52% |
| P3 | 0,25 | along_20 † | B | 29% | não atinge | não atinge | 59% | 4% | 0% | 38% |
| P3 | 0,25 | along_20 † | C | 5% | não atinge | não atinge | 48% | 19% | 15% | 52% |
| P3 | 0,50 | along_20 † | A | 0% | não atinge | não atinge | 63% | 17% | 14% | 37% |
| P3 | 0,50 | along_20 † | B | 0% | não atinge | não atinge | 80% | 0% | 0% | 20% |
| P3 | 0,50 | along_20 † | C | 0% | não atinge | não atinge | 63% | 14% | 8% | 37% |
| P3 | 0,25 | along_12 † | A | 4% | não atinge | não atinge | 47% | 23% | 23% | 53% |
| P3 | 0,25 | along_12 † | B | 30% | não atinge | não atinge | 59% | 4% | 0% | 38% |
| P3 | 0,25 | along_12 † | C | 6% | não atinge | não atinge | 47% | 18% | 13% | 53% |
| P3 | 0,25 | along_28 † | A | 2% | não atinge | não atinge | 49% | 23% | 25% | 51% |
| P3 | 0,25 | along_28 † | B | 29% | não atinge | não atinge | 59% | 3% | 0% | 37% |
| P3 | 0,25 | along_28 † | C | 4% | não atinge | não atinge | 48% | 19% | 15% | 51% |
| P3 | 0,25 | along_pre † | A | 2% | não atinge | não atinge | 50% | 18% | 19% | 50% |
| P3 | 0,25 | along_pre † | B | 29% | não atinge | não atinge | 59% | 3% | 0% | 38% |
| P3 | 0,25 | along_pre † | C | 2% | não atinge | não atinge | 50% | 15% | 11% | 50% |
| P3 | 0,25 | along_50 † | A | 1% | não atinge | não atinge | 52% | 24% | 23% | 48% |
| P3 | 0,25 | along_50 † | B | 31% | não atinge | não atinge | 59% | 2% | 0% | 37% |
| P3 | 0,25 | along_50 † | C | 0% | não atinge | não atinge | 52% | 20% | 14% | 48% |
| P1 | 0,00 | sem | A | 84% | 0,42 | 0,84 | 0% | 25% | 23% | 22% |
| P1 | 0,00 | sem | B | 5% | não atinge | não atinge | 58% | 27% | 29% | 15% |
| P1 | 0,00 | sem | C | 87% | 0,50 | 0,85 | 0% | 38% | 30% | 19% |
| P1 | 0,00 | along_20 | A | 86% | 0,45 | 0,83 | 0% | 27% | 27% | 22% |
| P1 | 0,00 | along_20 | B | 2% | não atinge | não atinge | 58% | 31% | 33% | 14% |
| P1 | 0,00 | along_20 | C | 87% | 0,50 | 0,82 | 0% | 39% | 31% | 20% |
| P2 | 0,00 | sem | A | 87% | 0,42 | 0,79 | 4% | 24% | 26% | 25% |
| P2 | 0,00 | sem | B | 4% | não atinge | não atinge | 56% | 27% | 29% | 16% |
| P2 | 0,00 | sem | C | 88% | 0,46 | 0,82 | 4% | 32% | 25% | 26% |
| P2 | 0,00 | along_20 | A | 87% | 0,46 | 0,78 | 4% | 26% | 29% | 26% |
| P2 | 0,00 | along_20 | B | 2% | não atinge | não atinge | 56% | 30% | 33% | 16% |
| P2 | 0,00 | along_20 | C | 89% | 0,47 | 0,77 | 4% | 32% | 26% | 26% |

Erosão da dívida pela inflação (P3, trajetória determinística, soma em 10 anos, p.p. do PIB): total = redução do valor real da dívida não indexada (LFT, prefixados, cambial) pela inflação; não antecipada = parte acima da inflação embutida no custo de cada título.

| φ | Alongamento | Cenário | λ | Erosão total | Não antecipada | Fração não antecipada | Dívida final | Inflação final |
|---|---|---|---|---|---|---|---|---|
| 0,00 | sem | A | 0,5 | -13,8 | -17,4 | — (deflação) | 97,3 | -3,0 |
| 0,00 | sem | A | 0,9 | 15,8 | -5,2 | -33% | 80,1 | 2,0 |
| 0,00 | sem | B | 0,5 | 15,7 | -6,5 | -41% | 102,5 | 1,4 |
| 0,00 | sem | B | 0,9 | 19,9 | -2,5 | -13% | 96,8 | 2,8 |
| 0,00 | sem | C | 0,5 | 4,7 | -9,9 | -209% | 97,6 | 1,1 |
| 0,00 | sem | C | 0,9 | 15,0 | -4,6 | -31% | 74,9 | 2,3 |
| 0,00 | along_20 | A | 0,5 | -6,9 | -13,2 | — (deflação) | 94,1 | -2,4 |
| 0,00 | along_20 | A | 0,9 | 15,2 | -3,5 | -23% | 81,5 | 2,4 |
| 0,00 | along_20 | B | 0,5 | 16,5 | -5,6 | -34% | 99,6 | 1,6 |
| 0,00 | along_20 | B | 0,9 | 18,2 | -2,2 | -12% | 98,5 | 2,8 |
| 0,00 | along_20 | C | 0,5 | 5,7 | -8,2 | -143% | 95,6 | 1,2 |
| 0,00 | along_20 | C | 0,9 | 14,1 | -3,6 | -26% | 74,7 | 2,4 |
| 0,25 | sem | A | 0,5 | 193,1 | 59,3 | 31% | 162,8 | 38,4 |
| 0,25 | sem | A | 0,9 | 49,9 | 23,9 | 48% | 82,2 | 8,5 |
| 0,25 | sem | B | 0,5 | 25,6 | -2,3 | -9% | 43,9 | 0,3 |
| 0,25 | sem | B | 0,9 | 42,7 | 20,0 | 47% | 62,0 | 7,3 |
| 0,25 | sem | C | 0,5 | 158,6 | 48,2 | 30% | 140,9 | 34,5 |
| 0,25 | sem | C | 0,9 | 43,2 | 19,6 | 45% | 74,7 | 7,8 |
| 0,25 | along_20 | A | 0,5 | 80,8 | 21,1 | 26% | 119,4 | 15,7 |
| 0,25 | along_20 | A | 0,9 | 34,3 | 13,4 | 39% | 79,3 | 5,8 |
| 0,25 | along_20 | B | 0,5 | 25,7 | -2,2 | -9% | 44,0 | 0,3 |
| 0,25 | along_20 | B | 0,9 | 37,9 | 16,8 | 44% | 67,6 | 6,7 |
| 0,25 | along_20 | C | 0,5 | 74,4 | 19,3 | 26% | 108,8 | 15,5 |
| 0,25 | along_20 | C | 0,9 | 31,6 | 11,9 | 38% | 72,2 | 5,7 |

Erosão negativa: a inflação ficou abaixo da embutida no custo dos títulos (deflação ou desinflação não antecipada), o que aumenta a dívida real; nesses casos a fração não é calculada.

Custo do alongamento com φ = 0 (a lacuna já está precificada: só custo, sem benefício): custo real efetivo médio da dívida (i_ef − π, média de 10 anos) e dívida final, trajetória determinística.

| Especificação | Cenário | λ | Custo real sem → com | Δ custo (p.p. a.a.) | Dívida final sem → com | Duração final sem → com (anos) |
|---|---|---|---|---|---|---|
| P1 | A | 0,5 | 6,06 → 6,17 | 0,11 | 81,5 → 82,5 | 2,2 → 3,5 |
| P1 | A | 0,9 | 5,91 → 5,93 | 0,01 | 79,0 → 79,0 | 2,2 → 3,5 |
| P1 | B | 0,5 | -2,11 → -1,68 | 0,42 | rompeu → rompeu | rompeu → rompeu |
| P1 | B | 0,9 | 5,46 → 5,83 | 0,37 | 96,3 → 100,8 | 2,4 → 3,3 |
| P1 | C | 0,5 | 5,96 → 6,00 | 0,04 | 75,1 → 75,4 | 2,3 → 3,4 |
| P1 | C | 0,9 | 5,78 → 5,76 | -0,02 | 72,6 → 72,4 | 2,3 → 3,5 |
| P2 | A | 0,5 | 6,08 → 6,21 | 0,13 | 81,7 → 83,0 | 2,2 → 3,5 |
| P2 | A | 0,9 | 5,90 → 5,94 | 0,04 | 78,8 → 79,2 | 2,2 → 3,5 |
| P2 | B | 0,5 | -2,75 → -2,43 | 0,33 | 18,5 → 19,4 | 9,0 → 8,9 |
| P2 | B | 0,9 | 5,44 → 5,72 | 0,28 | 95,8 → 99,1 | 2,4 → 3,3 |
| P2 | C | 0,5 | 5,94 → 5,97 | 0,04 | 74,7 → 75,0 | 2,3 → 3,5 |
| P2 | C | 0,9 | 5,75 → 5,72 | -0,03 | 72,0 → 71,7 | 2,3 → 3,5 |
| P3 | A | 0,5 | 7,00 → 6,87 | -0,13 | 97,3 → 94,1 | 2,2 → 3,4 |
| P3 | A | 0,9 | 5,91 → 6,07 | 0,16 | 80,1 → 81,5 | 2,2 → 3,5 |
| P3 | B | 0,5 | 6,08 → 5,88 | -0,21 | 102,5 → 99,6 | 2,3 → 3,2 |
| P3 | B | 0,9 | 5,59 → 5,74 | 0,16 | 96,8 → 98,5 | 2,4 → 3,3 |
| P3 | C | 0,5 | 7,59 → 7,47 | -0,12 | 97,6 → 95,6 | 2,2 → 3,3 |
| P3 | C | 0,9 | 5,94 → 5,92 | -0,01 | 74,9 → 74,7 | 2,3 → 3,4 |

"rompeu": a trajetória determinística passou de 50% de inflação e foi encerrada; o custo real é a média até a ruptura.

- **O alongamento reabre a válvula?** Com φ = 0,25, a maior P(sucesso) de A ou C vai de 0% sem alongamento para 5% com along_20: não — os cenários continuam falhando, sobretudo por inflação acima do teto; a migração vai em 70% para NTN-B, que é indexada e não sofre erosão.
- **Velocidade e composição:** P(sucesso) máx. de A/C com φ = 0,25 — along_12: 6%; along_20: 5%; along_28: 4%; along_pre: 2%; along_50: 1%. Melhor caso: along_12, ainda abaixo de 50%: nenhuma velocidade testada reabre a válvula.
- **Custo com φ = 0 (cenário A):** variação do custo real efetivo médio de P1 λ=0,5: 0,11 p.p. a.a. (dívida final 1,0 p.p.); P1 λ=0,9: 0,01 p.p. a.a. (dívida final 0,0 p.p.); P2 λ=0,5: 0,13 p.p. a.a. (dívida final 1,2 p.p.); P2 λ=0,9: 0,04 p.p. a.a. (dívida final 0,4 p.p.); P3 λ=0,5: -0,13 p.p. a.a. (dívida final -3,3 p.p.); P3 λ=0,9: 0,16 p.p. a.a. (dívida final 1,3 p.p.).

Gráfico `14_alongamento`.

## 9. Premissas e limitações

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
- O bootstrap mede apenas a incerteza do Monte Carlo, não a dos parâmetros. A incerteza de b3 entra pelas variantes estimada_b3_baixo e estimada_b3_alto; ω não é identificado nos dados, e sua incerteza entra pela grade ω ∈ {0; 0,38; 0,5; 1} (0,38 = 1 − b da verificação cruzada).
- Estimação: o EMBI+ termina em jul/2024 (ω estimado até essa data); o DXY foi substituído pelo dólar amplo do Fed (DTWEXBGS, encadeado com DTWEXB antes de 2006); o IC-Br entra em US$ porque a versão em reais contém o próprio câmbio; hiato e desvio do Focus entram defasados porque reagem ao câmbio no próprio mês.
- Alongamento: aplicado ao fim de cada trimestre, depois da emissão; a restrição de rolagem atua no trimestre seguinte sobre a LFT restante, de modo que as duas nunca movem o mesmo estoque. A emissão primária continua com a composição inicial e o teto devolve o excedente ao fim do trimestre.

## 10. Síntese

(a) **A e C são estatisticamente distinguíveis?** Na base, empate estatístico em λ\*₈₀ em 2 de 3 especificações (P1, P2); P1: Δλ\*₈₀ = 0,01 [-0,05; 0,05]; P2: Δλ\*₈₀ = 0,03 [-0,01; 0,07]; P3: Δλ\*₈₀ = 0,07 [0,06; 0,09].
Na área de sucesso (base): P1: empate estatístico; P2: empate estatístico; P3: A significativamente mais robusto ao descompasso entre λ_π e λ_fiscal.
(b) **Com os parâmetros estimados, quem fica à frente?** P1: A ≈ C > B; P2: A ≈ C > B; P3: A > C > B (b3 calibrado por especificação; ψ estimado = 4,23, IC de Fieller [0,02; 13,48]: identificado, mas com estimativa pontual fora de [0, 1]; a variante estimada usa ω = 0, e o efeito de ω fica na grade {0; 0,5; 1}). Com a grade de ω, que tem o mesmo peso da base porque ω não é calibrado pelos dados: P1: ω = 0 → A ≈ C > B, ω = 0,5 → A ≈ C > B, ω = 1 → A > C > B, ω = 0,38 (verificação cruzada) → A ≈ C > B; P2: ω = 0 → A ≈ C > B, ω = 0,5 → A ≈ C > B, ω = 1 → A ≈ C > B, ω = 0,38 (verificação cruzada) → A ≈ C > B; P3: ω = 0 → A > C > B, ω = 0,5 → A > C > B, ω = 1 → A > C > B, ω = 0,38 (verificação cruzada) → A > C > B. Em P3, com θ no intervalo sustentado pela validação: θ = 0,25 → A > C > B; θ = 0 → C > A > B.
(d) **Critério de inflação com banda simétrica (1,5%–4,5%):** P1: A ≈ C > B (teto) → A ≈ C > B (banda); P2: A ≈ C > B (teto) → A ≈ C > B (banda); P3: A > C > B (teto) → C > A > B (banda). Ver seção 2.
(c) **O alongamento reabre a válvula da erosão inflacionária?** Não: com φ = 0,25, a maior P(sucesso) de A ou C passa de 0% para no máximo 6% (along_12 6%, along_20 5%, along_28 4%, along_pre 2%, along_50 1%); a inflação continua acima do teto porque 70% da LFT migra para NTN-B, que é indexada. Com φ = 0, o custo é pequeno: entre -0,13 e 0,16 p.p. a.a. no custo real da dívida e entre -3,3 e 1,3 p.p. do PIB na dívida final do cenário A.
