"""Quanto da inércia do IPCA o governo consegue reindexar à meta sem mexer no salário mínimo nem nos aluguéis?

θ = Σ_reindexados (peso × grau de indexação ao passado × parcela reajustável) / Σ_IPCA (peso × grau de indexação)

O denominador é a "massa inercial" do IPCA: cada componente pesa pelo seu peso no índice e pelo quanto o seu
reajuste segue a inflação passada (formal ou informalmente). Os graus de indexação são hipóteses explícitas,
com faixas baixa/central/alta; os pesos vêm do IPCA (energia e produtos farmacêuticos: informativo do
Ministério da Fazenda, set/2025; segmentos: BCB, RPM mar/2026, boxe 10; demais subitens: aproximações a conferir
com o IBGE).

Cenário pedido: tarifas de concessões com regulação discricionária (energia e saneamento, mais gás canalizado)
passam a ser reajustadas pela meta; salário mínimo segue a regra atual (INPC + crescimento do PIB); aluguéis
seguem os contratos. Extensões avaliadas à parte: planos de saúde (teto anual da ANS, regulação discricionária,
sem concessão) e medicamentos (fórmula da CMED, que exige mudança da Lei 10.742/2003).

Uso: python -m src.indexacao_theta
"""
import pandas as pd

from .busca_contra_mercado import SAIDA

# componente: (peso no IPCA, grau de indexação ao passado baixo/central/alto, parcela reindexável, grupo)
COMPONENTES = {
    # concessões com regulação discricionária
    "Energia elétrica residencial": (3.95, (0.25, 0.30, 0.40), 1.0, "concessao"),   # só a parcela B segue IPCA
    "Água e esgoto": (1.60, (0.70, 0.80, 0.90), 1.0, "concessao"),
    "Gás canalizado": (0.10, (0.40, 0.50, 0.60), 1.0, "concessao"),
    # outros administrados com regra de reajuste
    "Plano de saúde (ANS)": (3.90, (0.70, 0.80, 0.90), 1.0, "ans"),
    "Produtos farmacêuticos (CMED)": (3.49, (0.70, 0.80, 0.90), 1.0, "cmed"),
    "Transporte público e pedágio (contratos e municípios)": (2.50, (0.40, 0.50, 0.60), 0.0, "fora"),
    "Combustíveis e gás de botijão (preço de mercado)": (7.00, (0.00, 0.05, 0.10), 0.0, "fora"),
    "Demais administrados (impostos, taxas, jogos, telefonia)": (3.29, (0.40, 0.50, 0.60), 0.0, "fora"),
    # livres
    "Aluguel residencial (contratos)": (4.00, (0.90, 1.00, 1.00), 0.0, "fora"),
    "Demais serviços (salários; salário mínimo pela regra atual)": (31.50, (0.40, 0.50, 0.60), 0.0, "fora"),
    "Alimentação no domicílio": (15.75, (0.05, 0.10, 0.15), 0.0, "fora"),
    "Bens industriais": (22.92, (0.05, 0.10, 0.15), 0.0, "fora"),
}
CENARIOS = {"concessões (energia, saneamento, gás)": {"concessao"},
            "+ planos de saúde (ANS)": {"concessao", "ans"},
            "+ planos de saúde e medicamentos (CMED)": {"concessao", "ans", "cmed"}}


def main():
    linhas, tab = [], []
    for nome, (w, graus, parc, grp) in COMPONENTES.items():
        tab.append({"componente": nome, "peso": w, "grau_baixo": graus[0], "grau_central": graus[1],
                    "grau_alto": graus[2], "grupo": grp})
    for cen, grupos in CENARIOS.items():
        lin = {"cenario": cen}
        for k, nome in enumerate(("baixo", "central", "alto")):
            den = sum(w * g[k] for w, g, _, _ in COMPONENTES.values())
            num = sum(w * g[k] for w, g, _, grp in COMPONENTES.values() if grp in grupos)
            lin[f"theta_{nome}"] = num / den
        lin["peso_reindexado"] = sum(w for w, _, _, grp in COMPONENTES.values() if grp in grupos)
        linhas.append(lin)
    pd.DataFrame(tab).to_csv(SAIDA / "theta_componentes.csv", index=False)
    d = pd.DataFrame(linhas)
    d.to_csv(SAIDA / "theta_cenarios.csv", index=False)
    print(d.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
