# Versão 2: λ endógeno no experimento argentino

Código: `src/argmodel/dinamico.py` (pipeline), `model._revisar_lambda` (regra), `credibility.dinamica` em
`config/params.yaml` (desligada por padrão; a v1 continua reproduzível), `src/argmodel/dinamico_figura.py`.

## Regra

A cada 3 meses, com a média do trimestre:

- g = (tol − |inflação mensal média − âncora média|) / tol, com tol = 50% da âncora (mínimo de 0,5% ao mês),
  truncado em [−4, 1];
- Δλ = 0,0105·max(g, 0) + 0,0266·min(g, 0).

Âncoras: λ_câmbio, a depreciação anunciada (crawl/bandas na referência; regra SCRER com câmbio competitivo);
λ_juros, a meta do BC (só JUROS+). λ_fiscal da troca de dívida: Δ = 0,025 por p.p. do PIB de primário contra a
meta do FMI (0,5% do PIB).

Os coeficientes vêm da estimação brasileira (Focus, 2005–2025: −0,071 por p.p. de inflação fora do intervalo,
+0,028 por p.p. de folga; λ_fiscal 0,10 por p.p.), convertidos para unidades de tolerância (no Brasil,
tol = 1,5 p.p. = 50% da meta) e para revisão trimestral (÷4). O truncamento em −4 tolerâncias evita extrapolar
além do suporte da estimação (o Brasil nunca passou de ~3,2): sem ele, os primeiros meses de 2024 (inflação de
20% ao mês contra crawl de 2%) zerariam λ em uma revisão.

## Calibração (regra do CLAUDE.md)

Recalibrado com λ endógeno: 7 de 8 alvos dentro das tolerâncias, o mesmo que a v1 (pobreza do 2º semestre de
2025 2,1 p.p. acima, o desvio conhecido do canal de aluguéis). Parâmetros praticamente iguais aos da v1
(c0 2,52 → 2,78, compensando a queda de λ_câmbio na referência; `income.catchup` no limite inferior, como na v1).
O gatilho de abandono do crawl não dispara no caminho calibrado (mínimo do câmbio real 0,047 contra −0,15). O
cenário extremo (câmbio competitivo sem juros) mantém as direções esperadas (mais inflação e pobreza, menos renda).

## Resultados

1. **O ranking dos 48 cenários quase não muda.** As quatro melhores combinações seguem sendo BMULT + Juros+
   (com ou sem privatização e troca): pobreza no 2º semestre de 2025 de 3,2 a 3,8 p.p. abaixo da referência
   (v1: 3,3 a 3,7). Gradual segue entre as piores (+5,7 a +6,4 p.p.).
2. **Na referência, λ_câmbio cai de 0,75 para 0,54 no 1º semestre de 2024** (inflação muito acima do crawl) e
   quase não se recupera (0,56 em dez/25), enquanto λ_fiscal sobe para 0,92 (primário acima da meta). A
   credibilidade efetiva do câmbio (`cred_x`) sobe mesmo assim, de 0,81 para 0,93, porque os fundamentos
   (superávit, reservas, risco país) a puxam. Na Argentina, o resultado fiscal substitui o histórico de
   inflação como fonte de credibilidade.
3. **O λ endógeno pune a inconsistência entre instrumentos.** Câmbio competitivo + juros: a regra SCRER gera
   inflação acima da trajetória da meta do BC, e λ_juros desaba (0,75 → 0,32) enquanto λ_câmbio sobe (0,81).
   Essas combinações pioram em relação à v1: inflação de 2025 3,5 a 4 p.p. maior e pobreza 0,6 a 1,5 p.p. maior.
4. **O λ endógeno pune o descumprimento fiscal.** No gradual, λ_fiscal cai de 0,75 para 0,37 (primário abaixo
   da meta do FMI) e `cred_x` fica em 0,6–0,7, contra 0,9 nos demais.
5. **O limiar de credibilidade inicial sobe um pouco.** Para BMULT + Juros+ vencer a referência nas três
   frentes (inflação, pobreza, renda): com λ inicial de 0,5, a chance cai de 22%–30% (v1) para 6%–8%; a partir
   de 0,625, fica em 82%–93%, como na v1.
6. **Sensibilidade (cada variante recalibrada):** com regra simétrica, coeficientes pela metade ou em dobro,
   BMULT + Juros+ segue 3,8–3,9 p.p. abaixo da referência em pobreza; a piora de câmbio competitivo + juros
   cresce com os coeficientes (+0,1 a +0,9 p.p. de pobreza contra a referência).

## Leitura comparada com o Brasil

No Brasil, λ é toda a credibilidade e só se reconstrói pelos resultados de inflação: com λ endógeno, a
credibilidade baixa se autoperpetua e o sucesso cai um terço. Na Argentina, a credibilidade efetiva tem uma
segunda fonte, os fundamentos fiscais e externos, que compensa a perda de λ_câmbio, e os resultados quase não
mudam. O que o λ endógeno pune nos dois países é o mesmo: desinflação lenta (gradual), descumprimento fiscal e,
na Argentina, a incoerência entre uma regra cambial que gera inflação e uma meta de juros que promete
desinflação. A composição de baixo multiplicador não é punida em nenhum dos dois.

## Limitações

- Os coeficientes são os do Brasil, transportados em unidades de tolerância; o REM não permite estimá-los na
  Argentina (a credibilidade de pesquisa fica perto de zero o tempo todo).
- A meta do BC (12% ao mês decaindo 20% ao mês até 1,5%) é a da v1, uma hipótese.
- λ_π da troca de dívida segue fixo.
