# Instruções para a versão 2.2 do modelo de credibilidade fiscal

Três tarefas sobre a v2.1 já implementada. Tudo o que não está descrito aqui permanece como na v2.1. Resultados em `outputs/v2_2/`; manter `outputs/v2_1/` intacto para comparação.

**Ordem de execução:**
1. Tarefa 3 (estimar b3 e ω), porque gera as calibrações usadas nas outras duas.
2. Tarefa 2 (alongamento da dívida).
3. Tarefa 1 (bootstrap), aplicada a todas as variantes, incluindo as novas.

---

## Tarefa 1. Intervalos de confiança por bootstrap para a comparação A × C

### Objetivo

Verificar formalmente se A e C estão empatados na diagonal (λ\*₈₀, λ\*₅₀) e se a vantagem de A na área de sucesso é significativa. Hoje as diferenças são de 0,01 a 0,03 em λ\*, dentro do ruído aparente do Monte Carlo.

### Pré-requisito: guardar o sucesso por trajetória

O bootstrap precisa dos resultados individuais, não só das probabilidades agregadas. Salvar:

- `sucesso_trajetorias.npz`: array booleano com dimensões (especificação, variante, cenário, λ, trajetória). Ordem de grandeza: 3 × 20 × 3 × 101 × 1.000 ≈ 18 milhões de valores; usar `np.packbits` se necessário.
- `sucesso_superficie.npz`: idem para a superfície (variante, especificação, cenário, λ_π, λ_fiscal, trajetória), N = 300.
- Guardar também, por trajetória, qual critério falhou (código inteiro), para o bootstrap das taxas de falha.

### Método

1. **Bootstrap pareado:** como A, B e C usam os mesmos choques (common random numbers), reamostrar **os mesmos índices de trajetória** para os três cenários em cada réplica. Não reamostrar cenários de forma independente, ou a variância da diferença fica superestimada.
2. **Réplicas:** R = 1.000 (seed fixa, distinta da seed da simulação).
3. Em cada réplica, para cada (especificação, variante):
   - recalcular P(sucesso) em toda a grade de λ para A e C;
   - recalcular λ\*₅₀ e λ\*₈₀ de cada um;
   - calcular Δλ\*₈₀ = λ\*₈₀(C) − λ\*₈₀(A) e Δλ\*₅₀ da mesma forma.
4. **Censura:** quando um cenário não atinge o limiar em uma réplica, atribuir λ\* = 1,01 e registrar a fração de réplicas censuradas. Se mais de 20% das réplicas forem censuradas para algum cenário, marcar o resultado como pouco confiável.
5. **Área de sucesso:** mesmo procedimento na superfície (reamostragem pareada em cada ponto da grade 21 × 21), com ΔÁrea = Área(A) − Área(C).
6. **Intervalos:** percentis 2,5% e 97,5%; reportar também a fração de réplicas em que C supera A.

### Regras de leitura

| Resultado | Leitura no relatório |
|---|---|
| IC de 95% de Δλ\*₈₀ contém zero | "empate estatístico na diagonal" |
| IC de 95% inteiramente de um lado | "vantagem significativa de A" ou "de C" |
| IC de ΔÁrea inteiramente positivo | "A é significativamente mais robusto ao descompasso entre λ_π e λ_fiscal" |

Aplicar essas regras na seção de ordenamento e na tabela por variante: onde houver empate estatístico, escrever "A ≈ C > B" em vez de uma ordem estrita.

**Limitação a registrar:** o bootstrap mede apenas a incerteza do Monte Carlo, não a incerteza dos parâmetros. A incerteza de b3 e ω entra pela Tarefa 3, com variantes nos limites dos intervalos estimados.

### Saídas

- `bootstrap_diagonal.csv`: especificação, variante, λ\*₈₀ e λ\*₅₀ de A e C (pontual), Δ, IC 2,5–97,5%, fração C > A, fração censurada.
- `bootstrap_area.csv`: idem para a área de sucesso.
- Gráfico `13_bootstrap_delta.png`: intervalos de Δλ\*₈₀ por especificação e variante (forest plot), com linha vertical em zero.

### Testes

- Com R = 1 e reamostragem identidade, o bootstrap reproduz os valores pontuais.
- A reamostragem usa os mesmos índices para os três cenários.
- Seed fixa gera os mesmos intervalos.

---

## Tarefa 2. Variante de alongamento da dívida

### Objetivo

Testar se reduzir a fatia de LFT reabre a "válvula" de erosão inflacionária da dívida e restaura o sucesso dos cenários quando a lacuna fiscal inicial não está totalmente precificada (φ > 0 em P3). Na v2.1, com φ = 0,25 e 0,5, A e C ficam em 0% de sucesso porque a inflação não corrói a dívida indexada à Selic.

### Passo prévio: separar LFT do Tesouro e compromissadas

Os 59% de "LFT + compromissadas" precisam ser decompostos:
- LFT do Tesouro em mercado (Tesouro Transparente, estoque da DPMFi por título);
- operações compromissadas do BCB (BCB/SGS ou nota de política fiscal; validar o código).

O alongamento atua **apenas sobre a LFT do Tesouro**. As compromissadas dependem da política de liquidez do BCB e da venda de reservas. Reportar a decomposição em t0. Se a meta de 40% para o total não for alcançável reduzindo só a LFT do Tesouro, aplicar a redução máxima possível e registrar o valor efetivamente atingido.

### Especificação

Trajetória exógena para a fatia da LFT do Tesouro:

```
w_lft_meta[t] = w_lft_0 - (w_lft_0 - w_lft_alvo) * min(1, t / T_along)
w_lft[t]      = min(w_lft[t], w_lft_meta[t])     # a meta é um teto
```

- A parcela retirada da LFT vai para títulos de prazo maior: fração `s_ipca` para NTN-B e `1 − s_ipca` para prefixados. Padrão `s_ipca = 0,7`.
- **Custo do alongamento:** a nova emissão paga as taxas correntes do modelo (NTN-B ao `r_long[t]` mais inflação; prefixados à taxa prefixada implícita). O term premium pago é o custo explícito da medida e precisa aparecer no relatório.
- **Interação com a restrição de rolagem:** a migração por juro real baixo (v2) e o alongamento movem a mesma parcela. Aplicar primeiro o alongamento e depois a restrição de rolagem sobre o que restar de LFT, sem contar a mesma migração duas vezes.
- A duração da dívida é recalculada a cada trimestre a partir da composição (duração de Macaulay por tipo, como na v2.1).

### Variantes

| Nome | `w_lft_alvo` (total LFT + compromissadas) | `T_along` | `s_ipca` |
|---|---|---|---|
| `along_20` (referência) | 40% | 20 trimestres | 0,7 |
| `along_12` | 40% | 12 | 0,7 |
| `along_28` | 40% | 28 | 0,7 |
| `along_pre` | 40% | 20 | 0,3 |
| `along_50` | 50% | 20 | 0,7 |

### Experimentos

- **P3:** φ ∈ {0; 0,25; 0,5} × {sem alongamento, `along_20`} × cenários A, B, C × grade de λ, N = 1.000. As demais variantes de alongamento apenas com φ = 0,25.
- **P1 e P2:** apenas `along_20` com a calibração base, para medir o custo do alongamento quando não há lacuna não precificada.

### Saídas

- Tabela: por (especificação, φ, variante de alongamento, cenário), P(sucesso) máxima, λ\*₅₀, λ\*₈₀, fração de falhas por critério, com a marcação † quando nenhum cenário atinge 50%.
- **Decomposição da erosão:** fração da redução da dívida real atribuível a inflação não antecipada, com e sem alongamento, em λ = 0,5 e 0,9.
- **Custo:** diferença no custo real efetivo médio da dívida (p.p. a.a.) e no estoque final, com e sem alongamento, para φ = 0 (onde o alongamento só tem custo, não benefício).
- Gráfico `14_alongamento.png`: P(sucesso) × λ para A, B e C em P3 com φ = 0,25, sem e com alongamento.

### Leitura esperada no relatório

Responder explicitamente: o alongamento reabre a válvula (os cenários voltam a ter sucesso com φ > 0)? A partir de que velocidade de alongamento? Qual o custo em juros quando a lacuna já está precificada (φ = 0)?

### Testes

- A soma dos pesos da composição continua igual a 1 em todo t.
- `w_lft` nunca supera a trajetória-meta quando o alongamento está ativo.
- A duração média da dívida aumenta ao longo do alongamento.
- Com φ = 0, λ = 1 e sem choques, P3 com alongamento continua sem inflação fiscal.
- A migração por rolagem e por alongamento não se sobrepõem (teste com juro real abaixo do piso e alongamento ativo ao mesmo tempo).

---

## Tarefa 3. Estimação de b3 e ω com dados

### Objetivo

Estimar os dois parâmetros que, na v2.1, fazem C passar à frente de A: o repasse cambial (b3) e a fração do prêmio de risco que passa pela Selic (ω). A estimação original de b3 (0,012, trimestral) foi rejeitada por estar fora da faixa de teste.

### 3.1 Repasse cambial (b3)

**Dados (frequência mensal, 2004–2026):** IPCA mensal; IPCA de comercializáveis e de preços livres (BCB/SGS); câmbio R$/US$; expectativas Focus de 12 meses; índice de commodities IC-Br (BCB/SGS); índice do dólar (DXY) e VIX como instrumentos. Validar todos os códigos SGS e registrar a fonte de DXY e VIX. Tratar 2020 com dummy e testar a exclusão.

**Especificações:**

1. **Referência (comparabilidade):** a regressão trimestral da v1.
2. **Projeções locais (Jordà):** para h = 0, …, 12 meses,
   ```
   p[t+h] - p[t-1] = α_h + β_h * (e[t] - e[t-1]) + controles + u[t+h]
   e[t+h] - e[t-1] = γ_h + δ_h * (e[t] - e[t-1]) + controles + v[t+h]
   ```
   com `p` e `e` em log, e controles: 12 defasagens da inflação mensal, hiato, desvio do Focus em relação à meta e variação do IC-Br.
   **Repasse acumulado:** `ERPT_h = β_h / δ_h`, reportado em h = 3, 6 e 12 meses, com IC por Newey-West (ou bootstrap em blocos).
3. **Variável instrumental:** a depreciação do real responde a notícias domésticas que também afetam a inflação. Repetir (2) em 2SLS, instrumentando a depreciação com a variação do DXY e do VIX. Reportar o F do primeiro estágio; se for menor que 10, sinalizar instrumentos fracos e manter a versão OLS como principal.
4. **Robustez:** repetir com IPCA de comercializáveis e com preços livres; e em duas subamostras (2004–2015 e 2016–2026).

**Mapeamento para o modelo.** O b3 do modelo multiplica a depreciação de 12 meses numa equação trimestral com inércia (P1, P2) ou sem inércia (P3), então não é diretamente comparável a `ERPT_h`. Calibrar b3 **por especificação** com casamento de funções impulso-resposta:
- simular no modelo um choque de 10% de depreciação, com todos os demais choques nulos, Selic fixa e λ = 0,5;
- escolher b3 para que o repasse acumulado simulado em 4 trimestres seja igual ao `ERPT_12` estimado;
- conferir o ajuste em 2 e 8 trimestres e reportar a discrepância.

Produzir b3 pontual e os valores correspondentes aos limites do IC de 95% de `ERPT_12`.

### 3.2 Fração do prêmio que passa pela Selic (ω)

**Dados (mensal ou por reunião do Copom, 2005–2026):** meta Selic; expectativa Focus de inflação 12 meses à frente e meta; hiato (como no modelo); medida de prêmio soberano: EMBI+ Brasil (Ipeadata) e, se disponível, CDS de 5 anos. Converter o prêmio para pontos percentuais.

**Estimação principal: regra de Taylor com prêmio**

```
i[t] = ρ i[t-1] + (1 - ρ) * (c + φπ (pi_e[t] - meta[t]) + φh h[t-1] + ψ (prem[t-1] - prem_médio)) + u[t]
```

- Estimar por mínimos quadrados não lineares; robustez por GMM com instrumentos defasados (no espírito de Clarida, Galí e Gertler).
- **ω estimado = ψ**, o efeito de longo prazo de 1 p.p. de prêmio sobre a Selic, que corresponde à definição do modelo: `r_neutro[t] = r_neutro_base + ω (prem[t] − p0)`.
- Usar o prêmio defasado para reduzir a simultaneidade. Registrar que, como as expectativas de inflação já estão na regra, ψ mede o efeito do prêmio **além** do canal das expectativas.

**Verificação cruzada: canal do juro longo**

No modelo, o juro longo recebe a fração (1 − ω) do prêmio. Estimar:

```
Δ NTN-B10[t] = a + b * Δprem[t] + c * Δ Selic_esperada[t] + e[t]
```

com a Selic esperada do Focus (horizonte de 12 a 24 meses). Se o modelo estiver bem especificado, `b ≈ 1 − ω`. Reportar `ψ + b` e discutir se a soma é próxima de 1; se for muito diferente, registrar que a premissa de prêmio integralmente repassado (sem dupla contagem) pode não valer nos dados.

**Robustez:** subamostras 2005–2015 e 2016–2026 (a autonomia formal do BC é de 2021; testar também a quebra nessa data). Se ω estimado sair fora de [0, 1], limitar ao intervalo e registrar.

### 3.3 Uso das estimativas no modelo

Criar as variantes:

| Nome | b3 | ω |
|---|---|---|
| `estimada` | pontual | pontual |
| `estimada_b3_baixo` / `_b3_alto` | limites do IC | pontual |
| `estimada_omega_baixo` / `_omega_alto` | pontual | limites do IC |

Rodar as três especificações, a superfície para `estimada` e o bootstrap da Tarefa 1 em todas. A variante `estimada` passa a ser apresentada **ao lado** da base no relatório. Não substituir a base, para manter a comparabilidade com a v2.1.

### Saídas

- `estimacao_b3.csv` e `estimacao_omega.csv`: coeficientes, erros-padrão, IC, F do primeiro estágio, subamostras.
- Gráficos `15_erpt_lp.png` (repasse acumulado por horizonte, OLS e IV) e `16_taylor_premio.png` (ψ por subamostra, com IC).
- Seção nova no relatório: "Parâmetros estimados", com a calibração resultante de b3 por especificação e o ordenamento A × C na variante `estimada`.

### Testes

- A calibração por impulso-resposta reproduz o `ERPT_12` alvo com erro menor que 0,01.
- Com dados simulados pelo próprio modelo (b3 e ω conhecidos), as rotinas de estimação recuperam os parâmetros dentro do IC de 95% (teste de recuperação).
- Todos os códigos de séries são validados antes da estimação, com falha explícita e registrada se alguma série não existir.

---

## Relatório v2.2

Acrescentar à estrutura da v2.1:

1. **Parâmetros estimados** (Tarefa 3), logo após a checagem de consistência.
2. Na seção de ordenamento, usar as regras de leitura do bootstrap: ordem estrita apenas quando o IC excluir zero; caso contrário, "A ≈ C".
3. **Alongamento da dívida** (Tarefa 2), como seção própria depois da validação.
4. **Síntese final** em até 10 linhas respondendo: (a) A e C são estatisticamente distinguíveis? (b) com os parâmetros estimados, quem fica à frente? (c) o alongamento reabre a válvula da erosão inflacionária e a que custo?

Manter a marcação † para variantes em que nenhum cenário atinge 50%, e a regra de que a leitura fiscal da validação só é feita quando o θ de melhor ajuste for maior que zero.