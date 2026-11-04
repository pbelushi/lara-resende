# Instruções: efeito recessivo das estratégias (PIB, setores e emprego)

Módulo novo sobre o modelo v2.2 já calibrado (R_min = US$ 300 bi, mesmos choques: seed 42; bootstrap: seed 2026). Não altera a lógica de sucesso já reportada; acrescenta medidas de atividade, emprego e distribuição setorial. Resultados em `outputs/v2_2/recessivo/`.

**Perguntas que o relatório deve responder:**
1. Qual estratégia tem menor perda de produto e menor probabilidade de recessão nos primeiros 8 trimestres e até a eleição de outubro de 2030?
2. A composição do pacote fiscal muda o efeito recessivo? Quanto?
3. Quais setores e quantos empregos (formais e informais) ganham ou perdem em cada estratégia?
4. Existe troca entre robustez (λ\*) e custo recessivo?

---

## 1. Estratégias comparadas

| Código | Descrição |
|---|---|
| S | **Referência sem ajuste:** sem pacote fiscal, Selic pela Taylor, sem venda de reservas. Contrafactual para medir perdas. |
| A | Ortodoxo (pacote + Taylor). |
| A_res60 | A com venda de US$ 60 bi. |
| A_res100 | A com venda de até US$ 100 bi (efetiva: 76). |
| B | Lara Resende puro. |
| C | Lara Resende condicionado (com piso). |
| C_sem_piso | C sem piso após a transição (efetiva: 76). |

Especificações P1, P2 e P3 (θ = 0,5 e θ = 0,25). Adesão λ ∈ {0,3; 0,5; 0,7; 0,9} na diagonal, N = 1.000, mesmos choques em todas as estratégias. Os resultados de B com inflação explosiva entram na contagem, mas as métricas de atividade são reportadas também só sobre trajetórias não explosivas, com a fração explosiva ao lado.

---

## 2. Métricas agregadas de atividade

Calcular por trajetória e resumir por mediana, faixa de 10 a 90% e média:

| Métrica | Definição |
|---|---|
| Crescimento anual do PIB | por ano civil, anos 1 a 10 |
| Perda acumulada de produto | Σ (PIB da estratégia − PIB de S) / PIB de S, em % do PIB de um ano, em três janelas: trimestres 1–8, até a eleição (2030T3) e horizonte completo |
| Hiato mínimo e trimestre em que ocorre | |
| Probabilidade de recessão técnica | fração de trajetórias com dois trimestres seguidos de queda do PIB, por janela |
| Anos com crescimento negativo | contagem por trajetória |
| Taxa de sacrifício | perda acumulada de produto ÷ redução da inflação média entre o ano 1 e os anos 3–4 (só quando a inflação cai) |

**Comparações por bootstrap pareado** (mesmos índices de trajetória): diferença de perda acumulada e de probabilidade de recessão entre cada par relevante: A × C, A × C_sem_piso, A × A_res60, C_sem_piso × A_res100 (mesma venda) e cada estratégia × S.

**Janela política:** com t0 = 2026T3, a eleição de outubro de 2030 corresponde ao trimestre 16. Reportar todas as métricas separadamente para os trimestres 1–8 e 1–16.

---

## 3. Composição do pacote fiscal e multiplicadores

Hoje o modelo usa um multiplicador único (`a3 = 0,4`) para todo o impulso fiscal. O efeito recessivo depende da composição, então substituir por multiplicadores por item.

### 3.1 Itens e canais de demanda

Cada item do pacote é ligado a um componente da demanda final e a um multiplicador. Os valores abaixo são **pontos de partida a calibrar pela literatura brasileira** (por exemplo, Orair, Siqueira e Gobetti, IPEA, 2016, com multiplicadores dependentes do ciclo). O agente deve buscar as estimativas, registrar a fonte de cada uma e usar faixas de sensibilidade.

| Item | Canal de demanda | Multiplicador inicial | Faixa |
|---|---|---|---|
| Fim de renúncias regressivas (deduções do IRPF, isenções financeiras) | consumo das famílias de alta renda | 0,3 | 0,1–0,5 |
| Revisão de benefícios setoriais a empresas | investimento privado e margens | 0,3 | 0,1–0,6 |
| Focalização de subsídios creditícios (grandes tomadores) | investimento privado | 0,4 | 0,2–0,7 |
| Teto para verbas acima do teto remuneratório | consumo das famílias de alta renda | 0,3 | 0,1–0,5 |
| Previdência dos militares | consumo das famílias de renda média e alta | 0,5 | 0,3–0,8 |
| Limite para emendas parlamentares | investimento e custeio municipal | 0,8 | 0,5–1,2 |
| Custeio administrativo | consumo do governo | 0,6 | 0,4–0,9 |
| Nova regra dos pisos de saúde e educação | consumo do governo (serviços) | 0,8 | 0,5–1,2 |
| Investimento público (só nas variantes de corte linear) | formação bruta de capital, construção | 1,2 | 0,8–1,8 |
| Transferências a famílias de baixa renda (só nas variantes de corte linear) | consumo das famílias de baixa renda | 1,0 | 0,7–1,5 |

O multiplicador efetivo do pacote em cada trimestre é a média dos multiplicadores ponderada pelo valor de cada item já em vigor naquele trimestre (pelas rampas de `cenarios.yaml`).

**Dependência do ciclo (variante `mult_ciclo`):** multiplicar os valores por (1 + γ · max(0, −hiato)), com γ calibrado para que, com hiato de −3%, o multiplicador do investimento fique perto do topo da faixa. Reportar com e sem.

### 3.2 Variantes de composição (mesmo valor total do pacote, 2,7% do PIB)

| Variante | Composição |
|---|---|
| `pacote_base` | composição atual do modelo (renúncias 1,2; emendas 0,3; subsídios 0,4; pisos 0,8) |
| `pacote_qualidade` | concentrado em itens de baixo multiplicador: renúncias regressivas, benefícios setoriais, subsídios a grandes tomadores, verbas acima do teto, previdência militar; sem corte em pisos, investimento e transferências de baixa renda |
| `pacote_linear` | corte proporcional sobre o gasto discricionário, incluindo investimento e custeio, como um contingenciamento |

Rodar as três composições para A, C e C_sem_piso. A pergunta 2 é respondida pela diferença de perda acumulada entre `pacote_qualidade` e `pacote_linear`.

**Atenção:** a composição também afeta a credibilidade (um pacote baseado em receita e em itens de difícil aprovação pode ter λ_fiscal menor). Não modelar isso automaticamente; registrar como limitação e mostrar a perda de produto para cada λ.

---

## 4. Bloco setorial

### 4.1 Insumos já prontos

Copiar para `data/processed/mip/` (arquivos produzidos nesta conversa a partir da MIP 2015 nível 67, da TRU 2015 nível 68 e da TRU 2023 nível 12):
- `mip2015_multiplicadores_67.csv`, `mip2015_multiplicadores_setores.csv`, `multiplicadores_tru12_2023.csv`
- `emprego_renda_67.csv`, `emprego_renda_setores.csv`, `emprego_renda_tru12.csv`, `sensibilidade_tipo2.csv`
- scripts `extrair_mip.py` e `extrair_emprego.py` (em `src/`, para reprodução)

Os arquivos brutos do IBGE (`Matriz_de_Insumo_Produto_2015_Nivel_67.xls`, `68_tab2_2015.xls`, `12_tab*_2023.xls`) vão para `data/raw/ibge/`.

Para o cálculo setorial é preciso a matriz de Leontief completa (67 × 67) e os vetores de demanda final por componente; o script `extrair_mip.py` já lê as tabelas 03, 13, 14 e 15 da MIP. Estendê-lo para salvar `L` (tipo I) e `L2` (tipo II) em `.npy` e os vetores de demanda final de 2015 por componente (exportação, consumo do governo, consumo das famílias, FBCF) em CSV.

### 4.2 Choques de demanda final por componente

A cada trimestre, decompor a variação da demanda agregada da trajetória (em relação a S) nos componentes:

| Componente | Origem no modelo |
|---|---|
| Consumo das famílias | efeito do juro real longo sobre o consumo + itens do pacote com canal no consumo, cada um com o vetor de consumo da faixa de renda correspondente |
| FBCF privada | efeito do juro real longo + subsídios + CAPEX de PPPs (vetor concentrado em construção e máquinas) |
| Consumo do governo e FBCF pública | itens do pacote com canal no governo |
| Exportações líquidas | câmbio real, com elasticidade por setor estimada nas Contas Nacionais Trimestrais |

**Reconciliação com o agregado:** a soma setorial do valor adicionado tem que reproduzir a variação do PIB do modelo macro. Usar o modelo macro para o total e a matriz para a distribuição, escalando proporcionalmente; reportar o fator de escala médio como diagnóstico (se ficar fora de 0,7–1,3, há incoerência entre os multiplicadores do bloco fiscal e os da matriz, e o relatório deve dizer isso).

**Vetores de consumo por faixa de renda:** a MIP traz só o consumo total das famílias. Para diferenciar alta e baixa renda, usar a estrutura de consumo da POF 2017–2018 (IBGE) por faixa de renda, compatibilizada com os produtos da MIP. Se a compatibilização for muito custosa, usar o vetor total e registrar a limitação.

### 4.3 Elasticidades setoriais

Estimar com as Contas Nacionais Trimestrais (IBGE/SIDRA, valor adicionado por atividade, 2004–2026) a sensibilidade do valor adicionado de cada um dos 12 grupos da TRU ao hiato agregado, ao juro real longo, ao câmbio real e aos preços de commodities (IC-Br). Usá-las como verificação das respostas obtidas pela matriz e, para as exportações líquidas, como a fonte principal.

### 4.4 Tratamento dos setores

Todos os setores recebem o mesmo tratamento metodológico e a mesma forma de apresentação. Para setores com maior exposição ao câmbio (agropecuária, indústria extrativa, transformação), reportar também o efeito de volta sobre exportações e balança comercial, porque ele afeta as reservas e o câmbio do próprio cenário.

---

## 5. Emprego

### 5.1 Atualização dos coeficientes para 2025–2026

Os coeficientes de emprego da TRU são de 2015. Atualizá-los com a **PNAD Contínua trimestral**, buscada pela API do SIDRA:

1. **Pessoas ocupadas por grupamento de atividade do trabalho principal** (Brasil, trimestral, 2012 em diante).
2. **Rendimento médio real habitual do trabalho principal por grupamento de atividade.**
3. **Ocupados por posição na ocupação e categoria do emprego** (com e sem carteira, conta própria com e sem CNPJ, empregador, setor público), por grupamento de atividade quando disponível.

Antes de usar qualquer tabela, validar pelo nome e pelas variáveis no metadado do SIDRA (não confiar em números de tabela memorizados) e registrar no relatório o número e o nome de cada tabela usada.

**Procedimento:**
- Compatibilizar os grupamentos da PNAD com os 12 grupos da TRU. Onde a PNAD agrega mais (por exemplo, a indústria geral), dividir pelas proporções de ocupações da TRU 2015 nível 68.
- Coeficiente de emprego atualizado = ocupados (PNAD, média de 2025) ÷ valor da produção do grupo em 2025 (Contas Nacionais, a preços correntes); corrigir para preços da simulação.
- Conferir que os multiplicadores tipo I e II atualizados mantêm a ordem relativa dos setores; reportar a variação em relação a 2015.

### 5.2 Métricas

| Métrica | Definição |
|---|---|
| Ocupações | diferença em relação a S, em milhares, por setor e total, nas janelas 1–8 e 1–16 |
| Ocupações formais | idem, aplicando a fração formal de cada setor (PNAD) |
| Massa salarial | ocupações × rendimento médio, por setor |
| Taxa de desocupação | via lei de Okun estimada com PNAD (variação da desocupação sobre o hiato, 2012–2026); reportar o coeficiente e o IC |
| Efeito induzido | separar tipo I e tipo II; usar a premissa central do tipo II (propensão a consumir 0,9, impostos 15%) e reportar a sensibilidade já calculada |

### 5.3 Retorno fiscal

Calcular as contribuições previdenciárias e o IR sobre a massa salarial adicional (coeficientes de `mult_prev_oficial_fgts` e alíquota efetiva do IR por faixa).

**Não somar esse retorno ao primário do modelo macro**, porque a elasticidade da receita ao hiato (`ε_rec`) já capta a arrecadação cíclica; somar duplicaria o efeito. Usar o cálculo setorial como decomposição da receita cíclica, e reportar a diferença entre as duas medidas como diagnóstico.

---

## 6. Saídas

Arquivos em `outputs/v2_2/recessivo/`:
- `atividade_agregada.csv`: métricas da seção 2 por estratégia, especificação, λ e janela
- `bootstrap_atividade.csv`: diferenças pareadas com IC
- `composicao_pacote.csv`: métricas por variante de composição
- `setorial_va.csv` e `setorial_emprego.csv`: por estratégia, λ, janela e grupo da TRU
- `pnad_coeficientes.csv`: coeficientes de emprego e formalidade atualizados, com as tabelas do SIDRA usadas

Gráficos:
1. **Crescimento anual do PIB** (mediana e faixa 10–90%) por estratégia, um painel por especificação, λ = 0,5 e 0,9.
2. **Probabilidade de recessão técnica** × λ, por estratégia, nas janelas 1–8 e 1–16.
3. **Fronteira robustez × custo:** eixo x = λ\*₇₀ (dívida líquida, banda), eixo y = perda acumulada de produto até a eleição; um ponto por estratégia e especificação.
4. **Composição do pacote:** perda acumulada nas três composições para A, C e C_sem_piso.
5. **Emprego por setor:** barras de ocupações (formais e informais) em relação a S, por estratégia, janela 1–16, λ = 0,7.
6. **Mapa de calor do valor adicionado setorial:** grupos da TRU × estratégias, variação em relação a S.

Relatório `relatorio_recessivo.md`, com uma síntese de até 10 linhas respondendo às quatro perguntas do início.

---

## 7. Testes

- Os multiplicadores lidos dos CSVs reproduzem os valores de referência (por exemplo, multiplicador de produção tipo I da indústria de transformação = 2,16).
- Com choque de demanda nulo, todas as variações setoriais são zero.
- A soma setorial do valor adicionado reproduz a variação agregada do PIB depois da reconciliação (tolerância de 0,1%).
- Com todos os multiplicadores por item iguais a 0,4 e sem dependência do ciclo, o modelo reproduz os resultados atuais (`a3 = 0,4`).
- O total de ocupados no ano-base após a atualização é igual ao total da PNAD (tolerância de 1%).
- As três composições do pacote têm o mesmo valor total em todos os trimestres.
- Mesma seed gera os mesmos resultados.

---

## 8. Limitações a registrar

- Os multiplicadores por item vêm da literatura e têm incerteza grande; os resultados de composição devem ser lidos pelas faixas de sensibilidade.
- A matriz de 2015 supõe coeficientes técnicos fixos; a atualização para 2025 corrige o emprego e o valor adicionado, não a estrutura de insumos.
- A credibilidade de cada composição do pacote não é modelada.
- A lei de Okun é uma relação reduzida e pode variar com a formalidade do mercado de trabalho.
- O bloco setorial não retroalimenta o modelo macro: a distribuição setorial não altera inflação, câmbio ou dívida.