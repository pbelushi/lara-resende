"""Quanto da inércia do IPCA o governo consegue reindexar à meta sem mexer no salário mínimo nem nos aluguéis?

θ = Σ_reindexados (peso × grau de indexação ao passado) / Σ_IPCA (peso × grau de indexação ao passado)

Pesos: IPCA de setembro de 2026, Brasil, 377 subitens (IBGE, Tabela 7060; data/raw/ibge_ipca/ipca_pesos_set2026.csv).
Grau de indexação: quanto o reajuste do subitem segue a inflação passada, formal ou informalmente (hipóteses
explícitas, com faixas baixa/central/alta, atribuídas por regra em CLASSES abaixo; a tabela subitem a subitem fica
em outputs/.../theta_subitens.csv).

Cenário pedido: tarifas de concessões com regulação discricionária (energia elétrica, água e esgoto, gás encanado),
transporte público (ônibus urbano, intermunicipal e interestadual, trem, metrô, integração) e telefonia e internet
(telefonia fixa e móvel, acesso à internet, combo) passam a ser reajustados pela meta; salário mínimo segue a regra atual (INPC + crescimento do PIB, que preserva a
indexação dos serviços ligados a ele, como o emprego doméstico); aluguéis seguem os contratos. Extensões avaliadas
à parte: planos de saúde (teto anual da ANS, regulação discricionária) e medicamentos (fórmula da CMED, que exige
mudança da Lei 10.742/2003).

Uso: python -m src.indexacao_theta
"""
import re

import pandas as pd

from .busca_contra_mercado import SAIDA
from .credibilidades_separadas import RAIZ

ARQ = RAIZ / "data" / "raw" / "ibge_ipca" / "ipca_pesos_set2026.csv"

# (regra sobre a descrição ou o código, classe, grupo de política, grau baixo/central/alto)
CLASSES = [
    (r"^Energia elétrica residencial$", "concessão: energia (só a parcela B segue a inflação)", "concessao", (0.25, 0.30, 0.40)),
    (r"^Taxa de água e esgoto$", "concessão: saneamento", "concessao", (0.70, 0.80, 0.90)),
    (r"^Gás encanado$", "concessão: gás canalizado", "concessao", (0.40, 0.50, 0.60)),
    (r"^Plano de saúde$", "regulado: plano de saúde (ANS)", "ans", (0.70, 0.80, 0.90)),
    ("cod:6101", "regulado: medicamentos (CMED)", "cmed", (0.70, 0.80, 0.90)),
    (r"^Aluguel residencial$", "contrato: aluguel", "fora", (0.90, 1.00, 1.00)),
    (r"^Pedágio$", "contrato: pedágio", "fora", (0.80, 0.90, 1.00)),
    (r"^(Ônibus urbano|Ônibus intermunicipal|Ônibus interestadual|Trem|Metrô|Integração transporte público)$",
     "administrado: transporte público", "transporte", (0.40, 0.50, 0.60)),
    (r"^Plano de telefonia fixa$", "telecom: telefonia fixa", "telecom", (0.50, 0.65, 0.80)),
    (r"^(Plano de telefonia móvel|Acesso à internet|Combo de telefonia, internet e tv por assinatura)$",
     "telecom: telefonia móvel e internet (preço livre)", "telecom", (0.20, 0.30, 0.40)),
    (r"^(Gasolina|Etanol|Óleo diesel|Gás veicular|Gás de botijão|Carvão vegetal)$",
     "administrado/mercado: combustíveis", "fora", (0.00, 0.05, 0.10)),
    (r"^(Cartório|Conselho de classe|Correio)$", "administrado: taxas e tarifas", "fora",
     (0.50, 0.65, 0.80)),
    (r"^(Emplacamento e licença|Multa|Jogos de azar|Cigarro)$", "administrado: tributos e outros", "fora",
     (0.05, 0.15, 0.25)),
    (r"^Empregado doméstico$", "serviço ligado ao salário mínimo", "fora", (0.60, 0.70, 0.80)),
    (r"^Condomínio$", "serviço: condomínio", "fora", (0.50, 0.60, 0.70)),
    ("cod:8101", "serviço: educação regular", "fora", (0.60, 0.70, 0.80)),
    (r"^(Médico|Dentista|Aparelho ortodôntico|Fisioterapeuta|Psicólogo|Exame de laboratório|Hospitalização e cirurgia|Exame de imagem)$",
     "serviço: saúde", "fora", (0.50, 0.60, 0.70)),
    (r"^(Mão de obra|Mudança|Costureira|Manicure|Cabeleireiro e barbeiro|Depilação|Sobrancelha|Despachante|Transporte escolar|Conserto de automóvel|Pintura de veículo|Estacionamento|Autoescola|Curso preparatório|Curso de idioma|Curso de informática|Atividades físicas)$|^Conserto|^Reforma",
     "serviço: pessoais e reparos", "fora", (0.40, 0.50, 0.60)),
    ("cod:1201", "serviço: alimentação fora do domicílio", "fora", (0.30, 0.40, 0.50)),
    (r"^(Serviço bancário|Táxi|Transporte por aplicativo|Seguro voluntário de veículo|Aluguel de veículo|Clube|Casa noturna|Tratamento de animais \(clínica\)|Serviço de higiene para animais|Cinema, teatro e concertos|Tv por assinatura|Serviços de streaming)$",
     "serviço: outros", "fora", (0.20, 0.30, 0.40)),
    (r"^(Passagem aérea|Hospedagem|Pacote turístico)$", "serviço: preços flexíveis", "fora", (0.05, 0.10, 0.20)),
]
PADRAO = ("bens: alimentos e industriais", "fora", (0.05, 0.10, 0.15))
CENARIOS = {"concessões (energia, saneamento, gás encanado)": {"concessao"},
            "concessões + transporte público + telefonia e internet": {"concessao", "transporte", "telecom"},
            "+ planos de saúde (ANS)": {"concessao", "transporte", "telecom", "ans"},
            "+ planos de saúde e medicamentos (CMED)": {"concessao", "transporte", "telecom", "ans", "cmed"}}


def classificar(codigo: str, desc: str):
    for regra, classe, grupo, graus in CLASSES:
        if regra.startswith("cod:"):
            if codigo.startswith(regra[4:]):
                return classe, grupo, graus
        elif re.search(regra, desc):
            return classe, grupo, graus
    return PADRAO


def main():
    d = pd.read_csv(ARQ, dtype={"codigo": str})
    s = d[d.nivel == "subitem"].copy()
    cl = [classificar(c, x) for c, x in zip(s.codigo, s.descricao)]
    s["classe"] = [c[0] for c in cl]
    s["grupo"] = [c[1] for c in cl]
    for k, nome in enumerate(("baixo", "central", "alto")):
        s[f"grau_{nome}"] = [c[2][k] for c in cl]
    s.to_csv(SAIDA / "theta_subitens.csv", index=False)
    linhas = []
    for cen, grupos in CENARIOS.items():
        lin = {"cenario": cen, "peso_reindexado": s.loc[s.grupo.isin(grupos), "peso"].sum()}
        for nome in ("baixo", "central", "alto"):
            massa = s["peso"] * s[f"grau_{nome}"]
            lin[f"theta_{nome}"] = massa[s.grupo.isin(grupos)].sum() / massa.sum()
        linhas.append(lin)
    r = pd.DataFrame(linhas)
    r.to_csv(SAIDA / "theta_cenarios.csv", index=False)
    resumo = s.assign(massa=s.peso * s.grau_central).groupby("classe")[["peso", "massa"]].sum()
    resumo["fracao_da_massa_inercial"] = resumo.massa / resumo.massa.sum()
    resumo.sort_values("massa", ascending=False).to_csv(SAIDA / "theta_massa_por_classe.csv")
    pd.set_option("display.width", 200)
    print(resumo.sort_values("massa", ascending=False).round(3).to_string())
    print(r.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
