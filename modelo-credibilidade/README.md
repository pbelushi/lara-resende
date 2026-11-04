# Modelo de credibilidade: Selic, reservas, ajuste fiscal (v2.2)

Modelo semiestrutural trimestral que compara três estratégias para o Brasil e mede **qual depende de menor
adesão do mercado** para estabilizar a dívida sem perder o controle da inflação. Especificações:
`../docs/especificacoes/modelo_credibilidade_fiscal.md` (v1), `../docs/especificacoes/Modelo_credibilidade_fiscal_v2.md` (v2) e
`../docs/especificacoes/Modelo_credibilidade_fiscal_v2_1.md` (correções da v2.1) e `../docs/especificacoes/Modelo_credibilidade_fiscal_v2_2.md` (v2.2,
implementada aqui).

| Cenário | Política |
|---|---|
| A. Ortodoxo | Pacote fiscal, Selic pela regra de Taylor, sem venda de reservas |
| B. Lara Resende puro | Selic exógena até 7,5% em 6 trimestres, venda de US$ 100 bi em reservas, sem pacote |
| C. Lara Resende condicionado | Pacote + corte rumo a 7,5% limitado por `i_taylor − δ[t]` (δ cai a zero após o corte) + reservas |

**Novidades da v2:** três teorias de inflação intercambiáveis (P1 Phillips híbrida, P2 Phillips achatada,
P3 fechamento fiscal/FTPL); adesão em duas dimensões (λ_π na meta de inflação, λ_fiscal nos superávits);
restrição de rolagem da LFT; critério de inflação explosiva com truncamento das trajetórias; term premium
convergente; matriz de experimentos com variantes obrigatórias; superfície λ_π × λ_fiscal; validação por
especificação.

**Correções da v2.1:** juro real longo neutro calibrado diretamente (`r_long_neutro` = 5,5; `tp_lp` derivado como
`r_long_neutro − r_neutro_base`); o prêmio de risco entra uma única vez, com fração ω pela Taylor e 1 − ω pelo
juro longo, e `p0` fora do nível dos juros; checagem de consistência com portão de qualidade antes do ranking;
θ calibrado a partir de 0; duração de Macaulay de NTN-B e prefixados a partir do estoque da DPF; variantes de φ.

**Tarefas da v2.2:** (3) estimação de b3 (projeções locais mensais, OLS e IV, com calibração por
impulso-resposta em cada especificação) e de ω (regra de Taylor com prêmio, NLS e 2SLS) → variantes `estimada*`;
(2) variante de alongamento da dívida (teto para LFT + compromissadas reduzindo só a LFT do Tesouro);
(1) bootstrap pareado da comparação A × C na diagonal e na área de sucesso, com leitura "A ≈ C" quando o IC de 95%
contém zero.

## Uso

```bash
pip install -r requirements.txt
python run.py --atualizar-dados --sem-sensibilidade --mc 50   # baixa dados e preenche config/calibracao.yaml
python run.py --experimentos config/experimentos.yaml --calibracao config/calibracao.yaml \
              --mc 1000 --seed 42 --especificacoes P1,P2,P3 --superficie
python -m pytest -q
```

Opções: `--monetizacao` (LFT não rolada vira expansão monetária em vez de migrar para NTN-B), `--retomar`
(reaproveita os parquets de `outputs/v2/parciais/`), `--sem-sensibilidade`, `--n-jobs`, `--offline`.

Saídas em `outputs/v2_2/` (as rodadas anteriores ficam em `outputs/v2/` e `outputs/v2_1/`): `resultados_lambda.parquet`, `superficie.parquet`, `lambda_star.csv`,
`area_sucesso.csv`, `ordenamento.csv`, `consistencia.csv`, `validacao.csv`, `sucesso_trajetorias.npz`,
`sucesso_superficie.npz`, `bootstrap_diagonal.csv`, `bootstrap_area.csv`, `estimacao_b3.csv`, `estimacao_omega.csv`,
`calibracao_b3.csv`, `variantes_estimadas.yaml`, `alongamento*.csv`, decomposições, gráficos 1–13 (PNG 300 dpi e SVG; 1–7
com sufixo por especificação) e `relatorio.md`. A rodada da v1 continua em `outputs/` (raiz).

## Estrutura

```
config/calibracao.yaml   parâmetros editáveis no topo; bloco AUTO (valores iniciais, estimativas, choques)
config/cenarios.yaml     cenários A, B, C, pacote fiscal, CAPEX/PPP
config/experimentos.yaml especificações × variantes, superfície, sensibilidade
src/dados.py             coleta (SGS, Focus, Tesouro Direto, RTN), validação dos códigos, trimestralização, OLS
src/inflacao.py          módulos P1, P2, P3 com interface comum (π e componentes)
src/fiscal_valoracao.py  valor presente dos superávits, fração não lastreada, inflação fiscal (P3)
src/rolagem.py           restrição de rolagem da LFT (migração para NTN-B ou monetização)
src/modelo.py            equações, condições iniciais derivadas, plano anunciado, simulação vetorizada
src/politicas.py         regras de Selic (δ decrescente), reservas, medidas fiscais
src/varredura.py         matriz de experimentos, diagonal, superfície, leques, decomposições, sensibilidade
src/metricas.py          critério de sucesso (com inflação explosiva), λ*, área de sucesso
src/validacao.py         validação por especificação (2016–2019 e 2020–2022)
src/consistencia.py      checagem de consistência e portão de qualidade (v2.1)
src/estimacao.py         estimação de b3 e ω e calibração de b3 por impulso-resposta (v2.2)
src/bootstrap.py         bootstrap pareado de Δλ* e da área de sucesso (v2.2)
src/analises.py          arrays de sucesso por trajetória e análises do alongamento (v2.2)
src/graficos.py          gráficos 1–13
src/reservas_choque.py   carregamento das reservas, parada súbita redesenhada, c3 e R_min pela dívida líquida
src/extrair_mip.py       MIP 2015 (Leontief tipo I e II, demanda final, multiplicadores) e TRU 2023 nível 12
src/extrair_emprego.py   coeficientes de emprego e renda; PNAD, Censo 2022 e CNT pelo SIDRA; Okun; elasticidades
src/recessivo.py         efeito recessivo: atividade, composição do pacote, setores e emprego
src/recessivo_relatorio.py  gráficos e relatorio_recessivo.md
tests/                   testes da v1 e v2; tests/dados guarda a referência numérica da v1
```

## Dados

t0 = **último trimestre fechado**; o relatório traz a data real da última observação de cada variável.
Os 25 códigos SGS são validados contra o nome oficial do BCB no início da coleta.

| Variável | Fonte |
|---|---|
| Meta Selic, Selic efetiva, IPCA, dívida bruta e líquida, reservas, câmbio, primário (NFSP), PIB | SGS 432, 4189, 433, 13762, 4513, 3546, 1, 5793/5783, 4382, 22109 |
| Composição da DPMFi (com compromissadas) e prazos de LTN, NTN-B e LFT | SGS 10622–10632, 10613, 10608, 10614 |
| Expectativas (IPCA 12m; histórico anual de Selic, PIB, câmbio, IPCA, primário e DLSP) | Focus/Olinda |
| NTN-B ~5 e ~10 anos; taxas por vencimento de NTN-B e prefixados | Tesouro Direto |
| Estoque da DPF por título e vencimento (duração de Macaulay; LFT do Tesouro em mercado) | Tesouro Transparente |
| IPCA comercializáveis e itens livres, câmbio médio mensal, IC-Br em US$, meta de inflação | SGS 4447, 11428, 3698, 29042, 13521 |
| Dólar amplo (proxy do DXY) e VIX | FRED DTWEXBGS (encadeado com DTWEXB antes de 2006) e VIXCLS |
| Prêmio soberano | Ipeadata JPM366_EMBI366 (EMBI+ Brasil, inativo desde jul/2024) |
| Receita e despesa do governo central | RTN, tabela 1.1 |

Diferenças em relação às fontes pedidas: prazos e composição vêm do SGS (mesma base do RMD); ANBIMA exige
credenciais, então a checagem do term premium usa a inclinação NTN-B 10a − 5a do Tesouro Direto; as renúncias
(DGT) servem só de referência para o tamanho das medidas.

## Escolhas de implementação

Da v1 (mantidas): índice de inconsistência em p.p. (μ = 0,25, p3 = 0,3); Taylor "sombra" suavizada sobre o
próprio valor anterior; ponto fixo intratrimestral entre Taylor, expectativas e prêmio; `+a5·de_real` na IS;
plano anunciado = cenário simulado com adesão total; bloco fiscal com arcabouço e piso de discricionárias.

Da v2:

1. **Diagonal reproduz a v1.** Com P1, sem rolagem, δ e term premium constantes, a calibração congelada em
   `tests/dados/` e o modo `_legado_v1` (que restaura só para esse teste a forma da v1 de somar o prêmio inteiro
   ao juro longo e à Taylor), a simulação bate com a v1 com erro < 1e-8 (`test_diagonal_reproduz_v1`).
2. **Inflação fiscal (P3) medida contra a trajetória anunciada.** A especificação escreve
   `θ·(lacuna − φ·lacuna_0)/(d_net·duração)`, mas diz que com φ = 0 "só revisões geram inflação". Implementado:
   - a lacuna entra como **fração da dívida líquida** (a parte que o nível de preços teria de absorver);
   - a referência é a fração ao longo do **plano anunciado** (simulado sem inflação fiscal, pois o anúncio supõe
     credibilidade), deslocada para partir da fração inicial de cada λ;
   - `pi_fiscal = θ·(fração − referência + φ·fração_0)/duração·100`.
   Sem isso, uma lacuna inicial grande (≈ 80% do PIB) gerava inflação só por crescer junto com a dívida, e a
   janela móvel do VP gerava deflação ao incorporar anos de superávit já anunciados. Com λ = 1 e sem choques,
   `pi_fiscal = 0` (teste `test_p3_plano_crivel_sem_inflacao_fiscal`).
3. **Valor terminal de P3.** Padrão = fórmula literal `s_H / max(r − g, Δ_min)` (`escala_vt = 1`). A perpetuidade em
   unidades consistentes (`100·s_H/(r − g)`) torna o VP tão sensível ao juro longo que a realimentação
   juro → VP → deflação → Selic tem ganho maior que 1; ela roda como variante `vt_perpetuidade`.
4. **Explosão.** Inflação acima de 50% encerra a trajetória (valores seguintes = NaN, trimestre em `ruptura`);
   acima de 20% em qualquer trimestre falha pelo critério de inflação explosiva, que tem precedência.
   Percentis de dívida e inflação usam só trajetórias não rompidas; a fração explosiva é reportada ao lado.
   Mantém-se um piso de −5% a.a. para a inflação.
5. **Rolagem.** As compromissadas (parcela de mercado aberto da LFT) não migram; a venda de reservas as reduz.
   A NTN-B que recebe a migração é precificada ao juro longo corrente.
6. **Variantes restritas a C** (`C_lento`, `C_sem_tolerancia`) são ordenadas contra A e B da variante base.
7. **Ordenamento:** menor λ*₈₀; desempate por λ*₅₀, λ* determinístico e P(sucesso) máxima.
8. **Juro neutro (v2.1).** `r_long_neutro` é um único parâmetro, usado na IS, na eficácia do CAPEX, no desconto do
   valor terminal de P3 e na checagem de consistência. No VP de P3, o horizonte explícito é descontado ao juro longo
   corrente e o valor terminal (estado estacionário) ao juro longo neutro.
9. **Duração de Macaulay.** Cada título do estoque da DPF (mês mais recente até t0, mercado + carteira do BC) é
   descontado à taxa do Tesouro Direto da mesma classe com vencimento mais próximo; NTN-B com cupom de 6% a.a. e
   NTN-F de 10% a.a., em parcelas semestrais; LTN e NTN-B Principal sem cupom. Se o estoque não estiver
   disponível, usa a aproximação 0,7 × prazo (NTN-B) e 1,0 × prazo (LTN) e o relatório registra isso.
10. **Portão de qualidade.** Se A não estabilizar a dívida com P1, λ = 1 e sem choques, o relatório abre com o aviso
    e o pacote adicional necessário (busca binária sobre uma medida de receita com a rampa da primeira medida).

11. **Estimação (v2.2).** Controles da projeção local: hiato e desvio do Focus defasados (o Focus reage ao câmbio
    no mesmo mês) e IC-Br em US$ (a versão em reais contém o câmbio e absorvia o repasse, dando ERPT negativo).
    IV é a estimativa principal quando o F do primeiro estágio passa de 10. b3 de cada especificação é escolhido para
    que o repasse simulado em 4 trimestres (choque de 10%, Selic fixa, λ = 0,5) iguale ERPT_12; limites do IC
    abaixo do repasse obtido com b3 = 0 são limitados a 0.
    ω: o EMBI+ (Ipeadata, em pontos-base) entra em p.p.; a regra de Taylor reporta ρ e o coeficiente de curto prazo do
    prêmio, e o IC de ψ = b_curto/(1 − ρ) é calculado por Fieller (não pelo método delta). A estimativa nunca é cortada
    em [0, 1]. Classificação: IC ilimitado → "não identificado"; IC limitado contendo 0 e 1 → "não informativo para o
    modelo"; IC limitado inteiramente fora de [0, 1] → "possível erro de especificação"; IC limitado, informativo,
    mas ponto fora de [0, 1] → "identificado, ponto fora do domínio". Só no caso "identificado" (ponto em [0, 1]) ω é
    usado: nos demais, a variante `estimada` usa ω = 0 com o b3 estimado, não há variantes estimada_omega_*, e as
    variantes ω = 0,5 e ω = 1 aparecem no relatório com o mesmo destaque da base.
12. **Alongamento (v2.2).** Teto `w_lft_meta[t]` para LFT + compromissadas, aplicado ao fim do trimestre e só sobre
    a LFT do Tesouro (`s_ipca` para NTN-B, o resto para prefixados, às taxas correntes); a rolagem do trimestre
    seguinte atua sobre o que restar. As compromissadas passaram a ser limitadas ao estoque de LFT (antes podiam
    excedê-lo no fim do horizonte, quando superávits resgatavam LFT — correção que também afetaria a v2.1).
13. **Bootstrap (v2.2).** R = 1.000 réplicas com os mesmos índices de trajetória para A, B e C; λ* censurado em
    1,01 quando o limiar não é atingido (⚠ se mais de 20% das réplicas forem censuradas). Variantes restritas a C
    usam o A da base, com os mesmos choques.
14. **Reservas (v2.2, `python -m src.reservas_choque`).** `de_tendencia` (% a.a., ou `"pdj"` para a paridade
    descoberta: [(1 + Selic − prêmio)/(1 + juro externo)]^¼ − 1 por trimestre) entra só na valorização do câmbio
    (reservas e dívida cambial); o repasse e o câmbio real da demanda usam o componente cíclico. Canal
    reservas → prêmio: `kappa_R × max(0, R_adequado − R)/R_adequado`, com R do trimestre anterior;
    `R_adequado` = US$ 300 bi (100% da ARA; 363 = caso pessimista). `R_min` = US$ 300 bi limita a venda
    programada; a defesa do câmbio na parada súbita (até US$ 50 bi) pode rompê-lo (`R_min_defesa = 0`), e o
    critério de reservas olha só a janela final (`reservas_janela`). Com R_adequado = R_min o canal só age
    quando a defesa rompe o piso. Com reservas iniciais de US$ 363 bi, a venda de 100 bi fica limitada a ~76 bi.
15. **Efeito recessivo (`python -m src.extrair_mip`, `python -m src.extrair_emprego`, `python -m src.recessivo`,
    `python -m src.recessivo_relatorio`; saídas em `outputs/v2_2/recessivo/`).** Os itens do pacote podem ter
    multiplicador próprio (`multiplicador` em cada medida; ausente = a3) e dependência do ciclo
    (`gamma_ciclo`): o termo fiscal do hiato vira `a3·(impulso − Σ impulso_k) + Σ m_k·(1 + γ·max(0, −h₋₁))·impulso_k`,
    com `impulso_k = −Δ medida_k`; com todos os m_k = a3 e γ = 0 reproduz `a3·impulso` (teste). Os padrões de
    `cenarios.yaml` não têm multiplicador por item: só o módulo recessivo os usa (`config/recessivo.yaml`, com as
    fontes). A simulação guarda os termos da equação do hiato (`dem_*`), que o bloco setorial acumula com a
    persistência a1 e distribui pela MIP 2015 (Leontief tipo I, 67 atividades → 12 grupos da TRU), reconciliando o
    VA com o PIB do modelo macro trimestre a trimestre. Emprego = variação % da produção × ocupados de 2025 (PNAD
    5434, distribuídos pelas ocupações da TRU 2015); formalidade do Censo 2022 (tabela 10262) calibrada à
    informalidade da PNAD (4093); Okun com PNAD 4099. A referência S é o cenário A sem pacote.
    Efeito fiscal em nível (`fiscal_nivel`, padrão no módulo recessivo, desligado no modelo principal): o item entra
    como `m·(medida_t − ρ_f·medida_{t−1})`; com `rho_f` = a1 o efeito direto sobre o hiato é m × medida e o
    multiplicador acumulado direto é m em qualquer horizonte (`test_calibracao_rho_f`). `--impulso` roda a forma
    anterior. A reconciliação setorial é aditiva (o resíduo macro − matriz entra como absorção doméstica). As métricas
    de produto excluem trajetórias com inflação acima de 20% (o modelo não tem o custo de produto da inflação alta).
    `validacao.validar_recessao_2015` simula 2015T1–2016T4 com Selic, primário estrutural e câmbio observados.

## Leitura dos resultados

- Na v2, a soma juro curto neutro + tp_lp + p0 levava o juro real longo de equilíbrio a ≈ 7,25–7,75%, e nenhum
  cenário estabilizava a dívida com folga. A v2.1 corrige a dupla contagem; o relatório traz o ordenamento para
  r_long_neutro ∈ {4,5; 5,5; 6,5}, que é o parâmetro que decide entre A e C.
- A monotonicidade não é garantida: o teste avisa sem falhar e o relatório lista intervalos não contíguos.
- O mapa de sensibilidade (`6_sensibilidade_*`) e a superfície (`10_superficie_*`) devem acompanhar o gráfico
  principal (`8_prob_sucesso_especificacoes`).
