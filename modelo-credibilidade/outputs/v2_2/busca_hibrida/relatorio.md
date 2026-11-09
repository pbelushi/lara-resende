# Busca híbrida com λ endógeno: início concentrado e só cortes de baixo multiplicador

Código: `src/busca_hibrida.py`, `src/busca_hibrida_figura.py`. Regra central de λ endógeno (seção 2.9);
λ_π inicial ~ U(0,2; 0,5), λ_fiscal inicial 0,2/0,35/0,5; choques seed 42; combinações seed 23.

Espaço híbrido: itens com multiplicador ≤ 0,6 (renúncias regressivas, benefícios setoriais, subsídios,
verbas acima do teto, previdência militar, custeio), 2% a 5,5% do PIB, início no 1º ou 2º trimestre, rampa de
1 a 6 trimestres. Controle: 1.500 combinações do espaço irrestrito, com a mesma regra. 3.000 híbridos +
1.500 irrestritos + 1.500 mutações híbridas (N = 200, P2); 38 finalistas novas + as 34 da busca anterior
com N = 1.000, P1/P2/P3, regras central e simétrica.

## Resultados (regra central)

| Família | Sucesso P2 (média) | Sucesso P1 (média) | Atividade P2 até 2030 |
|---|---|---|---|
| Híbrido | 34% (até 36%) | 35% (até 36%) | +1,1 (0 a +2,9) |
| Choque (busca anterior) | 34% (até 36,5%) | 25% | −4,3 (−2,4 a −7,9) |
| Gradual longo (busca anterior) | 26% (até 31%) | 28% | +2,1 |
| Espaço irrestrito (controle) | 35% (até 36%) | 29% | −2,6 |
| Estratégias do paper | 21% | 23% | +0,2 |

1. **O híbrido iguala o choque em sucesso sem recessão.** Em P2, os melhores híbridos chegam a 36%, contra
   36,5% do melhor choque, com atividade entre zero e +2,9 pontos do PIB de um ano contra a referência, em vez
   de −2,4 a −7,9. Em P1, o híbrido é a melhor família (35%–36%, contra 25%–29% do choque).
2. **A troca entre eficácia e custo social some em P1 e quase some em P2.** Dentro dos híbridos, a regra de
   Taylor dá 1 ponto a mais de sucesso (36% contra 35%) e o alívio condicionado sem piso, cerca de 2 pontos a
   mais de atividade.
3. **Perfis da fronteira:**
   - m00349: 5,5% do PIB (renúncias 2,5; benefícios 1,0; custeio 0,8; subsídios 0,6; previdência militar 0,4;
     verbas acima do teto 0,2), início no 1º trimestre, rampa de 3, regra de Taylor, sem reservas: 36% em P2 e
     35% em P1, atividade ≈ 0;
   - m00998: 4,7% do PIB (mesmos itens, sem custeio), início e rampa de 1 trimestre, alívio condicionado sem
     piso (alvo de 7,2%), venda de US$ 93 bi em reservas: 35% em P2 e 36% em P1, atividade +2,2 a +2,3;
   - m01474: 3,6% do PIB, mesma regra: 29% em P2 e 34% em P1, atividade +2,5.
4. **O controle irrestrito confirma o desenho:** suas melhores combinações também concentram o ajuste no
   início (início no 1º–3º trimestre, rampa de 1 a 8), mas, quando usam itens de multiplicador alto, pagam com
   atividade (−1,4 a −9,5) o mesmo sucesso.
5. **O teto não muda:** cerca de 36% pela banda em P2 (45%–46% com recuperação simétrica), e λ_π continua
   caindo em média (0,26 no 4º ano). O híbrido não interrompe a erosão da credibilidade; apenas a reduz tanto
   quanto o choque, sem o custo do choque.
6. **Em P3, todos falham pela banda** (híbridos até 5%, choques até 9%).

## Leitura

Com λ endógeno, o que importa é a velocidade com que a inflação volta ao intervalo, não o tamanho da
recessão. Um ajuste concentrado no início, mas feito com cortes de baixo multiplicador (renúncias
regressivas, benefícios setoriais, subsídios, previdência militar), entrega a mesma desinflação inicial e a
mesma preservação de credibilidade que o choque, sem a contração da atividade. O custo é o tamanho: 4,5% a
5,5% do PIB, perto do limite dos tetos por item, com o desafio político de aprovar de uma vez cortes em
renúncias e benefícios.

## Limitações

As das seções 2.8 e 2.9, mais: a busca esbarra no teto conjunto dos itens de baixo multiplicador (5,5% do
PIB), de modo que o tamanho ótimo pode ser maior que o permitido; a regra de λ não premia a composição do
ajuste nem a sua aprovação rápida, só o resultado.
