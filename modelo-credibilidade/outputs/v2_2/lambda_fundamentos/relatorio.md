# Canal de fundamentos na credibilidade (modelo brasileiro)

Código: `src/lambda_fundamentos_estimacao.py`, `src/modelo.py` (`canal_fundamentos`; desligado por padrão e
neutro com β = 0, verificado), `src/lambda_fundamentos_validacao.py`, `src/lambda_fundamentos_aplicacao.py`.

λ_efetivo = logística(logit(λ_reputação) + β_s·Δ(s − s_estab) + β_d·Δd), com os fundamentos do trimestre
anterior em desvio do ponto de partida. λ_reputação é o λ revisto anualmente pela regra da seção 2.9.

## 1. Estimação no painel do Focus (2005–2025, trimestral)

| Credibilidade | Primário − estabilizador (real) | Dívida bruta | Reservas |
|---|---|---|---|
| Fiscal (cumprimento esperado) | +0,12 por p.p. (nível; p = 0,11) | −0,13 por p.p. (diferenças; p = 0,01) | n.s. |
| Meta de inflação (de Mendonça) | **−0,33 por p.p. (diferenças; p < 0,01): sinal trocado** | n.s. | n.s. (negativo) |

- O canal fiscal → credibilidade fiscal tem o sinal esperado.
- O canal fiscal → credibilidade da meta tem o sinal trocado em todas as especificações (primário em nível,
  primário menos estabilizador real ou nominal). No Brasil de 2005–2025, a credibilidade da meta subiu com
  Bancos Centrais duros em anos de déficit (2016–21) e caiu com primários altos (2011–14). Os juros altos que
  reconstroem a credibilidade da meta também elevam o primário estabilizador. É o mesmo resultado do teste de
  antecedência da seção 2.7: no Focus, a credibilidade fiscal não antecede a da meta.

## 2. Validação conjunta (2015–16, 2016–19, 2020–22; P2)

| Canal | Erro com λ por episódio | Erro com λ comum aos três |
|---|---|---|
| Sem canal | 10,06 | 13,27 |
| Focus (só λ_fiscal: +0,12 / −0,13) | 9,97 (−1%) | 13,28 (0%) |
| Melhor da grade (fiscal → λ_π, 0,12) | 10,84 (+8%) | 12,19 (−8%) |

O teste forte (um único ponto de partida ajusta os três episódios?) não passa: o canal estimado não reduz o
erro comum, e o canal fiscal → λ_π reduz o erro comum só piorando o ajuste por episódio (sobretudo em
2020–22). Motivo visível nos dados: a credibilidade fiscal saltou para 0,75 no início de 2016–19, com o teto de
gastos, quando o primário menos o estabilizador estava no pior ponto da série (−9 p.p.); a melhora dos
fundamentos só veio em 2018–19. No Brasil, o ganho de credibilidade de 2016 foi institucional (o anúncio de uma
regra), não um efeito de fundamentos realizados.

## 3. Sensibilidade ("e se"): finalistas da busca híbrida com o canal (λ endógeno, regra central)

| P2, sucesso pela banda | Sem canal | Canal do Focus | Canal tipo Argentina |
|---|---|---|---|
| Híbrido | 34% (até 36%) | 34% | 80% (até 81%) |
| Choque | 34% (até 37%) | 33% | 72% (até 81%) |
| Gradual longo | 26% | 25% | 60% |
| Estratégias do paper | 21% | 21% | 46% |

Atividade até 2030 (P2), canal tipo Argentina: híbrido +2,6; choque −3,7; gradual +3,3.

- Com o canal estimado no Focus (só sobre λ_fiscal), nada muda: λ_fiscal pesa pouco no sucesso.
- Com um canal do tipo argentino (primário menos estabilizador e dívida movendo as duas credibilidades, com o
  coeficiente argentino do primário), o sucesso mais que dobra, o círculo vicioso da seção 2.9 se rompe e o
  híbrido passa a dominar: mais sucesso que o choque em P1 (79% contra 62%) e igual em P2, com atividade acima
  da referência.

## Leitura

O canal que tornaria o ajuste fiscal de baixo multiplicador autossustentável — bons resultados fiscais
elevando a credibilidade da meta — existe na Argentina de 2024–25 e não aparece no Brasil de 2005–2025. No
Brasil, a credibilidade fiscal mudou com regras e instituições (o teto em 2016, sua erosão em 2021–22) antes
dos resultados, e a da meta seguiu o Banco Central. Para o artigo comparado, isso tem duas implicações: o
modelo brasileiro não precisa de um canal de fundamentos para reproduzir a história, mas precisa de um canal
institucional (anúncio crível de regra), que é justamente o instrumento que um governo de baixa credibilidade
pode acionar; e a diferença entre os dois países é um resultado, não um defeito de especificação.

## Limitações

- As medidas de pesquisa (Focus) divergem do λ efetivo em nível; a estimação usa variações e níveis em logit.
- A validação usa as mesmas três janelas de antes, com reservas não observadas (o modelo não reproduz as
  compras e vendas do BC), o que limita o teste do canal de reservas.
- O canal tipo Argentina transporta um coeficiente calibrado em outro regime (âncora cambial, inflação de três
  dígitos).
