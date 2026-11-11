# Argentina 2023–2025: ajustes alternativos ao de Milei

Modelo semiestrutural mensal, calibrado na trajetória efetiva (dez/2023–dez/2025),
para testar 48 combinações de cinco medidas de ajuste e seus efeitos sobre
**inflação, pobreza e renda média**, com **risco país endógeno** e **Congresso
estocástico** calibrado na dificuldade histórica de aprovar reformas radicais.

```bash
pip install -r requirements.txt
python run_all.py            # ~15 s: calibração → 48 cenários × 400 simulações → sensibilidade → gráficos
```

## As cinco alavancas

| Alavanca | ON | OFF (= o que foi feito) |
|---|---|---|
| **DEV** câmbio | Câmbio real competitivo e estável (regra SCRER: crawl = 0,7·π(t−1) + 0,3·2% + correção à meta de câmbio real) para acumular reservas via superávit externo | Salto de 118% e crawl fixo de 2% como âncora nominal; bandas a partir de abr/25 |
| **JUROS** | Juro real ex-ante positivo (~10% a.a.) desde dez/23 | Repressão financeira efetiva (juro abaixo da inflação, "licuadora") |
| **FISCAL** (3 níveis) | `baixo_multiplicador`: mesmos 4,75 p.p. do PIB, concentrados em subsídios (com tarifa social), folha/custeio, transferências discricionárias a províncias e fundos; protege obra pública, aposentadorias e AUH. `gradual`: 2 p.p. em 24 meses | `motosserra`: composição efetiva (aposentadorias via liquefação, obra pública, subsídios, províncias) |
| **PRIV** | Envia ao Congresso a lista ampla (41 empresas, ~US$10 bi a preços normais) | Não envia |
| **SWAP** | Troca dívida externa por interna: canje de 4% do PIB + 50% do serviço FX refinanciado em pesos (precisa de autorização legislativa; sem ela, só 30%) | Paga em divisas |

A combinação **DEV− JUROS− MOTOSSERRA PRIV+ SWAP−** é a política efetiva — é a
referência contra a qual todo efeito é medido, e o caminho em que o modelo foi calibrado.

## Estrutura do modelo (`src/argmodel/model.py`)

- **Inflação**: inércia + expectativas ancoradas no crawl anunciado (e na meta do BC
  se JUROS+), com credibilidade endógena (superávit, reservas, risco país, dívida em
  pesos); repasse cambial distribuído em 6 meses e assimétrico (desvalorização acima
  da inflação esperada × crawl abaixo dela); tarifas pelo corte de subsídios;
  excesso de emissão (déficit monetizado + juros dos passivos remunerados do BCRA +
  compras de divisas não esterilizadas).
- **Atividade**: arrasto fiscal por categoria com multiplicadores próprios; salário
  real (desvalorização contracionista); câmbio real (exportações); confiança via
  risco país; custo do juro real; crowding out da dívida doméstica.
- **Salários e renda**: indexação defasada; perda "dente de serra" entre reajustes;
  salário real de equilíbrio cai com câmbio real mais depreciado (o trade-off central
  da alavanca DEV); renda dos pobres mais sensível à atividade e às transferências.
  A indexação é calibrada no salário real registrado privado (INDEC).
- **Pobreza**: probit log-normal da renda dos pobres contra a linha. A linha (CBT)
  relativa ao IPC sobe com o câmbio real, com repasse defasado (meia-vida ~2 meses),
  e cai com a alta de tarifas do corte de subsídios, que pesa menos na cesta básica
  que no IPC (`eta_reg`).
- **Setor externo**: balança comercial (sazonalidade da safra, câmbio real, Vaca
  Muerta), vazamento pela brecha, fuga com câmbio apreciado, serviço da dívida,
  FMI condicionado a superávit.
- **Risco país**: ajuste parcial a um fundamental (dívida FX/PIB, dívida nova em
  pesos, reservas, primário, inflação, reformas aprovadas) + choques políticos comuns
  (eleição em Buenos Aires set/25, legislativas out/25), amplificados por reservas negativas.
- **Congresso** (`legislative.*`): hazard mensal de aprovação depende de coalizão,
  popularidade, crise (hipótese de Drazen), radicalismo da proposta, tamanho do
  pacote (efeito Ómnibus) e cortes às províncias (governadores no Senado); primeira
  votação pode cair; escopo aprovado ~ Beta. Calibrado para reproduzir a Lei Bases
  (mediana 6 meses, ~22% do escopo; o observado foi 41 → 6–8 empresas) e dar
  aprovação rápida e ampla com coalizão majoritária (caso Menem 1989).

## Validação (`outputs/fig1_validacao.png`, `outputs/calibracao_ajuste.csv`)

| | Observado | Modelo |
|---|---|---|
| Inflação 2024 / 2025 | 117,8% / 31,5% | 117,1% / 29,0% |
| PIB 2024 / 2025 | −1,7% / +4,4% | −0,8% / +5,0% |
| Pobreza 1º sem 24 / 2º sem 24 / 1º sem 25 / 2º sem 25 | 52,9 / 38,1 / 31,6 / 28,2 | 53,6 / 36,0 / 31,7 / 30,3 |
| Salário real registrado privado (nov/23 = 100) mar/24 / set/24 / dez/25 | 87,9 / 98,5 / 98,4 | 85,8 / 98,8 / 99,5 |
| Linha CBT/IPC (nov/23 = 100) mar/24 / dez/24 / dez/25 | 104,1 / 96,0 / 93,3 | 99,6 / 96,9 / 96,9 |
| Resultado primário 2024 | +1,8% | +0,6% |
| Risco país dez/24 | ~640 | ~890 |

Desde nov/26 a calibração também usa, a cada trimestre de dez/23 a dez/25, o salário
real registrado privado e a razão CBT/IPC (`data/relative_prices_wages.csv`, séries
oficiais do datos.gob.ar). Sem esses alvos o modelo recuperava o salário real
uns 4–5 meses antes do observado.

**Repasse cambial assimétrico (nov/26).** O repasse passou a ter dois coeficientes:
`beta_fx` para desvalorizações acima da inflação esperada (o salto) e `beta_fx_down`
para um crawl abaixo dela (a âncora). Com um coeficiente só, a calibração ficava presa
no piso (0,16): os dados pedem o primeiro efeito forte e o segundo fraco. Separados,
calibram em 0,28 e 0,08, e o erro ponderado total cai de 350 para 303. Peso menor do
câmbio oficial no repasse e repasse mais curto foram testados e descartados como
explicação. A versão anterior (0,16 nos dois) está na sensibilidade.

**Tolerâncias.** Inflação e PIB passam com folga. Duas pobrezas ficam 0,1 p.p. fora de
±2: o 2º sem/24 (−2,1) e o 2º sem/25 (+2,1). A do 2º sem/25 vem do canal que falta na
linha de pobreza (abaixo); a calibração não foi reponderada para forçar a entrada,
porque isso esconderia o problema em vez de resolvê-lo.

Erros conhecidos:
- **PIB 2024:** o modelo subestima a queda (−0,8% contra −1,7%). A média do EMAE
  dessazonalizado (−1,37%) não substitui a variação anual das contas nacionais; se o
  alvo for revisto, use o informe de nível de atividade mais recente do INDEC.
- **Linha de pobreza no início de 2024:** em mar/24 a razão CBT/IPC observada é 104,1
  e a do modelo, 99,6. Como o modelo ainda acerta a pobreza do 1º sem/24, a renda dos
  pobres deve estar caindo demais para compensar — o que tende a exagerar o canal da
  renda nos contrafactuais de câmbio competitivo.
- **Linha de pobreza em 2025:** o modelo não reproduz a queda de ~7–10% da razão
  CBT/IPC, porque aluguéis e serviços privados se normalizaram e o modelo não tem
  esse canal. Por isso a pobreza de 2025 sai alta (+2,1 p.p. no 2º sem).
- **Outros:** superávit de 2024 e compressão do risco país no fim de 2024 abaixo do
  observado; inflação de dez/23 abaixo do observado.

## Resultados (medianas de 400 simulações; `outputs/cenarios_resumo.csv`)

| Cenário | Inflação 2025 | Pobreza 2º sem 25 | Renda média 2025 (nov/23=100) | PIB 2025 | Risco país dez/25 | Reservas dez/25 |
|---|---|---|---|---|---|---|
| **Referência (efetivo)** | 29% | 30,3% | 96,8 | +5,0% | 597 | −US$ 2 bi |
| Baixo multiplicador (só) | 30% | 27,6% | 97,4 | +5,1% | 599 | −US$ 6 bi |
| Baixo multiplicador + troca de dívida | 29% | 27,4% | 97,6 | +5,5% | 492 | +US$ 4 bi |
| ↳ + juros reais positivos | **22%** | **26,6%** | **98,3** | +5,2% | 495 | +US$ 3 bi |
| Juros reais positivos (só) | 23% | 29,4% | 97,5 | +4,8% | 597 | −US$ 4 bi |
| Câmbio competitivo + juros positivos | 27% | 32,6% | 94,7 | +6,5% | 491 | +US$ 17 bi |
| Câmbio competitivo, juros reprimidos | 144% | 36,5% | 90,9 | +7,2% | 591 | +US$ 14 bi |
| Ajuste gradual | 39% | 36,6% | 97,8 | +3,6% | 992 | −US$ 21 bi |

Leituras principais (efeitos contra a referência, mediana da diferença simulação a simulação):

1. **Composição do ajuste importa mais que o tamanho, para a pobreza.** O mesmo
   ajuste concentrado em gastos de baixo multiplicador reduz a pobreza em 2,7 p.p. no
   fim de 2025, em todas as simulações. O sinal nunca muda nas 22 hipóteses da
   sensibilidade (de −1,8 a −5,0 p.p.); a magnitude depende da velocidade de
   recuperação do salário real (`catchup`) e de quanto o tarifaço entra na linha
   (`eta_reg`). O custo é inflação: +11 p.p. em 2024, pelo corte maior de subsídios, e
   +0,4 p.p. em 2025 — pequeno, mas presente em todas as simulações.
2. **Juros reais positivos** cortam 6,4 p.p. da inflação de 2025 e reduzem a pobreza do
   fim de 2025 em 0,9 p.p. (78% das simulações), com 0,8 p.p. a mais de pobreza no
   1º sem/24. Com o repasse separado, deixaram de custar PIB em 2024.
3. **Câmbio competitivo compra reservas com pobreza.** Acumula US$ 16–19 bi a mais e
   eleva o crescimento de 2025, mas o salário real mais baixo empurra a pobreza do
   1º sem/24 para 66–71% e a deixa 6,2 p.p. acima da referência no fim de 2025 (faixa
   de +2,5 a +10,3). A inflação de 2024 vai a 270% com juros positivos e 573% sem,
   contra 117% na referência. **Sem juros positivos como âncora, a inflação de 2025
   passa de 140%.** Com juros, o custo em pobreza cai para +2,4 p.p. (faixa de 0 a +9,2)
   e a inflação de 2025 fica perto da referência — mas esse último resultado é frágil
   (ver Sensibilidade). Somando o ajuste de baixo multiplicador, o câmbio competitivo
   com juros termina 2025 igual à referência em inflação e pobreza (29% e 30,1–30,6%),
   com US$ 18–28 bi a mais de reservas e risco país de 385–533 pb — depois de um 2024
   com inflação de ~300% e pobreza de 66% no 1º semestre.
4. **Ajuste gradual** é o pior caminho: perde o desembolso do FMI, o risco país fica
   perto de 1.000 pb e a pobreza termina 6,3 p.p. acima. A renda média até sobe
   (aposentadorias perdem menos), mas a renda dos pobres cai 5,9 pontos.
5. **Privatizações quase não movem o resultado no horizonte**: o Congresso aprova em
   ~87% das simulações, mas corta o escopo para ~20%; a venda leva 6–18 meses e o risco
   país alto deprecia o preço. Não enviar a lista custa ~35 pb de risco país e nada mais.
6. **Troca de dívida externa por interna** reduz o risco país em ~130 pb e libera
   ~US$ 10 bi de reservas, mas a dívida em pesos sobe 3 p.p. do PIB. Esse resultado
   supõe adesão alta do mercado (λ = 0,75). Com adesão nula, o ganho no risco país cai
   para ~45 pb e o de reservas some (ver "Troca de dívida e adesão do mercado").

A melhor combinação é **baixo multiplicador + troca de dívida + juros reais
positivos**: −3,8 p.p. de pobreza e −6,6 p.p. de inflação em 2025, melhor que a
referência em pobreza em 100% das simulações e em inflação em 97%. Dez cenários
superam a referência ao mesmo tempo em inflação, pobreza e renda média; todos usam
câmbio como âncora, e oito deles juros reais positivos.

## Sensibilidade (`outputs/sensibilidade.csv`)

Sinais e ordem dos efeitos sobre a pobreza se mantêm nas 22 hipóteses alternativas.
A exceção é a inflação de **câmbio competitivo + juros positivos**, que vai de −8 a
+18 p.p. em 2025. Os extremos vêm do repasse do salto (`beta_fx` = 0,45 → +18) e da
força do canal monetário (`phi_money` = 0 → −8): juros altos sobre passivos
remunerados do BCRA de ~11% do PIB geram emissão quase-fiscal. `phi_money` **não é
identificável** só com o caminho observado (a calibração livre o zera), então está
fixo em 0,08 e deve ser lido como hipótese, não estimativa.

Parâmetros fixos por não serem identificados (a calibração livre os levava a zero ou
ao limite) e cobertos na sensibilidade com valores baixo e alto: `phi_money`,
`agri_rebound` (rebote da safra) e `eta_reg` (tarifas na linha).

Parâmetros livres fracamente identificados, também cobertos na sensibilidade:

- `catchup` = 0,010, no piso. Os alvos de salário real querem recuperação lenta.
- `zeta_rer` = 0,034: perto de zero porque a linha sobe em 2024 e cai 7–10% em 2025
  com o câmbio subindo; o canal que falta (aluguéis e serviços) puxa o parâmetro para
  zero. Na prática, o canal do câmbio na linha está quase desligado nos contrafactuais.
- `sigma` = 0,43 (piso 0,35).

As hipóteses que mais movem os efeitos sobre a pobreza são `catchup` alto (0,12),
`beta_fx` alto (0,45), `zeta_rer` alto (0,25), `phi_money` e a volta ao repasse
simétrico.

## Troca de dívida e adesão do mercado (`python -m argmodel.lambda_swap`)

A troca depende de os credores aceitarem pesos. Dois parâmetros de adesão, de 0 a 1,
medem isso (`debt_swap.*` em `params.yaml`). λ = 0,75 reproduz a calibração.

- `lambda_fiscal`: com adesão baixa, menos credores aceitam a troca (piso de 25%) e a
  dívida trocada paga prêmio. O mercado também passa a temer a rolagem em pesos, o que
  sobe o risco país, e parte dos pesos vira dólar a cada vencimento (até 3% ao mês),
  consumindo reservas.
- `lambda_pi`: com adesão baixa, a dívida em pesos derruba a credibilidade e as
  expectativas de inflação.

Resultado da troca isolada, mediana de 300 simulações contra a referência
(`outputs/lambda_troca_*.csv`):

| λ (fiscal = π) | Risco país dez/25 | Reservas dez/25 | Inflação 2025 | Pobreza 2º sem 25 |
|---|---|---|---|---|
| 1,0 | −134 pb | +US$ 10 bi | −0,3 p.p. | −0,3 p.p. |
| 0,75 (calibração) | −122 pb | +US$ 10 bi | −0,4 p.p. | −0,3 p.p. |
| 0,5 | −77 pb | +US$ 4 bi | −0,2 p.p. | −0,2 p.p. |
| 0,25 | −50 pb | +US$ 1 bi | −0,1 p.p. | −0,2 p.p. |
| 0 | −44 pb | −US$ 0,3 bi | ~0 | −0,2 p.p. |

- **Quase tudo depende de `lambda_fiscal`.** `lambda_pi` move o risco país em menos de
  3 pb, porque o canal de credibilidade via dívida em pesos é fraco no modelo.
- **Os ganhos encolhem, mas o sinal não se inverte.** Com adesão baixa, o efeito sobre
  reservas some, e o efeito sobre o risco país cai cerca de dois terços.
- **Efeitos sobre inflação e pobreza são pequenos em qualquer λ** (≤ 0,6 p.p.), e a
  troca melhora a pobreza em só ~54% das simulações. A troca é uma alavanca de
  balanço externo, não de pobreza.
- **Teste de estresse.** Mesmo multiplicando por 6 a intensidade do medo (prêmio,
  risco de rolagem, dolarização, expectativas), a troca perde até US$ 5 bi de
  reservas, mas não chega a piorar o risco país em mediana. O risco país não piora
  porque, com adesão baixa, pouca dívida é trocada: o medo encolhe a própria troca.

**A melhor combinação sob adesão baixa** (`python -m argmodel.lambda_swap --combos`,
400 simulações, diferença contra a referência):

| Adesão | Combinação | Inflação 2025 | Pobreza 2º sem 25 | Renda média | Risco país | Reservas | Vence nas 3 frentes |
|---|---|---|---|---|---|---|---|
| qualquer | BMULT + JUROS+ (sem troca) | −6,2 | −3,5 | +1,2 | −2 pb | −US$ 5 bi | 100% |
| 0,75 | BMULT + SWAP+ + JUROS+ | −6,6 | −3,8 | +1,5 | −105 pb | +US$ 5 bi | 94% |
| 0,25 | BMULT + SWAP+ + JUROS+ | −6,3 | −3,6 | +1,3 | −44 pb | −US$ 4 bi | 91% |
| 0 | BMULT + SWAP+ + JUROS+ | −6,3 | −3,6 | +1,3 | −43 pb | −US$ 5 bi | 92% |
| 0,25, medo ×6 | BMULT + SWAP+ + JUROS+ | −6,1 | −3,4 | +1,1 | −1 pb | −US$ 10 bi | 89% |

O resultado social da melhor combinação vem de baixo multiplicador + juros positivos,
não da troca. A troca acrescenta ~0,3 p.p. de pobreza a menos com adesão alta e
quase nada com adesão baixa. O que ela acrescenta de fato é risco país e reservas,
e isso depende de λ. Sob medo forte, a troca piora as reservas da combinação em
~US$ 5 bi e deixa de reduzir o risco país. Nesse caso, a combinação sem troca passa
a ter a menor pobreza do grid.

Limite: o modelo não tem corrida descontínua contra a dívida em pesos (como o
reperfilamento de LETES/LECAPs de ago/2019). Por isso, ele não gera o caso em que a
troca precipita uma crise. Esse caso fica fora do que o modelo pode avaliar, e
"a troca nunca piora o risco país" não deve ser lido como conclusão.

## Credibilidade das âncoras: câmbio e juros

O modelo tem uma credibilidade (`cred`, 0 a 1) que diz quanto da expectativa de
inflação segue a âncora e quanto segue a inflação passada. A âncora é o crawl
anunciado ou, com juros positivos, metade crawl e metade meta do BC. Essa
credibilidade agora se divide em duas, cada uma com seu λ (`credibility.*` em
`params.yaml`). λ = 0,75 reproduz a calibração (diferença < 1e−10).

- `lambda_fx` (câmbio): quanto o mercado acredita no câmbio anunciado (crawl ou banda;
  regra de câmbio real se DEV+). Com λ baixo, o crawl pesa menos nas expectativas, a
  brecha abre, a fuga sobe e o repasse do salto aumenta.
- `lambda_rate` (juros, só JUROS+): quanto o mercado acredita na meta do BC. Com λ baixo,
  a meta pesa menos, o bônus de credibilidade do juro real some, e o juro nominal
  necessário sobe (mais emissão quase-fiscal).

Mudança necessária no modelo: **abandono forçado do crawl**. Sem crédito, a
inflação passava do crawl, o câmbio real se valorizava sem limite e o salário real
subia: 950% de inflação com pobreza *menor*. Agora, se o câmbio real fica abaixo de
`q_break` = −0,15 (nov/23 = 0), o BC desvaloriza e fecha metade do desalinhamento por
mês. No caminho calibrado o gatilho não dispara: o mínimo de q fica em −0,09 no 1º
percentil dos 48 cenários, e a calibração e os cenários não mudaram.

### Parte 1 — mapa contrafactual (`python -m argmodel.credibility`)

A credibilidade das âncoras do pacote alternativo varia de 0 a 1, e a referência fica
na credibilidade calibrada. Figura: `outputs/fig_credibilidade_mapa.png`; dados:
`outputs/credibilidade_*.csv`.

| Combinação | Vence a referência (inflação 2025 e pobreza 2º sem/25) se | Chance de vencer nas 3 frentes em λ = 0,75 |
|---|---|---|
| Juros+ (só) | λ câmbio ≥ 0,375 e λ juros ≥ 0,25 | 83% |
| Baixo mult. + juros+ | λ câmbio ≥ 0,5 e λ juros ≥ 0,375 | 92% |
| Baixo mult. + juros+ + troca | λ câmbio ≥ 0,375 e λ juros ≥ 0,375 | 93% |
| Baixo mult. (sem juros) | λ câmbio ≥ 0,625 | 45% |
| Câmbio comp. + juros+ | nunca (no máximo 15% de chance, com λ = 1) | 2% |
| Câmbio comp. + juros+ + baixo mult. | λ câmbio ≥ 0,875, ou λ juros = 1 com câmbio em 0,75 | 3% |

Os limiares em λ dependem da escala `k_fx`/`k_rate` (testada de 2 a 6) e da força dos
canais (×0,5 a ×2). **Em unidades de credibilidade, os limiares são estáveis.**
Baixo multiplicador + juros precisa de ~70% das expectativas seguindo o câmbio
anunciado em 2024 e ~60% seguindo a meta do BC. O caminho calibrado tem 85%. Perto
do limiar, a inflação de 2024 já passa de 150%. Abaixo dele, o crawl é abandonado e
a inflação de 2025 também sobe.

Leituras:

- **O núcleo baixo multiplicador + juros positivos aguenta uma queda moderada de
  credibilidade.** A pobreza no fim de 2025 fica abaixo da referência em quase todo o
  mapa; o que se perde primeiro é a inflação.
- **Câmbio competitivo + juros não vence com nenhuma credibilidade.** A pobreza fica
  sempre acima da referência; a inflação só fica abaixo com câmbio e juros muito
  críveis.
- **Choque comum.** Se o câmbio anunciado perdesse crédito também na referência, os
  cenários com juros positivos venceriam com folga: com λ câmbio ≤ 0,375, pobreza 2 a
  19 p.p. menor no fim de 2025. Os juros funcionam como seguro contra a falha da âncora cambial.
- Com credibilidade total do câmbio (λ = 1), a referência teria inflação menor em
  2024 (96% contra 117%), mas pobreza um pouco maior no fim de 2025. Inflação menor
  significa menos valorização real e salário real mais baixo, como em todo plano de
  estabilização com âncora cambial.

### Parte 2 — credibilidade medida pelo REM (`python -m argmodel.credibility_measure`)

Fonte: `data/rem_medianas.csv`, medianas do REM (BCRA) de nov/23 a dez/25, montadas a
partir dos relatórios e PDFs mensais do BCRA e da imprensa. A coluna `notes` marca os
valores menos seguros. A planilha histórica do BCRA (`historico-relevamiento-
expectativas-mercado.xlsx`) fecha as lacunas e deve substituir este arquivo quando
baixada localmente. Figura: `outputs/fig_credibilidade_rem.png`.

A medida usa a mesma fórmula do modelo:
c = (inflação passada − esperada) / (inflação passada − âncora), agregada por período
com mínimos quadrados e só nos meses em que âncora e inércia diferem em ≥ 1 p.p.

| Período | Modelo calibrado | REM: inflação esperada | REM: câmbio esperado × crawl |
|---|---|---|---|
| 1º tri/24 | 0,75 | 0,05 (0,10 com o nowcast do REM) | 0,39 (pesquisa de dez/23) |
| abr–dez/24 | 0,89 | 0,06 (0,16) | ~0 em jun–jul, 0,9–1,0 em ago–set |
| jan–abr/25 | 0,93 | 0,12 | 0,7–0,95 em jan–fev, 0,3–0,5 em mar–abr |
| mai–dez/25 | 0,95 | ~0 | não informativo (banda, inflação ≈ deriva) |

- **Pelas pesquisas, a inflação esperada quase não seguiu a âncora.** Os analistas
  projetavam a última inflação. Erraram para cima em −4,2 p.p. por mês no 1º tri/24 e
  em −0,9 p.p. em abr–dez/24: a inflação caiu mais rápido do que esperavam.
- **A credibilidade do câmbio foi conquistada, não dada.** Ela ficou perto de zero até
  julho/24, quando o mercado esperava depreciação igual à inflação, e subiu para
  ~1 em agosto–setembro/24. Ela voltou a cair antes das bandas de abril/25.
- **O modelo não reproduz 2024 com as expectativas do REM.** Com as expectativas do
  REM no lugar das do modelo (`inflation.pie_override`), a inflação de 2024 iria a
  254%, contra 118% observado. Logo, o `cred` do modelo não é a credibilidade das
  pesquisas. Ele é uma âncora efetiva na formação de preços, identificada pela
  própria trajetória da inflação. Inclui o que não está modelado à parte: a recessão,
  a contração dos saldos reais e o crawl como referência de preço dos bens comerciáveis.
- **Por isso o REM não dá um ponto no mapa da parte 1.** As unidades são outras. O que
  ele mostra é que a credibilidade de pesquisa veio depois da desinflação, e não antes.
- **λ_juros não tem medida observável:** o BCRA não teve meta de inflação em 2024–25.
  Continua hipótese.

Consequência para as conclusões: o ranking entre as alternativas se mantém, porque ele
compara pacotes com a mesma âncora efetiva. Mas a parte da desinflação que o modelo
atribui à credibilidade pode vir de canais de demanda que ele não separa. Para
separar, seria preciso disciplinar as expectativas pelo REM e recalibrar com um canal
de demanda/saldos reais explícito.

## Versão 2: λ endógeno (`python -m argmodel.dinamico`)

A cada trimestre, os λ de câmbio, juros e troca de dívida são revistos pelos resultados, com a regra estimada no
modelo brasileiro convertida para unidades de tolerância (50% da âncora) e truncada em quatro tolerâncias. O modelo
é recalibrado com a regra ligada (7 de 8 alvos dentro das tolerâncias). Relatório, cenários e sensibilidade da regra
(simétrica, coeficientes pela metade e em dobro) em `outputs/v2_lambda_endogeno/`.

## Limites que importam

- **A credibilidade do modelo é efetiva, não a das pesquisas** (ver "Credibilidade das
  âncoras"). Os λ de câmbio e juros são hipóteses; os limiares estão em unidades do modelo.
- **Um único caminho observado, ~60 alvos, 18 parâmetros livres** (1 no limite). A
  calibração usa prior para não sair de faixas plausíveis; não é estimação econométrica.
- **A pobreza é muito sensível** (σ ≈ 0,43) para reproduzir as oscilações da EPH;
  contrafactuais longe do caminho observado (ex.: 66–71% no 1º sem/24 com câmbio
  competitivo) são extrapolação. Com σ = 0,60 os efeitos caem ~1/4 mas mantêm o sinal.
- A única reação endógena do governo é o abandono do crawl quando o câmbio real se
  valoriza demais. Não há abandono da regra de câmbio real (DEV+) diante de inflação
  alta, nem efeito das medidas sobre a eleição de 2025.
- Choques externos (FMI, apoio dos EUA, eleições) são comuns a todos os cenários; o
  FMI é condicionado a superávit primário ≥ 0,5% do PIB.
- Valores mensais de inflação e alguns pontos do risco país estão marcados para
  conferência em `data/SOURCES.md`.

## Arquivos

```
config/params.yaml             parâmetros com justificativa (edite aqui)
config/params_calibrated.yaml  gerado pela calibração (não edite)
data/                          alvos observados e fontes
data/relative_prices_wages.csv salário real reg. privado, CBT/IPC e EMAE (INDEC, nov/23=100)
data/raw/                      séries oficiais baixadas (datos.gob.ar)
src/argmodel/model.py          o modelo
src/argmodel/calibrate.py      calibração com prior
src/argmodel/experiment.py     grid fatorial 48 cenários + efeitos e interações
src/argmodel/sensitivity.py    hipóteses alternativas
src/argmodel/report.py         gráficos
src/argmodel/lambda_swap.py    troca de dívida × adesão do mercado (--combos: combinações)
src/argmodel/credibility.py    mapa λ câmbio × λ juros (parte 1)
src/argmodel/credibility_measure.py  credibilidade medida pelo REM (parte 2)
data/rem_medianas.csv          medianas do REM nov/23–dez/25 (fontes por linha)
scripts/fetch_data.py          puxa séries do INDEC/BCRA (rodar localmente)
outputs/                       resultados e figuras
```
