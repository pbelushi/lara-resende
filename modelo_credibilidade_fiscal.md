# Modelo de simulação: Selic, reservas, ajuste fiscal e credibilidade

Instruções para implementar em Python um modelo de simulação que compara três estratégias de política econômica para o Brasil e identifica **qual delas depende de menor adesão do mercado** para estabilizar a dívida pública sem perder o controle da inflação.

---

## 1. Objetivo

Comparar três cenários:

| Cenário | Descrição |
|---|---|
| **A. Ortodoxo** | Pacote fiscal aprovado no ano 1; Selic segue regra de Taylor guiada pelas expectativas; sem venda de reservas. |
| **B. Lara Resende puro** | Selic cai por trajetória exógena até 7,5% a.a. em 12–18 meses; venda de reservas (até US$ 100 bi em 12 meses) para conter o câmbio; sem pacote fiscal novo. |
| **C. Lara Resende condicionado** | Pacote fiscal aprovado no ano 1 **e** corte gradual da Selic rumo a 7,5%, limitado por um piso derivado das expectativas; venda de reservas como ponte. |

A variável central é a **adesão do mercado**, λ ∈ [0, 1]:

- **λ = 0:** quebra total de expectativas. O mercado ignora anúncios, extrapola o passado e cobra prêmio máximo por inconsistências de política.
- **λ = 1:** adesão total. As expectativas ancoram na meta e o prêmio de risco reflete os fundamentos **planejados**, não os correntes.

O resultado principal é a curva de sucesso de cada cenário em função de λ e o **λ\* mínimo** de cada um: a menor adesão que ainda garante sucesso. **O cenário com menor λ\* é o mais robusto à desconfiança.**

---

## 2. Stack e estrutura do repositório

- Python 3.11+
- `numpy`, `pandas`, `scipy`, `matplotlib`, `pyyaml`, `python-bcb` (dados do BCB), `pytest`

```
modelo-credibilidade/
├── config/
│   ├── calibracao.yaml        # parâmetros estruturais e valores iniciais
│   └── cenarios.yaml          # definição dos cenários A, B, C
├── data/
│   ├── raw/                   # downloads brutos
│   └── processed/             # séries limpas e trimestralizadas
├── src/
│   ├── dados.py               # coleta e tratamento
│   ├── modelo.py              # equações e simulação de um cenário
│   ├── politicas.py           # regras de Selic, reservas e pacote fiscal
│   ├── varredura.py           # varredura em λ e Monte Carlo
│   ├── metricas.py            # critério de sucesso e λ*
│   └── graficos.py            # visualizações
├── notebooks/
│   └── exploracao.ipynb
├── tests/
│   └── test_modelo.py
├── run.py                     # CLI: roda tudo e salva resultados
└── README.md
```

---

## 3. Dados (fontes públicas)

Frequência do modelo: **trimestral**. Horizonte de simulação: **40 trimestres (10 anos)** a partir do último dado disponível.

| Variável | Fonte | Observação |
|---|---|---|
| Meta Selic | BCB/SGS 432 | conferir código |
| Selic efetiva anualizada | BCB/SGS 4189 | conferir código |
| IPCA mensal | BCB/SGS 433 | acumular em 12 meses |
| Dívida bruta do governo geral (% PIB) | BCB/SGS 13762 | conferir código |
| Dívida líquida do setor público (% PIB) | BCB/SGS 4513 | conferir código |
| Reservas internacionais (US$ mi) | BCB/SGS 3546 | conferir código |
| Câmbio R$/US$ | BCB/SGS 1 | média trimestral |
| Resultado primário | BCB (NFSP) / Tesouro (RTN) | usar governo central e setor público consolidado |
| Composição da DPMFi (LFT, prefixados, IPCA, câmbio) e prazo médio | Tesouro: Relatório Mensal da Dívida (Tesouro Transparente) | incluir compromissadas do BCB à parte |
| Expectativas (IPCA, Selic, PIB, câmbio) | BCB/Focus via API Olinda (`python-bcb`) | medianas |
| Taxas NTN-B longas | Tesouro Direto / ANBIMA | juro real de 5 e 10 anos |
| PIB nominal e real | IBGE/SIDRA (Contas Nacionais Trimestrais) | |
| Renúncias fiscais por item | Receita Federal: Demonstrativo de Gastos Tributários | base para as medidas fiscais |

Regras:
- Todos os códigos SGS devem ser **validados no início** (`dados.py` testa se a série existe e se o nome bate). Se falhar, registrar o erro sem interromper o resto.
- Valores iniciais do modelo = **última observação disponível**. Nada de valores fixos no código; tudo em `calibracao.yaml`, preenchido automaticamente a partir dos dados.

---

## 4. Especificação do modelo

Taxas anualizadas em % a.a.; o passo de simulação é trimestral. As defasagens são de um trimestre, salvo indicação.

### 4.1 Variáveis de estado

| Símbolo | Significado |
|---|---|
| `h` | hiato do produto (%) |
| `g` | crescimento real do PIB |
| `pi` | inflação (IPCA 12m) |
| `pi_e` | expectativa de inflação 12m à frente |
| `i` | Selic nominal |
| `r_long` | juro real longo (NTN-B 10 anos) |
| `prem` | prêmio de risco soberano |
| `de` | depreciação cambial trimestral |
| `R` | reservas (US$) |
| `s` | resultado primário (% PIB) |
| `d_gross`, `d_net` | dívida bruta e líquida (% PIB) |
| `w_lft`, `w_pre`, `w_ipca`, `w_fx` | composição da dívida |

### 4.2 Expectativas (onde λ atua)

```
pi_e[t] = λ * pi_meta
        + (1 - λ) * (pi[t-1] + κ * inconsistencia[t])
```

`inconsistencia[t]` mede o quanto a política se afasta do que um mercado cético consideraria sustentável:

```
inconsistencia[t] = max(0, i_taylor[t] - i[t]) / 100      # Selic abaixo da regra
                  + μ * max(0, s_estab[t] - s[t])          # primário abaixo do que estabiliza a dívida
```

- `i_taylor[t]`: Selic que a regra de Taylor indicaria (seção 4.5), calculada mesmo nos cenários em que ela não é seguida.
- `s_estab[t] = (r_efetivo[t] - g[t]) / (1 + g[t]) * d_gross[t]`: primário que estabiliza a dívida.

### 4.3 Prêmio de risco

```
F_corrente[t]  = p1 * (d_gross[t] - d_ref) + p2 * (s_estab[t] - s[t])
F_planejado[t] = mesma expressão avaliada na trajetória ANUNCIADA ao final do horizonte
prem[t] = p0 + λ * F_planejado[t] + (1 - λ) * (F_corrente[t] + p3 * inconsistencia[t])
prem[t] = max(prem[t], prem_min)
```

Com λ alto, o mercado precifica o plano. Com λ baixo, precifica a situação corrente e pune incoerências.

### 4.4 Juro real longo

```
r_long[t] = media_esperada(i - pi_e, próximos 8 trimestres) + term_premium + prem[t]
```

A média esperada usa a trajetória de Selic **anunciada** ponderada por λ e uma extrapolação ingênua (Selic atual constante) ponderada por (1 − λ).

### 4.5 Política monetária (depende do cenário)

Regra de Taylor:
```
i_taylor[t] = ρ * i[t-1] + (1 - ρ) * (r_neutro[t] + pi_e[t] + φπ * (pi[t-1] - pi_meta) + φh * h[t-1])
r_neutro[t] = r_neutro_base + prem[t] - p0
```

- **Cenário A:** `i[t] = i_taylor[t]`.
- **Cenário B:** `i[t] = trajetoria_exogena[t]`, descendo linearmente até `i_alvo = 7,5` no trimestre `T_corte` e ficando nesse nível.
- **Cenário C:** `i[t] = max(trajetoria_exogena[t], i_taylor[t] - δ)`. O corte avança só até onde as expectativas permitem; `δ` é a tolerância de desvio em relação à regra.

### 4.6 Demanda agregada (IS)

```
h[t] = a1 * h[t-1]
     - a2 * (r_long[t-1] - r_long_neutro)
     + a3 * impulso_fiscal[t]
     + a4 * capex_ppp[t]
     - a5 * de_real[t-1]          # câmbio valorizado reduz exportações líquidas
     + ε_h
g[t] = g_potencial + (h[t] - h[t-1]) * 4
```

- `capex_ppp[t]`: choque exógeno de investimento já contratado (% PIB), comum aos três cenários. A eficácia desse CAPEX é sensível a `r_long` pelo canal de financiamento: multiplicar por `(1 - a6 * max(0, r_long[t] - r_long_base))`.

### 4.7 Inflação (Phillips com repasse cambial)

```
pi[t] = b1 * pi[t-1] + (1 - b1) * pi_e[t] + b2 * h[t-1] + b3 * de_12m[t] + ε_pi
```

### 4.8 Câmbio

```
de[t] = - c1 * (i[t] - i_ext - (i[t-1] - i_ext))    # diferencial de juros
        + c2 * (prem[t] - prem[t-1])                 # choque de risco
        - c3 * venda_reservas[t] / PIB_usd[t]        # intervenção
        + (1 - λ) * c4 * inconsistencia[t]           # fuga por desconfiança
        + ε_e
```

A venda de reservas tem efeito decrescente: aplicar `c3_efetivo = c3 * (R[t] / R_inicial) ** η`, de modo que o mercado reage mais à intervenção quando o estoque restante é alto.

### 4.9 Reservas

```
R[t] = R[t-1] * (1 + rend_reservas/4) - venda_reservas[t]
```

- Cenários B e C: `venda_reservas` segue um cronograma (padrão US$ 25 bi/trimestre nos 4 primeiros trimestres), parametrizável.
- Restrição: `R[t] >= R_min` (piso de adequação, parâmetro). Se atingido, a venda para.

### 4.10 Fiscal

```
receita[t] = receita_base * (1 + ε_rec * h[t]/100) + medidas_receita[t]
despesa[t] = despesa_obrigatoria[t] + despesa_discricionaria[t]
s[t] = receita[t] - despesa[t]          # em % do PIB
```

- `despesa_obrigatoria[t]` cresce segundo as **regras de indexação** (parâmetros: crescimento real do salário mínimo, vínculo dos pisos de saúde e educação à receita, crescimento vegetativo da previdência).
- O **pacote fiscal** (cenários A e C) é uma lista de medidas em `cenarios.yaml`, cada uma com início, rampa e impacto final em % PIB:
  - extinção programada de renúncias (`sunset`);
  - limite para emendas;
  - revisão de subsídios;
  - mudança da regra dos pisos (ex.: inflação + componente real per capita).
- `impulso_fiscal[t] = -(s[t] - s[t-1])`.

### 4.11 Dívida por componente

Custo nominal efetivo:
```
i_efetivo[t] = w_lft * i[t]
             + w_pre * i_pre_estoque[t]
             + w_ipca * (r_long_estoque[t] + pi[t])
             + w_fx * (i_ext + de_anual[t])
```

- `i_pre_estoque` e `r_long_estoque` são médias móveis que se atualizam conforme o giro da dívida (`giro = 1 / prazo_medio`): a parcela que vence é refinanciada à taxa corrente.
- As compromissadas do BCB entram como parte de `w_lft` (custo à Selic).

Dinâmica:
```
γ[t] = (1 + g[t]) * (1 + deflator[t]) - 1
d_gross[t] = d_gross[t-1] * (1 + i_efetivo[t]) / (1 + γ[t]) - s[t] - Δcompromissadas_por_venda_reservas[t]
```

A venda de reservas reduz as compromissadas na mesma magnitude (convertida a R$ ao câmbio do trimestre), diminuindo a dívida bruta.

Dívida líquida: mesma lógica, mas com as reservas como ativo valorado a `R[t] * câmbio[t]`. Assim, a depreciação reduz a dívida líquida (hedge natural) e a venda de reservas reduz esse hedge.

### 4.12 Choques

`ε_h`, `ε_pi`, `ε_e` e um choque de prêmio `ε_prem` ~ Normal multivariada com matriz de covariância estimada nos resíduos históricos (2004–hoje, excluindo 2020 ou com dummy). Usados apenas no Monte Carlo.

---

## 5. Calibração (`calibracao.yaml`)

Valores padrão sugeridos a partir da literatura, **todos sujeitos a análise de sensibilidade**:

| Parâmetro | Padrão | Faixa de teste | Significado |
|---|---|---|---|
| `a1` | 0,7 | 0,5–0,85 | persistência do hiato |
| `a2` | 0,15 | 0,05–0,3 | sensibilidade do hiato ao juro real longo |
| `a3` | 0,4 | 0,2–0,8 | multiplicador fiscal |
| `a4` | 0,8 | 0,5–1,2 | multiplicador do CAPEX |
| `b1` | 0,6 | 0,4–0,8 | inércia inflacionária |
| `b2` | 0,15 | 0,05–0,3 | inclinação da Phillips |
| `b3` | 0,06 | 0,03–0,12 | repasse cambial |
| `ρ` | 0,8 | 0,6–0,9 | suavização da Taylor |
| `φπ`, `φh` | 1,5 / 0,5 | — | coeficientes da Taylor |
| `κ` | 0,5 | 0,2–1,0 | força da desancoragem |
| `p1`, `p2`, `p3` | 0,03 / 0,3 / 1,0 | ±50% | sensibilidade do prêmio |
| `c1` … `c4` | calibrar por regressão | — | câmbio |
| `ε_rec` | 1,0 | 0,8–1,3 | elasticidade da receita |
| `r_neutro_base` | 5,0 | 4–6 | juro neutro real |
| `pi_meta` | 3,0 | — | meta de inflação |
| `R_min` | parâmetro | — | piso de reservas (métrica ARA do FMI) |

Quando possível, estimar `a`, `b` e `c` por regressão nos dados históricos (OLS ou SUR) e usar os padrões apenas como *prior* ou alternativa.

---

## 6. Critério de sucesso

Um cenário é bem-sucedido para dado λ se, **simultaneamente**:

1. **Dívida estabilizada:** a inclinação de `d_gross` nos últimos 8 trimestres é ≤ 0 **e** `d_gross` no fim do horizonte ≤ `d_gross` inicial + `tolerancia_divida` (padrão: 5 p.p.).
2. **Inflação controlada:** média de `pi` nos últimos 8 trimestres ≤ `pi_meta + 1,5`.
3. **Reservas preservadas:** `R` nunca abaixo de `R_min`.

Todos os limiares ficam no YAML. A função `sucesso(trajetoria) -> bool` também retorna qual critério falhou, para diagnóstico.

---

## 7. Varredura em λ e Monte Carlo (`varredura.py`)

### 7.1 Determinística
- Grade `λ = 0,00, 0,01, …, 1,00`.
- Para cada cenário e cada λ, simular sem choques e guardar trajetórias e métricas.
- `λ*_det[cenário]` = menor λ com sucesso. Verificar se o sucesso é monotônico em λ; se não for, reportar os intervalos.

### 7.2 Estocástica
- Para cada (cenário, λ), N = 1.000 simulações com choques (seed fixa, reprodutível).
- `P_sucesso(λ)` = fração de simulações bem-sucedidas.
- `λ*_50` e `λ*_80` = menor λ com `P_sucesso` ≥ 50% e ≥ 80%.
- Usar **os mesmos choques** em todos os cenários (*common random numbers*) para que as diferenças reflitam a política, não o sorteio.
- Vetorizar em numpy (simulações em paralelo como dimensão do array) ou usar `joblib`.

---

## 8. Gráficos (`graficos.py`)

1. **Gráfico principal: probabilidade de sucesso × λ.** Três curvas (A, B, C), linhas horizontais em 50% e 80%, marcadores verticais em `λ*_80` de cada cenário. A curva que atinge 80% mais à esquerda é a do cenário que depende de menor adesão do mercado.
2. **Dívida bruta no fim do horizonte × λ:** mediana e faixa de 10 a 90% por cenário, com linha da dívida inicial.
3. **Inflação média final × λ:** mesmo formato, com faixa de tolerância da meta.
4. **Barras de λ\*:** `λ*_det`, `λ*_50`, `λ*_80` por cenário.
5. **Leques de trajetórias (fan charts):** dívida, Selic, inflação e câmbio para λ ∈ {0,3; 0,6; 0,9}, um painel por cenário.
6. **Mapa de calor de sensibilidade:** `λ*_80` em função de λ e de um parâmetro crítico (`a2`, `b3`, `κ` ou `p3`), um mapa por cenário.
7. **Decomposição da variação da dívida:** contribuições de juros, crescimento, primário e reservas para λ = 0,5.

Padrões: eixos rotulados em português, cores fixas por cenário (A, B, C), exportação em PNG (300 dpi) e SVG em `outputs/`.

---

## 9. Testes (`tests/test_modelo.py`)

- **Identidade contábil:** a soma das contribuições da decomposição é igual à variação total da dívida.
- **Pesos da dívida:** `w_lft + w_pre + w_ipca + w_fx = 1` em todo t.
- **Caso de controle:** sem choques, sem medidas e com Selic constante, o modelo reproduz a dinâmica `(r − g) × d − s` calculada à mão.
- **Monotonicidade:** com os parâmetros padrão, `prem` é não crescente em λ e `P_sucesso` é não decrescente em λ (avisar se for violado, sem falhar).
- **Reservas:** nunca negativas e nunca abaixo de `R_min`.
- **Reprodutibilidade:** mesma seed gera os mesmos resultados.

---

## 10. Validação qualitativa

Antes de usar os resultados, rodar o modelo em dois episódios históricos com a política efetivamente adotada e verificar se a direção dos movimentos é plausível:

- **2016–2019:** âncora fiscal com queda da Selic de 14,25% para 6,5%. Esperado: λ alto reproduz a queda de inflação e de juros longos.
- **2020–2022:** Selic a 2% com expansão fiscal, seguida de aperto até 13,75%. Esperado: λ baixo e intermediário reproduzem a aceleração inflacionária.

Reportar o λ que melhor ajusta cada episódio. Isso dá uma referência empírica de quais níveis de adesão são realistas.

---

## 11. Execução e saídas

```bash
python run.py --cenarios config/cenarios.yaml --calibracao config/calibracao.yaml --mc 1000 --seed 42
```

Saídas em `outputs/`:
- `resultados_lambda.csv`: métricas por cenário e λ;
- `lambda_star.csv`: `λ*_det`, `λ*_50` e `λ*_80` por cenário;
- gráficos da seção 8;
- `relatorio.md`: resumo automático com a ordenação dos cenários por robustez, as premissas usadas e os critérios que mais falharam.

---

## 12. Limitações a registrar no relatório

- λ é **exógeno e constante**. Na realidade, a credibilidade evolui com o histórico da política. Extensão sugerida: `λ[t] = λ[t-1] + ν * (sucesso_parcial[t] - 0,5)`, isto é, credibilidade adaptativa.
- O modelo é semiestrutural e reduzido; não captura efeitos de equilíbrio geral, distribuição de renda ou a composição setorial do investimento.
- Os resultados dependem da calibração do prêmio de risco (`p1` a `p3`) e do repasse cambial (`b3`). Os mapas de calor da seção 8 existem para mostrar essa dependência e precisam ser apresentados junto com o gráfico principal.
- O cenário B não inclui reação fiscal endógena. Uma variante pode adicionar uma regra de resposta do primário à dívida para testar se um ajuste reativo, em vez de anunciado, resolve o problema.