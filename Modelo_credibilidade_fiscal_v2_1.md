# Modelo de simulação: Selic, reservas, ajuste fiscal e credibilidade — versão 2.1

Correções sobre a versão 2. Tudo o que não está descrito aqui permanece como na v2.

---

## 0. O que muda e por quê

| # | Mudança | Problema na v2 |
|---|---|---|
| 1 | **Juro real longo neutro calibrado diretamente** (`r_long_neutro`), com `tp_lp` derivado dele. | A identidade somava juro curto neutro (5,0) + `tp_lp` (0,75) + `p0` (1,5), resultando em juro real longo neutro de 7,25%, com `p0` contado duas vezes. |
| 2 | **Prêmio de risco entra uma única vez**, dividido entre a Taylor e o juro longo por um parâmetro ω. | Os desvios do prêmio entravam no juro neutro da Taylor e de novo na identidade do juro longo. |
| 3 | **Checagem de consistência obrigatória** antes do ranking. | Com juro longo de 7,25%, nenhum cenário conseguia estabilizar a dívida, e o ranking comparava apenas graus de fracasso. |
| 4 | **Grade de θ desce até 0.** | O melhor ajuste de P3 ficou no limite inferior da grade (0,25). |
| 5 | **Duração de Macaulay** para NTN-B e LTN. | O prazo médio superestima a duração e atenua a inflação fiscal em P3. |
| 6 | **Sensibilidade de φ executada e reportada.** | Prevista na v2, não apareceu no relatório. |

---

## 1. Juro neutro e prêmio de risco (substitui 4.4 e o `r_neutro` de 4.5 da v2)

### 1.1 Parâmetros

| Parâmetro | Significado | Padrão | Grade obrigatória |
|---|---|---|---|
| `r_neutro_base` | juro real curto neutro (Selic real neutra) | 5,0 | 4,5 (variante `neutro_45`) |
| `r_long_neutro` | juro real longo neutro (NTN-B 10 anos em estado estacionário) | **5,5** | **4,5; 5,5; 6,5** |
| `tp_lp` | term premium de longo prazo | **derivado:** `r_long_neutro − r_neutro_base` (pode ser negativo) | — |
| `ω` | fração dos desvios do prêmio que passa pela Taylor | **0** | **0; 0,5; 1** |

Na variante `neutro_45`, reduzir `r_neutro_base` e `r_long_neutro` em 0,5 p.p. ao mesmo tempo, mantendo `tp_lp` constante. Assim a variante muda o nível dos juros, não a inclinação da curva.

**Referência empírica:** calcular e reportar, ao lado da grade, a média do NTN-B 10 anos real em 2017–2019 e em toda a amostra disponível. Não usar esses valores como padrão automaticamente; servem para o leitor situar a grade.

### 1.2 Equações

```
Taylor:       r_neutro[t] = r_neutro_base + ω * (prem[t] - p0)
Juro longo:   r_long[t]   = media_esperada(i - pi_e, 8 trimestres) + tp[t] + (1 - ω) * (prem[t] - p0)
Term premium: tp[t]       = tp_lp + (tp_0 - tp_lp) * exp(-t / τ_tp)
```

- `p0` **não entra no nível** de nenhuma das duas equações: o risco-país médio já está embutido em `r_neutro_base` e `r_long_neutro`.
- Para qualquer ω, um aumento de 1 p.p. no prêmio eleva o juro longo de estado estacionário em exatamente 1 p.p.: ω decide apenas por qual canal (Selic mais alta ou curva mais inclinada).
- **ω = 0 (padrão):** o BC não muda o juro neutro com o prêmio; o risco fiscal chega à economia pelo juro longo e pelo câmbio.
- **ω = 1:** todo o prêmio passa pela Taylor (equivalente à v2 sem a dupla contagem).
- `tp_0` continua calibrado para fechar a identidade em t0, agora com a nova equação.

### 1.3 Uso consistente

`r_long_neutro` é o mesmo parâmetro usado:
- na curva IS (`a2 * (r_long[t-1] - r_long_neutro)`);
- no valor presente dos superávits de P3, como taxa de desconto de estado estacionário;
- no primário estabilizador da checagem de consistência (seção 2).

Remover qualquer outra definição de juro longo neutro do código.

---

## 2. Checagem de consistência (nova seção do relatório, antes do ranking)

Para cada combinação de `r_long_neutro` e `ω`:

| Item | Cálculo |
|---|---|
| Juro real curto neutro | `r_neutro_base` |
| Juro real longo neutro | `r_long_neutro` |
| `tp_lp` | `r_long_neutro − r_neutro_base` |
| Custo real efetivo da dívida em estado estacionário | média ponderada pela composição final: LFT ao juro curto neutro, NTN-B e prefixados ao juro longo neutro |
| Primário estabilizador (dívida bruta) | `(r_efetivo − g_potencial) / (1 + g_potencial) × d_gross_inicial` |
| Primário estabilizador (dívida líquida) | idem com `d_net_inicial` |
| Primário final por cenário | trajetória determinística, P1, λ = 1, últimos 8 trimestres |
| Folga | primário final − primário estabilizador |

**Regra de interpretação (portão de qualidade):**
- Se o cenário A, na trajetória determinística com P1 e λ = 1, **não estabilizar a dívida**, o relatório abre com um aviso: "Com esta calibração, o pacote fiscal é insuficiente mesmo com adesão total; o ranking compara graus de fracasso e não deve ser lido como robustez relativa."
- Nesse caso, mostrar quanto de pacote adicional (% do PIB) seria necessário para A estabilizar a dívida com λ = 1.

---

## 3. P3: θ, duração e φ

### 3.1 θ

Grade de calibração na validação: **{0; 0,1; 0,25; 0,5; 0,75; 1,0}**.

- Se o melhor ajuste for θ = 0, registrar no relatório que, nos dados brasileiros, o canal fiscal não melhora o ajuste e P3 se reduz a uma Phillips achatada sem inércia.
- Manter a coluna de erro com θ fixo em 0,5.

### 3.2 Duração de Macaulay

Preferencial: calcular a duração de Macaulay de LTN e NTN-B a partir do estoque da DPMFi por vencimento (Tesouro Transparente), com os fluxos de cupom (NTN-B: 6% a.a. em cupons semestrais; LTN: zero cupom) descontados pela taxa de mercado de cada vértice.

Alternativa, se o estoque por vencimento não estiver disponível: `duração ≈ fator × prazo médio`, com `fator = 0,7` para NTN-B e `1,0` para LTN. Marcar no relatório como aproximação.

A duração da LFT continua em 0,25 ano (reprecificação trimestral).

### 3.3 φ

Executar e reportar P3 com **φ ∈ {0; 0,25; 0,5}** na variante base. Incluir na tabela de ordenamento por variante (gráfico 12).

---

## 4. Matriz de experimentos (substitui 7.1 da v2)

```yaml
especificacoes: [P1, P2, P3]
cenarios: [A, B, C]
variantes_obrigatorias:
  base:          {r_long_neutro: 5.5, omega: 0}
  rlong_45:      {r_long_neutro: 4.5}
  rlong_65:      {r_long_neutro: 6.5}
  neutro_45:     {r_neutro_base: 4.5, r_long_neutro: 5.0}
  omega_05:      {omega: 0.5}
  omega_1:       {omega: 1.0}
  inercia_alta:  {b1: 0.82}               # só P1 e P2
  repasse_est:   {b3: 0.012}
  C_lento:       {cenario: C, T_corte: 12}
  C_sem_tolerancia: {cenario: C, delta0: 0.0}
  phi_025:       {phi: 0.25}              # só P3
  phi_05:        {phi: 0.5}               # só P3
variantes_complementares:
  tp_050, tp_100 (substituídas por rlong_*; remover)
  rolagem_0, rolagem_2, p2_zero, p2_integral, vt_perpetuidade (manter)
superficie: [base, neutro_45, rlong_45, rlong_65]
```

---

## 5. Relatório (alterações em 11 da v2)

Nova ordem das seções:

0. **Checagem de consistência** (seção 2 desta versão), com o portão de qualidade.
1. Ordenamento por especificação na variante base.
2. **Ordenamento por `r_long_neutro`:** tabela com especificação × {4,5; 5,5; 6,5} × ordem dos cenários e λ\*₈₀ de cada um. É o resultado central desta versão, porque a v2 mostrou que o juro neutro é o parâmetro que decide entre A e C.
3. Robustez por variante (gráfico 12).
4. Área de sucesso na superfície.
5. Validação e especificação de referência.
6. Premissas e limitações.

Acrescentar ao relatório, para cada cenário, a **fração do tempo com juro real da LFT abaixo de zero** (repressão financeira) em λ = 0,3; 0,5 e 0,9, não apenas em λ = 0,5.

---

## 6. Testes (acrescentar aos da v2)

- **Estado estacionário:** com `prem = p0`, Selic no neutro, inflação na meta e choques nulos, `r_long` converge para `r_long_neutro` (tolerância de 0,05 p.p.) para ω ∈ {0; 0,5; 1}.
- **Sem dupla contagem:** em estado estacionário, aumentar `prem` em 1 p.p. eleva `r_long` em 1 p.p. (tolerância de 0,05) para ω ∈ {0; 0,5; 1}.
- **`tp_lp` derivado:** `tp_lp == r_long_neutro − r_neutro_base` em todas as variantes.
- **Parâmetro único:** a IS, o VP de P3 e a checagem de consistência usam o mesmo valor de `r_long_neutro` (testar alterando-o e verificando os três).
- **Duração:** a duração de Macaulay da NTN-B é menor que o prazo médio.
- **Portão de qualidade:** com um pacote fiscal artificialmente nulo, o aviso aparece no relatório.