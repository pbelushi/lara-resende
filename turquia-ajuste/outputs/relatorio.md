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
   A regra do salário mínimo pode preservar o poder de compra: nas finalistas com ganho real de 3% a 4% por reajuste,
   o mínimo real termina 2026 igual ao observado.

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
