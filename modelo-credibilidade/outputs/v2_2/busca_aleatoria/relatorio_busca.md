# Busca aleatória: ajuste com sucesso sob adesão baixa (λ ≤ 0,3) e baixo custo social

Código: `src/busca_aleatoria.py` e `src/busca_aleatoria_relatorio.py`. Choques com seed 42 (common random numbers); sorteio com seed 7.

## Desenho

- **Fase 1:** 6.000 combinações sorteadas, avaliadas em P2 com N = 200 e λ ∈ {0,1; 0,2; 0,3} (diagonal λ_π = λ_fiscal).
- **Fase 2:** 2.000 mutações em torno das 60 melhores e da fronteira sucesso × atividade.
- **Fase 3:** 33 finalistas com N = 1.000 em P1, P2 e P3 (θ = 0,5), λ de 0,1 a 0,3.
- **Espaço sorteado:** tamanho do pacote de 0,5% a 6% do PIB; composição entre os dez itens de `config/recessivo.yaml` (Dirichlet esparsa), com teto por item: renúncias 2,5; benefícios setoriais 1,0; subsídios 0,6; verbas acima do teto 0,2; previdência militar 0,4; emendas 0,5; custeio 0,8; pisos 1,2; investimento 1,0; transferências 1,5 (% do PIB; premissas da busca); início (1–4) e rampa (1–16 trimestres); regra monetária (Taylor ou condicionada sem piso, com alvo de 6,5% a 11%, corte em 4–12 trimestres, tolerância de 0 a 2 p.p. e prazo de 1–16 trimestres); venda de reservas de 0 a US$ 100 bi (limitada pelo piso de US$ 300 bi); alongamento da dívida (LFT a 30%–55% em 8–28 trimestres).
- **Sucesso:** critérios da seção 3.4, com dívida bruta, nas versões banda (1,5%–4,5%) e teto (≤ 4,5%).
- **Custo social:** diferença de PIB acumulada contra a referência sem ajuste (S) até a eleição de 2030, na mesma adesão e com os mesmos choques. Os cortes em transferências, pisos e investimento são reportados à parte.

## Resultados

1. **Com a banda, nenhuma combinação passa de cerca de 50% de sucesso com λ = 0,3, nem de 30% com λ = 0,1.** Entre 8.000 combinações, o máximo na triagem foi 46,5% (λ = 0,3) e 28,5% (λ = 0,1); nas finalistas, 44% a 50% conforme a especificação. O limite não vem da dívida: nas melhores combinações, a dívida se estabiliza em praticamente todas as trajetórias. Vem da inflação. Com λ_π baixo, as expectativas não se ancoram e a inflação final se dispersa para os dois lados da banda (no melhor caso, 29% das trajetórias abaixo de 1,5% e 26% acima de 4,5%, contra 12% e 10% com λ = 0,9). Nenhuma escolha fiscal corrige isso no modelo.
2. **Com o critério só de teto, é possível chegar a 75%–90% com λ = 0,3, mas só com pacotes de 6% do PIB aplicados de uma vez.** Eles custam de 3% a 13% do PIB de um ano até 2030 e, nas versões mais eficazes, cortam transferências; a dívida cai para 37%–60% do PIB, uma sobrecorreção.
3. **O perfil de baixo custo social existe, mas não garante sucesso com adesão baixa.** Combinação m00567: 4,4% do PIB em renúncias regressivas (2,45), benefícios setoriais (0,96), emendas (0,5), previdência militar (0,4) e custeio (0,1), sem corte de transferências, pisos ou investimento; início no 4º trimestre e rampa de 14; alívio condicionado sem piso (alvo de 6,5%); sem venda de reservas. Com λ = 0,3, o sucesso é de 73% (P1) e 52% (P2) pelo teto, de 37% e 31% pela banda, e quase nulo em P3. A atividade fica de 3,1 a 3,6 pontos do PIB de um ano acima de S até 2030, porque, com adesão baixa, a referência sem ajuste é uma espiral de prêmio e juros. Com λ = 0,1, o sucesso cai para 4%–16%.
4. **A alavanca que falta é a credibilidade do Banco Central, não o desenho fiscal.** Com λ_fiscal de 0,1 a 0,2 e λ_π = 0,8, o mesmo pacote de baixo custo chega a 70%–74% de sucesso pela banda e a 89%–94% pelo teto em P1 e P2 (`teste_credibilidades_separadas.csv`). Um governo com pouca credibilidade fiscal pode fazer um ajuste gradual e de baixo custo social dar certo se a meta de inflação e o Banco Central mantiverem a sua. Em P3 (FTPL), o pacote gradual continua falhando pela banda, por deflação; só o ajuste concentrado no início funciona ali.

## Limitações

- As duas credibilidades são tratadas como independentes; na prática, a perda de credibilidade fiscal tende a contaminar a da meta.
- Os tetos por item e a ausência de novos tributos (como a tributação de dividendos) são premissas da busca.
- A credibilidade de cada composição não é modelada: um pacote baseado em renúncias pode ser mais difícil de aprovar e, portanto, menos crível.
- A triagem usa N = 200 e só P2; as finalistas usam N = 1.000 nas três especificações.
