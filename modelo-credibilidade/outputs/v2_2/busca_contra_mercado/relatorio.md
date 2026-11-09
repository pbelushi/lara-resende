# Busca contra o mercado: o que funciona sem o apoio majoritário do mercado

Código: `src/busca_contra_mercado.py`, `src/busca_contra_mercado_theta.py`, `src/busca_contra_mercado_figura.py`;
alavanca nova em `src/modelo.py` e `src/inflacao.py` (`indexacao_meta`, desligada por padrão).

## Cenário

- Mercado minoritário: λ_π ~ U(0; 0,3) por trajetória; λ_fiscal 0/0,15/0,3.
- Mercado hostil: pune erros (−0,071 por p.p. de inflação fora do intervalo; −0,10 por p.p. de primário abaixo do
  anunciado) e não premia acertos.
- Sem regra fiscal crível nem ganho institucional.

## Instrumento novo: indexação à meta

Uma fração θ da inércia inflacionária passa a ser reajustada pela meta em vez da inflação passada (regra do
salário mínimo e dos benefícios, preços administrados, contratos do governo), em rampa de 4 trimestres. É a
lógica da inflação inercial de Arida e Lara Resende (1985): com expectativas que não se ancoram no anúncio, a
inflação tem raiz unitária (inércia + expectativas adaptativas = inflação passada), e só quebrar a indexação
a devolve à meta. O instrumento depende de lei e de decisões administrativas do governo, não da crença do
mercado.

## Resultados

Triagem (6.000 combinações, P2, mercado hostil), sucesso pela banda (média / máximo):

| θ | Média | Máximo | Máximo pelo teto |
|---|---|---|---|
| 0 | 8% | 19% | 67% |
| 0–0,1 | 11% | 33% | 79% |
| 0,1–0,2 | 21% | 45% | 84% |
| 0,2–0,3 | 33% | 58% | 87% |
| 0,3–0,4 | 50% | 66% | 89% |

Curva por θ (N = 1.000, mercado hostil), sucesso pela banda P2 / P1:

| Pacote | θ = 0 | 0,1 | 0,2 | 0,3 | 0,4 |
|---|---|---|---|---|---|
| Híbrido 5,5% do PIB, Taylor | 21% / 22% | 35% / 38% | 48% / 50% | 60% / 60% | 69% / 69% |
| Híbrido 4,1% do PIB, alívio condicionado | 18% / 21% | 30% / 34% | 43% / 46% | 56% / 57% | 66% / 66% |
| Estratégia A com reservas (paper) | 9% / 13% | 16% / 23% | 24% / 33% | 34% / 42% | 43% / 51% |
| Estratégia C sem piso (paper) | 7% / 10% | 13% / 20% | 21% / 30% | 30% / 40% | 39% / 50% |

Pacotes:
- Híbrido 5,5% (m01231): renúncias regressivas 2,5; benefícios setoriais 1,0; custeio 0,8; subsídios 0,6;
  previdência militar 0,4; verbas acima do teto 0,2 (% do PIB), início no 2º trimestre em uma etapa, regra de
  Taylor, venda de US$ 69 bi em reservas, alongamento da dívida. Atividade até 2030: ≈ 0 (P2) a +0,1 (P1).
- Híbrido 4,1% (m00295): renúncias 2,5; benefícios 1,0; subsídios 0,6; início imediato; alívio condicionado sem
  piso (alvo de 6,7%); US$ 80 bi em reservas. Atividade: +2,3 a +2,6.

Custo distributivo (perda real acumulada 2027–2030 de um rendimento reajustado integralmente pela meta,
mediana; P2, mercado hostil): híbrido 4,1% de 3,2% (θ = 0) a 1,2% (θ = 0,4); híbrido 5,5% perto de zero; nas
estratégias do paper, de 4% a 10%. Quanto maior θ, menor a perda, porque a inflação converge mais rápido; no
percentil 90, de 5% a 17%.

## Leitura

1. Sem a indexação à meta, nenhum pacote funciona contra o mercado: o máximo pela banda é de cerca de 20%
   (até 78% pelo critério só de teto, com o híbrido de 5,5% do PIB).
2. Com o mercado hostil, o instrumento decisivo não é fiscal: é quebrar a inércia por lei. O sucesso passa de
   50% a partir de θ ≈ 0,2 com o híbrido de 5,5% e de θ ≈ 0,25 com o de 4,1%, e chega a 66%–69% com θ = 0,4 —
   tanto quanto o melhor resultado com o mercado a favor (λ_π entre 0,5 e 1,0, seção 2.3).
3. O ajuste fiscal continua necessário: com o mesmo θ, as estratégias do paper (2,7% do PIB) ficam 20 a 25
   pontos abaixo dos híbridos.
4. Em P3 (FTPL), nada funciona.

## Limitações

- θ não é calibrado em dados. Os preços administrados pesam cerca de um quarto do IPCA e o salário mínimo
  afeta parte dos serviços, mas nem todos os reajustes são controláveis (contratos de concessão indexados,
  preços livres). θ = 0,2 exige reindexar à meta o salário mínimo, os benefícios previdenciários e
  assistenciais e os preços administrados federais; θ = 0,4 é um limite superior.
- O modelo não tem efeito de θ sobre as contas públicas (reajustar benefícios pela meta reduz o gasto quando a
  inflação está acima dela) nem a perda de consumo dos beneficiários; ambos os sinais ajudariam e pesariam,
  respectivamente.
- A regra hostil supõe que o mercado nunca premia; o λ_π de pesquisa e o efetivo divergem (seções 2.6–2.7).

## Adendo: reindexação só das tarifas reguladas (salário mínimo e aluguéis pela regra atual)

Código: `src/indexacao_theta.py` (θ a partir da composição do IPCA) e
`python -m src.busca_contra_mercado_theta --thetas 0.04,0.07,0.10,0.16,0.24 --saida curva_theta_regulados.csv`.

θ = parcela da "massa inercial" do IPCA (peso × grau de indexação ao passado) que passa a ser reajustada pela
meta. Pesos: energia elétrica residencial 3,95% e produtos farmacêuticos 3,49% (Ministério da Fazenda,
informativo IPCA set/2025); segmentos (serviços 35,50%, administrados 25,83%) do BCB (RPM mar/2026, boxe 10);
água e esgoto (1,6%), gás canalizado (0,1%), planos de saúde (3,9%) e aluguel (4,0%) aproximados, a conferir com
o IBGE. Na energia, só a parcela B da tarifa (distribuição) segue a inflação; a parcela A repassa custos.

| Reindexação à meta | Peso no IPCA | θ (faixa) | Híbrido 5,5%, Taylor (P2 / P1) | Híbrido 4,1%, alívio condicionado (P2 / P1) |
|---|---|---|---|---|
| Energia, saneamento e gás canalizado | 5,7% | 0,07 (0,07–0,08) | 30% / 33% | 25% / 30% |
| + planos de saúde (teto da ANS) | 9,6% | 0,16 (0,16–0,18) | 44% / 46% | 38% / 41% |
| + medicamentos (fórmula da CMED) | 13,0% | 0,24 (0,23–0,26) | 53% / 55% | 48% / 51% |

Sem reindexação: 21% / 22% e 18% / 21%.

Leitura: reindexar só as tarifas de energia e saneamento eleva o sucesso de cerca de 20% para 25%–33%, insuficiente
para dispensar o mercado. As tarifas reguladas pesam pouco na inércia: a energia tem só a parcela B indexada, e
a massa inercial está nos serviços (salários) e nos aluguéis, que ficam de fora por escolha. Para passar de 50%
sem mexer no salário mínimo nem nos contratos de aluguel, é preciso incluir também os planos de saúde (teto
anual da ANS, regulação discricionária) e os medicamentos (fórmula da CMED, que depende de mudança na Lei
10.742/2003), e usar o híbrido de 5,5% do PIB com regra de Taylor.
