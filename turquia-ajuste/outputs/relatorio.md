# Turquia, setembro de 2021: aperto tradicional ou saída heterodoxa?

Código: `src/turmodel/` (model, calibrate, search, report). Dados: `data/` (ver LEIAME; parte aproximada).

## Pergunta

Em setembro de 2021, a inflação era de 19% (meta de 5%), o juro real era zero, as reservas líquidas eram negativas
e três presidentes do banco central tinham sido demitidos. O governo cortou os juros. A alternativa clássica era o
aperto anticíclico. Havia espaço para uma terceira via: ajuste fiscal de qualidade com redução gradual dos juros,
controlando a inflação pelo fiscal? Sem reservas, não há âncora cambial: o câmbio flutua nas alternativas.

## Modelo e calibração

Modelo mensal com a mesma lógica dos casos brasileiro e argentino: λ é a fração das expectativas que segue a
âncora anunciada; é revista a cada trimestre pelos resultados (regra estimada no Brasil) e pode saltar com uma troca
institucional. Blocos de inflação (inércia de contratos anuais, expectativas, repasse cambial assimétrico, salário
mínimo, impostos indiretos), câmbio (flutuante, com fuga da moeda quando o juro real fica abaixo do neutro, ou
administrado com reservas), atividade, reservas e dívida.

Calibrado com a política observada como insumo (taxa básica, câmbio administrado fora de set–dez/2021 e
jun–jul/2023, reajustes do mínimo, impostos de 2023, KKM):

| | Inércia baixa (b1 = 0,3) | Inércia alta (b1 = 0,8) | Observado |
|---|---|---|---|
| Erro absoluto médio, inflação em 12 meses | 6,2 p.p. | 4,7 p.p. | — |
| Inflação dez/2022 | 79,6% | 69,3% | 64,3% |
| Inflação dez/2023 | 64,5% | 62,9% | 64,8% |
| Inflação dez/2024 | 44,4% | 46,2% | 44,4% |
| Inflação set/2026 | 21,5% | 23,9% | 29,7% |
| Câmbio dez/2021 (liras por dólar) | 14,5 | 14,5 | 13,6 |
| PIB 2022 / 2023 / 2024 / 2025 | 6,0 / 3,9 / 3,8 / 3,8 | 6,0 / 3,9 / 3,7 / 3,8 | 5,4 / 5,0 / 3,5 / 3,7 |

Três achados da calibração:

1. **A credibilidade inicial era quase nula** (λ0 entre 0 e 0,12) e **a guinada de 2023 quase não a elevou** (salto
   estimado em zero nas duas variantes; λ de 0,04 no fim de 2024). É o que a persistência da inflação perto de 30%
   em 2025–26, com juros de 37% a 50%, pede do modelo. As pesquisas de expectativas mostram o contrário (expectativas
   próximas das metas intermediárias): como no Brasil, a credibilidade de pesquisa e a efetiva divergem.
2. **O colapso da lira no fim de 2021 exige um mecanismo de fuga**: com o juro real abaixo do neutro, cada corte da
   taxa e cada depreciação alimentam a seguinte (ω ≈ 2,5). Com juro real no neutro ou acima, o mecanismo fica desligado.
3. **O peso da inércia não é identificado** (0,3 e 0,8 ajustam quase igualmente), daí as duas variantes. O modelo não
   reproduz a queda da inflação no 1º semestre de 2023 (gás gratuito e tarifas congeladas antes da eleição) e
   subestima a inflação de 2026 em 6 a 8 pontos.

## Busca

6.000 combinações, a partir de set/2021, com λ0 ~ U(0; 0,3): juro real ex ante (de −5% a +20%, com reação à
inflação), âncora anunciada (5% imediata ou trajetória de 12 a 60 meses), ajuste fiscal (0 a 5% do PIB,
multiplicador de 0,3 a 1,0, parcela em impostos indiretos), preços administrados reajustados pela âncora (θ até
0,4), regra do salário mínimo e compra de reservas. Sucesso: pico de inflação até 30% e inflação entre 0% e 10% em
set/2026. PIB: diferença acumulada em relação à política observada, com os mesmos choques, em pontos do PIB de um ano.

| Estratégia (inércia baixa / alta) | Sucesso | Inflação ≤ 15% em set/26 | Pico (mediana) | Inflação dez/23 | Inflação set/26 | PIB vs. observado |
|---|---|---|---|---|---|---|
| Política observada | 0% / 0% | 30% / 13% | 102% / 86% | 67% / 63% | 21% / 24% | 0 |
| Juro real zero + ajuste de qualidade + rendas | 2% / 5% | 38% / 40% | 65% / 53% | 23% / 21% | 27% / 22% | −1,4 / −1,5 |
| Só ajuste de qualidade + juro real de 3% a 2% | 4% / 9% | 54% / 50% | 47% / 38% | 20% / 21% | 13% / 15% | −3,4 / −3,3 |
| Heterodoxa: ajuste de qualidade + juro real de 3% a 2% + rendas | 5% / 16% | 61% / 64% | 42% / 33% | 17% / 16% | 10% / 10% | −3,0 / −2,8 |
| Aperto tradicional: juro real de 10% a 6% | 9% / 21% | 68% / 71% | 37% / 30% | 15% / 16% | 7% / 9% | −3,3 / −3,2 |
| Aperto tradicional + corte de demanda (2% do PIB) | 9% / 22% | 68% / 71% | 36% / 29% | 14% / 15% | 7% / 9% | −4,7 / −4,6 |
| Melhor da busca: juro real de 17% a 11%, meta de 5% imediata, administrados pela meta (θ = 0,33), sem ajuste fiscal | 25% / 57% | 77% / 92% | 25% / 21% | 7% / 7% | 6% / 6% | −4,2 / −4,0 |

Por região do espaço sorteado (sucesso médio / máximo, inércia alta): juro real médio até 2%: 2% / 12% (com
hiperinflação na mediana); de 2% a 5%: 5% / 21%; de 5% a 8%: 11% / 39%; de 8% a 11%: 23% / 50%; acima de 11%: 33% / 57%.

## Leitura

1. **Qualquer alternativa com juro real positivo teria sido muito melhor que a política adotada.** Mesmo a
   heterodoxa de referência termina 2023 com inflação de 16%–17%, contra 63%–67%.
2. **O instrumento decisivo é o juro real.** A correlação do sucesso com o juro real final é de 0,8; com o tamanho,
   a qualidade ou o tipo do ajuste fiscal, de zero. A Turquia não tinha problema fiscal (dívida de 40% do PIB,
   déficit moderado): o ajuste fiscal, de qualidade ou de demanda, custa atividade e não compra desinflação. O
   corte de demanda de 2% do PIB custa 1,4 ponto de PIB a mais, sem ganho.
3. **A terceira via pura não se sustenta.** Com juro real perto do neutro, a inflação cai devagar (10%–15% em 2026),
   o sucesso fica entre 4% e 16% e o risco de fuga da moeda é alto; com juro real zero, a inflação volta a subir.
   Isso vale mesmo com o risco de corrida pela metade (5%–20%) e com o canal de demanda três vezes mais forte.
4. **Há um complemento heterodoxo que funciona:** reajustar preços administrados pela meta. Com inércia alta, ele
   soma cerca de 10 pontos de sucesso em qualquer nível de juros e faz a diferença entre a heterodoxa (16%) e o só
   fiscal (9%). A melhor combinação da busca é um híbrido: juro real alto, meta ambiciosa anunciada de imediato e
   administrados pela meta, sem ajuste fiscal.
5. **O custo:** as alternativas bem-sucedidas custam de 3 a 4 pontos do PIB de um ano, acumulados em cinco anos,
   em relação à política observada, que produziu um boom em 2021–22 à custa de inflação de 85% e do salário real.
   O salário mínimo real termina 2026 abaixo do observado na maior parte das finalistas (20% abaixo no melhor
   cenário); só fica no mesmo nível com ganho real de 4% ou mais por reajuste e pouca indexação à meta.

## Reservas (`src/turmodel/reservas.py`, `outputs/reservas/`)

A variável de reservas da busca original não serve para comparar alternativas: a entrada autônoma calibrada
(US$ 5,5 bi por mês) reflete o regime observado e faria as reservas subirem US$ 330 bi em qualquer cenário. Aqui as
reservas seguem a regra do câmbio flutuante: só mudam quando o banco central compra. O banco central compra para
impedir que a lira se aprecie além de um piso em relação à trajetória da âncora; compra mais quem atrai capital
(juro real acima do neutro) e quem aceita menos apreciação, ao custo de menos desinflação pelo câmbio. As 6.000
combinações foram reavaliadas e 3.000 novas foram sorteadas na região de juro real positivo, com piso de −1% a +1%
ao mês (negativo = compra mesmo sem pressão de apreciação). Ponto de partida: −US$ 35 bi. Referência observada
(dados aproximados): −60 em 2023, +55 no fim de 2025.

| Cenário (inércia baixa / alta) | Sucesso | Reservas dez/23 | Reservas set/26 | Positivas em set/26 | Meses até positivas | Sucesso e reservas ≥ 50 | Inflação set/26 | PIB vs. observado |
|---|---|---|---|---|---|---|---|---|
| Juro real zero + ajuste de qualidade + rendas | 2% / 5% | −24 / −24 | −9 / −9 | 29% / 22% | nunca | 0% | 27% / 22% | −1,4 / −1,5 |
| Heterodoxa (juro real de 3% a 2%) | 5% / 16% | −21 / −20 | +1 / −1 | 53% / 46% | 60 / nunca | 0% | 10% / 10% | −3,0 / −2,9 |
| Aperto tradicional (juro real de 10% a 6%) | 9% / 21% | −16 / −14 | +9 / +9 | 78% / 86% | 50 | 1% / 0% | 7% / 9% | −3,3 / −3,2 |
| Melhor da busca original (c03002) | 25% / 57% | +6 / +10 | +46 / +50 | 100% | 24 / 21 | 8% / 28% | 6% / 6% | −4,2 / −4,0 |
| Melhor com reservas ≥ 50 (r01540): juro real de 16% a 10,5%, meta de 5% imediata, θ = 0,31, sem ajuste fiscal, compra de reservas mais agressiva (piso de −0,5% ao mês) | 18% / 44% | +11 / +17 | +58 / +67 | 100% | 21 / 18 | 16% / 44% | 10% / 9% | −4,2 / −4,1 |

1. **O melhor cenário recompõe as reservas**: positivas em cerca de dois anos (meados de 2023, quando as observadas
   estavam em −60) e perto de +50 em set/2026, sem controles nem swaps.
2. **Quem recompõe reservas é o juro real**: correlação de 0,7 entre o juro real final e as reservas de 2026. Com
   juro real perto do neutro ou abaixo, não há entrada de capital para comprar: as reservas ficam em torno de zero
   ou negativas.
3. **Há uma troca entre reservas e desinflação**: comprar mais agressivamente leva as reservas a +60/+65, mas a
   inflação termina em 9%–10% em vez de 6%, e o sucesso cai de 25%/57% para 18%/44%. O custo de PIB é o mesmo.
4. O ajuste fiscal não ajuda as reservas (correlação de −0,1).

Limitações específicas: não há custo de esterilização das compras; a eficácia da intervenção (ν) foi calibrada
nas vendas de 2022–23 e aplicada de forma simétrica às compras; o modelo não tem prêmio de risco que caia com as
reservas, o que subestima o ganho de recompô-las.

## Crédito direcionado para investimento (`src/turmodel/credito.py`, `outputs/credito/`)

Pergunta: dá para manter o aperto monetário que funciona e sustentar o PIB com uma linha de crédito subsidiado
para investimento, como o ajuste de baixo multiplicador fez no caso brasileiro?

Alavanca: uma fração ψ do gasto sensível a juros toma crédito ao juro real neutro (2%); o Tesouro paga a diferença
para o juro de mercado sobre o estoque da linha (desembolso de ψ × 12% do PIB por ano, amortização de 25% ao ano);
25% do crédito vaza para a compra de dólares e enfraquece o efeito do juro sobre o câmbio. Sem efeito do
investimento sobre o PIB potencial.

Melhor cenário da busca, com a linha (inércia baixa / alta):

| ψ (desembolso anual) | Sucesso | Inflação set/26 | PIB vs. observado | Subsídio médio / pico (% do PIB ao ano) | Dívida set/26 (% do PIB) | Reservas set/26 |
|---|---|---|---|---|---|---|
| 0 (sem linha) | 25% / 57% | 6,0% / 6,2% | −4,2 / −4,0 | 0 | 48 / 47 | +46 / +50 |
| 0,2 (2,4% do PIB) | 25% / 56% | 6,2% / 6,3% | −3,7 / −3,6 | 0,6 / 1,9 e 0,5 / 1,6 | 51 / 49 | +42 / +46 |
| 0,4 (4,8% do PIB) | 24% / 56% | 6,4% / 6,4% | −3,3 / −3,2 | 1,2 / 3,8 e 1,0 / 3,2 | 54 / 52 | +39 / +43 |
| 0,6 (7,2% do PIB) | 24% / 55% | 6,5% / 6,6% | −2,9 / −2,9 | 1,8 / 5,8 e 1,6 / 4,8 | 57 / 55 | +35 / +40 |
| 0,8 (9,6% do PIB) | 23% / 55% | 6,7% / 6,8% | −2,5 / −2,5 | 2,4 / 7,7 e 2,1 / 6,5 | 60 / 58 | +32 / +36 |

1. **A linha funciona no sentido pedido**: quase não mexe na desinflação nem na probabilidade de sucesso, porque a
   desinflação turca vem do câmbio e das expectativas, não da demanda. Isso vale com o canal de demanda três vezes
   mais forte (sucesso cai 1 a 4 pontos).
2. **Mas recupera só uma parte do PIB, e caro**: cada 0,2 de ψ devolve 0,4 ponto de PIB e custa cerca de 3 pontos
   de dívida em cinco anos. Com ψ = 0,4, recuperam-se 0,8 ponto dos 4, com subsídio médio de 1,1% do PIB ao ano.
3. **A razão**: a maior parte da diferença de PIB em relação ao observado não é contração causada pelo juro
   acima do neutro; é o estímulo do juro real de −40% que deixa de existir. No melhor cenário, sem linha, o PIB
   cresce 3,5% ao ano em 2022–23 (4,0%–4,1% no observado) e o hiato mínimo é de −1,2%: não há recessão. Uma linha
   ao juro neutro não repõe o superaquecimento; uma linha abaixo do neutro seria a política observada com outro nome.
4. **O vazamento é o risco**: com 50% do crédito indo para o dólar e ψ = 0,8, o sucesso cai de 25%/57% para
   20%/51% e as reservas de +46/+50 para +19/+24.
5. A busca com a linha (3.000 combinações) não desloca o ótimo: o juro real continua em 9%–11% e o melhor sucesso
   não sobe. Entre as combinações com sucesso médio acima de 30%, as de menor custo de PIB (−2,1 a −2,5) usam
   ψ de 0,7 a 0,8 e juro real final de 7% a 10%.

Limitações específicas: o volume da linha (12% do PIB de gasto sensível a juros) e a sensibilidade da atividade ao
juro (calibrada, baixa) determinam a relação custo-benefício; se a atividade for mais sensível ao juro do que o
modelo estima, a linha rende mais. Não há efeito do investimento sobre a capacidade produtiva nem sobre as
importações. O subsídio é de equalização (os bancos emprestam, o Tesouro paga a diferença); com funding do Tesouro,
a dívida bruta subiria também pelo estoque da linha.

## Choque de juros (`src/turmodel/choque.py`, `outputs/choque/`)

Pergunta: um choque de juros nos primeiros 6 ou 12 meses, com redução gradual depois, concentraria o custo no
primeiro ano e permitiria retomar o ritmo nos seguintes?

Grade sobre o melhor cenário (240 combinações): juro real do choque de 15% a 30%, mantido por 6 ou 12 meses, queda
em 12 ou 24 meses até um juro real final de 2% (neutro) a 11%; com corte por calendário (reação 0) ou condicionado
à queda da inflação (reação 0,5 e 0,95).

| Cenário (inércia baixa / alta) | Sucesso | Inflação dez/23 | Inflação set/26 | PIB 2022 / 2023 / 2024 / 2025 | Nível do PIB vs. observado: dez/22, dez/24, set/26 | Juro real no último ano | Reservas set/26 |
|---|---|---|---|---|---|---|---|
| Política observada | 0% | 67% / 63% | 21% / 24% | 5,9 / 3,9 / 3,7 / 3,8 | 0 | 14% / 11% | — |
| Melhor da busca (juro real de 17% a 11% em 27 meses) | 25% / 57% | 7% / 7% | 6% / 6% | 4,9 / 3,5 / 4,3 / 4,5 | −1,5 / −0,7 / 0,0 | 15% / 14% | +46 / +50 |
| Choque de 30% por 12 meses, volta a 11% | 26% / 58% | 5% / 5% | 6% / 6% | 4,8 / 3,4 / 4,3 / 4,6 | −1,6 / −0,8 / 0,0 | 15% / 14% | +59 / +67 |
| Choque de 30% por 12 meses, corte até 4% condicionado à inflação | 20% / 44% | 6% / 6% | 9% / 9% | 4,8 / 3,5 / 4,4 / 4,6 | −1,6 / −0,6 / +0,1 | 12% / 10% | +49 / +55 |
| Choque de 30% por 12 meses, corte até 4% por calendário | 13% / 26% | 6% / 6% | 16% / 14% | 4,8 / 3,5 / 4,4 / 4,8 | −1,6 / −0,5 / +0,4 | 5% / 4% | +34 / +41 |
| Choque de 30% por 12 meses, corte até o neutro por calendário | 8% / 13% | 6% / 6% | 43% / explosiva | 4,8 / 3,5 / 4,5 / 5,0 | −1,6 / −0,5 / +0,7 | 0% / negativo | +29 / +34 |

1. **O perfil de PIB que o choque buscaria já é o do melhor cenário**: a perda fica em 2022–23 (nível 1,5% abaixo
   do observado no fim de 2022), o crescimento de 2024–25 supera o observado (4,3%–4,5% contra 3,7%–3,8%) e o nível
   do PIB empata em 2026. Os "4 pontos" de custo são a área entre as trajetórias, não uma perda permanente.
2. **O choque acelera a desinflação** (5% em vez de 7% no fim de 2023) e as reservas, mas não eleva o sucesso
   (26%/58% contra 25%/57%) nem reduz o custo: o primeiro ano é quase igual, porque a atividade turca reage pouco ao juro.
3. **O que não funciona é a segunda metade da proposta, cortar depois por calendário.** A inflação volta: 14%–16%
   com juro real final de 4% e descontrole com o neutro. A credibilidade não se recompõe com a desinflação
   (λ continua perto de zero em 2026), então é o juro real, via câmbio, que segura a inflação.
4. Corte condicionado à inflação é o meio-termo: o juro só cai se a inflação cair. Ele entrega 9% em 2026 com
   sucesso de 20%/44%, e o juro real acaba em 10%–12%.
5. Sensibilidade: se o choque comprasse um salto imediato de credibilidade de 0,6, o corte por calendário até 4%
   daria sucesso de 24%/33% e inflação de 12% em 2026: melhor, mas ainda abaixo de manter o juro alto. O salto se
   perde porque a inflação do primeiro ano fica longe da meta de 5%.

Limitação central: a conclusão depende da regra de credibilidade (ganho lento, estimado no Brasil; na calibração
turca, a guinada de 2023 também não elevou λ). Se um choque bem executado reancorasse as expectativas de forma
duradoura, o corte posterior seria viável; o modelo não tem evidência de que isso aconteça.

## Comparação com Brasil e Argentina

Nos três países, o ajuste só funciona quando ataca a fonte da instabilidade nominal: a dívida e a indexação no
Brasil, as reservas e o fiscal na Argentina, o juro real negativo e a fuga da moeda na Turquia. A reindexação de
preços administrados à meta ajuda nos três. O ajuste fiscal de baixo multiplicador, decisivo no Brasil e melhor
que a motosserra na Argentina, é irrelevante onde o problema não é fiscal.

## Limitações

- Modelo estilizado, com dois ótimos de calibração e vários parâmetros fixados por não identificação (hiato →
  inflação, reversão do câmbio real, repasse do salário mínimo). O canal fiscal sobre a inflação é só o de demanda;
  não há canal fiscal de expectativas. A conclusão sobre o fiscal sobrevive ao triplo do coeficiente de demanda.
- O mecanismo de fuga da moeda é identificado por quatro meses (set–dez/2021).
- Os choques do modelo são grandes (o desvio-padrão vem do resíduo da calibração), o que baixa todas as
  probabilidades de sucesso; a ordenação entre estratégias é mais confiável que os níveis.
- As reservas das alternativas não são confiáveis (a entrada autônoma calibrada reflete o regime observado).
- Dados: primário, dívida, reservas líquidas e reajustes do mínimo são aproximados; a inflação de mai–set/2025 é de
  memória. A inflação oficial é contestada (o grupo ENAG calcula números maiores); o modelo usa a oficial.
- A regra de revisão de λ é a estimada no Brasil.
