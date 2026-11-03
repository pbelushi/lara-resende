# Efeito recessivo das estratégias: PIB, composição do pacote, setores e emprego

Modelo v2.2 calibrado (R_min = US$ 300 bi), N = 1000 trajetórias por estratégia e λ (seed 42, as mesmas da rodada principal), bootstrap pareado com R = 1000 (seed 2026). Especificações P1, P2 e P3 (θ = 0,5 e 0,25); adesão λ ∈ {0,3; 0,5; 0,7; 0,9} na diagonal. t0 = 2026T3: a eleição de outubro de 2030 é o trimestre 16. Os multiplicadores por item do pacote substituem a3 = 0,4 só neste módulo; a lógica de sucesso já reportada não muda.

**Perda acumulada de produto** = −Σ (PIB da estratégia − PIB de S) / PIB de S, em % do PIB de um ano: positivo = produto abaixo da referência sem ajuste (S); negativo = produto acima de S. Métricas de atividade sobre trajetórias não explosivas, com a fração explosiva ao lado; na probabilidade de recessão, a trajetória explosiva conta como recessão na janela em que rompe.

Estratégias: **S** = S. Referência sem ajuste; **A** = A. Ortodoxo; **A_res60** = A com venda de US$ 60 bi; **A_res100** = A com venda de até US$ 100 bi (efetiva: 76); **B** = B. Lara Resende puro; **C** = C. Lara Resende condicionado; **C_sem_piso** = C sem piso (venda efetiva: 76).

## Síntese

1. **Perda de produto e recessão.** Contra a referência sem ajuste (S), nenhuma estratégia com ajuste é recessiva para λ ≥ 0,5: sem ajuste, o prêmio e o juro real longo sobem, e esse efeito (+0,9 a +1,2 p.p. de hiato até a eleição, P1, λ = 0,7) supera o efeito direto do pacote (−0,3 p.p.). Até a eleição, o produto fica 2,3 (A) a 3,6 (C sem piso) % de um ano acima de S em P1; em P3 com λ = 0,3, A fica abaixo de S nos 8 primeiros trimestres (perda de 0,3 a 0,4).
2. Entre as estratégias com ajuste, **C sem piso tem a menor perda**: 1,2 a 1,6 % do PIB de um ano acima de A até a eleição, em todas as especificações (IC estreitos); contra A com a mesma venda efetiva, 0,7 a 1,0. A venda de reservas acrescenta 0,2 a 0,5. A probabilidade de recessão técnica quase não separa as estratégias (diferenças de 1 a 2 p.p., IC com zero na maioria); só S fica 5 a 8 p.p. acima.
3. **Composição do pacote.** Com o mesmo valor total, o pacote de qualidade (multiplicador efetivo 0,34) custa 0,7 a 0,9 % do PIB de um ano a menos que o corte linear (0,87) até a eleição; 0,6 a 1,6 na faixa de multiplicadores e 0,9 a 1,1 com multiplicadores dependentes do ciclo. O pacote atual (0,51) fica no meio. A credibilidade de cada composição não é modelada.
4. **Setores e emprego** (P1, λ = 0,7, média até a eleição): A gera 670 mil ocupações a mais que S (350 mil formais); C sem piso, 1,0 milhão (540 mil formais); desocupação 0,13 a 0,20 p.p. menor. Ganham construção, comércio, outros serviços e transformação; administração pública perde cerca de 70 mil ocupações com os cortes nos pisos e emendas.
5. **Robustez × custo.** Não há troca: as estratégias mais robustas pela dívida líquida (C sem piso, A com venda de reservas) também têm a menor perda; A sem venda é a menos robusta e a de maior custo entre as que ajustam. B tem o maior produto de curto prazo, mas nunca atinge 70% de sucesso e, com λ = 0,3 em P1 e P2, explode em 97% das trajetórias.

## 1. Perda de produto e recessão

Mediana da perda acumulada [faixa 10–90%] e P(recessão técnica), λ = 0,7:

| Especificação | Estratégia | Explosivas | Perda 1-8 | P(rec.) 1-8 | Perda 1-16 | P(rec.) 1-16 | Perda 1-40 | P(rec.) 1-40 |
|---|---|---|---|---|---|---|---|---|
| P1 | S | 0% | 0,00 [−0,0; 0,0] | 23% | 0,00 [−0,0; 0,0] | 38% | 0,00 [−0,0; 0,0] | 75% |
| P1 | A | 0% | −0,62 [−0,6; −0,6] | 18% | −2,33 [−2,4; −2,2] | 32% | −7,12 [−7,4; −6,7] | 74% |
| P1 | A_res60 | 0% | −0,72 [−0,7; −0,7] | 17% | −2,74 [−2,8; −2,5] | 31% | −7,86 [−8,2; −7,4] | 74% |
| P1 | A_res100 (ef. 76) | 0% | −0,75 [−0,8; −0,7] | 17% | −2,84 [−3,0; −2,6] | 31% | −8,03 [−8,4; −7,6] | 74% |
| P1 | B | 0% | −1,24 [−1,6; −0,9] | 14% | −3,95 [−6,1; −2,0] | 30% | −12,75 [−24,5; −3,4] | 73% |
| P1 | C | 0% | −1,23 [−1,3; −1,0] | 15% | −3,49 [−3,7; −2,6] | 33% | −8,08 [−8,9; −5,9] | 74% |
| P1 | C_sem_piso | 0% | −1,23 [−1,3; −1,1] | 14% | −3,55 [−3,8; −3,2] | 31% | −8,86 [−9,3; −8,3] | 73% |
| P2 | S | 0% | 0,00 [−0,0; 0,0] | 25% | 0,00 [−0,0; 0,0] | 40% | 0,00 [−0,0; 0,0] | 76% |
| P2 | A | 0% | −0,71 [−0,7; −0,7] | 18% | −2,75 [−2,8; −2,6] | 32% | −9,12 [−9,4; −8,7] | 72% |
| P2 | A_res60 | 0% | −0,82 [−0,8; −0,8] | 18% | −3,22 [−3,3; −3,0] | 31% | −10,08 [−10,4; −9,6] | 72% |
| P2 | A_res100 (ef. 76) | 0% | −0,85 [−0,9; −0,8] | 17% | −3,33 [−3,4; −3,1] | 31% | −10,31 [−10,7; −9,8] | 72% |
| P2 | B | 0% | −1,52 [−1,8; −1,2] | 14% | −5,03 [−7,1; −3,0] | 30% | −13,73 [−24,1; −6,3] | 75% |
| P2 | C | 0% | −1,42 [−1,5; −1,2] | 14% | −4,30 [−4,6; −3,5] | 32% | −10,68 [−11,7; −8,4] | 74% |
| P2 | C_sem_piso | 0% | −1,42 [−1,5; −1,3] | 14% | −4,35 [−4,6; −4,0] | 31% | −11,38 [−11,8; −10,8] | 72% |
| P3_theta05 | S | 0% | 0,00 [−0,0; 0,0] | 23% | 0,00 [−0,0; 0,0] | 39% | 0,00 [−0,0; 0,0] | 75% |
| P3_theta05 | A | 0% | −0,18 [−0,2; −0,1] | 22% | −1,03 [−1,1; −0,9] | 35% | −5,40 [−6,1; −4,1] | 73% |
| P3_theta05 | A_res60 | 0% | −0,21 [−0,2; −0,2] | 21% | −1,27 [−1,3; −1,1] | 34% | −6,14 [−6,7; −5,2] | 73% |
| P3_theta05 | A_res100 (ef. 76) | 0% | −0,22 [−0,2; −0,2] | 21% | −1,33 [−1,4; −1,2] | 34% | −6,32 [−6,9; −5,4] | 73% |
| P3_theta05 | B | 0% | −1,31 [−1,5; −1,1] | 14% | −3,92 [−4,9; −3,0] | 33% | −6,37 [−8,3; −4,5] | 78% |
| P3_theta05 | C | 0% | −0,81 [−0,9; −0,7] | 17% | −2,01 [−2,3; −1,6] | 37% | −3,15 [−4,1; −2,1] | 76% |
| P3_theta05 | C_sem_piso | 0% | −0,81 [−0,9; −0,7] | 17% | −2,30 [−2,4; −2,1] | 34% | −7,41 [−8,0; −6,4] | 74% |
| P3_theta025 | S | 0% | 0,00 [−0,0; 0,0] | 23% | 0,00 [−0,0; 0,0] | 38% | 0,00 [−0,0; 0,0] | 75% |
| P3_theta025 | A | 0% | −0,19 [−0,2; −0,2] | 22% | −1,13 [−1,2; −1,0] | 34% | −5,95 [−6,2; −5,7] | 72% |
| P3_theta025 | A_res60 | 0% | −0,22 [−0,2; −0,2] | 21% | −1,37 [−1,4; −1,2] | 34% | −6,55 [−6,8; −6,3] | 72% |
| P3_theta025 | A_res100 (ef. 76) | 0% | −0,23 [−0,2; −0,2] | 21% | −1,43 [−1,5; −1,3] | 34% | −6,70 [−6,9; −6,4] | 72% |
| P3_theta025 | B | 0% | −1,30 [−1,5; −1,1] | 13% | −4,05 [−5,1; −3,1] | 32% | −8,09 [−10,6; −5,9] | 77% |
| P3_theta025 | C | 0% | −0,81 [−0,9; −0,7] | 17% | −2,35 [−2,5; −2,0] | 35% | −4,98 [−5,9; −4,0] | 74% |
| P3_theta025 | C_sem_piso | 0% | −0,81 [−0,9; −0,7] | 17% | −2,44 [−2,6; −2,2] | 33% | −7,85 [−8,2; −7,5] | 72% |

Perda até a eleição (trimestres 1–16, mediana) por λ:

| Especificação | Estratégia | λ = 0,3 | λ = 0,5 | λ = 0,7 | λ = 0,9 |
|---|---|---|---|---|---|
| P1 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P1 | A | −1,51 | −1,90 | −2,33 | −2,77 |
| P1 | A_res60 | −2,08 | −2,34 | −2,74 | −3,19 |
| P1 | A_res100 (ef. 76) | −2,26 | −2,47 | −2,84 | −3,29 |
| P1 | B | 0,12 | −2,62 | −3,95 | −2,80 |
| P1 | C | −3,15 | −3,34 | −3,49 | −3,73 |
| P1 | C_sem_piso | −3,18 | −3,40 | −3,55 | −3,80 |
| P2 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P2 | A | −1,67 | −2,19 | −2,75 | −3,34 |
| P2 | A_res60 | −2,27 | −2,68 | −3,22 | −3,83 |
| P2 | A_res100 (ef. 76) | −2,45 | −2,81 | −3,33 | −3,94 |
| P2 | B | −1,53 | −7,65 | −5,03 | −3,91 |
| P2 | C | −3,58 | −3,97 | −4,30 | −4,76 |
| P2 | C_sem_piso | −3,59 | −4,00 | −4,35 | −4,80 |
| P3_theta05 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P3_theta05 | A | 0,10 | −0,42 | −1,03 | −1,68 |
| P3_theta05 | A_res60 | −0,13 | −0,66 | −1,27 | −1,92 |
| P3_theta05 | A_res100 (ef. 76) | −0,19 | −0,73 | −1,33 | −1,98 |
| P3_theta05 | B | −19,93 | −6,89 | −3,92 | −3,28 |
| P3_theta05 | C | 0,69 | −0,57 | −2,01 | −2,85 |
| P3_theta05 | C_sem_piso | −1,15 | −1,72 | −2,30 | −2,87 |
| P3_theta025 | S | 0,00 | 0,00 | 0,00 | 0,00 |
| P3_theta025 | A | −0,53 | −0,66 | −1,13 | −1,69 |
| P3_theta025 | A_res60 | −0,83 | −0,91 | −1,37 | −1,93 |
| P3_theta025 | A_res100 (ef. 76) | −0,92 | −0,98 | −1,43 | −1,98 |
| P3_theta025 | B | −28,51 | −7,87 | −4,05 | −3,29 |
| P3_theta025 | C | −0,88 | −1,57 | −2,35 | −2,87 |
| P3_theta025 | C_sem_piso | −1,78 | −2,04 | −2,44 | −2,88 |

Hiato mínimo (mediana, trimestres 1–40) e trimestre em que ocorre, anos com crescimento negativo (média, 2027–2035) e taxa de sacrifício (perda até o trimestre 16 ÷ queda da inflação média do ano 1 para os anos 3–4, só quando a inflação cai), λ = 0,7:

| Especificação | Estratégia | Hiato mínimo | Trimestre | Anos negativos | Sacrifício | Trajetórias com queda |
|---|---|---|---|---|---|---|
| P1 | S | −3,16 | 25 | 0,1 | 0,00 | 64% |
| P1 | A | −2,51 | 14 | 0,1 | −2,19 | 48% |
| P1 | A_res60 | −2,47 | 15 | 0,1 | −2,85 | 42% |
| P1 | A_res100 (ef. 76) | −2,45 | 15 | 0,1 | −3,06 | 38% |
| P1 | B | −2,20 | 6 | 0,1 | −3,04 | 32% |
| P1 | C | −2,41 | 22 | 0,1 | −3,55 | 41% |
| P1 | C_sem_piso | −2,32 | 18 | 0,1 | −3,81 | 40% |
| P2 | S | −3,31 | 24 | 0,1 | 0,00 | 62% |
| P2 | A | −2,48 | 12 | 0,0 | −2,63 | 54% |
| P2 | A_res60 | −2,42 | 10 | 0,0 | −3,25 | 49% |
| P2 | A_res100 (ef. 76) | −2,41 | 9 | 0,0 | −3,53 | 46% |
| P2 | B | −2,23 | 12 | 0,1 | −4,16 | 37% |
| P2 | C | −2,36 | 19 | 0,1 | −4,09 | 48% |
| P2 | C_sem_piso | −2,28 | 16 | 0,0 | −4,42 | 48% |
| P3_theta05 | S | −3,05 | 21 | 0,1 | 0,00 | 72% |
| P3_theta05 | A | −2,60 | 10 | 0,1 | −0,41 | 99% |
| P3_theta05 | A_res60 | −2,55 | 9 | 0,1 | −0,53 | 98% |
| P3_theta05 | A_res100 (ef. 76) | −2,54 | 9 | 0,1 | −0,58 | 98% |
| P3_theta05 | B | −2,61 | 29 | 0,1 | −3,21 | 72% |
| P3_theta05 | C | −2,75 | 25 | 0,1 | −0,83 | 97% |
| P3_theta05 | C_sem_piso | −2,39 | 12 | 0,0 | −0,90 | 98% |
| P3_theta025 | S | −3,07 | 22 | 0,1 | 0,00 | 69% |
| P3_theta025 | A | −2,57 | 9 | 0,0 | −0,71 | 90% |
| P3_theta025 | A_res60 | −2,52 | 9 | 0,0 | −0,95 | 86% |
| P3_theta025 | A_res100 (ef. 76) | −2,51 | 8 | 0,0 | −1,03 | 84% |
| P3_theta025 | B | −2,48 | 27 | 0,1 | −4,76 | 56% |
| P3_theta025 | C | −2,62 | 22 | 0,1 | −1,52 | 88% |
| P3_theta025 | C_sem_piso | −2,35 | 11 | 0,0 | −1,57 | 89% |

Bootstrap pareado (diferença de médias, IC de 95%; * = exclui zero). Perda em % do PIB de um ano; P(recessão) em p.p.; λ = 0,7:

| Especificação | Par | Perda 1–8 | Perda 1–16 | P(rec.) 1–8 | P(rec.) 1–16 |
|---|---|---|---|---|---|
| P1 | A − C | 0,58 [0,57; 0,59] * | 0,99 [0,96; 1,02] * | 4 [2; 5] * | −1 [−2; 1] |
| P1 | A − C_sem_piso | 0,60 [0,59; 0,60] * | 1,20 [1,19; 1,21] * | 4 [3; 5] * | 1 [−1; 2] |
| P1 | A − A_res60 | 0,10 [0,10; 0,10] * | 0,41 [0,41; 0,41] * | 1 [1; 2] * | 1 [0; 2] * |
| P1 | C_sem_piso − A_res100 | −0,47 [−0,48; −0,47] * | −0,69 [−0,70; −0,68] * | −2 [−4; −1] * | 0 [−1; 2] |
| P1 | A − S | −0,61 [−0,61; −0,61] * | −2,30 [−2,31; −2,30] * | −5 [−6; −3] * | −6 [−8; −4] * |
| P1 | A_res60 − S | −0,71 [−0,71; −0,71] * | −2,72 [−2,72; −2,71] * | −6 [−8; −4] * | −7 [−9; −5] * |
| P1 | A_res100 − S | −0,74 [−0,74; −0,73] * | −2,82 [−2,83; −2,81] * | −6 [−8; −5] * | −7 [−9; −5] * |
| P1 | B − S | −1,23 [−1,25; −1,22] * | −4,01 [−4,10; −3,91] * | −9 [−10; −7] * | −8 [−10; −6] * |
| P1 | C − S | −1,19 [−1,20; −1,18] * | −3,30 [−3,33; −3,27] * | −8 [−10; −7] * | −5 [−8; −3] * |
| P1 | C_sem_piso − S | −1,21 [−1,21; −1,20] * | −3,51 [−3,52; −3,49] * | −9 [−11; −7] * | −7 [−9; −5] * |
| P2 | A − C | 0,68 [0,67; 0,69] * | 1,42 [1,39; 1,44] * | 4 [3; 5] * | −0 [−2; 2] |
| P2 | A − C_sem_piso | 0,70 [0,69; 0,70] * | 1,58 [1,57; 1,59] * | 4 [3; 6] * | 1 [−0; 3] |
| P2 | A − A_res60 | 0,11 [0,11; 0,11] * | 0,47 [0,47; 0,47] * | 1 [0; 2] * | 0 [−0; 1] |
| P2 | C_sem_piso − A_res100 | −0,56 [−0,56; −0,55] * | −1,00 [−1,01; −0,99] * | −3 [−4; −2] * | −1 [−2; 1] |
| P2 | A − S | −0,70 [−0,70; −0,70] * | −2,72 [−2,73; −2,72] * | −6 [−8; −5] * | −8 [−10; −7] * |
| P2 | A_res60 − S | −0,81 [−0,81; −0,81] * | −3,19 [−3,20; −3,18] * | −7 [−9; −6] * | −9 [−11; −7] * |
| P2 | A_res100 − S | −0,84 [−0,84; −0,84] * | −3,31 [−3,32; −3,30] * | −8 [−9; −6] * | −9 [−11; −7] * |
| P2 | B − S | −1,51 [−1,53; −1,50] * | −5,02 [−5,11; −4,93] * | −11 [−13; −9] * | −10 [−12; −8] * |
| P2 | C − S | −1,38 [−1,39; −1,38] * | −4,14 [−4,17; −4,11] * | −10 [−12; −8] * | −8 [−10; −6] * |
| P2 | C_sem_piso − S | −1,40 [−1,40; −1,39] * | −4,31 [−4,32; −4,29] * | −11 [−13; −9] * | −10 [−12; −8] * |
| P3_theta05 | A − C | 0,62 [0,62; 0,62] * | 0,97 [0,95; 0,98] * | 4 [3; 6] * | −2 [−4; −0] * |
| P3_theta05 | A − C_sem_piso | 0,62 [0,62; 0,63] * | 1,27 [1,26; 1,27] * | 4 [3; 6] * | 1 [−1; 2] |
| P3_theta05 | A − A_res60 | 0,04 [0,03; 0,04] * | 0,24 [0,24; 0,24] * | 0 [−0; 1] | 0 [−0; 1] |
| P3_theta05 | C_sem_piso − A_res100 | −0,58 [−0,58; −0,58] * | −0,97 [−0,98; −0,97] * | −4 [−5; −2] * | 0 [−1; 2] |
| P3_theta05 | A − S | −0,17 [−0,17; −0,17] * | −1,01 [−1,02; −1,01] * | −2 [−3; −1] * | −4 [−5; −3] * |
| P3_theta05 | A_res60 − S | −0,21 [−0,21; −0,20] * | −1,25 [−1,26; −1,25] * | −2 [−3; −1] * | −4 [−6; −3] * |
| P3_theta05 | A_res100 − S | −0,22 [−0,22; −0,21] * | −1,31 [−1,32; −1,31] * | −2 [−4; −1] * | −5 [−7; −4] * |
| P3_theta05 | B − S | −1,31 [−1,32; −1,30] * | −3,93 [−3,98; −3,89] * | −10 [−12; −8] * | −6 [−8; −3] * |
| P3_theta05 | C − S | −0,79 [−0,80; −0,79] * | −1,98 [−2,00; −1,96] * | −6 [−8; −5] * | −2 [−4; 0] |
| P3_theta05 | C_sem_piso − S | −0,79 [−0,80; −0,79] * | −2,28 [−2,29; −2,27] * | −6 [−8; −5] * | −5 [−6; −3] * |
| P3_theta025 | A − C | 0,61 [0,61; 0,62] * | 1,19 [1,17; 1,20] * | 4 [3; 6] * | −0 [−2; 1] |
| P3_theta025 | A − C_sem_piso | 0,62 [0,61; 0,62] * | 1,30 [1,29; 1,30] * | 4 [3; 6] * | 1 [−0; 3] |
| P3_theta025 | A − A_res60 | 0,03 [0,03; 0,03] * | 0,23 [0,23; 0,24] * | 0 [−0; 1] | 1 [0; 1] |
| P3_theta025 | C_sem_piso − A_res100 | −0,58 [−0,58; −0,57] * | −1,00 [−1,01; −1,00] * | −4 [−5; −3] * | −1 [−2; 1] |
| P3_theta025 | A − S | −0,18 [−0,18; −0,18] * | −1,11 [−1,12; −1,11] * | −2 [−3; −1] * | −4 [−5; −3] * |
| P3_theta025 | A_res60 − S | −0,21 [−0,21; −0,21] * | −1,35 [−1,35; −1,34] * | −2 [−4; −1] * | −5 [−6; −3] * |
| P3_theta025 | A_res100 − S | −0,22 [−0,22; −0,22] * | −1,41 [−1,41; −1,40] * | −2 [−4; −1] * | −5 [−6; −3] * |
| P3_theta025 | B − S | −1,30 [−1,31; −1,28] * | −4,07 [−4,12; −4,03] * | −10 [−12; −8] * | −7 [−9; −5] * |
| P3_theta025 | C − S | −0,79 [−0,80; −0,79] * | −2,30 [−2,31; −2,29] * | −6 [−8; −5] * | −4 [−6; −2] * |
| P3_theta025 | C_sem_piso − S | −0,80 [−0,80; −0,79] * | −2,41 [−2,42; −2,40] * | −6 [−8; −5] * | −5 [−7; −4] * |

Decomposição da diferença de hiato contra S (média dos trimestres 1–16, p.p. do PIB, λ = 0,7): efeito direto do pacote (soma dos itens), juro real longo, câmbio real, CAPEX e restante.

| Especificação | Estratégia | Δ hiato | Pacote direto | Juro real longo | Câmbio | CAPEX | Fiscal fora do pacote | Outros |
|---|---|---|---|---|---|---|---|---|
| P1 | A | 0,58 | −0,29 | 0,86 | −0,05 | 0,07 | −0,01 | −0,00 |
| P1 | A_res60 | 0,68 | −0,29 | 0,98 | −0,08 | 0,08 | −0,01 | −0,00 |
| P1 | A_res100 (ef. 76) | 0,71 | −0,29 | 1,01 | −0,08 | 0,08 | −0,01 | 0,00 |
| P1 | B | 1,00 | 0,00 | 0,97 | −0,02 | 0,07 | −0,02 | −0,00 |
| P1 | C | 0,83 | −0,29 | 1,13 | −0,09 | 0,08 | −0,01 | −0,00 |
| P1 | C_sem_piso | 0,88 | −0,29 | 1,18 | −0,09 | 0,08 | −0,01 | −0,00 |
| P2 | A | 0,68 | −0,29 | 0,95 | −0,05 | 0,08 | −0,01 | −0,00 |
| P2 | A_res60 | 0,80 | −0,29 | 1,09 | −0,07 | 0,09 | −0,01 | −0,00 |
| P2 | A_res100 (ef. 76) | 0,83 | −0,29 | 1,12 | −0,08 | 0,09 | −0,01 | −0,00 |
| P2 | B | 1,25 | 0,00 | 1,20 | −0,01 | 0,09 | −0,02 | 0,00 |
| P2 | C | 1,04 | −0,29 | 1,33 | −0,08 | 0,10 | −0,02 | −0,00 |
| P2 | C_sem_piso | 1,08 | −0,29 | 1,36 | −0,08 | 0,10 | −0,02 | −0,00 |
| P3_theta05 | A | 0,26 | −0,29 | 0,50 | 0,01 | 0,04 | −0,00 | −0,00 |
| P3_theta05 | A_res60 | 0,31 | −0,29 | 0,59 | −0,03 | 0,05 | −0,01 | −0,00 |
| P3_theta05 | A_res100 (ef. 76) | 0,33 | −0,29 | 0,61 | −0,04 | 0,05 | −0,01 | −0,00 |
| P3_theta05 | B | 0,99 | 0,00 | 0,95 | −0,02 | 0,07 | −0,02 | 0,00 |
| P3_theta05 | C | 0,50 | −0,29 | 0,78 | −0,04 | 0,06 | −0,01 | −0,00 |
| P3_theta05 | C_sem_piso | 0,57 | −0,29 | 0,84 | −0,03 | 0,06 | −0,01 | −0,00 |
| P3_theta025 | A | 0,28 | −0,29 | 0,54 | −0,01 | 0,05 | −0,01 | −0,00 |
| P3_theta025 | A_res60 | 0,34 | −0,29 | 0,63 | −0,05 | 0,05 | −0,01 | −0,00 |
| P3_theta025 | A_res100 (ef. 76) | 0,35 | −0,29 | 0,65 | −0,05 | 0,06 | −0,01 | −0,00 |
| P3_theta025 | B | 1,02 | 0,00 | 0,98 | −0,02 | 0,07 | −0,02 | −0,00 |
| P3_theta025 | C | 0,58 | −0,29 | 0,86 | −0,05 | 0,07 | −0,01 | −0,00 |
| P3_theta025 | C_sem_piso | 0,61 | −0,29 | 0,89 | −0,05 | 0,07 | −0,01 | −0,00 |

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

Perda até a eleição (mediana, trimestres 1–16, λ = 0,7) por composição; entre parênteses, a faixa com multiplicadores baixos e altos; "ciclo" = multiplicadores dependentes do hiato (γ = 0,167):

| Especificação | Estratégia | Composição | Mult. efetivo | Central | (baixo; alto) | Com ciclo |
|---|---|---|---|---|---|---|
| P1 | A | pacote_base | 0,51 | −2,33 | (−2,72; −1,81) | −2,20 |
| P1 | A | pacote_qualidade | 0,34 | −2,50 | (−2,84; −2,04) | −2,41 |
| P1 | A | pacote_linear | 0,87 | −1,78 | (−2,28; −0,71) | −1,49 |
| P1 | C | pacote_base | 0,51 | −3,49 | (−3,90; −2,93) | −3,37 |
| P1 | C | pacote_qualidade | 0,34 | −3,68 | (−4,04; −3,19) | −3,60 |
| P1 | C | pacote_linear | 0,87 | −2,87 | (−3,41; −1,65) | −2,58 |
| P1 | C_sem_piso | pacote_base | 0,51 | −3,55 | (−3,96; −3,01) | −3,43 |
| P1 | C_sem_piso | pacote_qualidade | 0,34 | −3,73 | (−4,08; −3,25) | −3,65 |
| P1 | C_sem_piso | pacote_linear | 0,87 | −2,96 | (−3,49; −1,79) | −2,71 |
| P2 | A | pacote_base | 0,51 | −2,75 | (−3,20; −2,16) | −2,60 |
| P2 | A | pacote_qualidade | 0,34 | −2,94 | (−3,33; −2,42) | −2,83 |
| P2 | A | pacote_linear | 0,87 | −2,12 | (−2,70; −0,90) | −1,78 |
| P2 | C | pacote_base | 0,51 | −4,30 | (−4,77; −3,69) | −4,18 |
| P2 | C | pacote_qualidade | 0,34 | −4,51 | (−4,92; −3,97) | −4,43 |
| P2 | C | pacote_linear | 0,87 | −3,63 | (−4,23; −2,36) | −3,32 |
| P2 | C_sem_piso | pacote_base | 0,51 | −4,35 | (−4,81; −3,74) | −4,23 |
| P2 | C_sem_piso | pacote_qualidade | 0,34 | −4,56 | (−4,96; −4,01) | −4,46 |
| P2 | C_sem_piso | pacote_linear | 0,87 | −3,68 | (−4,28; −2,41) | −3,40 |
| P3_theta05 | A | pacote_base | 0,51 | −1,03 | (−1,47; −0,45) | −0,87 |
| P3_theta05 | A | pacote_qualidade | 0,34 | −1,25 | (−1,63; −0,74) | −1,14 |
| P3_theta05 | A | pacote_linear | 0,87 | −0,37 | (−0,93; 0,82) | −0,01 |
| P3_theta05 | C | pacote_base | 0,51 | −2,01 | (−2,44; −1,43) | −1,88 |
| P3_theta05 | C | pacote_qualidade | 0,34 | −2,21 | (−2,58; −1,71) | −2,12 |
| P3_theta05 | C | pacote_linear | 0,87 | −1,37 | (−1,93; −0,20) | −1,07 |
| P3_theta05 | C_sem_piso | pacote_base | 0,51 | −2,30 | (−2,75; −1,72) | −2,17 |
| P3_theta05 | C_sem_piso | pacote_qualidade | 0,34 | −2,53 | (−2,91; −2,01) | −2,43 |
| P3_theta05 | C_sem_piso | pacote_linear | 0,87 | −1,63 | (−2,20; −0,42) | −1,33 |
| P3_theta025 | A | pacote_base | 0,51 | −1,13 | (−1,57; −0,55) | −0,97 |
| P3_theta025 | A | pacote_qualidade | 0,34 | −1,35 | (−1,74; −0,84) | −1,24 |
| P3_theta025 | A | pacote_linear | 0,87 | −0,46 | (−1,02; 0,74) | −0,10 |
| P3_theta025 | C | pacote_base | 0,51 | −2,35 | (−2,80; −1,75) | −2,20 |
| P3_theta025 | C | pacote_qualidade | 0,34 | −2,57 | (−2,96; −2,05) | −2,47 |
| P3_theta025 | C | pacote_linear | 0,87 | −1,67 | (−2,24; −0,44) | −1,33 |
| P3_theta025 | C_sem_piso | pacote_base | 0,51 | −2,44 | (−2,89; −1,84) | −2,30 |
| P3_theta025 | C_sem_piso | pacote_qualidade | 0,34 | −2,67 | (−3,05; −2,14) | −2,57 |
| P3_theta025 | C_sem_piso | pacote_linear | 0,87 | −1,74 | (−2,32; −0,52) | −1,44 |

Pergunta 2: perda com pacote_qualidade − perda com pacote_linear (negativo = a composição de qualidade custa menos produto), bootstrap pareado, λ = 0,7:

| Especificação | Estratégia | 1–8 | 1–16 | 1–40 | 1–16, mult. baixos | 1–16, mult. altos | 1–16, ciclo |
|---|---|---|---|---|---|---|---|
| P1 | A | −0,53 [−0,53; −0,53] * | −0,72 [−0,72; −0,72] * | −0,55 [−0,55; −0,54] * | −0,56 [−0,56; −0,56] * | −1,33 [−1,33; −1,33] * | −0,92 [−0,93; −0,91] * |
| P1 | C | −0,56 [−0,56; −0,56] * | −0,81 [−0,82; −0,81] * | −0,70 [−0,71; −0,69] * | −0,63 [−0,63; −0,63] * | −1,56 [−1,57; −1,55] * | −1,01 [−1,02; −1,00] * |
| P1 | C_sem_piso | −0,55 [−0,55; −0,55] * | −0,76 [−0,77; −0,76] * | −0,57 [−0,57; −0,57] * | −0,59 [−0,59; −0,59] * | −1,45 [−1,46; −1,45] * | −0,94 [−0,95; −0,93] * |
| P2 | A | −0,55 [−0,55; −0,55] * | −0,82 [−0,82; −0,82] * | −0,60 [−0,60; −0,59] * | −0,63 [−0,63; −0,63] * | −1,51 [−1,52; −1,51] * | −1,05 [−1,06; −1,04] * |
| P2 | C | −0,58 [−0,58; −0,58] * | −0,89 [−0,89; −0,89] * | −0,74 [−0,74; −0,73] * | −0,69 [−0,69; −0,69] * | −1,63 [−1,63; −1,63] * | −1,09 [−1,10; −1,08] * |
| P2 | C_sem_piso | −0,58 [−0,58; −0,58] * | −0,87 [−0,87; −0,87] * | −0,69 [−0,69; −0,68] * | −0,68 [−0,68; −0,67] * | −1,60 [−1,60; −1,59] * | −1,06 [−1,07; −1,06] * |
| P3_theta05 | A | −0,57 [−0,57; −0,57] * | −0,89 [−0,89; −0,88] * | −0,99 [−1,00; −0,98] * | −0,70 [−0,71; −0,70] * | −1,56 [−1,56; −1,56] * | −1,13 [−1,14; −1,12] * |
| P3_theta05 | C | −0,59 [−0,59; −0,59] * | −0,83 [−0,84; −0,83] * | −0,70 [−0,70; −0,69] * | −0,65 [−0,65; −0,65] * | −1,51 [−1,51; −1,50] * | −1,04 [−1,05; −1,03] * |
| P3_theta05 | C_sem_piso | −0,59 [−0,59; −0,59] * | −0,90 [−0,90; −0,90] * | −1,03 [−1,03; −1,02] * | −0,71 [−0,71; −0,71] * | −1,59 [−1,59; −1,58] * | −1,11 [−1,11; −1,10] * |
| P3_theta025 | A | −0,58 [−0,58; −0,58] * | −0,90 [−0,90; −0,90] * | −0,96 [−0,96; −0,96] * | −0,72 [−0,72; −0,72] * | −1,58 [−1,58; −1,58] * | −1,14 [−1,15; −1,14] * |
| P3_theta025 | C | −0,60 [−0,60; −0,59] * | −0,91 [−0,91; −0,90] * | −0,85 [−0,86; −0,85] * | −0,72 [−0,72; −0,72] * | −1,60 [−1,60; −1,60] * | −1,12 [−1,13; −1,11] * |
| P3_theta025 | C_sem_piso | −0,60 [−0,60; −0,59] * | −0,92 [−0,92; −0,92] * | −0,99 [−1,00; −0,99] * | −0,73 [−0,73; −0,73] * | −1,62 [−1,62; −1,62] * | −1,13 [−1,14; −1,12] * |

A composição também afeta a credibilidade (um pacote de receita e de itens de difícil aprovação pode ter λ_fiscal menor); isso não é modelado: as tabelas mostram a perda para cada λ, e a comparação entre composições deve ser feita também em λ diferentes.

Gráfico: `graficos/4_composicao_pacote.png`.

## 3. Setores e emprego

A diferença de hiato contra S é decomposta pelos componentes da equação de demanda (juro real longo → metade consumo, metade FBCF; itens do pacote → canal de cada item; câmbio real → exportações; CAPEX → construção e máquinas; choques e restante → absorção doméstica), convertida em demanda final pelo PIB de 2015, distribuída pela Leontief tipo I da MIP 2015 (67 atividades) e reconciliada com o PIB do modelo macro trimestre a trimestre. Emprego = variação % da produção de cada atividade × ocupados de 2025 (PNAD).

Valor adicionado por grupo da TRU (% do VA do setor, média dos trimestres 1–16, λ = 0,7, P1):

| Grupo | A | A_res60 | A_res100 (ef. 76) | B | C | C_sem_piso |
|---|---|---|---|---|---|---|
| Agropecuária | 0,37 | 0,37 | 0,37 | 0,68 | 0,47 | 0,51 |
| Indústrias extrativas | 0,45 | 0,44 | 0,44 | 0,81 | 0,55 | 0,60 |
| Indústrias de transformação | 0,88 | 0,99 | 1,01 | 1,26 | 1,16 | 1,23 |
| Eletricidade e gás, água, esgoto e resíduos | 0,56 | 0,66 | 0,68 | 0,91 | 0,79 | 0,84 |
| Construção | 2,68 | 3,12 | 3,23 | 3,60 | 3,60 | 3,79 |
| Comércio | 0,84 | 0,97 | 1,00 | 1,18 | 1,14 | 1,20 |
| Transporte, armazenagem e correio | 0,65 | 0,73 | 0,76 | 0,99 | 0,88 | 0,93 |
| Informação e comunicação | 1,07 | 1,24 | 1,28 | 1,47 | 1,45 | 1,53 |
| Atividades financeiras e de seguros | 0,55 | 0,65 | 0,67 | 0,90 | 0,78 | 0,83 |
| Atividades imobiliárias | 0,67 | 0,79 | 0,82 | 0,95 | 0,93 | 0,98 |
| Outras atividades de serviços | 0,52 | 0,60 | 0,63 | 0,85 | 0,73 | 0,77 |
| Administração, defesa, saúde e educação públicas | −0,56 | −0,55 | −0,54 | 0,08 | −0,52 | −0,52 |

Ocupações contra S (mil; média dos trimestres de cada janela; λ = 0,7, P1). Formais pela fração formal de cada atividade (Censo 2022 calibrado à PNAD de 2025); induzido = tipo II − tipo I sem reconciliação (propensão a consumir 0,9, impostos 15%; sensibilidade em data/processed/mip/sensibilidade_tipo2.csv):

| Estratégia | Janela | Total | Formais | Informais | Massa salarial (R$ bi/ano) | Induzido tipo II | Desocupação (p.p.) [IC] |
|---|---|---|---|---|---|---|---|
| A | 1-8 | 370 | 191 | 179 | 12,7 | 90 | −0,07 [−0,14; −0,01] |
| A | 1-16 | 672 | 354 | 318 | 24,0 | 194 | −0,13 [−0,25; −0,01] |
| A_res60 | 1-8 | 431 | 224 | 207 | 15,0 | 112 | −0,08 [−0,16; −0,01] |
| A_res60 | 1-16 | 788 | 419 | 369 | 28,5 | 238 | −0,16 [−0,30; −0,01] |
| A_res100 (ef. 76) | 1-8 | 447 | 233 | 214 | 15,7 | 118 | −0,09 [−0,16; −0,01] |
| A_res100 (ef. 76) | 1-16 | 816 | 435 | 381 | 29,6 | 249 | −0,16 [−0,31; −0,01] |
| B | 1-8 | 677 | 381 | 297 | 26,2 | 256 | −0,14 [−0,27; −0,01] |
| B | 1-16 | 1094 | 616 | 477 | 42,4 | 417 | −0,23 [−0,44; −0,02] |
| C | 1-8 | 692 | 372 | 320 | 25,2 | 212 | −0,14 [−0,26; −0,01] |
| C | 1-16 | 945 | 509 | 436 | 34,7 | 299 | −0,19 [−0,36; −0,02] |
| C_sem_piso | 1-8 | 701 | 378 | 324 | 25,6 | 215 | −0,14 [−0,27; −0,01] |
| C_sem_piso | 1-16 | 1002 | 541 | 461 | 36,9 | 321 | −0,20 [−0,39; −0,02] |

Ocupações totais contra S por especificação (mil, trimestres 1–16, λ = 0,7):

| Especificação | A | A_res60 | A_res100 (ef. 76) | B | C | C_sem_piso |
|---|---|---|---|---|---|---|
| P1 | 672 | 788 | 816 | 1094 | 945 | 1002 |
| P2 | 786 | 917 | 949 | 1366 | 1173 | 1218 |
| P3_theta05 | 310 | 384 | 404 | 1074 | 582 | 663 |
| P3_theta025 | 339 | 413 | 438 | 1112 | 670 | 700 |

Diagnósticos (λ = 0,7, trimestres 1–16): fator de escala da reconciliação (PIB do modelo macro ÷ VA da matriz; fora de 0,7–1,3 indicaria incoerência entre os multiplicadores do bloco fiscal e os da matriz), efeito de volta sobre a balança comercial (exportações pelo canal do câmbio real; importações pelo conteúdo importado da demanda final e dos insumos) e retorno fiscal da massa salarial formal adicional (contribuições previdenciárias/FGTS pela razão da TRU 2015 e IRPF 2026 pela alíquota efetiva no rendimento médio do setor) contra a receita cíclica do modelo macro (rec_base × ε_rec × Δhiato). O retorno setorial não é somado ao primário: é uma decomposição parcial da receita cíclica.

| Especificação | Estratégia | Fator de escala | Exportações (% PIB) | Importações (% PIB) | Contribuições (R$ bi) | IRPF (R$ bi) | Receita cíclica macro (R$ bi) |
|---|---|---|---|---|---|---|---|
| P1 | A | 1,10 | −0,050 | 0,136 | 3,2 | −0,1 | 14,7 |
| P1 | A_res60 | 1,09 | −0,078 | 0,156 | 3,8 | −0,0 | 17,3 |
| P1 | A_res100 (ef. 76) | 1,09 | −0,085 | 0,161 | 3,9 | −0,0 | 17,9 |
| P1 | B | 1,06 | −0,019 | 0,193 | 5,7 | 0,1 | 25,4 |
| P1 | C | 1,08 | −0,087 | 0,184 | 4,6 | −0,0 | 20,9 |
| P1 | C_sem_piso | 1,08 | −0,085 | 0,194 | 4,9 | −0,0 | 22,3 |
| P2 | A | 1,09 | −0,046 | 0,157 | 3,8 | −0,0 | 17,3 |
| P2 | A_res60 | 1,09 | −0,074 | 0,179 | 4,4 | −0,0 | 20,3 |
| P2 | A_res100 (ef. 76) | 1,09 | −0,080 | 0,184 | 4,6 | −0,0 | 21,0 |
| P2 | B | 1,06 | −0,015 | 0,241 | 7,2 | 0,1 | 31,7 |
| P2 | C | 1,08 | −0,082 | 0,224 | 5,8 | 0,0 | 26,3 |
| P2 | C_sem_piso | 1,08 | −0,080 | 0,232 | 6,0 | 0,0 | 27,3 |
| P3_theta05 | A | 1,15 | 0,006 | 0,075 | 1,3 | −0,1 | 6,5 |
| P3_theta05 | A_res60 | 1,13 | −0,028 | 0,086 | 1,6 | −0,1 | 8,0 |
| P3_theta05 | A_res100 (ef. 76) | 1,12 | −0,036 | 0,089 | 1,7 | −0,1 | 8,4 |
| P3_theta05 | B | 1,06 | −0,016 | 0,190 | 5,6 | 0,1 | 25,0 |
| P3_theta05 | C | 1,10 | −0,042 | 0,121 | 2,7 | −0,1 | 12,6 |
| P3_theta05 | C_sem_piso | 1,10 | −0,031 | 0,135 | 3,1 | −0,0 | 14,5 |
| P3_theta025 | A | 1,14 | −0,013 | 0,079 | 1,4 | −0,1 | 7,1 |
| P3_theta025 | A_res60 | 1,12 | −0,047 | 0,091 | 1,8 | −0,1 | 8,6 |
| P3_theta025 | A_res100 (ef. 76) | 1,12 | −0,054 | 0,094 | 1,9 | −0,1 | 9,0 |
| P3_theta025 | B | 1,06 | −0,018 | 0,196 | 5,8 | 0,1 | 25,8 |
| P3_theta025 | C | 1,09 | −0,054 | 0,136 | 3,2 | −0,0 | 14,6 |
| P3_theta025 | C_sem_piso | 1,09 | −0,050 | 0,141 | 3,3 | −0,0 | 15,3 |

Fator de escala médio (todas as estratégias, especificações, λ e janelas): 1,09 (mín. 0,92, máx. 1,46). Fora de 0,7–1,3 em 2 de 288 casos, todos com Δ hiato médio perto de zero (componentes que se cancelam), em que a razão fica instável; não há incoerência sistemática entre os multiplicadores do bloco fiscal e os da matriz.

Efeito sobre os setores mais expostos ao câmbio (VA pelo canal das exportações, R$ milhões de 2015, trimestres 1–16, λ = 0,7, P1):

| Grupo | A | A_res60 | A_res100 (ef. 76) | B | C | C_sem_piso |
|---|---|---|---|---|---|---|
| Agropecuária | −424 | −669 | −720 | −148 | −701 | −688 |
| Indústrias extrativas | −235 | −371 | −399 | −82 | −389 | −381 |
| Indústrias de transformação | −671 | −1059 | −1139 | −235 | −1110 | −1089 |

Gráficos: `graficos/5_emprego_setores.png`, `graficos/6_mapa_va_setorial.png`.

## 4. Robustez × custo recessivo

λ\*₇₀ pela dívida líquida (banda e teto; 1,01 = não atinge 70%) e perda até a eleição (mediana, λ = 0,7):

| Especificação | Estratégia | λ\*₇₀ banda | λ\*₇₀ teto | Perda 1–16 |
|---|---|---|---|---|
| P1 | S | não atinge | não atinge | 0,00 |
| P1 | A | não atinge | não atinge | −2,33 |
| P1 | A_res60 | 0,99 | 0,78 | −2,74 |
| P1 | A_res100 (ef. 76) | 0,95 | 0,76 | −2,84 |
| P1 | B | não atinge | não atinge | −3,95 |
| P1 | C | não atinge | 0,93 | −3,49 |
| P1 | C_sem_piso | 0,88 | 0,70 | −3,55 |
| P2 | S | não atinge | não atinge | 0,00 |
| P2 | A | não atinge | 0,99 | −2,75 |
| P2 | A_res60 | 0,94 | 0,71 | −3,22 |
| P2 | A_res100 (ef. 76) | 0,91 | 0,66 | −3,33 |
| P2 | B | não atinge | não atinge | −5,03 |
| P2 | C | 0,99 | 0,90 | −4,30 |
| P2 | C_sem_piso | 0,88 | 0,63 | −4,35 |
| P3_theta05 | S | não atinge | não atinge | 0,00 |
| P3_theta05 | A | 0,96 | 0,65 | −1,03 |
| P3_theta05 | A_res60 | 0,90 | 0,63 | −1,27 |
| P3_theta05 | A_res100 (ef. 76) | 0,89 | 0,62 | −1,33 |
| P3_theta05 | B | não atinge | não atinge | −3,92 |
| P3_theta05 | C | 0,87 | 0,84 | −2,01 |
| P3_theta05 | C_sem_piso | 0,89 | 0,60 | −2,30 |
| P3_theta025 | S | não atinge | não atinge | 0,00 |
| P3_theta025 | A | 0,87 | 0,52 | −1,13 |
| P3_theta025 | A_res60 | 0,82 | 0,50 | −1,37 |
| P3_theta025 | A_res100 (ef. 76) | 0,81 | 0,49 | −1,43 |
| P3_theta025 | B | não atinge | não atinge | −4,05 |
| P3_theta025 | C | 0,82 | 0,79 | −2,35 |
| P3_theta025 | C_sem_piso | 0,81 | 0,47 | −2,44 |

Gráfico: `graficos/3_fronteira_robustez_custo.png`.

## 5. Dados e coeficientes

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

## 6. Limitações

- Os multiplicadores por item vêm da literatura e têm incerteza grande; os resultados de composição devem ser lidos pelas faixas de sensibilidade. No modelo, o multiplicador acumulado em 4 trimestres de uma medida permanente é cerca de 0,7 × m: os valores centrais ficam abaixo das estimativas SVAR mais altas para investimento e transferências.
- A matriz de 2015 supõe coeficientes técnicos fixos; a atualização para 2025 corrige o emprego, não a estrutura de insumos.
- A credibilidade de cada composição do pacote não é modelada.
- A lei de Okun é uma relação reduzida e pode variar com a formalidade do mercado de trabalho.
- O bloco setorial não retroalimenta o modelo macro: a distribuição setorial não altera inflação, câmbio, reservas ou dívida; o efeito sobre a balança comercial é reportado, não realimentado.
- Sem a POF por faixa de renda, os itens com canal no consumo de alta, média e baixa renda usam o vetor total de consumo das famílias: a distribuição setorial dos itens de consumo é a mesma.
- O juro real longo divide-se meio a meio entre consumo e investimento (premissa).
- A alíquota efetiva do IRPF é aplicada ao rendimento médio de cada setor; com a isenção até R$ 5.000 de 2026, quase todos os setores ficam com alíquota zero, o que subestima o IR da massa salarial adicional.
- Os coeficientes de emprego de 2025 usam o conceito da PNAD (pessoas no trabalho principal); os da TRU 2015, ocupações.
- A referência S também sofre com a falta de ajuste (prêmio e juro longo maiores): a "perda" de cada estratégia contra S inclui esse ganho de credibilidade, decomposto na seção 1.
