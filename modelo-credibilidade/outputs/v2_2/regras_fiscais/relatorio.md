# Canal institucional: LRF, teto de gastos e arcabouço como choques de credibilidade

Código: `src/regras_fiscais_eventos.py` (estudo de evento), `src/regras_fiscais_aplicacao.py` (aplicação),
`src/regras_fiscais_figura.py`. Dados novos: `data/raw/embi_brasil_mensal.csv` (EMBI+ Brasil, Ipeadata; ver o
LEIAME ao lado).

## 1. Estudo de evento

| Variação em 6 meses após o anúncio | LRF (abr/1999) | Teto (mai/2016) | Arcabouço (mar/2023) |
|---|---|---|---|
| EMBI+ Brasil | −328 p.b. (−24%) | −81 p.b. (−20%) | −49 p.b. (−19%) |
| Dólar amplo (controle global) | −2,4 | +6,2 | +1,3 |
| Primário esperado para o ano seguinte (Focus) | sem dado | −1,1 p.p. | +0,2 p.p. |
| Dívida líquida esperada para o ano seguinte | sem dado | +3,9 p.p. | −0,2 p.p. |
| IPCA esperado para o ano seguinte − meta | sem dado | −0,95 p.p. | −0,1 p.p. |

Na aprovação: LRF (mai/2000) EMBI +77 p.b. em 6 meses; teto (dez/2016) −39 p.b.; arcabouço (ago/2023) −2 p.b.

λ ajustado pelo modelo (validação 2D, P2; faixa = erro até 5% acima do mínimo):

| Evento | Janela | λ_π | λ_fiscal | Erro |
|---|---|---|---|---|
| Teto | 2015T2–2016T1 (antes) | 0,55 (0,50–0,55) | 0,00 (0,00–0,10) | 5,6 |
| Teto | 2016T2–2016T4 | 0,20 (0,20–0,25) | 1,00 (0,80–1,00) | 4,1 |
| Teto | 2016T3–2017T4 (depois) | 0,60 (0,55–0,60) | 1,00 (0,95–1,00) | 2,5 |
| Arcabouço | 2022T2–2023T1 (antes) | 0,45 | 1,00 (0,95–1,00) | 3,5 |
| Arcabouço | 2023T2–2023T4 | 0,00 | 0,00 (0,00–0,20) | 10,7 |
| Arcabouço | 2024 | 0,80 | 1,00 (0,80–1,00) | 2,0 |

Leitura por caso:

- **Teto: choque institucional claro.** O risco país caiu 20% em seis meses contra um dólar global mais forte;
  as expectativas de inflação convergiram para a meta; e o λ_fiscal do modelo saltou de 0–0,10 para
  0,80–1,00, com o ajuste melhorando. Tudo isso enquanto o mercado esperava primário pior e dívida maior: o
  ganho veio da regra, não dos fundamentos. Ressalva: coincide com a troca da diretoria do BC (junho de
  2016) e com o impeachment, o que impede atribuir ao teto o movimento das expectativas de inflação.
- **Arcabouço: sinal de mercado, sem confirmação no modelo.** O risco país caiu 19% em seis meses após o
  anúncio, com o dólar global estável, mas a queda se concentra em julho–agosto de 2023, junto com a melhora
  das perspectivas de rating (S&P em junho; elevação pela Fitch em julho). A aprovação não moveu o risco
  país. O modelo não ajusta bem 2023 (erro de 10,7, contra 2–5 nas outras janelas), e as estimativas de λ
  dessa janela não são confiáveis; em 2024, a NTN-B de 10 anos sobe de 5,6% para 6,8%.
- **LRF: não identificável com estes dados.** O Focus fiscal começa em 2000 e fica parado em 3,0% de
  primário, a meta do programa com o FMI de 1998, do qual a LRF fazia parte. O risco país cai em 1999 com a
  recuperação pós-desvalorização e a adoção do regime de metas, e sobe em 2000–01 com o estouro das ações de
  tecnologia e a crise argentina. Não há como separar a LRF desses choques.

## 2. Aplicação: pacote anunciado com uma regra crível

Choque do teto aplicado às finalistas da busca híbrida, com λ endógeno (regra central): λ_fiscal parte de 1,0
(0,2–0,5 + 0,8) e segue a regra de revisão; λ_π parte do mesmo sorteio U(0,2; 0,5).

| Sucesso pela banda (atividade até 2030) | Sem regra, P1 | Com regra, P1 | Sem regra, P2 | Com regra, P2 |
|---|---|---|---|---|
| Híbrido | 35% (+1,3) | 38% (+2,0) | 34% (+1,2) | 35% (+2,3) |
| Choque | 25% (−4,0) | 30% (−2,4) | 34% (−4,3) | 36% (−2,2) |
| Gradual longo | 28% (+1,9) | 34% (+4,0) | 26% (+2,2) | 31% (+4,7) |
| Estratégias do paper | 23% (+0,1) | 28% (+2,0) | 22% (+0,2) | 25% (+2,3) |

- A regra crível eleva o sucesso em 1 a 6 pontos e, sobretudo, reduz o custo: de 1 a 2,5 pontos do PIB a mais
  de atividade, porque o prêmio de risco e os juros longos caem. λ_fiscal se mantém perto de 0,93 em quatro
  anos, porque os pacotes entregam o primário anunciado.
- Quem mais ganha é o gradual longo, que passa a ter mais sucesso que o choque em P1 com quatro vezes menos
  custo; o híbrido continua o melhor em P1.
- O teto de sucesso não muda (cerca de 38%): a regra fiscal move λ_fiscal, e o sucesso depende de λ_π.
- Em P3, a regra muda a natureza do resultado (com λ_fiscal alto, o canal fiscal da inflação desaparece e o
  ajuste gera deflação); P3 segue sem sustentação na validação histórica.

## Leitura

Dos três casos, só o teto identifica um choque institucional, e ele é grande: λ_fiscal de perto de zero para
perto de um, contra fundamentos que pioravam. No modelo, esse choque barateia o ajuste mais do que o torna
provável, porque o gargalo do sucesso é a credibilidade da meta de inflação. A combinação que o conjunto dos
testes sugere para um governo de baixa credibilidade é, portanto: uma regra fiscal crível (reduz o custo e
estabiliza λ_fiscal), um ajuste híbrido de baixo multiplicador (desinflação rápida sem recessão) e ações que
elevem diretamente λ_π (autonomia e comunicação do Banco Central, engajamento do mercado).

## Limitações

- Estudo de evento com dados mensais, sem grupo de controle além do dólar amplo; o EMBI de outros emergentes
  ajudaria a separar o choque brasileiro do global.
- EMBI transcrito do Ipeadata por leitura assistida; conferir antes de publicar.
- A aplicação trata a regra como salto imediato de λ_fiscal; não modela a perda de credibilidade da própria
  regra quando ela é alterada (como o teto em 2021–22 e a meta de 2025 em abril de 2024).
