# Credibilidades separadas: λ_fiscal travado em 0,1–0,3, λ_π livre entre 0,5 e 1,0

Código: `src/credibilidades_separadas.py`. Choques com seed 42; λ_π sorteado por trajetória em U(0,5; 1,0) com seed 2027; sorteio das combinações com seed 11.

## 1. Validação em duas dimensões (P2)

| Episódio | λ_π | λ_fiscal | Faixa de λ_π (erro até 5% acima do mínimo) | Faixa de λ_fiscal |
|---|---|---|---|---|
| 2015–16 | 0,50 | 0,00 | 0,45–0,50 | 0,00–0,15 |
| 2016–19 | 1,00 | 0,75 | 0,90–1,00 | 0,60–0,90 |
| 2020–22 | 0,35 | 0,00 | 0,30–0,45 | 0,00–0,35 |

A credibilidade da meta fica acima da fiscal nos três episódios, e o ajuste em duas dimensões melhora o erro em relação à diagonal. Em 2020–22, porém, λ_π fica abaixo de 0,5; parte disso reflete choques de oferta que o modelo só capta pelo câmbio (seção 4.3 do paper).

## 2. Estratégias do paper (λ_fiscal = 0,2; banda)

Em P1 e P2, o sucesso depende quase só de λ_π: de 0,45–0,50 com λ_π = 0,5 a 0,72–0,79 com λ_π = 1,0. C sem piso e A com reservas lideram, e B falha sempre. Em P3, nenhuma estratégia do paper funciona pela banda (até 6%). Tabela completa: `estrategias_grade.csv`.

## 3. Busca aleatória (5.500 combinações na triagem; 29 finalistas com N = 1.000)

- **Teto de sucesso:** cerca de 70% pela banda (P1 e P2) e 89%–97% pelo teto. O limite vem da mistura de λ_π, não da política fiscal.
- **Muitas combinações chegam perto do teto:** 3.556 de 5.504 têm sucesso de pelo menos 65% em P2 com λ_fiscal = 0,2. O pacote mínimo nesse grupo é de 2,5% do PIB (mediana de 4,5%).
- **Perfil de menor custo social entre as bem-sucedidas** (finalistas m00785, m00421, m00600 e m01235): de 3,2% a 4,0% do PIB, multiplicador médio de 0,33 a 0,41, concentrado em renúncias regressivas, benefícios setoriais, subsídios, previdência militar e verbas acima do teto; nenhum corte em pisos ou investimento e no máximo 0,16% do PIB em transferências; início entre o 2º e o 4º trimestre, com rampa de 10 a 16 trimestres; alívio condicionado sem piso (alvo de 6,7% a 7,3%, tolerância de 1,6 a 1,9 p.p.). Sucesso de 66%–72% pela banda em P1 e P2 e atividade de 1,3 a 2,3 pontos do PIB de um ano acima de S até 2030, contra −1,4 a −1,5 do ortodoxo do paper.
- **O que explica a atividade entre as bem-sucedidas** (correlação com a diferença de PIB contra S): multiplicador médio (−0,67), corte de transferências (−0,45), de investimento (−0,41) e de pisos (−0,32), tamanho total (−0,39) e rampa mais longa (+0,54). Com a regra condicionada sem piso, a atividade média é de −2,5 pontos, contra −3,4 com a regra de Taylor.
- **Em P3 (FTPL), o pacote gradual falha:** de 0% a 2% de sucesso pela banda, por deflação. Só pacotes de 5,5%–6% do PIB concentrados no início funcionam (46%–61% pela banda), ao custo de −3 pontos do PIB em P1/P2 e de −7 a −9 em P3. A validação histórica não sustenta o canal fiscal de P3 (θ = 0).

## Limitações

λ_π e λ_fiscal são exógenos e independentes; a distribuição U(0,5; 1,0) de λ_π é uma premissa, que 2020–22 contraria. Tetos por item e ausência de novos tributos como na busca anterior.
