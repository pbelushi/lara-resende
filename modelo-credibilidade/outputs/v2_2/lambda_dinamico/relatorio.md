# λ endógeno: a credibilidade reage aos resultados

Código: `src/lambda_dinamico_estimacao.py` (estimação), `src/modelo.py` (`atualizar_lambda`, desligada por
padrão), `src/lambda_dinamico_aplicacao.py` (aplicação) e `src/lambda_dinamico_figura.py`.

## Regra

Revisão a cada 4 trimestres, assimétrica:

- Δλ_π = β⁺_π · max(g_π, 0) + β⁻_π · min(g_π, 0), com g_π = 1,5 − |inflação média do ano − meta|;
- Δλ_f = β⁺_f · max(g_f, 0) + β⁻_f · min(g_f, 0), com g_f = primário médio do ano − primário anunciado.

## Estimação (Brasil, 2005–2025)

| Coeficiente | Estimativa | Base |
|---|---|---|
| β⁻_π (por p.p. de inflação fora do intervalo) | 0,071 (p = 0,04) | Índice de de Mendonça do Focus, painel trimestral, HAC, 80 obs.; painel anual: 0,113 (p = 0,11) |
| β⁺_π (por p.p. de folga dentro do intervalo) | 0,028 (p = 0,59) | Idem; anual: 0,035. No máximo +0,04 por ano |
| β_f (por p.p. de primário) | 0,10, simétrico | Calibrado: queda de 0,75 do λ_fiscal efetivo em 2020, com primário 7,7 p.p. abaixo do plano |

Com o c do Focus (em vez do índice de de Mendonça), a estimação de λ_π não é significativa. A medida fiscal do
Focus dá o sinal trocado (descumprir a meta eleva a credibilidade medida), porque as metas são revistas depois
dos descumprimentos; por isso λ_fiscal foi calibrado no λ efetivo das validações. O efeito cruzado do fiscal
sobre λ_π também sai com sinal trocado e entra só como sensibilidade.

## Aplicação às 34 finalistas da busca com as duas credibilidades baixas

λ_π inicial ~ U(0,2; 0,5) por trajetória, λ_fiscal inicial 0,2/0,35/0,5, N = 1.000, P1/P2/P3.

| P2, sucesso pela banda (média da família) | λ fixo | Central | Simétrica | Metade | Anual | Cruzada |
|---|---|---|---|---|---|---|
| Choque | 50% | 34% | 43% | 38% | 29% | 27% |
| Gradual de baixo custo | 44% | 26% | 33% | 31% | 22% | 21% |
| Estratégias do paper | 30% | 21% | 29% | 24% | 19% | 18% |

1. **A credibilidade se deteriora em todas as famílias.** Com a regra central, λ_π médio cai de 0,35 para
   0,21–0,26 em quatro anos e para 0,10–0,14 em dez; só 5%–7% das trajetórias terminam com λ_π ≥ 0,5. O
   motivo: o ponto de partida (inflação de 4,6%, no limite do intervalo) e a dispersão da inflação com λ_π
   baixo produzem anos fora do intervalo com frequência, e cada p.p. fora custa 2,5 vezes o que um p.p. de
   folga devolve. Mesmo com recuperação simétrica, λ_π cai (para 0,24–0,31 em dez anos).
2. **O sucesso cai cerca de um terço** (P2: de 50% para 34% no choque, de 44% para 26% no gradual). Nenhuma
   variante da regra preserva os resultados com λ fixo.
3. **O choque passa a comprar sucesso em P2, mas não em P1.** Em P2, as melhores combinações de choque chegam
   a 36% contra 31% das graduais, porque derrubam a inflação mais cedo e perdem menos credibilidade no início
   (λ_π de 0,26 contra 0,21 no 4º ano). O custo não muda: 3 a 8 pontos do PIB de um ano abaixo da
   referência até 2030, contra 1,6 a 2,5 acima nas graduais. Em P1, o gradual tem sucesso igual ou maior
   (28% contra 25%).
4. **Ajustar é melhor que não ajustar também para a credibilidade:** sem ajuste, λ_π cai mais rápido (0,20
   no 4º ano em P2).
5. **Em P3, nada funciona** (até 4% pela banda).

## Leitura

O resultado com λ fixo tratava a credibilidade como um dado. Com λ endógeno calibrado no Brasil, a
credibilidade baixa tende a se autoperpetuar: começar com inflação no limite do intervalo e expectativas
pouco ancoradas gera erros que corroem a credibilidade mais do que os acertos a reconstroem. A implicação
para o desenho é que o primeiro e o segundo anos importam desproporcionalmente: o que preserva λ_π é
entregar inflação dentro do intervalo cedo. Isso dá ao choque uma vantagem de sucesso em P2, ao custo de
um ajuste muito mais recessivo, e reforça a importância de instrumentos que elevem λ_π diretamente
(engajamento ativo do mercado, preservação da autonomia do Banco Central) em vez de depender só dos
resultados para reconstruí-lo.

## Limitações

- β⁺_π não é estatisticamente diferente de zero; a assimetria é a estimativa pontual, não um resultado firme.
- λ_fiscal calibrado em um único episódio (2020), com as variantes ×0,5, ×2 e 0,30 por p.p.
- As medidas de pesquisa divergem do λ efetivo em nível; usa-se só a sensibilidade das variações.
- A regra só olha resultados; anúncios, reformas institucionais e comunicação não mudam λ no modelo.
