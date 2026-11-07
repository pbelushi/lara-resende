# As duas credibilidades baixas: λ_fiscal travado em 0,2/0,35/0,5 e λ_π ~ U(0,2; 0,5)

Motivação: as medidas do Focus (seções 2.6 e 2.7 da aba de credibilidade) indicam que, em 2024–26, as duas
credibilidades estão baixas ao mesmo tempo: c da meta de inflação entre 0,17 e 0,34 e expectativa de primário
abaixo do piso da meta.

Código: `python -m src.credibilidades_separadas --lf 0.2,0.35,0.5 --lp 0.2,0.5 --lp-grade 0.2,0.3,0.4,0.5
--tag ambas_0_2_a_0_5 --pular-validacao`; resumo: `python -m src.credibilidades_baixas_relatorio`.
Choques com seed 42; λ_π sorteado por trajetória com seed 2027; combinações com seed 11 (as mesmas 4.000
sorteadas na rodada com λ_π ~ U(0,5; 1,0)), 1.500 mutações e 34 finalistas com N = 1.000 em P1, P2 e P3.

## Resultados

1. **Teto de cerca de 50% de sucesso pela banda** (P1 e P2) e de 85% pelo teto. Nenhuma das 5.504
   combinações passa de 50% pela banda com λ_fiscal = 0,35. O limite é a dispersão da inflação com
   expectativas pouco ancoradas, como na busca da diagonal (47% com λ = 0,3).
2. **λ_fiscal continua quase irrelevante:** de 0,2 a 0,5, o sucesso das melhores combinações muda em até
   2 pontos. Quem decide é λ_π: as estratégias do paper vão de 18%–25% com λ_π = 0,2 a cerca de 50% com
   λ_π = 0,5 (C sem piso e A com reservas, P2).
3. **O choque não compra sucesso.** Entre as finalistas, os pacotes de choque (4% a 6% do PIB, início
   imediato, cortes em transferências, pisos e investimento, multiplicador médio de 0,57 a 0,80) chegam a
   50% pela banda em P2, com atividade de 2,3 a 7,6 pontos do PIB de um ano abaixo da referência sem ajuste
   até 2030. Os pacotes graduais de baixo custo (r00529, m01275, r02649, r01394, m00232: 4,3% a 6,0% do PIB,
   multiplicador de 0,39 a 0,51, concentrados em renúncias regressivas, benefícios setoriais, subsídios,
   previdência militar, emendas e custeio, sem corte de transferências, início no 1º–4º trimestre e rampa de
   até 16 trimestres, alívio condicionado sem piso com alvo de 6,6%–6,8%) chegam a 47%–49%, com atividade
   de 1,8 a 2,6 pontos **acima** da referência. Mesma probabilidade de sucesso, diferença de 4 a 10 pontos
   do PIB na atividade.
4. **Com credibilidade baixa, o pacote precisa ser maior.** O perfil de menor custo exigia 3,2%–4,0% do
   PIB com λ_π entre 0,5 e 1,0; agora fica entre 4,3% e 6,0%. O pacote de 3,1% (r00311) mantém a
   atividade 3 pontos acima da referência, mas o sucesso cai a 33% pela banda (51% pelo teto).
5. **Em P3 (FTPL), nada funciona pela banda:** até 36% nos pacotes de choque e 0%–6% nos graduais.
6. **O que explica o custo em atividade** (correlação com a diferença de PIB contra S): multiplicador médio
   (−0,54), cortes em transferências (−0,52) e investimento (−0,51), tamanho (−0,50) e pisos (−0,33); rampa
   mais longa (+0,46). O sucesso depende quase só do tamanho (+0,92).

## Leitura

Com as duas credibilidades baixas, nenhuma estratégia passa de uma chance em duas pela banda. Mas a escolha
entre choque e gradualismo deixa de ser uma troca entre eficácia e custo social: as duas famílias têm a
mesma probabilidade de sucesso, e só a gradual preserva a atividade. O argumento contra o fatalismo do
choque sobrevive em baixa credibilidade; o que muda é o tamanho necessário do pacote e o teto de sucesso,
que só sobe com a credibilidade da meta.

## Limitações

As mesmas das rodadas anteriores: λ_π e λ_fiscal exógenos e independentes; tetos por item; sem novos
tributos; credibilidade da composição não modelada. A distribuição U(0,2; 0,5) é uma leitura das medidas de
pesquisa, que divergem do λ efetivo (seções 2.6 e 2.7).
