# Efeito recessivo das estratégias: PIB, composição do pacote, setores e emprego

Modelo v2.2 calibrado (R_min = US$ 300 bi), N = 1000 trajetórias por estratégia e λ (seed 42, as mesmas da rodada principal), bootstrap pareado com R = 1000 (seed 2026). Especificações P1, P2 e P3 (θ = 0,5 e 0,25); adesão λ ∈ {0,3; 0,5; 0,7; 0,9} na diagonal. t0 = 2026T3: a eleição de outubro de 2030 é o trimestre 16. Os multiplicadores por item do pacote substituem a3 = 0,4 só neste módulo; a lógica de sucesso já reportada não muda.

**Diferença de produto acumulada contra S** = Σ (PIB da estratégia − PIB de S) / PIB de S, em % do PIB de um ano (positivo = produto acima de S; negativo = a estratégia é recessiva contra S).

**Efeito fiscal em nível.** Cada item do pacote entra na equação do hiato como m · (medida_t − ρ_f · medida_{t−1}), com ρ_f = a1 (= 0,777): o efeito direto sobre o hiato é m × medida em vigor, e o multiplicador acumulado direto é m em 4, 8 e 16 trimestres (seção 2). A versão anterior, com o efeito pelo impulso (m · (−Δmedida)), está em `relatorio_recessivo_impulso.md`.

**Inflação alta.** O modelo não tem custo de produto da inflação alta. Por isso as trajetórias com inflação acima de 20% em algum trimestre (da estratégia ou de S) saem das métricas de produto; a fração aparece ao lado. Na probabilidade de recessão, a trajetória explosiva (π > 50%) conta como recessão na janela em que rompe.

Estratégias: **S** = S. Referência sem ajuste; **A** = A. Ortodoxo; **A_res60** = A com venda de US$ 60 bi; **A_res100** = A com venda de até US$ 100 bi (efetiva: 76); **B** = B. Lara Resende puro; **C** = C. Lara Resende condicionado; **C_sem_piso** = C sem piso (venda efetiva: 76).

## Síntese

1. **Produto e recessão contra S.** Com o efeito fiscal em nível, o ajuste passa a ser recessivo contra a referência sem ajuste (S) nos primeiros 8 trimestres sempre que a adesão é baixa (λ = 0,3 em P1 e P2) e, em P3, até a eleição para λ ≤ 0,7. Com λ = 0,7 em P1, A fica 0,8% do PIB de um ano acima de S até a eleição (2,3% na versão pelo impulso): o efeito direto do pacote (−0,8 p.p. de hiato) quase anula o ganho do juro real longo (+1,0 p.p.). A probabilidade de recessão técnica de A e de S fica entre 36% e 40%.
2. **Entre as estratégias com ajuste, C sem piso tem o maior produto**: 1,2 a 1,6% do PIB de um ano acima de A até a eleição, em todas as especificações; contra A com a mesma venda efetiva (76 bi), 0,7 a 1,0. A venda de reservas acrescenta 0,2 a 0,5. B tem o maior produto de curto prazo, mas com λ ≤ 0,5 em P1 e P2 a inflação passa de 20% em quase todas as trajetórias, que saem da métrica, e nunca atinge 70% de sucesso.
3. **Composição do pacote.** Com o mesmo valor total, o pacote de qualidade preserva 2,5 a 3,1% do PIB de um ano a mais que o corte linear até a eleição (2,0 a 7,8 na faixa de multiplicadores; 3,1 a 6,2 com multiplicadores dependentes do ciclo). Com o corte linear, A fica abaixo de S até a eleição em P1 (−1,1). Pelo impulso, a diferença era de 0,7 a 0,9: o efeito em nível triplica a importância da composição.
4. **Setores e emprego** (P1, λ = 0,7, média até a eleição): A gera 290 mil ocupações a mais que S (120 mil formais); C sem piso, 620 mil (300 mil formais). Ganham construção, comércio, outros serviços e transformação; a administração pública perde 150 a 160 mil com os cortes em pisos e emendas. Desocupação 0,05 a 0,11 p.p. menor.
5. **Credibilidade de S e validação.** O ganho de A contra S depende do canal do juro longo: com a2 = 0,05 ou com p1 e p2 pela metade, A é recessivo contra S em todas as especificações e adesões; só com a2 = 0,30 deixa de ser em P1 e P2. Na validação de 2015–2016, o modelo não reproduz a recessão (simula +0,5 a +1,0% ao ano, contra −3,5% e −3,3%): os canais modelados explicam cerca de 1 p.p.; o restante fica com fatores não modelados (commodities, crise política, Lava Jato).
6. **Robustez × custo.** Não há troca: as estratégias mais robustas pela dívida líquida (C sem piso e A com venda de reservas) também têm o maior produto entre as que ajustam. Com o efeito em nível, C com piso deixa de atingir 70% em P1 e P2.

## 1. Produto e recessão

Mediana da diferença de produto acumulada contra S [faixa 10–90%] e P(recessão técnica), λ = 0,7:

| Especificação | Estratégia | Inflação > 20% | Dif. 1-8 | P(rec.) 1-8 | Dif. 1-16 | P(rec.) 1-16 | Dif. 1-40 | P(rec.) 1-40 |
|---|---|---|---|---|---|---|---|---|
| P1 | S | 0% | 0,00 [0,0; 0,0] | 23% | 0,00 [0,0; 0,0] | 38% | 0,00 [0,0; 0,0] | 75% |
| P1 | A | 0% | 0,31 [0,3; 0,3] | 20% | 0,82 [0,7; 0,9] | 36% | 1,15 [0,7; 1,4] | 75% |
| P1 | A_res60 | 0% | 0,41 [0,4; 0,4] | 20% | 1,21 [1,0; 1,3] | 35% | 1,86 [1,4; 2,2] | 75% |
| P1 | A_res100 (ef. 76) | 0% | 0,43 [0,4; 0,5] | 19% | 1,31 [1,1; 1,4] | 35% | 2,02 [1,6; 2,4] | 75% |
| P1 | B | 0% | 1,23 [0,9; 1,6] | 14% | 3,94 [2,0; 6,0] | 30% | 12,63 [3,4; 24,3] | 73% |
| P1 | C | 0% | 0,88 [0,6; 0,9] | 17% | 1,79 [0,9; 2,1] | 38% | 0,90 [−1,9; 2,3] | 77% |
| P1 | C_sem_piso | 0% | 0,92 [0,7; 1,0] | 17% | 2,00 [1,6; 2,2] | 36% | 2,81 [2,3; 3,3] | 75% |
| P2 | S | 0% | 0,00 [0,0; 0,0] | 25% | 0,00 [0,0; 0,0] | 40% | 0,00 [0,0; 0,0] | 76% |
| P2 | A | 0% | 0,36 [0,3; 0,4] | 21% | 1,03 [0,9; 1,1] | 37% | 1,68 [1,3; 2,0] | 75% |
| P2 | A_res60 | 0% | 0,46 [0,4; 0,5] | 20% | 1,48 [1,3; 1,6] | 37% | 2,62 [2,2; 3,0] | 75% |
| P2 | A_res100 (ef. 76) | 0% | 0,49 [0,4; 0,5] | 20% | 1,59 [1,4; 1,7] | 36% | 2,83 [2,4; 3,2] | 75% |
| P2 | B | 0% | 1,52 [1,2; 1,8] | 14% | 5,03 [3,0; 7,1] | 30% | 13,73 [6,3; 24,1] | 75% |
| P2 | C | 0% | 1,06 [0,8; 1,1] | 17% | 2,55 [1,7; 2,8] | 38% | 2,83 [0,3; 4,0] | 77% |
| P2 | C_sem_piso | 0% | 1,06 [0,9; 1,1] | 17% | 2,60 [2,2; 2,8] | 37% | 3,89 [3,3; 4,4] | 76% |
| P3_theta05 | S | 0% | 0,00 [0,0; 0,0] | 23% | 0,00 [0,0; 0,0] | 39% | 0,00 [0,0; 0,0] | 75% |
| P3_theta05 | A | 0% | −0,17 [−0,2; −0,2] | 24% | −0,65 [−0,7; −0,6] | 40% | −1,99 [−3,1; −1,4] | 76% |
| P3_theta05 | A_res60 | 0% | −0,14 [−0,2; −0,1] | 24% | −0,41 [−0,5; −0,4] | 39% | −1,28 [−2,2; −0,7] | 75% |
| P3_theta05 | A_res100 (ef. 76) | 0% | −0,13 [−0,2; −0,1] | 24% | −0,35 [−0,5; −0,3] | 40% | −1,11 [−2,0; −0,6] | 75% |
| P3_theta05 | B | 0% | 1,31 [1,1; 1,5] | 14% | 3,92 [3,0; 4,9] | 33% | 6,37 [4,5; 8,3] | 78% |
| P3_theta05 | C | 0% | 0,45 [0,3; 0,5] | 19% | 0,29 [−0,1; 0,6] | 42% | −4,53 [−5,6; −3,5] | 79% |
| P3_theta05 | C_sem_piso | 0% | 0,45 [0,4; 0,5] | 19% | 0,61 [0,4; 0,7] | 38% | −0,06 [−1,0; 0,5] | 75% |
| P3_theta025 | S | 0% | 0,00 [0,0; 0,0] | 23% | 0,00 [0,0; 0,0] | 38% | 0,00 [0,0; 0,0] | 75% |
| P3_theta025 | A | 0% | −0,16 [−0,2; −0,2] | 24% | −0,55 [−0,7; −0,5] | 39% | −1,55 [−1,8; −1,4] | 75% |
| P3_theta025 | A_res60 | 0% | −0,13 [−0,2; −0,1] | 24% | −0,32 [−0,4; −0,3] | 39% | −0,96 [−1,2; −0,7] | 75% |
| P3_theta025 | A_res100 (ef. 76) | 0% | −0,12 [−0,2; −0,1] | 24% | −0,26 [−0,4; −0,2] | 39% | −0,81 [−1,1; −0,6] | 75% |
| P3_theta025 | B | 0% | 1,30 [1,1; 1,5] | 13% | 4,05 [3,1; 5,1] | 32% | 8,09 [5,9; 10,6] | 77% |
| P3_theta025 | C | 0% | 0,46 [0,3; 0,5] | 19% | 0,62 [0,3; 0,8] | 40% | −2,85 [−3,8; −1,9] | 78% |
| P3_theta025 | C_sem_piso | 0% | 0,46 [0,4; 0,5] | 19% | 0,73 [0,5; 0,9] | 38% | 0,30 [−0,1; 0,6] | 75% |

Diferença de produto até a eleição contra S (trimestres 1–16, mediana) por λ; entre parênteses, a fração de trajetórias com inflação acima de 20%, quando houver:

| Especificação | Estratégia | λ = 0,3 | λ = 0,5 | λ = 0,7 | λ = 0,9 |
|---|---|---|---|---|---|
| P1 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P1 | A | −0,24 | 0,27 | 0,82 | 1,36 |
| P1 | A_res60 | 0,32 | 0,70 | 1,21 | 1,76 |
| P1 | A_res100 (ef. 76) | 0,50 | 0,83 | 1,31 | 1,85 |
| P1 | B | −0,15 (97%) | 1,97 (89%) | 3,94 | 2,80 |
| P1 | C | 1,32 | 1,57 | 1,79 | 2,13 |
| P1 | C_sem_piso | 1,43 | 1,75 | 2,00 | 2,36 |
| P2 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P2 | A | −0,19 | 0,41 | 1,03 | 1,67 |
| P2 | A_res60 | 0,40 | 0,88 | 1,48 | 2,15 |
| P2 | A_res100 (ef. 76) | 0,58 | 1,01 | 1,59 | 2,25 |
| P2 | B | 1,53 (98%) | 3,33 (88%) | 5,03 | 3,91 |
| P2 | C | 1,70 | 2,16 | 2,55 | 3,05 |
| P2 | C_sem_piso | 1,71 | 2,20 | 2,60 | 3,10 |
| P3_theta05 | S | 0,00 (2%) | 0,00 | 0,00 | 0,00 |
| P3_theta05 | A | −1,79 | −1,27 | −0,65 | 0,03 |
| P3_theta05 | A_res60 | −1,57 | −1,03 | −0,41 | 0,26 |
| P3_theta05 | A_res100 (ef. 76) | −1,50 | −0,96 | −0,35 | 0,32 |
| P3_theta05 | B | 17,63 (28%) | 6,89 | 3,92 | 3,28 |
| P3_theta05 | C | −2,45 | −1,16 | 0,29 | 1,17 |
| P3_theta05 | C_sem_piso | −0,58 | 0,03 | 0,61 | 1,19 |
| P3_theta025 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P3_theta025 | A | −1,19 | −1,05 | −0,55 | 0,03 |
| P3_theta025 | A_res60 | −0,90 | −0,80 | −0,32 | 0,27 |
| P3_theta025 | A_res100 (ef. 76) | −0,80 | −0,73 | −0,26 | 0,33 |
| P3_theta025 | B | 2,51 (98%) | 7,86 | 4,05 | 3,29 |
| P3_theta025 | C | −0,81 | −0,16 | 0,62 | 1,18 |
| P3_theta025 | C_sem_piso | 0,06 | 0,32 | 0,73 | 1,20 |

Hiato mínimo (mediana, trimestres 1–40) e trimestre em que ocorre, anos com crescimento negativo (média, 2027–2035) e taxa de sacrifício (perda de produto até o trimestre 16 ÷ queda da inflação média do ano 1 para os anos 3–4, só quando a inflação cai), λ = 0,7:

| Especificação | Estratégia | Hiato mínimo | Trimestre | Anos negativos | Sacrifício | Trajetórias com queda |
|---|---|---|---|---|---|---|
| P1 | S | −3,16 | 25 | 0,1 | 0,00 | 64% |
| P1 | A | −3,04 | 26 | 0,1 | −0,74 | 53% |
| P1 | A_res60 | −2,98 | 27 | 0,1 | −1,19 | 46% |
| P1 | A_res100 (ef. 76) | −2,97 | 27 | 0,1 | −1,34 | 43% |
| P1 | B | −2,21 | 6 | 0,1 | −3,04 | 32% |
| P1 | C | −3,10 | 29 | 0,1 | −1,52 | 46% |
| P1 | C_sem_piso | −2,89 | 27 | 0,1 | −2,10 | 44% |
| P2 | S | −3,31 | 24 | 0,1 | 0,00 | 62% |
| P2 | A | −3,13 | 26 | 0,1 | −0,96 | 54% |
| P2 | A_res60 | −3,05 | 26 | 0,1 | −1,50 | 50% |
| P2 | A_res100 (ef. 76) | −3,04 | 26 | 0,1 | −1,64 | 46% |
| P2 | B | −2,23 | 12 | 0,1 | −4,16 | 37% |
| P2 | C | −3,11 | 29 | 0,1 | −2,37 | 49% |
| P2 | C_sem_piso | −2,95 | 28 | 0,1 | −2,64 | 49% |
| P3_theta05 | S | −3,05 | 21 | 0,1 | 0,00 | 72% |
| P3_theta05 | A | −3,24 | 25 | 0,1 | 0,27 | 98% |
| P3_theta05 | A_res60 | −3,17 | 23 | 0,1 | 0,19 | 97% |
| P3_theta05 | A_res100 (ef. 76) | −3,16 | 23 | 0,1 | 0,17 | 96% |
| P3_theta05 | B | −2,61 | 29 | 0,1 | −3,21 | 72% |
| P3_theta05 | C | −3,58 | 29 | 0,1 | −0,12 | 97% |
| P3_theta05 | C_sem_piso | −3,03 | 26 | 0,1 | −0,24 | 98% |
| P3_theta025 | S | −3,07 | 22 | 0,1 | 0,00 | 69% |
| P3_theta025 | A | −3,20 | 22 | 0,1 | 0,38 | 89% |
| P3_theta025 | A_res60 | −3,16 | 22 | 0,1 | 0,24 | 84% |
| P3_theta025 | A_res100 (ef. 76) | −3,14 | 22 | 0,1 | 0,21 | 82% |
| P3_theta025 | B | −2,48 | 27 | 0,1 | −4,76 | 56% |
| P3_theta025 | C | −3,41 | 29 | 0,1 | −0,40 | 86% |
| P3_theta025 | C_sem_piso | −3,01 | 25 | 0,1 | −0,48 | 87% |

Bootstrap pareado (diferença de médias, IC de 95%; * = exclui zero). Diferença de produto em % do PIB de um ano (positivo = o primeiro tem mais produto); P(recessão) em p.p.; λ = 0,7:

| Especificação | Par | Produto 1–8 | Produto 1–16 | P(rec.) 1–8 | P(rec.) 1–16 |
|---|---|---|---|---|---|
| P1 | A − C | −0,53 [−0,54; −0,52] * | −0,80 [−0,83; −0,77] * | 3 [2; 4] * | −2 [−3; −0] * |
| P1 | A − C_sem_piso | −0,59 [−0,59; −0,58] * | −1,18 [−1,19; −1,16] * | 3 [2; 4] * | −0 [−2; 1] |
| P1 | A − A_res60 | −0,09 [−0,09; −0,09] * | −0,40 [−0,40; −0,39] * | 1 [0; 1] * | 1 [0; 1] * |
| P1 | C_sem_piso − A_res100 | 0,47 [0,46; 0,47] * | 0,68 [0,67; 0,69] * | −2 [−3; −1] * | 1 [−0; 3] |
| P1 | A − S | 0,30 [0,30; 0,30] * | 0,79 [0,78; 0,80] * | −3 [−4; −2] * | −2 [−3; −1] * |
| P1 | A_res60 − S | 0,39 [0,39; 0,40] * | 1,19 [1,18; 1,19] * | −4 [−5; −2] * | −3 [−4; −1] * |
| P1 | A_res100 − S | 0,42 [0,42; 0,42] * | 1,28 [1,28; 1,29] * | −4 [−5; −2] * | −3 [−4; −2] * |
| P1 | B − S | 1,23 [1,21; 1,25] * | 3,99 [3,90; 4,09] * | −9 [−10; −7] * | −8 [−10; −6] * |
| P1 | C − S | 0,83 [0,82; 0,84] * | 1,59 [1,56; 1,62] * | −6 [−7; −4] * | −0 [−2; 2] |
| P1 | C_sem_piso − S | 0,89 [0,88; 0,90] * | 1,97 [1,95; 1,98] * | −6 [−7; −4] * | −2 [−4; 0] |
| P2 | A − C | −0,67 [−0,68; −0,67] * | −1,37 [−1,40; −1,34] * | 4 [2; 5] * | −0 [−2; 1] |
| P2 | A − C_sem_piso | −0,69 [−0,69; −0,68] * | −1,55 [−1,56; −1,54] * | 4 [2; 5] * | 0 [−1; 2] |
| P2 | A − A_res60 | −0,10 [−0,10; −0,10] * | −0,45 [−0,45; −0,45] * | 0 [0; 1] * | 1 [0; 1] |
| P2 | C_sem_piso − A_res100 | 0,55 [0,55; 0,56] * | 0,99 [0,98; 1,00] * | −3 [−4; −2] * | 0 [−1; 2] |
| P2 | A − S | 0,35 [0,35; 0,35] * | 1,00 [1,00; 1,01] * | −4 [−5; −3] * | −3 [−4; −2] * |
| P2 | A_res60 − S | 0,45 [0,45; 0,46] * | 1,45 [1,45; 1,46] * | −4 [−6; −3] * | −4 [−5; −2] * |
| P2 | A_res100 − S | 0,48 [0,48; 0,49] * | 1,57 [1,56; 1,57] * | −4 [−6; −3] * | −4 [−5; −2] * |
| P2 | B − S | 1,51 [1,50; 1,53] * | 5,02 [4,93; 5,11] * | −11 [−13; −9] * | −10 [−12; −8] * |
| P2 | C − S | 1,02 [1,02; 1,03] * | 2,37 [2,34; 2,40] * | −7 [−9; −6] * | −3 [−5; −1] * |
| P2 | C_sem_piso − S | 1,04 [1,03; 1,04] * | 2,55 [2,54; 2,57] * | −8 [−9; −6] * | −4 [−6; −2] * |
| P3_theta05 | A − C | −0,61 [−0,62; −0,61] * | −0,92 [−0,94; −0,90] * | 5 [4; 6] * | −2 [−4; 0] |
| P3_theta05 | A − C_sem_piso | −0,61 [−0,62; −0,61] * | −1,24 [−1,25; −1,24] * | 5 [4; 6] * | 2 [0; 3] * |
| P3_theta05 | A − A_res60 | −0,03 [−0,03; −0,03] * | −0,23 [−0,23; −0,23] * | 0 [−0; 1] | 0 [−0; 1] |
| P3_theta05 | C_sem_piso − A_res100 | 0,57 [0,57; 0,58] * | 0,95 [0,95; 0,96] * | −5 [−6; −4] * | −2 [−3; −0] * |
| P3_theta05 | A − S | −0,18 [−0,18; −0,18] * | −0,66 [−0,66; −0,65] * | 1 [−0; 2] | 1 [−0; 2] |
| P3_theta05 | A_res60 − S | −0,14 [−0,15; −0,14] * | −0,43 [−0,43; −0,42] * | 0 [−1; 1] | 0 [−1; 1] |
| P3_theta05 | A_res100 − S | −0,14 [−0,14; −0,13] * | −0,37 [−0,37; −0,36] * | 1 [−0; 2] | 1 [−0; 2] |
| P3_theta05 | B − S | 1,31 [1,30; 1,32] * | 3,93 [3,89; 3,98] * | −10 [−12; −8] * | −6 [−8; −3] * |
| P3_theta05 | C − S | 0,43 [0,43; 0,44] * | 0,26 [0,24; 0,28] * | −4 [−6; −3] * | 3 [1; 5] * |
| P3_theta05 | C_sem_piso − S | 0,44 [0,43; 0,44] * | 0,59 [0,58; 0,59] * | −4 [−6; −3] * | −1 [−3; 1] |
| P3_theta025 | A − C | −0,61 [−0,61; −0,60] * | −1,14 [−1,16; −1,13] * | 4 [3; 6] * | −0 [−2; 1] |
| P3_theta025 | A − C_sem_piso | −0,61 [−0,61; −0,61] * | −1,28 [−1,28; −1,27] * | 4 [3; 6] * | 1 [−0; 3] |
| P3_theta025 | A − A_res60 | −0,03 [−0,03; −0,03] * | −0,23 [−0,23; −0,23] * | 0 [−0; 1] | 0 [−0; 1] |
| P3_theta025 | C_sem_piso − A_res100 | 0,57 [0,57; 0,57] * | 0,99 [0,98; 0,99] * | −5 [−6; −3] * | −1 [−3; 0] |
| P3_theta025 | A − S | −0,17 [−0,17; −0,17] * | −0,57 [−0,57; −0,56] * | 1 [−0; 2] | 1 [−0; 2] |
| P3_theta025 | A_res60 − S | −0,14 [−0,14; −0,14] * | −0,34 [−0,34; −0,33] * | 0 [−0; 1] | 1 [−0; 2] |
| P3_theta025 | A_res100 − S | −0,13 [−0,13; −0,13] * | −0,28 [−0,28; −0,28] * | 1 [−0; 2] | 1 [−0; 2] |
| P3_theta025 | B − S | 1,30 [1,28; 1,31] * | 4,07 [4,03; 4,12] * | −10 [−12; −8] * | −7 [−9; −5] * |
| P3_theta025 | C − S | 0,44 [0,44; 0,44] * | 0,57 [0,56; 0,59] * | −4 [−5; −3] * | 1 [−0; 3] |
| P3_theta025 | C_sem_piso − S | 0,44 [0,44; 0,45] * | 0,71 [0,70; 0,72] * | −4 [−5; −3] * | −0 [−2; 1] |

Decomposição da diferença de hiato contra S (média dos trimestres 1–16, p.p. do PIB, λ = 0,7): efeito direto do pacote (soma dos itens), juro real longo, câmbio real, CAPEX e restante.

| Especificação | Estratégia | Δ hiato | Pacote direto | Juro real longo | Câmbio | CAPEX | Fiscal fora do pacote | Outros |
|---|---|---|---|---|---|---|---|---|
| P1 | A | 0,20 | −0,78 | 0,95 | −0,04 | 0,08 | −0,00 | 0,00 |
| P1 | A_res60 | 0,30 | −0,78 | 1,08 | −0,07 | 0,08 | −0,00 | 0,00 |
| P1 | A_res100 (ef. 76) | 0,32 | −0,78 | 1,11 | −0,08 | 0,08 | −0,00 | 0,00 |
| P1 | B | 1,00 | 0,00 | 0,97 | −0,02 | 0,07 | −0,02 | −0,00 |
| P1 | C | 0,40 | −0,78 | 1,18 | −0,08 | 0,08 | −0,00 | 0,00 |
| P1 | C_sem_piso | 0,49 | −0,78 | 1,27 | −0,08 | 0,09 | −0,00 | 0,00 |
| P2 | A | 0,25 | −0,78 | 1,00 | −0,04 | 0,09 | −0,00 | 0,00 |
| P2 | A_res60 | 0,37 | −0,78 | 1,13 | −0,07 | 0,09 | −0,00 | 0,00 |
| P2 | A_res100 (ef. 76) | 0,39 | −0,78 | 1,16 | −0,08 | 0,09 | −0,01 | 0,00 |
| P2 | B | 1,25 | 0,00 | 1,20 | −0,01 | 0,09 | −0,02 | 0,00 |
| P2 | C | 0,60 | −0,78 | 1,36 | −0,08 | 0,10 | −0,01 | 0,00 |
| P2 | C_sem_piso | 0,64 | −0,78 | 1,41 | −0,08 | 0,10 | −0,01 | 0,00 |
| P3_theta05 | A | −0,17 | −0,78 | 0,56 | 0,01 | 0,05 | 0,00 | 0,00 |
| P3_theta05 | A_res60 | −0,11 | −0,78 | 0,64 | −0,03 | 0,06 | 0,00 | 0,00 |
| P3_theta05 | A_res100 (ef. 76) | −0,09 | −0,78 | 0,66 | −0,03 | 0,06 | 0,00 | 0,00 |
| P3_theta05 | B | 0,99 | 0,00 | 0,95 | −0,02 | 0,07 | −0,02 | 0,00 |
| P3_theta05 | C | 0,07 | −0,78 | 0,82 | −0,04 | 0,06 | 0,00 | 0,00 |
| P3_theta05 | C_sem_piso | 0,15 | −0,78 | 0,89 | −0,03 | 0,07 | 0,00 | 0,00 |
| P3_theta025 | A | −0,14 | −0,78 | 0,59 | −0,01 | 0,05 | 0,00 | 0,00 |
| P3_theta025 | A_res60 | −0,09 | −0,78 | 0,68 | −0,04 | 0,06 | 0,00 | 0,00 |
| P3_theta025 | A_res100 (ef. 76) | −0,07 | −0,78 | 0,70 | −0,05 | 0,06 | 0,00 | 0,00 |
| P3_theta025 | B | 1,02 | 0,00 | 0,98 | −0,02 | 0,07 | −0,02 | −0,00 |
| P3_theta025 | C | 0,14 | −0,78 | 0,91 | −0,05 | 0,07 | 0,00 | 0,00 |
| P3_theta025 | C_sem_piso | 0,18 | −0,78 | 0,94 | −0,05 | 0,07 | −0,00 | 0,00 |

Gráficos: `graficos/1_crescimento_anual.png`, `graficos/2_recessao.png`.

## 2. Composição do pacote fiscal

Mesmo valor total (2,7% do PIB) em todos os trimestres. Multiplicadores por item e fontes em `config/recessivo.yaml`; multiplicador efetivo = média ponderada pelo valor de cada item em vigor.

| Item | Canal | Multiplicador | Faixa |
|---|---|---|---|
| Fim de renúncias regressivas (deduções do IRPF, isenções financeiras) | consumo_alta | 0,3 | 0,1–0,6 |
| Revisão de benefícios setoriais a empresas | fbcf_privada | 0,3 | 0,1–0,6 |
| Focalização de subsídios creditícios (grandes tomadores) | fbcf_privada | 0,4 | 0,2–0,7 |
| Teto para verbas acima do teto remuneratório | consumo_alta | 0,3 | 0,1–0,5 |
| Previdência dos militares | consumo_media | 0,5 | 0,3–0,8 |
| Limite para emendas parlamentares | municipal | 0,8 | 0,5–1,2 |
| Custeio administrativo | governo | 0,6 | 0,4–0,9 |
| Nova regra dos pisos de saúde e educação | governo | 0,8 | 0,5–1,2 |
| Investimento público | fbcf_publica | 1,2 | 0,8–2,4 |
| Transferências a famílias de baixa renda | consumo_baixa | 1,0 | 0,7–1,8 |

Multiplicador acumulado efetivo de cada item (medida permanente de 1% do PIB desde o trimestre 1, estratégia A só com esse item contra S, sem choques, λ = 0,7): −Σ Δhiato ÷ Σ medida em 4, 8 e 16 trimestres. "Direto" acumula só o termo do item (calibração: igual a m; teste `test_calibracao_rho_f`); "modelo" inclui a resposta da Selic, do prêmio, do juro longo e do câmbio.

| Especificação | Item | m | Direto 4/8/16 | Modelo 4 | Modelo 8 | Modelo 16 |
|---|---|---|---|---|---|---|
| P1 | Fim de renúncias regressivas (deduções do IRPF, isenções financeiras) | 0,3 | 0,30 / 0,30 / 0,30 | 0,15 | −0,00 | −0,15 |
| P1 | Revisão de benefícios setoriais a empresas | 0,3 | 0,30 / 0,30 / 0,30 | 0,15 | −0,00 | −0,15 |
| P1 | Focalização de subsídios creditícios (grandes tomadores) | 0,4 | 0,40 / 0,40 / 0,40 | 0,23 | 0,05 | −0,11 |
| P1 | Teto para verbas acima do teto remuneratório | 0,3 | 0,30 / 0,30 / 0,30 | 0,14 | −0,03 | −0,18 |
| P1 | Previdência dos militares | 0,5 | 0,50 / 0,50 / 0,50 | 0,32 | 0,14 | −0,04 |
| P1 | Limite para emendas parlamentares | 0,8 | 0,80 / 0,80 / 0,80 | 0,59 | 0,39 | 0,17 |
| P1 | Custeio administrativo | 0,6 | 0,60 / 0,60 / 0,60 | 0,41 | 0,22 | 0,03 |
| P1 | Nova regra dos pisos de saúde e educação | 0,8 | 0,80 / 0,80 / 0,80 | 0,59 | 0,39 | 0,17 |
| P1 | Investimento público | 1,2 | 1,20 / 1,20 / 1,20 | 0,95 | 0,72 | 0,45 |
| P1 | Transferências a famílias de baixa renda | 1,0 | 1,00 / 1,00 / 1,00 | 0,77 | 0,55 | 0,31 |
| P2 | Fim de renúncias regressivas (deduções do IRPF, isenções financeiras) | 0,3 | 0,30 / 0,30 / 0,30 | 0,15 | −0,01 | −0,16 |
| P2 | Revisão de benefícios setoriais a empresas | 0,3 | 0,30 / 0,30 / 0,30 | 0,15 | −0,01 | −0,16 |
| P2 | Focalização de subsídios creditícios (grandes tomadores) | 0,4 | 0,40 / 0,40 / 0,40 | 0,23 | 0,05 | −0,12 |
| P2 | Teto para verbas acima do teto remuneratório | 0,3 | 0,30 / 0,30 / 0,30 | 0,14 | −0,04 | −0,20 |
| P2 | Previdência dos militares | 0,5 | 0,50 / 0,50 / 0,50 | 0,32 | 0,14 | −0,04 |
| P2 | Limite para emendas parlamentares | 0,8 | 0,80 / 0,80 / 0,80 | 0,60 | 0,41 | 0,20 |
| P2 | Custeio administrativo | 0,6 | 0,60 / 0,60 / 0,60 | 0,42 | 0,23 | 0,04 |
| P2 | Nova regra dos pisos de saúde e educação | 0,8 | 0,80 / 0,80 / 0,80 | 0,60 | 0,41 | 0,20 |
| P2 | Investimento público | 1,2 | 1,20 / 1,20 / 1,20 | 0,97 | 0,76 | 0,52 |
| P2 | Transferências a famílias de baixa renda | 1,0 | 1,00 / 1,00 / 1,00 | 0,79 | 0,59 | 0,36 |
| P3_theta05 | Fim de renúncias regressivas (deduções do IRPF, isenções financeiras) | 0,3 | 0,30 / 0,30 / 0,30 | 0,22 | 0,15 | 0,02 |
| P3_theta05 | Revisão de benefícios setoriais a empresas | 0,3 | 0,30 / 0,30 / 0,30 | 0,22 | 0,15 | 0,02 |
| P3_theta05 | Focalização de subsídios creditícios (grandes tomadores) | 0,4 | 0,40 / 0,40 / 0,40 | 0,31 | 0,22 | 0,09 |
| P3_theta05 | Teto para verbas acima do teto remuneratório | 0,3 | 0,30 / 0,30 / 0,30 | 0,21 | 0,13 | 0,01 |
| P3_theta05 | Previdência dos militares | 0,5 | 0,50 / 0,50 / 0,50 | 0,40 | 0,31 | 0,17 |
| P3_theta05 | Limite para emendas parlamentares | 0,8 | 0,80 / 0,80 / 0,80 | 0,67 | 0,57 | 0,41 |
| P3_theta05 | Custeio administrativo | 0,6 | 0,60 / 0,60 / 0,60 | 0,49 | 0,39 | 0,25 |
| P3_theta05 | Nova regra dos pisos de saúde e educação | 0,8 | 0,80 / 0,80 / 0,80 | 0,67 | 0,57 | 0,41 |
| P3_theta05 | Investimento público | 1,2 | 1,20 / 1,20 / 1,20 | 1,04 | 0,91 | 0,73 |
| P3_theta05 | Transferências a famílias de baixa renda | 1,0 | 1,00 / 1,00 / 1,00 | 0,86 | 0,74 | 0,57 |
| P3_theta025 | Fim de renúncias regressivas (deduções do IRPF, isenções financeiras) | 0,3 | 0,30 / 0,30 / 0,30 | 0,21 | 0,12 | 0,01 |
| P3_theta025 | Revisão de benefícios setoriais a empresas | 0,3 | 0,30 / 0,30 / 0,30 | 0,21 | 0,12 | 0,01 |
| P3_theta025 | Focalização de subsídios creditícios (grandes tomadores) | 0,4 | 0,40 / 0,40 / 0,40 | 0,30 | 0,20 | 0,07 |
| P3_theta025 | Teto para verbas acima do teto remuneratório | 0,3 | 0,30 / 0,30 / 0,30 | 0,21 | 0,11 | −0,01 |
| P3_theta025 | Previdência dos militares | 0,5 | 0,50 / 0,50 / 0,50 | 0,39 | 0,29 | 0,15 |
| P3_theta025 | Limite para emendas parlamentares | 0,8 | 0,80 / 0,80 / 0,80 | 0,67 | 0,55 | 0,39 |
| P3_theta025 | Custeio administrativo | 0,6 | 0,60 / 0,60 / 0,60 | 0,48 | 0,37 | 0,23 |
| P3_theta025 | Nova regra dos pisos de saúde e educação | 0,8 | 0,80 / 0,80 / 0,80 | 0,67 | 0,55 | 0,39 |
| P3_theta025 | Investimento público | 1,2 | 1,20 / 1,20 / 1,20 | 1,04 | 0,90 | 0,72 |
| P3_theta025 | Transferências a famílias de baixa renda | 1,0 | 1,00 / 1,00 / 1,00 | 0,85 | 0,72 | 0,55 |

Diferença de produto até a eleição contra S (mediana, trimestres 1–16, λ = 0,7) por composição; entre parênteses, a faixa com multiplicadores baixos e altos; "ciclo" = multiplicadores dependentes do hiato (γ = 0,167):

| Especificação | Estratégia | Composição | Mult. efetivo | Central | (baixo; alto) | Com ciclo |
|---|---|---|---|---|---|---|
| P1 | A | pacote_base | 0,51 | 0,82 | (1,95; −0,72) | 0,60 |
| P1 | A | pacote_qualidade | 0,34 | 1,40 | (2,39; 0,06) | 1,26 |
| P1 | A | pacote_linear | 0,87 | −1,07 | (0,44; −4,32) | −1,97 |
| P1 | C | pacote_base | 0,51 | 1,79 | (3,05; −0,22) | 1,28 |
| P1 | C | pacote_qualidade | 0,34 | 2,47 | (3,55; 0,90) | 2,24 |
| P1 | C | pacote_linear | 0,87 | −0,63 | (1,33; −6,86) | −4,01 |
| P1 | C_sem_piso | pacote_base | 0,51 | 2,00 | (3,17; 0,46) | 1,74 |
| P1 | C_sem_piso | pacote_qualidade | 0,34 | 2,61 | (3,63; 1,24) | 2,43 |
| P1 | C_sem_piso | pacote_linear | 0,87 | 0,09 | (1,60; −3,36) | −0,58 |
| P2 | A | pacote_base | 0,51 | 1,03 | (2,32; −0,67) | 0,55 |
| P2 | A | pacote_qualidade | 0,34 | 1,69 | (2,82; 0,18) | 1,38 |
| P2 | A | pacote_linear | 0,87 | −1,05 | (0,60; −4,57) | −2,41 |
| P2 | C | pacote_base | 0,51 | 2,55 | (3,88; 0,63) | 2,13 |
| P2 | C | pacote_qualidade | 0,34 | 3,25 | (4,40; 1,68) | 2,99 |
| P2 | C | pacote_linear | 0,87 | 0,22 | (2,09; −4,39) | −1,55 |
| P2 | C_sem_piso | pacote_base | 0,51 | 2,60 | (3,92; 0,86) | 2,23 |
| P2 | C_sem_piso | pacote_qualidade | 0,34 | 3,29 | (4,44; 1,74) | 3,06 |
| P2 | C_sem_piso | pacote_linear | 0,87 | 0,46 | (2,15; −3,22) | −0,61 |
| P3_theta05 | A | pacote_base | 0,51 | −0,65 | (0,61; −2,31) | −1,15 |
| P3_theta05 | A | pacote_qualidade | 0,34 | 0,04 | (1,13; −1,44) | −0,28 |
| P3_theta05 | A | pacote_linear | 0,87 | −2,72 | (−1,11; −6,15) | −4,15 |
| P3_theta05 | C | pacote_base | 0,51 | 0,29 | (1,56; −1,52) | −0,21 |
| P3_theta05 | C | pacote_qualidade | 0,34 | 0,97 | (2,08; −0,55) | 0,69 |
| P3_theta05 | C | pacote_linear | 0,87 | −1,92 | (−0,16; −6,10) | −3,53 |
| P3_theta05 | C_sem_piso | pacote_base | 0,51 | 0,61 | (1,88; −1,07) | 0,19 |
| P3_theta05 | C_sem_piso | pacote_qualidade | 0,34 | 1,30 | (2,41; −0,20) | 1,03 |
| P3_theta05 | C_sem_piso | pacote_linear | 0,87 | −1,50 | (0,13; −5,03) | −2,70 |
| P3_theta025 | A | pacote_base | 0,51 | −0,55 | (0,72; −2,22) | −1,05 |
| P3_theta025 | A | pacote_qualidade | 0,34 | 0,14 | (1,24; −1,35) | −0,19 |
| P3_theta025 | A | pacote_linear | 0,87 | −2,65 | (−1,03; −6,10) | −4,07 |
| P3_theta025 | C | pacote_base | 0,51 | 0,62 | (1,92; −1,20) | 0,13 |
| P3_theta025 | C | pacote_qualidade | 0,34 | 1,33 | (2,45; −0,21) | 1,04 |
| P3_theta025 | C | pacote_linear | 0,87 | −1,63 | (0,14; −5,83) | −3,22 |
| P3_theta025 | C_sem_piso | pacote_base | 0,51 | 0,73 | (2,02; −0,96) | 0,32 |
| P3_theta025 | C_sem_piso | pacote_qualidade | 0,34 | 1,43 | (2,55; −0,07) | 1,17 |
| P3_theta025 | C_sem_piso | pacote_linear | 0,87 | −1,40 | (0,25; −4,95) | −2,59 |

Pergunta 2: produto com pacote_qualidade − produto com pacote_linear (positivo = a composição de qualidade preserva mais produto), bootstrap pareado, λ = 0,7:

| Especificação | Estratégia | 1–8 | 1–16 | 1–40 | 1–16, mult. baixos | 1–16, mult. altos | 1–16, ciclo |
|---|---|---|---|---|---|---|---|
| P1 | A | 0,86 [0,86; 0,86] * | 2,47 [2,47; 2,47] * | 6,80 [6,80; 6,81] * | 1,95 [1,95; 1,95] * | 4,38 [4,38; 4,38] * | 3,27 [3,24; 3,30] * |
| P1 | C | 1,11 [1,11; 1,11] * | 3,14 [3,13; 3,14] * | 10,31 [10,26; 10,35] * | 2,25 [2,24; 2,25] * | 7,75 [7,74; 7,76] * | 6,19 [6,14; 6,23] * |
| P1 | C_sem_piso | 0,90 [0,90; 0,90] * | 2,51 [2,51; 2,51] * | 6,84 [6,83; 6,84] * | 2,02 [2,02; 2,02] * | 4,59 [4,58; 4,59] * | 3,08 [3,05; 3,12] * |
| P2 | A | 0,92 [0,92; 0,92] * | 2,74 [2,74; 2,74] * | 8,36 [8,36; 8,36] * | 2,22 [2,21; 2,22] * | 4,74 [4,74; 4,75] * | 3,81 [3,78; 3,85] * |
| P2 | C | 1,03 [1,03; 1,03] * | 3,05 [3,04; 3,05] * | 9,69 [9,67; 9,71] * | 2,33 [2,32; 2,33] * | 6,10 [6,09; 6,10] * | 4,52 [4,48; 4,55] * |
| P2 | C_sem_piso | 0,96 [0,96; 0,96] * | 2,83 [2,83; 2,83] * | 8,51 [8,51; 8,52] * | 2,29 [2,29; 2,29] * | 4,96 [4,96; 4,96] * | 3,75 [3,71; 3,78] * |
| P3_theta05 | A | 0,94 [0,94; 0,94] * | 2,76 [2,76; 2,76] * | 8,71 [8,70; 8,72] * | 2,25 [2,25; 2,25] * | 4,71 [4,71; 4,71] * | 3,87 [3,83; 3,90] * |
| P3_theta05 | C | 1,01 [1,01; 1,01] * | 2,89 [2,88; 2,89] * | 9,63 [9,63; 9,64] * | 2,23 [2,23; 2,24] * | 5,55 [5,55; 5,56] * | 4,25 [4,22; 4,28] * |
| P3_theta05 | C_sem_piso | 0,96 [0,96; 0,96] * | 2,79 [2,79; 2,79] * | 8,81 [8,80; 8,81] * | 2,27 [2,27; 2,27] * | 4,83 [4,83; 4,83] * | 3,78 [3,75; 3,81] * |
| P3_theta025 | A | 0,95 [0,95; 0,95] * | 2,78 [2,78; 2,79] * | 8,80 [8,80; 8,80] * | 2,27 [2,27; 2,27] * | 4,75 [4,75; 4,75] * | 3,89 [3,86; 3,93] * |
| P3_theta025 | C | 1,01 [1,01; 1,01] * | 2,96 [2,96; 2,96] * | 9,87 [9,86; 9,87] * | 2,31 [2,31; 2,31] * | 5,62 [5,61; 5,62] * | 4,27 [4,24; 4,31] * |
| P3_theta025 | C_sem_piso | 0,97 [0,97; 0,97] * | 2,82 [2,82; 2,83] * | 8,87 [8,87; 8,87] * | 2,30 [2,30; 2,30] * | 4,88 [4,87; 4,88] * | 3,81 [3,77; 3,84] * |

A composição também afeta a credibilidade (um pacote de receita e de itens de difícil aprovação pode ter λ_fiscal menor); isso não é modelado: as tabelas mostram o produto para cada λ, e a comparação entre composições deve ser feita também em λ diferentes.

Gráfico: `graficos/4_composicao_pacote.png`.

## 3. Setores e emprego

A diferença de hiato contra S é decomposta pelos componentes da equação de demanda (juro real longo → metade consumo, metade FBCF; itens do pacote → canal de cada item; câmbio real → exportações; CAPEX → construção e máquinas; choques e restante → absorção doméstica), convertida em demanda final pelo PIB de 2015, distribuída pela Leontief tipo I da MIP 2015 (67 atividades) e reconciliada com o PIB do modelo macro trimestre a trimestre: o resíduo entre o PIB do modelo e o VA da matriz entra como demanda de absorção doméstica (reconciliação aditiva; a escala proporcional fica instável quando o efeito direto do pacote e o do juro, de sinais opostos, se cancelam). Emprego = variação % da produção de cada atividade × ocupados de 2025 (PNAD).

Valor adicionado por grupo da TRU (% do VA do setor, média dos trimestres 1–16, λ = 0,7, P1):

| Grupo | A | A_res60 | A_res100 (ef. 76) | B | C | C_sem_piso |
|---|---|---|---|---|---|---|
| Agropecuária | 0,24 | 0,25 | 0,25 | 0,68 | 0,31 | 0,38 |
| Indústrias extrativas | 0,29 | 0,29 | 0,29 | 0,79 | 0,35 | 0,43 |
| Indústrias de transformação | 0,62 | 0,72 | 0,75 | 1,23 | 0,83 | 0,95 |
| Eletricidade e gás, água, esgoto e resíduos | 0,28 | 0,37 | 0,40 | 0,91 | 0,47 | 0,55 |
| Construção | 1,51 | 1,92 | 2,02 | 3,44 | 2,25 | 2,56 |
| Comércio | 0,57 | 0,70 | 0,73 | 1,17 | 0,82 | 0,93 |
| Transporte, armazenagem e correio | 0,41 | 0,49 | 0,51 | 0,99 | 0,59 | 0,68 |
| Informação e comunicação | 0,75 | 0,92 | 0,96 | 1,44 | 1,07 | 1,21 |
| Atividades financeiras e de seguros | 0,27 | 0,36 | 0,39 | 0,90 | 0,46 | 0,54 |
| Atividades imobiliárias | 0,45 | 0,57 | 0,60 | 0,96 | 0,67 | 0,76 |
| Outras atividades de serviços | 0,26 | 0,34 | 0,37 | 0,85 | 0,43 | 0,51 |
| Administração, defesa, saúde e educação públicas | −1,26 | −1,25 | −1,24 | 0,14 | −1,23 | −1,21 |

Ocupações contra S (mil; média dos trimestres de cada janela; λ = 0,7, P1). Formais pela fração formal de cada atividade (Censo 2022 calibrado à PNAD de 2025); induzido = tipo II − tipo I sem reconciliação (propensão a consumir 0,9, impostos 15%; sensibilidade em data/processed/mip/sensibilidade_tipo2.csv):

| Estratégia | Janela | Total | Formais | Informais | Massa salarial (R$ bi/ano) | Induzido tipo II | Desocupação (p.p.) [IC] |
|---|---|---|---|---|---|---|---|
| A | 1-8 | 209 | 97 | 112 | 5,9 | 2 | −0,03 [−0,07; −0,00] |
| A | 1-16 | 294 | 120 | 175 | 7,3 | −31 | −0,05 [−0,09; −0,00] |
| A_res60 | 1-8 | 266 | 128 | 138 | 8,1 | 24 | −0,05 [−0,09; −0,00] |
| A_res60 | 1-16 | 406 | 183 | 223 | 11,6 | 11 | −0,07 [−0,13; −0,01] |
| A_res100 (ef. 76) | 1-8 | 282 | 137 | 145 | 8,7 | 29 | −0,05 [−0,09; −0,00] |
| A_res100 (ef. 76) | 1-16 | 434 | 198 | 235 | 12,7 | 22 | −0,07 [−0,14; −0,01] |
| B | 1-8 | 674 | 381 | 293 | 26,2 | 256 | −0,14 [−0,27; −0,01] |
| B | 1-16 | 1086 | 616 | 470 | 42,3 | 415 | −0,23 [−0,44; −0,02] |
| C | 1-8 | 504 | 263 | 241 | 17,4 | 114 | −0,10 [−0,18; −0,01] |
| C | 1-16 | 515 | 245 | 270 | 15,9 | 53 | −0,09 [−0,18; −0,01] |
| C_sem_piso | 1-8 | 535 | 281 | 254 | 18,6 | 126 | −0,10 [−0,20; −0,01] |
| C_sem_piso | 1-16 | 618 | 304 | 315 | 19,9 | 93 | −0,11 [−0,22; −0,01] |

Ocupações totais contra S por especificação (mil, trimestres 1–16, λ = 0,7):

| Especificação | A | A_res60 | A_res100 (ef. 76) | B | C | C_sem_piso |
|---|---|---|---|---|---|---|
| P1 | 294 | 406 | 434 | 1086 | 515 | 618 |
| P2 | 352 | 479 | 510 | 1361 | 728 | 778 |
| P3_theta05 | −108 | −40 | −23 | 1071 | 149 | 236 |
| P3_theta025 | −81 | −13 | 4 | 1108 | 236 | 272 |

Diagnósticos (λ = 0,7, trimestres 1–16): fator de escala (VA do modelo macro ÷ VA da matriz, somando os componentes em módulo; fora de 0,7–1,3 indicaria incoerência entre os multiplicadores do bloco fiscal e os da matriz; o fator com sinal, instável quando os componentes se cancelam, está no CSV), efeito de volta sobre a balança comercial (exportações pelo canal do câmbio real; importações pelo conteúdo importado da demanda final e dos insumos) e retorno fiscal da massa salarial formal adicional (contribuições previdenciárias/FGTS pela razão da TRU 2015 e IRPF 2026 pela alíquota efetiva no rendimento médio do setor) contra a receita cíclica do modelo macro (rec_base × ε_rec × Δhiato). O retorno setorial não é somado ao primário: é uma decomposição parcial da receita cíclica.

| Especificação | Estratégia | Fator de escala | Exportações (% PIB) | Importações (% PIB) | Contribuições (R$ bi) | IRPF (R$ bi) | Receita cíclica macro (R$ bi) |
|---|---|---|---|---|---|---|---|
| P1 | A | 1,04 | −0,044 | 0,097 | 0,8 | −0,2 | 5,0 |
| P1 | A_res60 | 1,04 | −0,072 | 0,116 | 1,4 | −0,2 | 7,6 |
| P1 | A_res100 (ef. 76) | 1,04 | −0,079 | 0,121 | 1,6 | −0,2 | 8,2 |
| P1 | B | 1,06 | −0,019 | 0,190 | 5,7 | 0,1 | 25,3 |
| P1 | C | 1,04 | −0,080 | 0,135 | 2,0 | −0,2 | 10,1 |
| P1 | C_sem_piso | 1,04 | −0,079 | 0,153 | 2,6 | −0,2 | 12,5 |
| P2 | A | 1,04 | −0,043 | 0,107 | 1,1 | −0,2 | 6,4 |
| P2 | A_res60 | 1,04 | −0,070 | 0,129 | 1,8 | −0,2 | 9,3 |
| P2 | A_res100 (ef. 76) | 1,04 | −0,077 | 0,134 | 2,0 | −0,2 | 10,0 |
| P2 | B | 1,06 | −0,015 | 0,239 | 7,2 | 0,1 | 31,7 |
| P2 | C | 1,04 | −0,079 | 0,172 | 3,1 | −0,2 | 15,1 |
| P2 | C_sem_piso | 1,04 | −0,076 | 0,181 | 3,4 | −0,2 | 16,2 |
| P3_theta05 | A | 1,03 | 0,008 | 0,027 | −1,3 | −0,3 | −4,2 |
| P3_theta05 | A_res60 | 1,03 | −0,026 | 0,039 | −0,9 | −0,3 | −2,7 |
| P3_theta05 | A_res100 (ef. 76) | 1,03 | −0,033 | 0,041 | −0,8 | −0,2 | −2,3 |
| P3_theta05 | B | 1,06 | −0,016 | 0,187 | 5,7 | 0,1 | 25,0 |
| P3_theta05 | C | 1,04 | −0,040 | 0,071 | 0,1 | −0,2 | 1,7 |
| P3_theta05 | C_sem_piso | 1,04 | −0,028 | 0,087 | 0,5 | −0,2 | 3,7 |
| P3_theta025 | A | 1,03 | −0,011 | 0,032 | −1,1 | −0,3 | −3,6 |
| P3_theta025 | A_res60 | 1,03 | −0,044 | 0,043 | −0,8 | −0,2 | −2,2 |
| P3_theta025 | A_res100 (ef. 76) | 1,03 | −0,051 | 0,046 | −0,7 | −0,2 | −1,8 |
| P3_theta025 | B | 1,06 | −0,018 | 0,194 | 5,9 | 0,1 | 25,8 |
| P3_theta025 | C | 1,04 | −0,052 | 0,086 | 0,5 | −0,2 | 3,7 |
| P3_theta025 | C_sem_piso | 1,04 | −0,048 | 0,093 | 0,7 | −0,2 | 4,5 |

Fator de escala médio (todas as estratégias, especificações, λ e janelas): 1,04 (mín. 1,01, máx. 1,07). Fora de 0,7–1,3 em 0 de 288 casos. O fator reflete o vazamento da demanda final para importações e impostos na matriz (o VA por unidade de demanda final é menor que 1), não uma divergência entre os multiplicadores.

Efeito sobre os setores mais expostos ao câmbio (VA pelo canal das exportações, R$ milhões de 2015, trimestres 1–16, λ = 0,7, P1):

| Grupo | A | A_res60 | A_res100 (ef. 76) | B | C | C_sem_piso |
|---|---|---|---|---|---|---|
| Agropecuária | −336 | −550 | −600 | −143 | −607 | −604 |
| Indústrias extrativas | −186 | −305 | −333 | −79 | −337 | −335 |
| Indústrias de transformação | −533 | −871 | −950 | −227 | −961 | −956 |

Gráficos: `graficos/5_emprego_setores.png`, `graficos/6_mapa_va_setorial.png`.

## 4. Robustez × custo recessivo

λ\*₇₀ pela dívida líquida (banda e teto; 1,01 = não atinge 70%) e diferença de produto até a eleição contra S (mediana, λ = 0,7):

| Especificação | Estratégia | λ\*₇₀ banda | λ\*₇₀ teto | Produto 1–16 |
|---|---|---|---|---|
| P1 | S | não atinge | não atinge | 0,00 |
| P1 | A | não atinge | 0,93 | 0,82 |
| P1 | A_res60 | 1,00 | 0,61 | 1,21 |
| P1 | A_res100 (ef. 76) | 0,97 | 0,58 | 1,31 |
| P1 | B | não atinge | não atinge | 3,94 |
| P1 | C | não atinge | não atinge | 1,79 |
| P1 | C_sem_piso | 0,90 | 0,52 | 2,00 |
| P2 | S | não atinge | não atinge | 0,00 |
| P2 | A | não atinge | não atinge | 1,03 |
| P2 | A_res60 | não atinge | 0,78 | 1,48 |
| P2 | A_res100 (ef. 76) | 0,97 | 0,71 | 1,59 |
| P2 | B | não atinge | não atinge | 5,03 |
| P2 | C | não atinge | não atinge | 2,55 |
| P2 | C_sem_piso | 0,90 | 0,64 | 2,60 |
| P3_theta05 | S | não atinge | não atinge | 0,00 |
| P3_theta05 | A | não atinge | 0,67 | −0,65 |
| P3_theta05 | A_res60 | 0,91 | 0,65 | −0,41 |
| P3_theta05 | A_res100 (ef. 76) | 0,90 | 0,64 | −0,35 |
| P3_theta05 | B | não atinge | não atinge | 3,92 |
| P3_theta05 | C | 0,91 | 0,90 | 0,29 |
| P3_theta05 | C_sem_piso | 0,89 | 0,62 | 0,61 |
| P3_theta025 | S | não atinge | não atinge | 0,00 |
| P3_theta025 | A | não atinge | 0,54 | −0,55 |
| P3_theta025 | A_res60 | 0,83 | 0,52 | −0,32 |
| P3_theta025 | A_res100 (ef. 76) | 0,82 | 0,51 | −0,26 |
| P3_theta025 | B | não atinge | não atinge | 4,05 |
| P3_theta025 | C | 0,88 | 0,88 | 0,62 |
| P3_theta025 | C_sem_piso | 0,80 | 0,49 | 0,73 |

Gráfico: `graficos/3_fronteira_robustez_custo.png`.

## 5. Validação no ajuste de 2015–2016

Episódio 2015T1–2016T4 (t0 = 2014T4) com Selic, primário e câmbio observados. O impulso fiscal vem do primário estrutural observado (primário − rec_base·ε_rec·hiato observado), em nível, com multiplicador 0,5; λ (e θ em P3) é escolhido pelo ajuste de inflação e NTN-B 10 anos, como nos demais episódios. Crescimento anual ≈ crescimento potencial + variação da média anual do hiato. O episódio fica fora da escolha da especificação de referência da rodada principal.

| Especificação | Caso | λ | θ | Potencial | PIB 2015 simulado | PIB 2016 simulado | Hiato 2016T4 sim. / obs. |
|---|---|---|---|---|---|---|---|
| P1 | melhor ajuste | 0,50 | — | 1,92 | 0,5 | 0,9 | −0,4 / −3,1 |
| P1 | λ = 0,1 | 0,10 | — | 1,92 | 1,4 | 5,9 | 9,1 / −3,1 |
| P1 | λ = 0,5 | 0,50 | — | 1,92 | 0,5 | 0,9 | −0,4 / −3,1 |
| P1 | λ = 0,9 | 0,90 | — | 1,92 | −0,2 | −1,2 | −3,9 / −3,1 |
| P2 | melhor ajuste | 0,50 | — | 1,92 | 0,5 | 0,7 | −0,6 / −3,1 |
| P2 | λ = 0,1 | 0,10 | — | 1,92 | 1,3 | 5,3 | 7,9 / −3,1 |
| P2 | λ = 0,5 | 0,50 | — | 1,92 | 0,5 | 0,7 | −0,6 / −3,1 |
| P2 | λ = 0,9 | 0,90 | — | 1,92 | −0,2 | −1,2 | −4,0 / −3,1 |
| P3 | melhor ajuste | 0,40 | 0,00 | 1,92 | 0,8 | 1,0 | −0,1 / −3,1 |
| P3 | λ = 0,1 | 0,10 | 0,00 | 1,92 | 1,4 | — | — / −3,1 |
| P3 | λ = 0,5 | 0,50 | 0,00 | 1,92 | 0,6 | 0,3 | −1,4 / −3,1 |
| P3 | λ = 0,9 | 0,90 | 0,00 | 1,92 | 0,1 | −0,8 | −3,3 / −3,1 |

Observado: PIB −3,5% em 2015 e −3,3% em 2016 (IBGE; pela média anual do índice dessazonalizado do painel, −3,5% e −3,5%).

Contribuição de cada canal ao crescimento anual simulado (p.p., λ de melhor ajuste):

| Especificação | Canal | 2015 | 2016 |
|---|---|---|---|
| P1 | fiscal (primário estrutural) | −0,10 | 0,57 |
| P1 | juro real longo | −0,81 | −0,37 |
| P1 | câmbio real | 0,60 | −0,28 |
| P1 | fiscal fora do item | 0,00 | 0,00 |
| P1 | CAPEX | 0,00 | 0,00 |
| P1 | hiato inicial (persistência) | −1,07 | −0,95 |
| P1 | crescimento potencial | 1,92 | 1,92 |
| P2 | fiscal (primário estrutural) | −0,10 | 0,57 |
| P2 | juro real longo | −0,84 | −0,55 |
| P2 | câmbio real | 0,60 | −0,27 |
| P2 | fiscal fora do item | 0,00 | 0,00 |
| P2 | CAPEX | 0,00 | 0,00 |
| P2 | hiato inicial (persistência) | −1,07 | −0,95 |
| P2 | crescimento potencial | 1,92 | 1,92 |
| P3 | fiscal (primário estrutural) | −0,10 | 0,57 |
| P3 | juro real longo | −0,61 | −0,32 |
| P3 | câmbio real | 0,61 | −0,23 |
| P3 | fiscal fora do item | 0,00 | 0,00 |
| P3 | CAPEX | 0,00 | 0,00 |
| P3 | hiato inicial (persistência) | −1,07 | −0,95 |
| P3 | crescimento potencial | 1,92 | 1,92 |

Fatores não modelados: queda dos preços das commodities (IC-Br em US$ −40% de meados de 2014 ao início de 2016); crise política e processo de impeachment (2015–2016); Operação Lava Jato: paralisação de investimentos da Petrobras e das construtoras; realinhamento de preços administrados (energia e combustíveis) em 2015; aperto de crédito dos bancos públicos.

## 6. Sensibilidade do canal de credibilidade em S

S e A com a sensibilidade do prêmio à dívida (p1, p2 e p2 de P3) pela metade e a2 nos limites da faixa (0,05 e 0,30; o valor estimado é 0,182). Diferença de produto de A contra S até a eleição (mediana; IC de 95% da média) e fração das trajetórias em que A fica abaixo de S. **Negrito** = A recessivo contra S (mediana negativa).

| Especificação | Combinação | λ = 0,3 | λ = 0,5 | λ = 0,7 | λ = 0,9 |
|---|---|---|---|---|---|
| P1 | base | **−0,24 [−0,28; −0,27], 100%** | 0,27 [0,25; 0,26], 2% | 0,82 [0,78; 0,80], 0% | 1,36 [1,33; 1,35], 0% |
| P1 | p1_p2_metade | **−1,42 [−1,45; −1,44], 100%** | **−1,19 [−1,22; −1,21], 100%** | **−0,91 [−0,93; −0,92], 100%** | **−0,58 [−0,61; −0,59], 100%** |
| P1 | a2_005 | **−1,95 [−1,97; −1,96], 100%** | **−1,71 [−1,72; −1,72], 100%** | **−1,48 [−1,49; −1,48], 100%** | **−1,24 [−1,25; −1,24], 100%** |
| P1 | a2_030 | 1,02 [0,94; 0,96], 2% | 1,50 [1,45; 1,47], 0% | 1,94 [1,88; 1,92], 0% | 2,27 [2,20; 2,25], 0% |
| P1 | p_metade_a2_005 | **−2,39 [−2,41; −2,40], 100%** | **−2,29 [−2,30; −2,30], 100%** | **−2,18 [−2,18; −2,18], 100%** | **−2,04 [−2,05; −2,04], 100%** |
| P1 | p_metade_a2_030 | **−0,46 [−0,53; −0,50], 100%** | **−0,09 [−0,13; −0,12], 90%** | 0,33 [0,30; 0,32], 6% | 0,80 [0,76; 0,79], 0% |
| P2 | base | **−0,19 [−0,22; −0,21], 100%** | 0,41 [0,38; 0,39], 0% | 1,03 [1,00; 1,01], 0% | 1,67 [1,64; 1,66], 0% |
| P2 | p1_p2_metade | **−1,51 [−1,53; −1,52], 100%** | **−1,27 [−1,29; −1,28], 100%** | **−0,98 [−1,00; −1,00], 100%** | **−0,65 [−0,68; −0,67], 100%** |
| P2 | a2_005 | **−2,02 [−2,03; −2,03], 100%** | **−1,78 [−1,79; −1,79], 100%** | **−1,55 [−1,55; −1,55], 100%** | **−1,31 [−1,32; −1,31], 100%** |
| P2 | a2_030 | 1,28 [1,24; 1,26], 0% | 2,03 [1,99; 2,00], 0% | 2,84 [2,78; 2,80], 0% | 3,69 [3,64; 3,67], 0% |
| P2 | p_metade_a2_005 | **−2,48 [−2,49; −2,49], 100%** | **−2,38 [−2,39; −2,39], 100%** | **−2,27 [−2,28; −2,28], 100%** | **−2,15 [−2,16; −2,16], 100%** |
| P2 | p_metade_a2_030 | **−0,74 [−0,78; −0,77], 100%** | **−0,44 [−0,48; −0,46], 100%** | **−0,05 [−0,10; −0,08], 75%** | 0,40 [0,36; 0,38], 3% |
| P3_theta05 | base | **−1,79 [−2,07; −1,95], 100%** | **−1,27 [−1,35; −1,32], 100%** | **−0,65 [−0,66; −0,65], 100%** | 0,03 [−0,00; 0,01], 38% |
| P3_theta05 | p1_p2_metade | **−2,43 [−2,66; −2,53], 100%** | **−2,12 [−2,20; −2,17], 100%** | **−1,77 [−1,78; −1,77], 100%** | **−1,35 [−1,37; −1,37], 100%** |
| P3_theta05 | a2_005 | **−2,69 [−2,75; −2,69], 100%** | **−2,25 [−2,29; −2,27], 100%** | **−2,07 [−2,07; −2,07], 100%** | **−1,91 [−1,92; −1,92], 100%** |
| P3_theta05 | a2_030 | **−1,01 [−1,44; −1,22], 96%** | **−0,52 [−0,59; −0,56], 100%** | 0,34 [0,31; 0,33], 2% | 1,41 [1,36; 1,38], 0% |
| P3_theta05 | p_metade_a2_005 | **−2,88 [−2,94; −2,88], 100%** | **−2,55 [−2,59; −2,57], 100%** | **−2,47 [−2,47; −2,47], 100%** | **−2,40 [−2,41; −2,40], 100%** |
| P3_theta05 | p_metade_a2_030 | **−1,73 [−2,13; −1,95], 100%** | **−1,75 [−1,82; −1,79], 100%** | **−1,29 [−1,31; −1,29], 100%** | **−0,60 [−0,63; −0,62], 100%** |
| P3_theta025 | base | **−1,19 [−1,36; −1,31], 100%** | **−1,05 [−1,06; −1,06], 100%** | **−0,55 [−0,57; −0,56], 100%** | 0,03 [0,00; 0,01], 35% |
| P3_theta025 | p1_p2_metade | **−1,76 [−1,95; −1,90], 100%** | **−1,92 [−1,93; −1,92], 100%** | **−1,69 [−1,70; −1,69], 100%** | **−1,35 [−1,37; −1,36], 100%** |
| P3_theta025 | a2_005 | **−2,23 [−2,33; −2,30], 100%** | **−2,20 [−2,20; −2,20], 100%** | **−2,08 [−2,09; −2,09], 100%** | **−1,92 [−1,93; −1,92], 100%** |
| P3_theta025 | a2_030 | **−0,37 [−0,47; −0,42], 99%** | **−0,22 [−0,24; −0,23], 100%** | 0,53 [0,50; 0,51], 0% | 1,43 [1,38; 1,40], 0% |
| P3_theta025 | p_metade_a2_005 | **−2,43 [−2,53; −2,50], 100%** | **−2,50 [−2,51; −2,50], 100%** | **−2,49 [−2,49; −2,49], 100%** | **−2,41 [−2,42; −2,41], 100%** |
| P3_theta025 | p_metade_a2_030 | **−1,21 [−1,34; −1,29], 100%** | **−1,49 [−1,51; −1,50], 100%** | **−1,12 [−1,14; −1,13], 100%** | **−0,58 [−0,61; −0,60], 100%** |

Combinações em que A é recessivo contra S (mediana negativa), por janela: 1-16: P1, a2_005, λ = 0,3; 1-16: P1, a2_005, λ = 0,5; 1-16: P1, a2_005, λ = 0,7; 1-16: P1, a2_005, λ = 0,9; 1-16: P1, base, λ = 0,3; 1-16: P1, p1_p2_metade, λ = 0,3; 1-16: P1, p1_p2_metade, λ = 0,5; 1-16: P1, p1_p2_metade, λ = 0,7; 1-16: P1, p1_p2_metade, λ = 0,9; 1-16: P1, p_metade_a2_005, λ = 0,3; 1-16: P1, p_metade_a2_005, λ = 0,5; 1-16: P1, p_metade_a2_005, λ = 0,7; 1-16: P1, p_metade_a2_005, λ = 0,9; 1-16: P1, p_metade_a2_030, λ = 0,3; 1-16: P1, p_metade_a2_030, λ = 0,5; 1-16: P2, a2_005, λ = 0,3; 1-16: P2, a2_005, λ = 0,5; 1-16: P2, a2_005, λ = 0,7; 1-16: P2, a2_005, λ = 0,9; 1-16: P2, base, λ = 0,3; 1-16: P2, p1_p2_metade, λ = 0,3; 1-16: P2, p1_p2_metade, λ = 0,5; 1-16: P2, p1_p2_metade, λ = 0,7; 1-16: P2, p1_p2_metade, λ = 0,9; 1-16: P2, p_metade_a2_005, λ = 0,3; 1-16: P2, p_metade_a2_005, λ = 0,5; 1-16: P2, p_metade_a2_005, λ = 0,7; 1-16: P2, p_metade_a2_005, λ = 0,9; 1-16: P2, p_metade_a2_030, λ = 0,3; 1-16: P2, p_metade_a2_030, λ = 0,5; 1-16: P2, p_metade_a2_030, λ = 0,7; 1-16: P3_theta025, a2_005, λ = 0,3; 1-16: P3_theta025, a2_005, λ = 0,5; 1-16: P3_theta025, a2_005, λ = 0,7; 1-16: P3_theta025, a2_005, λ = 0,9; 1-16: P3_theta025, a2_030, λ = 0,3; 1-16: P3_theta025, a2_030, λ = 0,5; 1-16: P3_theta025, base, λ = 0,3; 1-16: P3_theta025, base, λ = 0,5; 1-16: P3_theta025, base, λ = 0,7; 1-16: P3_theta025, p1_p2_metade, λ = 0,3; 1-16: P3_theta025, p1_p2_metade, λ = 0,5; 1-16: P3_theta025, p1_p2_metade, λ = 0,7; 1-16: P3_theta025, p1_p2_metade, λ = 0,9; 1-16: P3_theta025, p_metade_a2_005, λ = 0,3; 1-16: P3_theta025, p_metade_a2_005, λ = 0,5; 1-16: P3_theta025, p_metade_a2_005, λ = 0,7; 1-16: P3_theta025, p_metade_a2_005, λ = 0,9; 1-16: P3_theta025, p_metade_a2_030, λ = 0,3; 1-16: P3_theta025, p_metade_a2_030, λ = 0,5; 1-16: P3_theta025, p_metade_a2_030, λ = 0,7; 1-16: P3_theta025, p_metade_a2_030, λ = 0,9; 1-16: P3_theta05, a2_005, λ = 0,3; 1-16: P3_theta05, a2_005, λ = 0,5; 1-16: P3_theta05, a2_005, λ = 0,7; 1-16: P3_theta05, a2_005, λ = 0,9; 1-16: P3_theta05, a2_030, λ = 0,3; 1-16: P3_theta05, a2_030, λ = 0,5; 1-16: P3_theta05, base, λ = 0,3; 1-16: P3_theta05, base, λ = 0,5; 1-16: P3_theta05, base, λ = 0,7; 1-16: P3_theta05, p1_p2_metade, λ = 0,3; 1-16: P3_theta05, p1_p2_metade, λ = 0,5; 1-16: P3_theta05, p1_p2_metade, λ = 0,7; 1-16: P3_theta05, p1_p2_metade, λ = 0,9; 1-16: P3_theta05, p_metade_a2_005, λ = 0,3; 1-16: P3_theta05, p_metade_a2_005, λ = 0,5; 1-16: P3_theta05, p_metade_a2_005, λ = 0,7; 1-16: P3_theta05, p_metade_a2_005, λ = 0,9; 1-16: P3_theta05, p_metade_a2_030, λ = 0,3; 1-16: P3_theta05, p_metade_a2_030, λ = 0,5; 1-16: P3_theta05, p_metade_a2_030, λ = 0,7; 1-16: P3_theta05, p_metade_a2_030, λ = 0,9; 1-40: P1, a2_005, λ = 0,3; 1-40: P1, a2_005, λ = 0,5; 1-40: P1, a2_005, λ = 0,7; 1-40: P1, a2_005, λ = 0,9; 1-40: P1, p1_p2_metade, λ = 0,3; 1-40: P1, p1_p2_metade, λ = 0,5; 1-40: P1, p1_p2_metade, λ = 0,7; 1-40: P1, p1_p2_metade, λ = 0,9; 1-40: P1, p_metade_a2_005, λ = 0,3; 1-40: P1, p_metade_a2_005, λ = 0,5; 1-40: P1, p_metade_a2_005, λ = 0,7; 1-40: P1, p_metade_a2_005, λ = 0,9; 1-40: P1, p_metade_a2_030, λ = 0,5; 1-40: P1, p_metade_a2_030, λ = 0,7; 1-40: P2, a2_005, λ = 0,3; 1-40: P2, a2_005, λ = 0,5; 1-40: P2, a2_005, λ = 0,7; 1-40: P2, a2_005, λ = 0,9; 1-40: P2, p1_p2_metade, λ = 0,3; 1-40: P2, p1_p2_metade, λ = 0,5; 1-40: P2, p1_p2_metade, λ = 0,7; 1-40: P2, p1_p2_metade, λ = 0,9; 1-40: P2, p_metade_a2_005, λ = 0,3; 1-40: P2, p_metade_a2_005, λ = 0,5; 1-40: P2, p_metade_a2_005, λ = 0,7; 1-40: P2, p_metade_a2_005, λ = 0,9; 1-40: P2, p_metade_a2_030, λ = 0,5; 1-40: P2, p_metade_a2_030, λ = 0,7; 1-40: P2, p_metade_a2_030, λ = 0,9; 1-40: P3_theta025, a2_005, λ = 0,3; 1-40: P3_theta025, a2_005, λ = 0,5; 1-40: P3_theta025, a2_005, λ = 0,7; 1-40: P3_theta025, a2_005, λ = 0,9; 1-40: P3_theta025, base, λ = 0,3; 1-40: P3_theta025, base, λ = 0,5; 1-40: P3_theta025, base, λ = 0,7; 1-40: P3_theta025, base, λ = 0,9; 1-40: P3_theta025, p1_p2_metade, λ = 0,3; 1-40: P3_theta025, p1_p2_metade, λ = 0,5; 1-40: P3_theta025, p1_p2_metade, λ = 0,7; 1-40: P3_theta025, p1_p2_metade, λ = 0,9; 1-40: P3_theta025, p_metade_a2_005, λ = 0,3; 1-40: P3_theta025, p_metade_a2_005, λ = 0,5; 1-40: P3_theta025, p_metade_a2_005, λ = 0,7; 1-40: P3_theta025, p_metade_a2_005, λ = 0,9; 1-40: P3_theta025, p_metade_a2_030, λ = 0,5; 1-40: P3_theta025, p_metade_a2_030, λ = 0,7; 1-40: P3_theta025, p_metade_a2_030, λ = 0,9; 1-40: P3_theta05, a2_005, λ = 0,3; 1-40: P3_theta05, a2_005, λ = 0,5; 1-40: P3_theta05, a2_005, λ = 0,7; 1-40: P3_theta05, a2_005, λ = 0,9; 1-40: P3_theta05, a2_030, λ = 0,5; 1-40: P3_theta05, base, λ = 0,3; 1-40: P3_theta05, base, λ = 0,5; 1-40: P3_theta05, base, λ = 0,7; 1-40: P3_theta05, base, λ = 0,9; 1-40: P3_theta05, p1_p2_metade, λ = 0,3; 1-40: P3_theta05, p1_p2_metade, λ = 0,5; 1-40: P3_theta05, p1_p2_metade, λ = 0,7; 1-40: P3_theta05, p1_p2_metade, λ = 0,9; 1-40: P3_theta05, p_metade_a2_005, λ = 0,3; 1-40: P3_theta05, p_metade_a2_005, λ = 0,5; 1-40: P3_theta05, p_metade_a2_005, λ = 0,7; 1-40: P3_theta05, p_metade_a2_005, λ = 0,9; 1-40: P3_theta05, p_metade_a2_030, λ = 0,5; 1-40: P3_theta05, p_metade_a2_030, λ = 0,7; 1-40: P3_theta05, p_metade_a2_030, λ = 0,9; 1-8: P1, a2_005, λ = 0,3; 1-8: P1, a2_005, λ = 0,5; 1-8: P1, a2_005, λ = 0,7; 1-8: P1, a2_005, λ = 0,9; 1-8: P1, a2_030, λ = 0,3; 1-8: P1, base, λ = 0,3; 1-8: P1, base, λ = 0,5; 1-8: P1, p1_p2_metade, λ = 0,3; 1-8: P1, p1_p2_metade, λ = 0,5; 1-8: P1, p1_p2_metade, λ = 0,7; 1-8: P1, p1_p2_metade, λ = 0,9; 1-8: P1, p_metade_a2_005, λ = 0,3; 1-8: P1, p_metade_a2_005, λ = 0,5; 1-8: P1, p_metade_a2_005, λ = 0,7; 1-8: P1, p_metade_a2_005, λ = 0,9; 1-8: P1, p_metade_a2_030, λ = 0,3; 1-8: P1, p_metade_a2_030, λ = 0,5; 1-8: P2, a2_005, λ = 0,3; 1-8: P2, a2_005, λ = 0,5; 1-8: P2, a2_005, λ = 0,7; 1-8: P2, a2_005, λ = 0,9; 1-8: P2, base, λ = 0,3; 1-8: P2, p1_p2_metade, λ = 0,3; 1-8: P2, p1_p2_metade, λ = 0,5; 1-8: P2, p1_p2_metade, λ = 0,7; 1-8: P2, p1_p2_metade, λ = 0,9; 1-8: P2, p_metade_a2_005, λ = 0,3; 1-8: P2, p_metade_a2_005, λ = 0,5; 1-8: P2, p_metade_a2_005, λ = 0,7; 1-8: P2, p_metade_a2_005, λ = 0,9; 1-8: P2, p_metade_a2_030, λ = 0,3; 1-8: P2, p_metade_a2_030, λ = 0,5; 1-8: P3_theta025, a2_005, λ = 0,3; 1-8: P3_theta025, a2_005, λ = 0,5; 1-8: P3_theta025, a2_005, λ = 0,7; 1-8: P3_theta025, a2_005, λ = 0,9; 1-8: P3_theta025, a2_030, λ = 0,3; 1-8: P3_theta025, a2_030, λ = 0,5; 1-8: P3_theta025, base, λ = 0,3; 1-8: P3_theta025, base, λ = 0,5; 1-8: P3_theta025, base, λ = 0,7; 1-8: P3_theta025, p1_p2_metade, λ = 0,3; 1-8: P3_theta025, p1_p2_metade, λ = 0,5; 1-8: P3_theta025, p1_p2_metade, λ = 0,7; 1-8: P3_theta025, p1_p2_metade, λ = 0,9; 1-8: P3_theta025, p_metade_a2_005, λ = 0,3; 1-8: P3_theta025, p_metade_a2_005, λ = 0,5; 1-8: P3_theta025, p_metade_a2_005, λ = 0,7; 1-8: P3_theta025, p_metade_a2_005, λ = 0,9; 1-8: P3_theta025, p_metade_a2_030, λ = 0,3; 1-8: P3_theta025, p_metade_a2_030, λ = 0,5; 1-8: P3_theta025, p_metade_a2_030, λ = 0,7; 1-8: P3_theta025, p_metade_a2_030, λ = 0,9; 1-8: P3_theta05, a2_005, λ = 0,3; 1-8: P3_theta05, a2_005, λ = 0,5; 1-8: P3_theta05, a2_005, λ = 0,7; 1-8: P3_theta05, a2_005, λ = 0,9; 1-8: P3_theta05, a2_030, λ = 0,3; 1-8: P3_theta05, a2_030, λ = 0,5; 1-8: P3_theta05, base, λ = 0,3; 1-8: P3_theta05, base, λ = 0,5; 1-8: P3_theta05, base, λ = 0,7; 1-8: P3_theta05, p1_p2_metade, λ = 0,3; 1-8: P3_theta05, p1_p2_metade, λ = 0,5; 1-8: P3_theta05, p1_p2_metade, λ = 0,7; 1-8: P3_theta05, p1_p2_metade, λ = 0,9; 1-8: P3_theta05, p_metade_a2_005, λ = 0,3; 1-8: P3_theta05, p_metade_a2_005, λ = 0,5; 1-8: P3_theta05, p_metade_a2_005, λ = 0,7; 1-8: P3_theta05, p_metade_a2_005, λ = 0,9; 1-8: P3_theta05, p_metade_a2_030, λ = 0,3; 1-8: P3_theta05, p_metade_a2_030, λ = 0,5; 1-8: P3_theta05, p_metade_a2_030, λ = 0,7; 1-8: P3_theta05, p_metade_a2_030, λ = 0,9.

## 7. Dados e coeficientes

Matriz insumo-produto: MIP 2015 nível 67 (IBGE), tabelas 03, 04, 12, 13, 14 e 15; TRU 2015 nível 68 (valor adicionado, remunerações, ocupações); TRU 2023 nível 12 (valor da produção e VA; a TRU 2023 publica zeradas as ocupações e os componentes da renda). Multiplicador de produção tipo I da transformação: 2,16 (MIP 2015) e 2,21 (TRU 2023, aproximação). Scripts: `src/extrair_mip.py`, `src/extrair_emprego.py`.

Tabelas do SIDRA usadas (validadas pelo nome e pela variável no metadado):

| Tabela | Nome | Variável |
|---|---|---|
| 5434 | Pessoas de 14 anos ou mais de idade, ocupadas na semana de referência, por grupamentos de atividades no trabalho principal | Pessoas de 14 anos ou mais de idade ocupadas na semana de referência (Mil pessoas) |
| 5442 | Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupadas na semana de referência com rendimento de trabalho, habitualmente e efetivamente recebidos no trabalho principal, por grupamentos de atividades no trabalho principal | Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupadas na semana de referência com rendimento de trabalho, habitualmente recebido no trabalho principal (Reais) |
| 4097 | Pessoas de 14 anos ou mais de idade, ocupadas na semana de referência, por posição na ocupação e categoria do emprego no trabalho principal | Pessoas de 14 anos ou mais de idade ocupadas na semana de referência (Mil pessoas) |
| 4093 | Pessoas de 14 anos ou mais de idade, total, na força de trabalho, ocupadas, desocupadas, fora da força de trabalho, em situação de informalidade e respectivas taxas e níveis, por sexo | Taxa de informalidade das pessoas de 14 anos ou mais de idade ocupadas na semana de referência (%) |
| 4099 | Taxas de desocupação e de subutilização da força de trabalho, na semana de referência, das pessoas de 14 anos ou mais de idade | Taxa de desocupação, na semana de referência, das pessoas de 14 anos ou mais de idade (%) |
| 10262 | Pessoas de 14 anos ou mais de idade ocupadas na semana de referência, por posição na ocupação e categoria do emprego no trabalho principal e seção de atividade do trabalho principal | Pessoas de 14 anos ou mais de idade ocupadas na semana de referência (Pessoas) |
| 1846 | Valores a preços correntes | Valores a preços correntes (Milhões de Reais) |
| 1621 | Série encadeada do índice de volume trimestral com ajuste sazonal (Base: média 1995 = 100) | Série encadeada do índice de volume trimestral com ajuste sazonal (Base: média 1995 = 100) (Número-índice) |

Ocupados de 2025 (média dos 4 trimestres, PNAD): 102064 mil; distribuídos pelas 67 atividades: 102065 mil. Informalidade: PNAD 2025 37,8%, Censo 2022 38,6% (a estrutura setorial do Censo é calibrada à taxa da PNAD por razão de chances constante).

| Grupo | Ocupados 2025 (mil) | Ocupações TRU 2015 (mil) | Fração formal | Rendimento médio (R$/mês) | Coef. emprego 2025 | Coef. 2015 | Variação real | Mult. emprego tipo I 2015 → 2025 |
|---|---|---|---|---|---|---|---|---|
| Agropecuária | 7777 | 13138 | 27% | 2308 | 5,25 | 27,44 | −60% | 32,5 → 15,0 |
| Indústrias extrativas | 405 | 288 | 83% | 3504 | 0,50 | 1,10 | 44% | 6,1 → 6,0 |
| Indústrias de transformação | 11840 | 11214 | 74% | 3321 | 1,92 | 4,04 | 14% | 13,6 → 12,0 |
| Eletricidade e gás, água, esgoto e resíduos | 954 | 677 | 65% | 3504 | 1,49 | 2,09 | 11% | 6,4 → 6,3 |
| Construção | 7405 | 8640 | 36% | 2840 | 7,12 | 13,66 | −29% | 20,3 → 15,7 |
| Comércio | 19359 | 18873 | 68% | 2954 | 8,99 | 17,15 | −11% | 21,3 → 18,8 |
| Transporte, armazenagem e correio | 5917 | 4711 | 61% | 3430 | 5,37 | 9,32 | −3% | 14,7 → 13,8 |
| Informação e comunicação | 1582 | 1350 | 81% | 5162 | 2,08 | 3,85 | −21% | 9,6 → 7,8 |
| Atividades financeiras e de seguros | 1406 | 1200 | 88% | 5162 | 1,01 | 2,09 | 6% | 5,8 → 5,3 |
| Atividades imobiliárias | 489 | 417 | 57% | 5162 | 0,47 | 0,76 | −4% | 1,4 → 1,3 |
| Outras atividades de serviços | 32219 | 30270 | 58% | 3616 | 9,69 | 20,59 | −22% | 25,4 → 20,0 |
| Administração, defesa, saúde e educação públicas | 12711 | 11168 | 83% | 5015 | 5,25 | 9,25 | 8% | 12,8 → 13,0 |

Coeficiente de emprego: ocupações por R$ milhão de produção (2015: R$ de 2015; 2025: R$ de 2025, e a variação real deflaciona pelo deflator implícito do VA de cada grupo nas Contas Trimestrais). Ordem relativa dos multiplicadores de emprego preservada: Spearman 0,95 (tipo I) e 0,89 (tipo II). A queda real na agropecuária reflete sobretudo a diferença de conceito: a TRU conta ocupações (inclusive trabalhos secundários e familiares); a PNAD, pessoas pelo trabalho principal.

Lei de Okun (PNAD 4099 e hiato do modelo, diferenças de 4 trimestres, 2013–2026, erro-padrão de Newey-West): Δ desocupação = −0,231 × Δ hiato, IC de 95% [−0,441; −0,021], n = 54.

Elasticidades setoriais (CNT, tabela 1621; crescimento trimestral anualizado do VA sobre Δ hiato, Δ juro real longo, depreciação real e variação do IC-Br em US$, 2005–2026) em `data/processed/mip/elasticidades_cnt.csv`: servem de verificação da distribuição pela matriz. As do câmbio real saíram pequenas e quase todas não significativas, por isso não foram usadas para as exportações: o canal do câmbio usa o vetor de exportações da MIP.

## 8. Limitações

- Os multiplicadores por item vêm da literatura e têm incerteza grande; os resultados de composição devem ser lidos pelas faixas de sensibilidade. No modelo, o multiplicador acumulado em 4 trimestres de uma medida permanente é cerca de 0,7 × m: os valores centrais ficam abaixo das estimativas SVAR mais altas para investimento e transferências.
- A matriz de 2015 supõe coeficientes técnicos fixos; a atualização para 2025 corrige o emprego, não a estrutura de insumos.
- A credibilidade de cada composição do pacote não é modelada.
- A lei de Okun é uma relação reduzida e pode variar com a formalidade do mercado de trabalho.
- O bloco setorial não retroalimenta o modelo macro: a distribuição setorial não altera inflação, câmbio, reservas ou dívida; o efeito sobre a balança comercial é reportado, não realimentado.
- Sem a POF por faixa de renda, os itens com canal no consumo de alta, média e baixa renda usam o vetor total de consumo das famílias: a distribuição setorial dos itens de consumo é a mesma.
- O juro real longo divide-se meio a meio entre consumo e investimento (premissa).
- A alíquota efetiva do IRPF é aplicada ao rendimento médio de cada setor; com a isenção até R$ 5.000 de 2026, quase todos os setores ficam com alíquota zero, o que subestima o IR da massa salarial adicional.
- Os coeficientes de emprego de 2025 usam o conceito da PNAD (pessoas no trabalho principal); os da TRU 2015, ocupações.
- O critério de produto exclui as trajetórias com inflação acima de 20%: o modelo não tem o custo de produto da inflação alta (desorganização de preços relativos, encurtamento de contratos), o que favorece B e C com adesão baixa.
- A referência S também sofre com a falta de ajuste (prêmio e juro longo maiores): a diferença de cada estratégia contra S inclui esse ganho de credibilidade, decomposto na seção 1.
