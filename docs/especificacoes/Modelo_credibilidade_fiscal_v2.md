# Modelo de simulação: Selic, reservas, ajuste fiscal e credibilidade — versão 2

Instruções para atualizar o modelo em Python que compara três estratégias de política econômica para o Brasil e identifica **qual delas depende de menor adesão do mercado** para estabilizar a dívida pública sem perder o controle da inflação.

---

## 0. O que muda em relação à versão 1

| # | Mudança | Motivo (rodada de 02/11/2026) |
|---|---|---|
| 1 | **Equação da inflação vira módulo intercambiável:** P1 (Phillips híbrida), P2 (Phillips achatada) e P3 (fechamento fiscal, FTPL). | Testar se o ranking dos cenários depende da teoria de inflação adotada. |
| 2 | **λ separado em λ_π (meta de inflação) e λ_fiscal (fundamentos fiscais).** A diagonal λ_π = λ_fiscal reproduz a versão 1. | A janela não monotônica de B (0,77–0,84) mostrou que um único λ mistura duas crenças distintas. |
| 3 | **Restrição de rolagem:** o Tesouro não consegue rolar LFT com juro real abaixo de um piso; a parcela que vence migra para títulos indexados. | Em B com λ baixo, a dívida chegava a −10% do PIB com inflação de 200%: artefato de rolagem irrestrita. |
| 4 | **Novo critério de falha:** inflação explosiva (acima de 20% em qualquer trimestre). Sem teto artificial de 200% na simulação. | O critério de dívida perde sentido quando a dívida é dissolvida por inflação. |
| 5 | **Tolerância δ do cenário C cai a zero** em 8 trimestres após o fim do corte. | Com δ permanente, a Selic de C ficava 1 p.p. abaixo da Taylor para sempre. |
| 6 | **Term premium converge** do valor calibrado em t0 para um valor de longo prazo. | O term premium de −3,33 p.p. constante favorecia mecanicamente os cenários de corte. |
| 7 | **Rodadas de sensibilidade obrigatórias:** `r_neutro_base = 4,5`, `b1 = 0,82` e `b3` estimado. | Coerência entre a Selic de 7,5% e o juro neutro; inércia e repasse estimados foram rejeitados na v1. |
| 8 | **Validação histórica por especificação de inflação**, usada como critério de escolha entre P1, P2 e P3. | P1 não reproduziu o pico de 2021–22. |
| 9 | **Gráficos novos:** P(sucesso) × λ por especificação, fronteira dívida × inflação, superfície λ_π × λ_fiscal; câmbio em escala log. | A troca entre dívida e inflação de A e C não aparecia no ranking único. |

Tudo o que não está descrito aqui permanece como na versão 1.

---

## 1. Objetivo

Comparar três cenários:

| Cenário | Descrição |
|---|---|
| **A. Ortodoxo** | Pacote fiscal aprovado no ano 1; Selic segue regra de Taylor guiada pelas expectativas; sem venda de reservas. |
| **B. Lara Resende puro** | Selic cai por trajetória exógena até 7,5% a.a. em 6 trimestres; venda de reservas (US$ 100 bi em 4 trimestres); sem pacote fiscal novo. |
| **C. Lara Resende condicionado** | Pacote fiscal aprovado no ano 1 **e** corte rumo a 7,5% limitado por um piso derivado da Taylor, com tolerância que desaparece após a transição; venda de reservas como ponte. |

### 1.1 Duas dimensões de adesão do mercado

| Parâmetro | O que mede | Onde atua |
|---|---|---|
| **λ_π ∈ [0, 1]** | crença na meta de inflação e na trajetória anunciada da Selic | expectativas de inflação (4.2), Selic esperada no juro longo (4.4) |
| **λ_fiscal ∈ [0, 1]** | crença de que os superávits anunciados vão se materializar | prêmio de risco (4.3), fuga cambial (4.8), superávits esperados no P3 (4.7) |

- **0** = quebra total: o mercado extrapola o passado e pune inconsistências.
- **1** = adesão total: o mercado precifica o plano anunciado.
- **Diagonal** λ_π = λ_fiscal = λ: reproduz a análise unidimensional da v1 e continua sendo o resultado de referência.

### 1.2 Resultados principais

1. Para cada especificação de inflação (P1, P2, P3): curva P(sucesso) × λ na diagonal e o λ\*₈₀ de cada cenário.
2. **Área de sucesso:** fração do quadrado [0,1] × [0,1] em que P(sucesso) ≥ 80%. O cenário com maior área é o mais robusto às duas formas de desconfiança.
3. **Robustez à teoria:** se o ordenamento dos cenários se mantém nas três especificações.

---

## 2. Stack e estrutura do repositório

Sem mudanças de stack. Novos arquivos e alterações:

```
modelo-credibilidade/
├── config/
│   ├── calibracao.yaml        # + parâmetros de P3, rolagem, term premium
│   ├── cenarios.yaml          # + δ decrescente, variantes de C
│   └── experimentos.yaml      # NOVO: matriz especificação × cenário × variante
├── src/
│   ├── inflacao.py            # NOVO: módulos P1, P2, P3 com interface comum
│   ├── fiscal_valoracao.py    # NOVO: valor presente dos superávits e lacuna (P3)
│   ├── rolagem.py             # NOVO: restrição de rolagem e migração da composição
│   ├── modelo.py              # chama inflacao.py pelo nome da especificação
│   ├── varredura.py           # + varredura em especificação e superfície λ_π × λ_fiscal
│   ├── metricas.py            # + critério de inflação explosiva, área de sucesso
│   ├── validacao.py           # NOVO (antes dentro de run.py): validação por especificação
│   └── graficos.py            # + gráficos 8 a 11
```

Interface comum dos módulos de inflação:

```python
def inflacao(estado: Estado, params: Params, choque: float) -> tuple[float, dict]:
    """Retorna a inflação do trimestre e um dicionário de componentes
    (inércia, expectativa, hiato, câmbio, fiscal) para a decomposição."""
```

---

## 3. Dados

Mantém a seção 3 da v1, com acréscimos:

| Variável | Fonte | Uso |
|---|---|---|
| Expectativas de resultado primário e de dívida líquida | BCB/Focus (API Olinda), medianas anuais | `s_planejado` histórico na validação de P3 |
| Prazo médio e duração por tipo de título | Tesouro: Relatório Mensal da Dívida | `duracao[t]` em P3 e giro na rolagem |
| Taxas implícitas prefixadas e NTN-B por vértice | ANBIMA | checagem do term premium |

**Datas:** usar apenas o **último trimestre fechado** como t0. Um trimestre parcial não pode ser rotulado com a data de fim de trimestre. Se for usado algum dado do trimestre corrente, registrar no relatório a data real da última observação.

---

## 4. Especificação do modelo

As seções não listadas aqui seguem a v1.

### 4.2 Expectativas (λ_π)

```
pi_e[t] = λ_π * pi_meta
        + (1 - λ_π) * (pi[t-1] + κ * inconsistencia[t])
```

`inconsistencia[t]` continua medida em p.p. (como implementado na v1), com `μ` e `p3` recalibrados.

No módulo P3, as expectativas também incorporam a inflação fiscal esperada:

```
pi_e[t] += (1 - λ_π) * pi_fiscal[t-1]
```

### 4.3 Prêmio de risco (λ_fiscal)

```
prem[t] = p0 + λ_fiscal * F_planejado[t]
             + (1 - λ_fiscal) * (F_corrente[t] + p3 * inconsistencia[t])
```

**Em P3**, a lacuna fiscal já gera inflação. Para não contar o mesmo efeito duas vezes, rodar P3 com `p2` reduzido (padrão: metade) e reportar a sensibilidade a `p2` ∈ {0; metade; integral}.

### 4.4 Juro real longo e term premium

```
r_long[t] = media_esperada(i - pi_e, próximos 8 trimestres) + tp[t] + prem[t]
tp[t]     = tp_lp + (tp_0 - tp_lp) * exp(-t / τ_tp)
```

- `tp_0`: valor calibrado para fechar a identidade em t0 (na v1, −3,33 p.p.).
- `tp_lp`: term premium de longo prazo. Padrão **+0,75 p.p.**; testar 0,5 e 1,0.
- `τ_tp`: velocidade de convergência. Padrão **6 trimestres** (meia-vida de cerca de 4 trimestres; convergência quase completa em 12).
- A Selic esperada usa a trajetória anunciada ponderada por **λ_π** e a extrapolação ingênua por (1 − λ_π).

### 4.5 Política monetária

Cenário C:

```
δ[t] = δ0                                     se t <= T_corte
δ[t] = δ0 * max(0, 1 - (t - T_corte) / T_δ)   se t >  T_corte
i[t] = max(trajetoria_exogena[t], i_taylor[t] - δ[t])
```

- Padrões: `δ0 = 1,0`, `T_δ = 8` trimestres.
- Depois de `T_corte + T_δ`, C segue a Taylor com o piso de 7,5% apenas como limite inferior.

**Coerência entre a meta de Selic e o juro neutro.** Com `pi_meta = 3`, uma Selic de 7,5% só é neutra se `r_neutro_base = 4,5`. Rodar todos os cenários com:
- `r_neutro_base = 5,0` (padrão da v1: 7,5% é levemente expansionista);
- `r_neutro_base = 4,5` (7,5% é neutra).

Registrar no relatório o juro real longo neutro implícito em cada caso e a diferença em relação ao juro curto neutro.

### 4.7 Inflação: três módulos

Todos os módulos compartilham repasse cambial, choque e decomposição em componentes.

#### P1. Phillips híbrida (base, igual à v1)

```
pi[t] = b1 * pi[t-1] + (1 - b1) * pi_e[t] + b2 * h[t-1] + b3 * de_12m[t] + ε_pi
```

Representa o modelo semiestrutural convencional, com inércia (a inflação inercial do diagnóstico do Larida) e canal de demanda.

#### P2. Phillips achatada

Mesma equação de P1, com `b2` em grade: **{0; 0,025; 0,05; 0,10; 0,15}**. O valor de referência de P2 é `b2 = 0,025`.

Representa a crítica empírica à inclinação da curva. A inércia (`b1`) e o repasse (`b3`) permanecem, porque são canais distintos da inclinação.

#### P3. Fechamento fiscal (FTPL)

```
pi[t] = pi_e[t] + pi_fiscal[t] + b2_p3 * h[t-1] + b3 * de_12m[t] + ε_pi
```

- `b2_p3`: inclinação residual pequena. Padrão **0,025**; testar 0.
- Sem termo de inércia própria: a persistência vem de `pi_e` (com λ_π < 1) e da duração da dívida.

**Superávits esperados (λ_fiscal).**
```
s_esperado[t+k] = λ_fiscal * s_planejado[t+k] + (1 - λ_fiscal) * s[t]     # s corrente persistido
```
- `s_planejado`: trajetória do primário anunciada pelo cenário (pacote fiscal em A e C; ausência dele em B).

**Valor presente dos superávits (% do PIB)** — em `fiscal_valoracao.py`:
```
fator_k = ((1 + g_esp/100) / (1 + r_desc/100)) ** (k/4)
VP[t]   = Σ_{k=1}^{H} (s_esperado[t+k] / 4) * fator_k  +  VT[t]
VT[t]   = s_esperado[t+H] / max(r_desc - g_esp, Δ_min) * fator_H
```
- `r_desc = r_long[t]` (juro real longo); `g_esp = g_potencial`.
- `H = 40` trimestres.
- `Δ_min = 0,5 p.p.`: piso de (r − g) para evitar valor terminal explosivo. Reportar sensibilidade.

**Lacuna e inflação fiscal.**
```
lacuna[t]     = d_net[t] - VP[t]
pi_fiscal[t]  = θ * (lacuna[t] - φ * lacuna_0) / (d_net[t] * duracao[t]) * 100
pi_fiscal[t]  = suavizado: 0,5 * pi_fiscal[t] + 0,5 * pi_fiscal[t-1]
```
- **Dívida líquida, não bruta:** a FTPL trata do passivo nominal líquido. As reservas entram como ativo real, de modo que a venda de reservas aumenta o passivo líquido em reais na margem e reduz o hedge cambial.
- `duracao[t] = w_lft * 0,25 + w_pre * dur_pre + w_ipca * dur_ipca + w_fx * dur_fx` (em anos, a partir do RMD). A LFT reprecifica a cada trimestre, então dívida mais pós-fixada significa ajuste fiscal via inflação mais rápido.
- `θ ∈ [0, 1]`: fração da lacuna absorvida por inflação (o restante vai para prêmio e juro real). Padrão **0,5**; calibrar na validação (seção 10) com grade {0,25; 0,5; 0,75; 1,0}.
- `φ ∈ [0, 1]`: fração da lacuna inicial que ainda não está precificada. **Padrão 0**: a lacuna existente em t0 já está refletida na inflação e no prêmio correntes, e só revisões geram inflação fiscal. Testar φ = 0,25 e 0,5.
- `pi_fiscal` pode ser negativo: um ajuste crível acima do esperado reduz a inflação (desinflação fiscal).

**Implicação para os cenários.** Em P3, um corte de juros reduz o custo da dívida e eleva o VP, o que reduz a inflação fiscal (o argumento de Lara Resende). Ao mesmo tempo, se λ_fiscal for baixo e não houver pacote fiscal, o VP continua baixo e a lacuna gera inflação (o argumento de Cochrane). O módulo captura os dois efeitos na mesma equação.

### 4.8 Câmbio

O termo de fuga passa a usar λ_fiscal:

```
... + (1 - λ_fiscal) * c4 * inconsistencia[t]
```

### 4.11 Dívida: restrição de rolagem

Em `rolagem.py`, aplicado a cada trimestre antes do cálculo do custo efetivo:

```
r_real_lft[t] = i[t] - pi_e[t]
if r_real_lft[t] < r_min_rolagem:
    migracao   = w_lft[t] * giro_lft * min(1, (r_min_rolagem - r_real_lft[t]) / banda)
    w_lft[t]  -= migracao
    w_ipca[t] += migracao        # refinanciada em NTN-B ao r_long[t] corrente
```

- `r_min_rolagem`: juro real mínimo que o mercado aceita para carregar LFT. Padrão **1,0%**; testar 0 e 2,0.
- `giro_lft`: fração da LFT que vence por trimestre (do RMD).
- `banda`: suavização da migração. Padrão **2 p.p.**
- As compromissadas do BCB não migram (o BCB precisa enxugar liquidez), mas, se `r_real_lft < 0`, registrar no relatório os trimestres de juro real negativo como indicador de repressão financeira.

**Alternativa (opcional, flag `--monetizacao`):** em vez de migrar para NTN-B, o excesso vira expansão monetária, somando `ψ * migracao / d` à inflação do trimestre seguinte.

Com isso, a dívida não pode mais ser dissolvida por inflação a custo zero: a parcela que vence passa a pagar juro real positivo.

### 4.12 Simulação sem teto artificial

Remover o teto de 200% para a inflação. Se `pi > 50%` em algum trimestre, encerrar a trajetória, marcá-la como **explosiva** e registrar o trimestre de ruptura. Trajetórias explosivas contam como falha e ficam fora dos percentis de dívida e inflação (reportados apenas sobre trajetórias não explosivas, com a fração explosiva informada ao lado).

---

## 5. Calibração

Acrescentar ao `calibracao.yaml`:

| Parâmetro | Padrão | Faixa de teste | Módulo |
|---|---|---|---|
| `b2` (P2) | 0,025 | 0–0,15 | P2 |
| `b2_p3` | 0,025 | 0–0,05 | P3 |
| `θ` | 0,5 | 0,25–1,0 | P3 |
| `φ` | 0 | 0–0,5 | P3 |
| `Δ_min` | 0,5 | 0,25–1,0 | P3 |
| `p2` em P3 | 0,15 | 0–0,3 | P3 |
| `tp_lp` | 0,75 | 0,5–1,0 | todos |
| `τ_tp` | 6 | 4–12 | todos |
| `δ0`, `T_δ` | 1,0 / 8 | δ0 0–1; T_δ 4–12 | C |
| `r_min_rolagem` | 1,0 | 0–2,0 | todos |
| `banda` | 2,0 | — | todos |
| `r_neutro_base` | 5,0 | **4,5 obrigatório** | todos |
| `b1` | 0,6 | **0,82 obrigatório** | P1, P2 |
| `b3` | 0,06 | **0,012 (estimado) obrigatório**, 0,03–0,12 | todos |

As rodadas marcadas como obrigatórias entram no relatório principal, não apenas no anexo de sensibilidade.

---

## 6. Critério de sucesso

Um cenário é bem-sucedido se, **simultaneamente**:

1. **Dívida estabilizada:** inclinação de `d_gross` nos últimos 8 trimestres ≤ 0 **e** `d_gross` final ≤ inicial + 5 p.p.
2. **Inflação controlada:** média de `pi` nos últimos 8 trimestres ≤ `pi_meta + 1,5`.
3. **Inflação não explosiva (NOVO):** `pi` ≤ 20% em todos os trimestres.
4. **Reservas preservadas:** `R` ≥ `R_min` em todos os trimestres.

O critério 3 tem precedência no diagnóstico: se falhar, a falha é registrada como "inflação explosiva" e os critérios de dívida não são interpretados.

Reportar também, separadamente, P(dívida ok) e P(inflação ok), para a fronteira do gráfico 9.

**Sensibilidade do teto de inflação:** rodar também com `pi_meta + 2,0` (5%) e mostrar se o ordenamento muda.

---

## 7. Varredura (`varredura.py`, `experimentos.yaml`)

### 7.1 Matriz de experimentos

```yaml
especificacoes: [P1, P2, P3]
cenarios: [A, B, C]
variantes:
  base:           {}
  neutro_45:      {r_neutro_base: 4.5}
  inercia_alta:   {b1: 0.82}          # só P1 e P2
  repasse_est:    {b3: 0.012}
  C_lento:        {cenario: C, T_corte: 12}
  C_sem_tolerancia: {cenario: C, delta0: 0.0}
```

### 7.2 Diagonal (λ_π = λ_fiscal = λ)

- Grade λ = 0,00, 0,01, …, 1,00.
- Determinística e Monte Carlo com N = 1.000, seed fixa, **mesmos choques entre cenários, especificações e variantes** (common random numbers).
- Saída: λ\*_det, λ\*₅₀, λ\*₈₀ por (especificação, cenário, variante).

### 7.3 Superfície (λ_π × λ_fiscal)

- Grade 21 × 21 (passo 0,05), N = 300 por ponto.
- Apenas para a variante `base` e para `neutro_45`.
- Saída: P(sucesso) por ponto e **área de sucesso** (fração dos pontos com P ≥ 80%).

### 7.4 Custo computacional

A matriz completa tem cerca de 3 especificações × 3 cenários × 6 variantes × 101 λ × 1.000 trajetórias. Vetorizar trajetórias como dimensão do array; paralelizar especificações e variantes com `joblib`. Salvar resultados intermediários em parquet por (especificação, variante) para permitir retomada.

---

## 8. Gráficos

Mantêm-se os gráficos 1 a 7 da v1 (gerados por especificação), com estes ajustes:
- **Gráfico 5 (leques):** câmbio em **escala logarítmica**; inflação com eixo limitado a [−2, 25] e anotação da fração de trajetórias explosivas.

Novos gráficos:

8. **P(sucesso) × λ por especificação:** três painéis (P1, P2, P3), três curvas por painel, λ\*₈₀ marcado. É o gráfico central da versão 2.
9. **Fronteira dívida × inflação:** eixo x = P(dívida ok), eixo y = P(inflação ok), uma curva por cenário percorrendo λ de 0 a 1, com pontos rotulados em λ = 0,3; 0,6; 0,9. Um painel por especificação.
10. **Superfície λ_π × λ_fiscal:** mapa de calor de P(sucesso) por cenário, contorno de 80% destacado, área de sucesso no título. Painéis: cenários × especificações (3 × 3).
11. **Decomposição da inflação:** contribuições de inércia, expectativa, hiato, câmbio e componente fiscal, para cada cenário em λ = 0,5, nas três especificações.
12. **Ordenamento por variante:** tabela-gráfico (heatmap de posições 1–3) com o ranking dos cenários por especificação × variante. Mostra de relance se a conclusão é robusta.

---

## 9. Testes

Mantêm-se os testes da v1. Acrescentar:

- **Diagonal reproduz a v1:** com λ_π = λ_fiscal, especificação P1, sem rolagem, δ constante e term premium constante, os resultados batem com os da v1 (tolerância numérica).
- **P3, lacuna nula:** se `VP = d_net` em todo t e `φ = 0`, então `pi_fiscal = 0`.
- **P3, sinal:** um aumento de `s_planejado` com λ_fiscal = 1 reduz `pi_fiscal`.
- **P3, duração:** para a mesma lacuna, dívida mais curta gera `pi_fiscal` maior por trimestre.
- **P3, valor terminal:** finito para qualquer `r_desc − g_esp` (piso Δ_min ativo).
- **Rolagem:** com juro real abaixo do piso, `w_lft` cai e `w_ipca` sobe na mesma magnitude; a soma dos pesos continua 1.
- **Explosão:** trajetória com `pi > 50%` é encerrada e contada como falha.
- **δ decrescente:** em C, `i[t] >= i_taylor[t]` para todo `t > T_corte + T_δ` (respeitado o piso de 7,5%).

---

## 10. Validação por especificação

Para cada especificação (P1, P2, P3) e episódio (2016–2019 e 2020–2022):

1. Impor Selic, primário e depreciação cambial observados.
2. Em P3, usar como `s_planejado` as expectativas do Focus para o primário em cada data (o que o mercado esperava, não o que ocorreu).
3. Calibrar por grade: λ (diagonal) e, em P3, θ.
4. Medir o erro normalizado (RMSE/desvio-padrão) de inflação e de NTN-B 10 anos.

Tabela de saída:

| Especificação | Episódio | λ de melhor ajuste | θ (P3) | Erro mín. | Erro λ = 0 | Erro λ = 1 | Reproduz o pico de 2021–22? |
|---|---|---|---|---|---|---|---|

**Regra de uso dos resultados:**
- A especificação com menor erro combinado nos dois episódios é apresentada como **referência** no relatório.
- As outras duas continuam no relatório principal (gráficos 8 e 12). A conclusão só é considerada robusta se o ordenamento dos cenários for o mesmo nas três.
- Se P3 reproduzir o pico de 2021–22 e P1 não, isso é evidência a favor da leitura fiscal da inflação recente no Brasil. Se nenhuma reproduzir, registrar que o pico tem componente de oferta não modelado.
- Atenção ao sobreajuste: P3 tem um parâmetro livre a mais (θ). Reportar também o erro de P3 com θ fixo em 0,5.

---

## 11. Execução e saídas

```bash
python run.py --experimentos config/experimentos.yaml \
              --calibracao config/calibracao.yaml \
              --mc 1000 --seed 42 \
              [--especificacoes P1,P2,P3] [--superficie] [--monetizacao]
```

Saídas em `outputs/v2/`:
- `resultados_lambda.parquet`: métricas por especificação, variante, cenário e λ (inclui P(dívida ok), P(inflação ok), fração explosiva);
- `superficie.parquet`: P(sucesso) por (especificação, variante, cenário, λ_π, λ_fiscal);
- `lambda_star.csv` e `area_sucesso.csv`;
- `validacao.csv`;
- gráficos 1 a 12;
- `relatorio.md`, com nova estrutura:
  1. ordenamento por especificação (P1, P2, P3) na variante base;
  2. robustez do ordenamento entre especificações e variantes (gráfico 12);
  3. área de sucesso na superfície λ_π × λ_fiscal;
  4. validação e especificação de referência;
  5. premissas e limitações.

---

## 12. Limitações a registrar no relatório

- λ_π e λ_fiscal são **exógenos e constantes**. Extensão sugerida: credibilidade adaptativa, `λ[t] = λ[t−1] + ν (sucesso_parcial[t] − 0,5)`, separadamente para cada dimensão.
- P3 é uma versão reduzida da FTPL: não resolve um equilíbrio com expectativas racionais; a lacuna é absorvida por inflação na proporção θ, e θ é calibrado, não derivado.
- A escolha de **φ = 0** (a lacuna inicial já está precificada) é uma hipótese forte. Com φ > 0, todos os cenários começam com pressão inflacionária adicional.
- A restrição de rolagem é uma regra de comportamento, não um modelo de demanda por títulos.
- O modelo continua semiestrutural e sem choques de oferta e commodities.
- Os resultados de P1 e P2 dependem de `b1` e `b3`; os de P3 dependem de `θ`, `Δ_min` e da duração da dívida. Os gráficos de sensibilidade precisam acompanhar o gráfico principal.
- O piso de reservas (`R_min`) é ilustrativo e deve ser alinhado à métrica ARA do FMI.