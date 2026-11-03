"""CLI (v2.2): matriz especificação × cenário × variante, superfície λ_π × λ_fiscal, validação e relatório."""
from __future__ import annotations

import argparse
import copy
import logging
import re
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src import (analises, bootstrap, consistencia, dados, estimacao, graficos, modelo, reservas_choque, validacao,
                 varredura)

RAIZ = Path(__file__).resolve().parent
ROTULOS_SENS = {"a2": "a2 (hiato × juro longo)", "b3": "b3 (repasse cambial)", "kappa": "κ (desancoragem)",
                "p3": "p3 (prêmio × inconsistência)", "b2_p2": "b2 (inclinação, P2)", "theta": "θ (lacuna → inflação)",
                "phi": "φ (lacuna inicial não precificada)", "delta_min": "Δ_min (piso de r − g)",
                "p2_p3": "p2 em P3 (prêmio fiscal)"}
ROTULOS_CRIT = {"inflacao_explosiva": "inflação explosiva (>20%)", "divida_inclinacao": "dívida ainda subindo",
                "divida_nivel": "dívida acima da tolerância", "inflacao": "inflação acima do teto",
                "reservas": "reservas abaixo do piso"}
DESCR_VAR = {"base": "r_long_neutro = 5,5; ω = 0", "neutro_45": "r_neutro = 4,5 e r_long_neutro = 5,0 (mesmo tp_lp)",
             "rlong_45": "r_long_neutro = 4,5", "rlong_65": "r_long_neutro = 6,5", "omega_05": "ω = 0,5",
             "omega_1": "ω = 1 (todo o prêmio pela Taylor)", "phi_025": "P3 com φ = 0,25", "phi_05": "P3 com φ = 0,5",
             "inercia_alta": "b1 = 0,82 (estimado)", "repasse_est": "b3 = 0,012 (estimado)",
             "C_lento": "C com corte em 12 trimestres", "C_sem_tolerancia": "C com δ0 = 0",
             "C_sem_piso": "C com a trajetória como teto (Taylor − δ ≤ i ≤ Taylor); sem piso de 7,5% após T_corte + T_δ",
             "A_reservas": "A com a mesma venda programada de C (até US$ 100 bi em reservas)",
             "C_piso_corte": "C com piso de 7,5% só durante o corte (sem piso após T_corte + T_δ)",
             "C_sem_piso_inercia": "C_sem_piso com b1 = 0,82 (comparado com A sob a mesma inércia)",
             "C_sem_piso_b3_alto": "C_sem_piso com b3 no limite superior do IC (comparado com A sob o mesmo b3)",
             "p2_zero": "P3 com p2 = 0", "p2_integral": "P3 com p2 integral (0,3)",
             "vt_perpetuidade": "P3 com valor terminal 100·s/(r−g)",
             "rolagem_0": "r_min_rolagem = 0",
             "rolagem_2": "r_min_rolagem = 2,0",
             "along_20": "alongamento: LFT + compromissadas ≤ 40% em 20 trimestres, 70% para NTN-B",
             "phi_025_along_20": "P3, φ = 0,25 com along_20", "phi_05_along_20": "P3, φ = 0,5 com along_20",
             "phi_025_along_12": "P3, φ = 0,25, alongamento em 12 trimestres",
             "phi_025_along_28": "P3, φ = 0,25, alongamento em 28 trimestres",
             "phi_025_along_pre": "P3, φ = 0,25, alongamento 70% para prefixados",
             "phi_025_along_50": "P3, φ = 0,25, meta de 50%",
             "estimada": "b3 estimado; ω = 0 (ω não identificado)", "theta_025": "P3 com θ = 0,25 (validação 2016–2019)",
             "omega_038": "ω = 0,38 = 1 − b (verificação cruzada pelo juro longo)",
             "theta_0": "P3 com θ = 0 (validação 2020–2022: Phillips achatada sem inércia)",
             "pe_fiscal_0": "P3 sem inflação fiscal nas expectativas", "pe_fiscal_05": "P3 com peso 0,5 da inflação fiscal nas expectativas", "estimada_b3_baixo": "b3 no limite inferior do IC",
             "estimada_b3_alto": "b3 no limite superior do IC", "estimada_omega_baixo": "ω no limite inferior do IC",
             "estimada_omega_alto": "ω no limite superior do IC"}

log = logging.getLogger("run")


SINTESE = ['(a) **B falha em todas as especificações, critérios e variantes.** Sem ajuste fiscal, a política monetária expansionista leva à desancoragem (P1, P2) ou à dívida crescente (P3).', '', '(b) **A e C base.** Com o critério de teto, há empate em P1 e P2 e vantagem de A em P3. Com a banda simétrica, que reprova trajetórias deflacionárias, a vantagem de A em P3 desaparece e C fica à frente. Parte da vantagem de A vinha de deflação aceita como sucesso.', '', '(c) **O piso de 7,5% em C.** Remover o piso após a transição (C sem piso) faz C exigir significativamente menos adesão que A base nas três especificações com o critério de teto. Quase todo o efeito vem do fim do piso, não da troca de piso por teto durante o corte.', '', '(d) **Reservas.** A com a mesma venda efetiva empata com C sem piso na maior parte das comparações. O ganho vem principalmente da venda de reservas e se mantém pela dívida líquida, porque decorre do custo de carregamento. Ele desaparece quando o carregamento se aproxima de zero e tem retorno decrescente: vendas de cerca de US$ 60 bi preservam a maior parte do ganho e mantêm as reservas perto de 100% da métrica ARA do FMI. O alívio monetário de C sem piso acrescenta um ganho pequeno e consistente sobre A com a mesma venda, que aumenta quando há menos reservas disponíveis.', '', '(e) **Custo de cauda.** Choques transitórios nos anos 2 e 3 não produzem custo mensurável da venda de reservas. Choques persistentes ou tardios eliminam a vantagem de quem vendeu. O canal das reservas para o prêmio de risco tem efeito pequeno quando o nível adequado é 100% da ARA, e moderado no caso pessimista.', '', '(f) **Parâmetros não identificados.** ω (resposta da Selic ao prêmio) e θ (canal fiscal da inflação) não são determinados pelos dados. As conclusões (a) a (d) valem em toda a grade testada. A exceção é P3 com θ alto e critério de teto, em que A fica à frente.', '', '(g) **Alongamento.** Não reabre a erosão inflacionária quando a lacuna fiscal não está precificada, mas custa pouco quando está.', '', '**Conclusão:** a estratégia de melhor desempenho combina ajuste fiscal, Taylor sem piso, alívio monetário limitado e temporário, e venda moderada de reservas. Seu ganho depende do custo de carregamento e de não haver uma crise persistente durante o ajuste.']


def rotular_secao5(texto: str, ef: float) -> str:
    """Seção 5: A_reservas → A_reservas (efetiva: 76), pois o piso R_min limita a venda programada."""
    if "\n## 5. " not in texto or "\n## 6. " not in texto:
        return texto
    i, j = texto.index("\n## 5. "), texto.index("\n## 6. ")
    meio = re.sub(r"(?<![\w])A_reservas(?![\w]| \(efetiva)", f"A_reservas (efetiva: {ef:.0f})", texto[i:j])
    return texto[:i] + meio + texto[j:]


def _fmt(x, casas=2):
    return "não atinge" if x is None or not np.isfinite(x) else f"{x:.{casas}f}".replace(".", ",")


def _iv(txt: str) -> str:
    """Intervalos "[0.33, 1.00]; [...]" no formato brasileiro "[0,33 – 1,00]"."""
    return txt.replace(", ", " – ").replace(".", ",")


def _pct(x):
    return "—" if x is None or not np.isfinite(x) else f"{100 * x:.0f}%"


def _ordem_txt(ordem, espec, var, col="posicao"):
    o = ordem[(ordem["especificacao"] == espec) & (ordem["variante"] == var)].sort_values(col)
    return " > ".join(o["cenario"]) if len(o) else "—"


def _todos_falham(ls, espec, var, suf: str = "") -> bool:
    """Nenhum cenário atinge P(sucesso) ≥ 50%: a ordem vem só do desempate e compara graus de fracasso."""
    l = ls[(ls["especificacao"] == espec) & (ls["variante"].isin([var, "base"]))]
    l = l[(l["variante"] == var) | ~l["cenario"].isin(l.loc[l["variante"] == var, "cenario"])]
    return bool(len(l)) and l[f"lambda_star_50{suf}"].isna().all()


def _boot(bd, espec, var):
    if bd is None:
        return None
    r = bd[(bd["especificacao"] == espec) & (bd["variante"] == var)]
    return None if r.empty else r.iloc[0]


def _empate(bd, espec, var, rot: str = "80") -> bool:
    r = _boot(bd, espec, var)
    return r is not None and r.get(f"leitura_{rot}") == "empate estatístico"


def _ordem_marcada(ordem, ls, espec, var, bd=None, suf: str = "", rot: str = "80") -> str:
    """Ordem com "A ≈ C" quando o IC de 95% de Δλ*₈₀ contém zero, e † quando nenhum cenário atinge 50%.

    suf = "" (critério de inflação só com teto) ou "_bil" (banda simétrica); ordem e bd devem ser os da mesma métrica.
    """
    txt = bootstrap.ordem_com_empate(_ordem_txt(ordem, espec, var), _empate(bd, espec, var, rot))
    return txt + " †" if txt != "—" and _todos_falham(ls, espec, var, suf) else txt


def _ic(r, rot="80") -> str:
    return (f"{_fmt(r[f'delta_{rot}'])} [{_fmt(r[f'ic_lo_{rot}'])}; {_fmt(r[f'ic_hi_{rot}'])}]"
            + (" ⚠" if r[f"pouco_confiavel_{rot}"] else ""))


def relatorio(ctx: dict, saida: Path) -> Path:
    p, cfg, exp = ctx["p"], ctx["cfg"], ctx["exp"]
    ini = p["ini"]
    ls, ordem, df, especs = ctx["ls"], ctx["ordem"], ctx["df"], ctx["especs"]
    nomes = {k: v["nome"] for k, v in cfg["cenarios"].items()}
    bd, ba, est, al = ctx.get("boot_d"), ctx.get("boot_a"), ctx.get("est"), ctx.get("along")
    L = ["# Relatório v2.2: credibilidade, teoria da inflação e estabilização da dívida", "",
         f"Gerado em {time.strftime('%Y-%m-%d %H:%M')} · t0 = {ini.get('trimestre_base', ini['data_base'])} "
         f"(último trimestre fechado, {ini['data_base']}) · Monte Carlo N = {ctx['args'].mc} por (especificação, "
         f"variante, cenário, λ), semente {ctx['args'].seed}, mesmos choques em todos os experimentos"
         + (" · **com monetização** em vez de migração para NTN-B" if ctx["args"].monetizacao else "") + ".", ""]

    # 0. checagem de consistência e portão de qualidade
    cons, port = ctx["consistencia"], ctx["portao"]
    if port["aviso"]:
        L += [f"> **Aviso:** {port['aviso']} Pacote adicional necessário para A estabilizar a dívida com λ = 1: "
              + (f"**{_fmt(port['pacote_adicional'], 2)}% do PIB**." if np.isfinite(port["pacote_adicional"])
                 else "mais de 10% do PIB (não encontrado na busca)."), ""]
    L += ["## 0. Checagem de consistência", "",
          "Trajetória determinística, P1, λ = 1. Custo real efetivo em estado estacionário = composição final de A, "
          "com LFT ao juro curto neutro e NTN-B, prefixados e cambial ao juro longo neutro. Primário estabilizador "
          f"= (r − g)/(1 + g) × dívida inicial, com g = {_fmt(p.get('g_potencial') or ini['g_potencial'])}% a.a. "
          "Folga = primário final (média dos últimos 8 trimestres) − estabilizador da dívida bruta.", "",
          "| r_long neutro | ω | r neutro curto | tp_lp | Custo real efetivo | Estabilizador bruta | "
          "Estabilizador líquida | Primário final A / B / C | Folga A / B / C | A estabiliza? |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in cons.iterrows():
        L.append(f"| {_fmt(r['r_long_neutro'], 1)} | {_fmt(r['omega'], 1)} | {_fmt(r['r_neutro_base'], 1)} | "
                 f"{_fmt(r['tp_lp'])} | {_fmt(r['r_efetivo_ss'])} | {_fmt(r['s_estab_bruta'])} | "
                 f"{_fmt(r['s_estab_liquida'])} | "
                 + " / ".join(_fmt(r[f's_final_{c}']) for c in cfg["cenarios"]) + " | "
                 + " / ".join(_fmt(r[f'folga_{c}']) for c in cfg["cenarios"]) + " | "
                 + ("sim" if r["A_estabiliza"] else "**não**") + " |")
    L += ["", f"Portão de qualidade (calibração base): A {'estabiliza' if port['A_estabiliza'] else 'NÃO estabiliza'} "
          "a dívida com adesão total" + ("; o ranking abaixo compara robustez relativa." if port["A_estabiliza"]
                                          else f"; ver aviso no topo."),
          f"Referência empírica (não usada como padrão): NTN-B 10 anos real média de "
          f"{_fmt(ini.get('ntnb10_media_2017_2019', np.nan))}% em 2017–2019 e "
          f"{_fmt(ini.get('ntnb10_media_amostra', np.nan))}% desde {ini.get('ntnb10_amostra_inicio', '?')}.", ""]

    # 1. parâmetros estimados
    if est is not None:
        pr, om, cj = est["b3_principal"], est["omega_principal"], est["canal_longo"]
        b3t = est["b3"]
        L += ["## 1. Parâmetros estimados", "", "### Repasse cambial (b3)", "",
              "Projeções locais mensais (2004–2026): repasse acumulado ERPT_h = β_h/δ_h (preço e câmbio na mesma "
              "janela), controles de 12 defasagens da inflação, hiato e desvio do Focus em relação à meta (ambos "
              "defasados) e variação do IC-Br em US$; dummy de 2020. IC de 95% por bootstrap em blocos de 12 meses. "
              "IV: depreciação instrumentada pela variação do dólar amplo e do VIX.", "",
              "| Método | Índice | Amostra | ERPT 3m | ERPT 6m | ERPT 12m [IC 95%] | ERPT 24m | F 1º estágio (12m) |",
              "|---|---|---|---|---|---|---|---|"]
        for (met, ind, am), g in b3t.groupby(["metodo", "indice", "amostra"], sort=False):
            g = g.set_index("h")
            f1 = g.loc[12, "F1"] if "F1" in g and pd.notna(g.loc[12].get("F1", np.nan)) else np.nan
            L.append(f"| {met} | {ind} | {am} | {_pct(g.loc[3, 'erpt'])} | {_pct(g.loc[6, 'erpt'])} | "
                     f"{_pct(g.loc[12, 'erpt'])} [{_pct(g.loc[12, 'ic_lo'])}; {_pct(g.loc[12, 'ic_hi'])}] | "
                     f"{_pct(g.loc[24, 'erpt'])} | {_fmt(f1, 1) if np.isfinite(f1) else '—'} |")
        L += ["", f"Referência da v1 (regressão trimestral, coeficiente da depreciação em 12 meses): "
              f"{_fmt(p['b3_v1_trimestral'], 3) if p.get('b3_v1_trimestral') is not None else '—'}.",
              f"**Estimativa principal: {pr['metodo']}**, ERPT em 12 meses = {_pct(pr['erpt_12'])} "
              f"[{_pct(pr['erpt_12_lo'])}; {_pct(pr['erpt_12_hi'])}]; F do primeiro estágio = {_fmt(pr['F1_iv_h12'], 1)}"
              + (" (instrumentos fracos: OLS mantido como principal)." if pr["instrumentos_fracos"] else
                 " (instrumentos fortes: IV é a estimativa principal)."), "",
              "Calibração de b3 por impulso-resposta (choque de 10% de depreciação, Selic fixa, λ = 0,5): b3 tal que "
              "o repasse simulado em 4 trimestres = ERPT_12; conferência em 2 e 8 trimestres contra ERPT_6 e ERPT_24.",
              "", "| Especificação | b3 pontual | b3 (IC inferior) | b3 (IC superior) | Modelo 2t / LP 6m | "
              "Modelo 4t / LP 12m | Modelo 8t / LP 24m |", "|---|---|---|---|---|---|---|"]
        for r in est["calibracao_b3"].itertuples():
            L.append(f"| {r.especificacao} | {_fmt(r.b3_pontual, 4)} | {_fmt(r.b3_baixo, 4)} | {_fmt(r.b3_alto, 4)} | "
                     f"{_pct(r.erpt_modelo_2t)} / {_pct(r.erpt_lp_6m)} | {_pct(r.erpt_modelo_4t)} / "
                     f"{_pct(r.erpt_lp_12m)} | {_pct(r.erpt_modelo_8t)} / {_pct(r.erpt_lp_24m)} |")
        cb = est["calibracao_b3"]
        for rot, col_erpt, nome_lim in (("baixo", "erpt_12_lo", "inferior"), ("alto", "erpt_12_hi", "superior"),
                                        ("pontual", "erpt_12", "pontual")):
            zerados = [r.especificacao for r in cb.itertuples() if getattr(r, f"obs_{rot}")]
            if zerados:
                L.append(f"b3 ({'IC ' + nome_lim if rot != 'pontual' else 'pontual'}) = 0 em {', '.join(zerados)}: o "
                         f"{'limite ' + nome_lim + ' do IC de ' if rot != 'pontual' else ''}ERPT_12 "
                         f"({_pct(pr[col_erpt])}) é menor que o repasse que o modelo já gera com b3 = 0 (via expectativas "
                         "e inércia); como b3 negativo não tem interpretação, o parâmetro foi fixado em 0 nesse limite.")
        excesso = [r for r in cb.itertuples() if r.erpt_modelo_8t > 2 * max(r.erpt_lp_24m, 0.01)]
        if excesso:
            L.append("Em " + ", ".join(r.especificacao for r in excesso) + ", o modelo repassa "
                     + ", ".join(f"{_pct(r.erpt_modelo_8t)}" for r in excesso) + " em 8 trimestres, contra "
                     f"{_pct(excesso[0].erpt_lp_24m)} estimado em 24 meses: a inércia acumula o repasse além do que os "
                     "dados mostram, mesmo com o ajuste exato em 4 trimestres.")
        oe, ue, lc = est["omega"], est["unidade_embi"], est["leitura_canal"]
        L += ["", "### Fração do prêmio que passa pela Selic (ω)", "",
              f"Regra de Taylor mensal com prêmio, {om['inicio']} a {om['fim']} (o EMBI+ foi descontinuado em jul/2024; "
              "não há CDS público por API). Unidade conferida: o Ipeadata publica o EMBI+ em pontos-base (média de "
              f"{_fmt(ue['bruto_media_bp'], 0)} bp em 2005–2024, de {_fmt(ue['bruto_min_bp'], 0)} a "
              f"{_fmt(ue['bruto_max_bp'], 0)}); o painel divide por 100 e usa p.p. (média {_fmt(ue['painel_media_pp'])}).",
              "ψ = b_curto/(1 − ρ) é o efeito de longo prazo de 1 p.p. de prêmio sobre a Selic, além do canal das "
              "expectativas. IC de 95% de ψ pelo método de Fieller (não pelo método delta): quando 1 − ρ não é "
              "significativamente diferente de zero, o conjunto é ilimitado. A estimativa não é cortada em [0, 1].", "",
              "| Amostra | Método | n | ρ (EP) | Coef. curto prazo do prêmio (EP) | ψ | IC 95% de Fieller | Classificação |",
              "|---|---|---|---|---|---|---|---|"]
        for r in oe.itertuples():
            if pd.isna(getattr(r, "psi", np.nan)):
                continue
            L.append(f"| {r.amostra} | {r.metodo} | {int(r.n)} | {_fmt(r.rho, 3)} ({_fmt(r.se_rho, 3)}) | "
                     f"{_fmt(r.b_curto, 3)} ({_fmt(r.se_b_curto, 3)}) | {_fmt(r.psi)} | {r.ic_texto} | "
                     f"{estimacao.CLASSES_OMEGA[r.classe]} |")
        L += ["", f"**Estimativa principal (NLS, amostra completa): ψ = {_fmt(om['psi'])}, IC de Fieller "
              f"{om['ic_texto']} — {om['classe_texto']}.**"]
        L.append(f"- **Magnitude:** {texto_magnitude(om)}")
        L.append(f"- **Sinal:** {texto_sinal(oe)}")
        L.append("")
        if om["usado_no_modelo"]:
            L.append(f"ω = {_fmt(om['omega'])} entra na variante `estimada`; as variantes estimada_omega_* usam os "
                     "limites do IC restritos a [0, 1].")
        else:
            motivo = {"nao_identificado": "ψ pode assumir qualquer valor",
                      "nao_informativo": "o intervalo não discrimina entre os valores da grade",
                      "erro_especificacao": "o modelo exige ω entre 0 e 1 por construção",
                      "fora_do_dominio": "o ponto está fora do domínio que o modelo admite e o intervalo, embora "
                                         "limitado, vai de praticamente zero a mais de dez, sem discriminar entre os "
                                         "valores da grade"}[om["classe"]]
            L.append(f"Como {motivo}, ω **não é usado** no modelo: a variante `estimada` usa ω = 0 (o mesmo da base) "
                     "com o b3 estimado, não há variantes estimada_omega_* e a incerteza sobre ω fica representada pela "
                     "grade {0; 0,5; 1} (variantes base, omega_05 e omega_1).")
        if (oe["classe"] == "erro_especificacao").any():
            L.append("Há regressões com IC inteiramente fora de [0, 1]: possível erro de especificação, por exemplo "
                     "variável omitida (crises de 2008 ou 2020 afetando prêmio e Selic ao mesmo tempo).")
        else:
            L.append("Nenhuma regressão tem IC limitado e inteiramente fora de [0, 1]. As estimativas pontuais acima de 1 "
                     "e os ρ próximos de 1 (Selic muito persistente) são compatíveis com variável omitida que move "
                     "prêmio e Selic juntos (2008, 2015–16, 2020), mas os dados não permitem afirmar erro de "
                     "especificação.")
        L += ["", f"Verificação cruzada pelo juro longo ({cj['inicio']} a {cj['fim']}, n = {cj['n']}): "
              f"Δ NTN-B10 = a + b·Δprêmio + c·ΔSelic esperada, b = {_fmt(cj['b'])} (EP {_fmt(cj['se_b'])}; IC 95% "
              f"[{_fmt(cj['b_lo'])}; {_fmt(cj['b_hi'])}]). O modelo implica b ≈ 1 − ω; ψ + b = {_fmt(lc['soma'])}.",
              ("**A soma é informativa**: ψ está identificado e b é preciso." if lc["informativa"] else
               "**A soma ψ + b não é informativa**, porque ψ não está identificado com precisão útil: qualquer valor de "
               "ψ no intervalo é compatível com os dados, e a soma herda essa indeterminação.")
              + (f" Isoladamente, b é preciso: se o modelo valesse, implicaria ω ≈ 1 − b = {_fmt(lc['omega_implicito'])} "
                 f"[{_fmt(lc['omega_implicito_lo'])}; {_fmt(lc['omega_implicito_hi'])}], isto é, cerca de "
                 f"{_pct(cj['b'])} do prêmio chegando ao juro longo. Esse valor é uma leitura indireta, condicionada "
                 "à estrutura do modelo, e não substitui a estimação direta de ω; não é usado como calibração."
                 if lc["b_preciso"] else ""), ""]
        if bd is not None:
            L += ["Ordenamento A × C na variante `estimada` (ao lado da base):", "",
                  "| Especificação | Base | Estimada | Δλ*₈₀ estimada [IC 95%] | Leitura |", "|---|---|---|---|---|"]
            for e in especs:
                r = _boot(bd, e, "estimada")
                L.append(f"| {e} | {_ordem_marcada(ordem, ls, e, 'base', bd)} | {_ordem_marcada(ordem, ls, e, 'estimada', bd)} | "
                         f"{_ic(r) if r is not None else '—'} | {r['leitura_80'] if r is not None else '—'} |")
            L.append("")

    if ctx.get("ordem_bil") is not None:
        L += secao_criterio(ctx)

    # 2. ordenamento por especificação
    L += ["## 3. Ordenamento por especificação (variante base e estimada; critério de teto)", "",
          "Critério: menor λ\\*₈₀ na diagonal λ_π = λ_fiscal; desempate por λ\\*₅₀, λ\\* determinístico e "
          "P(sucesso) máxima. Ordem estrita entre A e C só quando o IC de 95% de Δλ\\*₈₀ (bootstrap pareado, "
          f"R = {ctx['args'].boot_r}) exclui zero; caso contrário, \"A ≈ C\".", ""]
    for e in especs:
        b = ls[(ls["especificacao"] == e) & (ls["variante"] == "base")]
        rb, re_ = _boot(bd, e, "base"), _boot(bd, e, "estimada")
        L += [f"### {graficos.NOMES_ESPEC[e]}", "",
              f"Base: **{_ordem_marcada(ordem, ls, e, 'base', bd)}**"
              + (f" — Δλ\\*₈₀ = {_ic(rb)}, Δλ\\*₅₀ = {_ic(rb, '50')}, C supera A em {_pct(rb['frac_C_supera_80'])} "
                 f"das réplicas: {rb['leitura_80']}." if rb is not None else ""),
              (f"Estimada: **{_ordem_marcada(ordem, ls, e, 'estimada', bd)}** — Δλ\\*₈₀ = {_ic(re_)}: {re_['leitura_80']}."
               if re_ is not None else ""), "",
              "Grade de ω (mesmo destaque da base, porque ω não é calibrado pelos dados):", "",
              "| ω | Variante | Ordem | λ\\*₈₀ A | λ\\*₈₀ C | λ\\*₈₀ B | Δλ\\*₈₀ (C − A) [IC 95%] | Leitura |",
              "|---|---|---|---|---|---|---|---|"]
        for w_txt, var in (("0", "base"), ("0,38 (1 − b)", "omega_038"), ("0,5", "omega_05"), ("1", "omega_1")):
            lv = ls[(ls["especificacao"] == e) & (ls["variante"] == var)].set_index("cenario")
            rv = _boot(bd, e, var)
            L.append(f"| {w_txt} | {var} | {_ordem_marcada(ordem, ls, e, var, bd)} | "
                     + " | ".join(_fmt(lv.loc[c, "lambda_star_80"]) if c in lv.index else "—" for c in ("A", "C", "B"))
                     + f" | {_ic(rv) if rv is not None else '—'} | {rv['leitura_80'] if rv is not None else '—'} |")
        if e == "P3":
            L += ["", "θ (fração da lacuna absorvida por inflação): base θ = 0,5; θ = 0,25, o melhor ajuste da validação "
                  "2016–2019; e θ = 0, o melhor ajuste de 2020–2022, em que P3 vira uma Phillips achatada sem inércia e "
                  "serve de limite inferior para o canal fiscal. As três linhas cobrem o intervalo sustentado pelos dados.",
                  "",
                  "| θ | Variante | Ordem | λ\\*₈₀ A | λ\\*₈₀ C | λ\\*₈₀ B | Δλ\\*₈₀ (C − A) [IC 95%] | Leitura |",
                  "|---|---|---|---|---|---|---|---|"]
            for th_txt, var in (("0,5", "base"), ("0,25", "theta_025"), ("0", "theta_0")):
                lv = ls[(ls["especificacao"] == e) & (ls["variante"] == var)].set_index("cenario")
                rv = _boot(bd, e, var)
                L.append(f"| {th_txt} | {var} | {_ordem_marcada(ordem, ls, e, var, bd)} | "
                         + " | ".join(_fmt(lv.loc[c, "lambda_star_80"]) if c in lv.index else "—" for c in ("A", "C", "B"))
                         + f" | {_ic(rv) if rv is not None else '—'} | {rv['leitura_80'] if rv is not None else '—'} |")
        L += ["", "Variante base em detalhe:", "",
              "| Cenário | λ\\* det. | λ\\*₅₀ | λ\\*₈₀ | P(sucesso) máx. | Explosivas em λ = 0,5 | Intervalos de sucesso (det.) |",
              "|---|---|---|---|---|---|---|"]
        for _, r in b.iterrows():
            m = df[(df["especificacao"] == e) & (df["variante"] == "base") & (df["cenario"] == r["cenario"])]
            ex = m.iloc[(m["lambda"] - 0.5).abs().argmin()]["frac_explosiva"]
            L.append(f"| {nomes[r['cenario']]} | {_fmt(r['lambda_star_det'])} | {_fmt(r['lambda_star_50'])} | "
                     f"{_fmt(r['lambda_star_80'])} | {_pct(r['p_sucesso_max'])} | {_pct(ex)} | {_iv(r['det_intervalos'])} |")
        L.append("")
    L += ["Critérios que mais falharam (média da grade de λ; explosivas sobre o total, demais entre as não "
          "explosivas):", "", "| Especificação | Cenário | " + " | ".join(ROTULOS_CRIT.values()) + " |",
          "|---|---|" + "---|" * len(ROTULOS_CRIT)]
    for e in especs:
        for ch in cfg["cenarios"]:
            m = df[(df["especificacao"] == e) & (df["variante"] == "base") & (df["cenario"] == ch)]
            L.append(f"| {e} | {ch} | " + " | ".join(_pct(m[f"falha_{k}"].mean()) for k in ROTULOS_CRIT) + " |")

    # 2. ordenamento por r_long_neutro
    grade_rl = {float(k): v for k, v in exp.get("grade_rlong", {}).items()}
    L += ["", "## 4. Ordenamento por juro real longo neutro (r_long_neutro = 4,5; 5,5; 6,5)", "",
          "Ordem e λ\\*₈₀ (λ\\*₅₀ entre parênteses) de cada cenário em cada valor da grade; \"A ≈ C\" quando o IC de 95% "
          "de Δλ\\*₈₀ do bootstrap pareado contém zero.", "",
          "| Especificação | r_long neutro | Ordem | " + " | ".join(f"λ\\*₈₀ {c}" for c in cfg["cenarios"]) + " |",
          "|---|---|---|" + "---|" * len(cfg["cenarios"])]
    rel_rl = {}
    for e in especs:
        for rl, var in sorted(grade_rl.items()):
            rel_rl.setdefault(e, set()).add(_relacao_ac(_ordem_marcada(ordem, ls, e, var, bd)))
            l = ls[(ls["especificacao"] == e) & (ls["variante"] == var)].set_index("cenario")
            cel = [f"{_fmt(l.loc[c, 'lambda_star_80'])} ({_fmt(l.loc[c, 'lambda_star_50'])})" if c in l.index else "—"
                   for c in cfg["cenarios"]]
            L.append(f"| {e} | {_fmt(rl, 1)} | {_ordem_marcada(ordem, ls, e, var, bd)} | " + " | ".join(cel) + " |")

    muda_rl = [e for e, r in rel_rl.items() if len(r - {"="}) > 1]
    L += ["", ("**O juro neutro muda os níveis de λ\\* (todos sobem com r_long_neutro), mas não o ordenamento:** "
               "em nenhuma especificação C passa à frente de A ao longo da grade." if not muda_rl else
               f"O juro neutro inverte a relação entre A e C em {', '.join(muda_rl)}.")]

    # 3. robustez
    base_ordens = {e: _ordem_marcada(ordem, ls, e, "base", bd) for e in especs}
    L += ["", "## 5. Robustez do ordenamento por variante", "",
          f"Nas três especificações (variante base): " + "; ".join(f"{e}: {o}" for e, o in base_ordens.items())
          + ". " + frase_robustez(base_ordens),
          "", "Gráfico `12_ordenamento_variantes`. Ordem por variante (1º → 3º):", "",
          "| Variante | Descrição | " + " | ".join(especs) + " |", "|---|---|" + "---|" * len(especs)]
    for v in [v for v in exp["variantes"] if not v.startswith(("phi_025_along", "phi_05_along", "sens_"))
              and "choque" not in v]:
        L.append(f"| {v}{' (obrigatória)' if v in exp['obrigatorias'] else ''} | {DESCR_VAR.get(v, '')} | "
                 + " | ".join(_ordem_marcada(ordem, ls, e, v, bd) for e in especs) + " |")
    L += ["", "† Nenhum cenário atinge P(sucesso) ≥ 50% nesta variante: a ordem vem só do desempate pela "
          "probabilidade máxima e compara graus de fracasso, não robustez relativa. "
          "\"A ≈ C\": IC de 95% de Δλ\\*₈₀ contém zero (empate estatístico na diagonal); ⚠: mais de 20% das réplicas "
          "censuradas (λ\\* não atingido), resultado pouco confiável. Variantes de alongamento com φ > 0 na seção 8."]
    if bd is not None:
        L += ["", "Bootstrap pareado por variante (gráfico `13_bootstrap_delta`): Δλ\\*₈₀ = λ\\*₈₀(C) − λ\\*₈₀(A); "
              "negativo = C exige menos adesão.", "",
              "| Especificação | Variante | λ\\*₈₀ A | λ\\*₈₀ C | Δλ\\*₈₀ [IC 95%] | C supera A | Censura A / C | Leitura |",
              "|---|---|---|---|---|---|---|---|"]
        for r in bd.itertuples():
            L.append(f"| {r.especificacao} | {r.variante} | {_fmt(r.A_80) if r.A_80 < 1.01 else 'não atinge'} | "
                     f"{_fmt(r.C_80) if r.C_80 < 1.01 else 'não atinge'} | {_ic(r._asdict())} | "
                     f"{_pct(r.frac_C_supera_80)} | {_pct(r.censura_A_80)} / {_pct(r.censura_C_80)} | {r.leitura_80} |")
    muda = [(e, v) for e in especs for v in exp["obrigatorias"]
            if _ordem_marcada(ordem, ls, e, v, bd) not in ("—", _ordem_marcada(ordem, ls, e, "base", bd))
            and not _todos_falham(ls, e, v)]
    L += ["", "Variantes obrigatórias que alteram o ordenamento da base (excluídas as marcadas com †): "
          + ("; ".join(f"{v} em {e} ({_ordem_marcada(ordem, ls, e, v, bd)})" for e, v in muda) if muda else "nenhuma")
          + "."]
    o5 = varredura.ordenar(ls, "lambda_star_80_teto5")
    rel5 = {e: _relacao_ac(_ordem_txt(o5, e, "base")) for e in especs}
    L += ["", f"Teto de inflação em meta + {_fmt(p['criterios'].get('tolerancia_inflacao_alt', 2.0), 1)} p.p. "
          "(variante base): " + "; ".join(f"{e}: {_ordem_txt(o5, e, 'base')}" for e in especs)
          + (" (mesmo ordenamento)." if all(_ordem_txt(o5, e, 'base') == base_ordens[e] for e in especs)
             else " (o ordenamento muda com o teto).")]
    if all(r == "A" for r in rel5.values()):
        fA = df[(df["variante"] == "base") & (df["cenario"] == "A")].groupby("especificacao")["falha_divida_inclinacao"].mean()
        fC = df[(df["variante"] == "base") & (df["cenario"] == "C")].groupby("especificacao")["falha_divida_inclinacao"].mean()
        L.append("Com o teto mais folgado, A vence em todas as especificações: o critério de inflação deixa de "
                 "restringir, o de dívida passa a dominar, e C perde nele (dívida ainda subindo no fim, média da grade "
                 "de λ: " + "; ".join(f"{e}: A {_pct(fA[e])}, C {_pct(fC[e])}" for e in especs)
                 + "). Ver o diagnóstico de C abaixo.")

    dg = ctx.get("diag_c")
    if dg is not None:
        res = dg["resumo"]
        L += ["", "### Diagnóstico: dívida de C no fim do horizonte (P1 base, λ = 0,9)", "",
              f"Medianas de {dg['N']} trajetórias nos últimos 12 trimestres (gráfico `18_diagnostico_C`). δ de C chega a "
              f"zero no trimestre {dg['t_delta_zero']}; depois disso, i_C = max(7,5; Taylor).", "",
              "| Trimestre | Selic A | Taylor A | Dívida A | Selic C | Taylor C | Dívida C | C no piso de 7,5% acima da "
              "Taylor |", "|---|---|---|---|---|---|---|---|"]
        for r in dg["tabela"].itertuples():
            L.append(f"| {r.t} | {_fmt(r.i_A)} | {_fmt(r.tay_A)} | {_fmt(r.d_A, 1)} | {_fmt(r.i_C)} | {_fmt(r.tay_C)} | "
                     f"{_fmt(r.d_C, 1)} | {_pct(r.piso_acima_taylor_C)} |")
        L += ["", f"Dívida ainda subindo nos últimos 8 trimestres: A {_pct(res['subindo_A'])}, C {_pct(res['subindo_C'])}. "
              f"Entre as trajetórias de C com dívida subindo, a Selic média dos últimos 8 trimestres é "
              f"{_fmt(res['i_C_subindo'])}% contra {_fmt(res['i_C_estavel'])}% nas demais; a Taylor, "
              f"{_fmt(res['tay_C_subindo'])}% contra {_fmt(res['tay_C_estavel'])}%; o piso de 7,5% fica acima da Taylor "
              f"em {_pct(res['piso_C_subindo'])} dos trimestres finais das trajetórias que sobem.", "", dg["leitura"]]
        mb = df[(df["especificacao"] == "P1") & (df["variante"] == "base")]
        lams = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        pv = mb.pivot(index="lambda", columns="cenario", values="falha_divida_inclinacao")
        L += ["", "Fração das trajetórias com dívida ainda subindo no fim, por λ (P1 base, N = 1.000):", "",
              "| λ | " + " | ".join(_fmt(l, 1) for l in lams) + " | média da grade |",
              "|---|" + "---|" * (len(lams) + 1)]
        for ch in ("A", "C"):
            L.append(f"| {ch} | " + " | ".join(_pct(pv.loc[pv.index[np.argmin(np.abs(pv.index - l))], ch]) for l in lams)
                     + f" | {_pct(pv[ch].mean())} |")
        L.append(f"Os {_pct(pv['C'].mean())} de C (contra {_pct(pv['A'].mean())} de A) são a média sobre toda a grade de λ; "
                 "a diferença se concentra nos λ em que a coluna de C excede a de A, e não no fim do horizonte com "
                 "adesão alta.")

    comp, comp_area = ctx.get("comp"), ctx.get("comp_area")
    if comp is not None and len(comp):
        L += secao_testes_sem_piso(comp, comp_area, especs, ctx.get("comp_bil"), ctx.get("comp_area_bil"))
    if ctx.get("divida_res"):
        L += secao_divida_liquida(ctx["divida_res"], ctx["ls"], especs)
    if ctx.get("choque"):
        L += secao_parada_subita(ctx["choque"])
    if ctx.get("sens_reservas"):
        L += secao_sens_reservas(ctx["sens_reservas"])

    # 4. superfície
    L += ["", "## 6. Área de sucesso na superfície λ_π × λ_fiscal", ""]
    if ctx.get("areas") is not None:
        ar = ctx["areas"]
        L += ["Fração do quadrado [0,1]² com P(sucesso) ≥ 80% (grade 21 × 21, N = "
              f"{exp['superficie']['N']} por ponto). Maior área = mais robusto às duas formas de desconfiança.", "",
              "| Variante | Cenário | " + " | ".join(especs) + " |", "|---|---|" + "---|" * len(especs)]
        for v in exp["superficie"]["variantes"]:
            for ch in cfg["cenarios"]:
                vals = [ar[(ar["especificacao"] == e) & (ar["variante"] == v) & (ar["cenario"] == ch)]["area_sucesso"]
                        for e in especs]
                L.append(f"| {v} | {nomes[ch]} | " + " | ".join(_pct(x.iloc[0]) if len(x) else "—" for x in vals) + " |")
        L += ["", "Gráficos " + ", ".join(f"`10_superficie_{v}`" for v in exp["superficie"]["variantes"]) + "."]
        if ba is not None and len(ba):
            L += ["", "Bootstrap pareado da área (ΔÁrea = Área(A) − Área(C)):", "",
                  "| Especificação | Variante | Área A | Área C | ΔÁrea [IC 95%] | C supera A | Leitura |",
                  "|---|---|---|---|---|---|---|"]
            for r in ba.itertuples():
                L.append(f"| {r.especificacao} | {r.variante} | {_pct(r.area_A)} | {_pct(r.area_C)} | "
                         f"{_fmt(100 * r.delta_area, 1)} p.p. [{_fmt(100 * r.ic_lo, 1)}; {_fmt(100 * r.ic_hi, 1)}] | "
                         f"{_pct(r.frac_C_supera)} | {r.leitura} |")
    else:
        L.append("Superfície não calculada nesta rodada (use `--superficie`).")

    # 5. validação
    val = ctx["val_df"]
    ref = validacao.especificacao_referencia(val)
    L += ["", "## 7. Validação e especificação de referência", "",
          "Selic, primário e depreciação cambial observados; em P3, primário anunciado = mediana do Focus em cada "
          "data. Erro = RMSE/desvio-padrão de inflação + NTN-B 10 anos.", "",
          "| Especificação | Episódio | λ de melhor ajuste | θ (P3) | Erro mín. | Erro λ = 0 | Erro λ = 1 | "
          "Erro P3 com θ = 0,5 | Pico obs. / sim. | Reproduz o pico de 2021–22? |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in val.iterrows():
        pico = (f"{_fmt(r['pico_observado'], 1)} / {_fmt(r['pico_simulado'], 1)}" if np.isfinite(r["pico_observado"])
                else "—")
        rep = {True: "sim", False: "não", None: "—"}.get(r["reproduz_pico"], "—")
        L.append(f"| {r['especificacao']} | {r['episodio']} | {_fmt(r['lambda_melhor_ajuste'])} | "
                 f"{_fmt(r['theta']) if pd.notna(r['theta']) else '—'} | {_fmt(r['erro_normalizado_min'])} | "
                 f"{_fmt(r['erro_lambda_0'])} | {_fmt(r['erro_lambda_1'])} | "
                 f"{_fmt(r['erro_theta_fixo_05']) if pd.notna(r['erro_theta_fixo_05']) else '—'} | {pico} | {rep} |")
    soma = val.groupby("especificacao")["erro_normalizado_min"].sum()
    picos = val.dropna(subset=["reproduz_pico"]).set_index("especificacao")["reproduz_pico"]
    L += ["", f"Erro combinado: " + "; ".join(f"{e} = {_fmt(v)}" for e, v in soma.items())
          + f". **Especificação de referência: {graficos.NOMES_ESPEC[ref]}** (ordem: {base_ordens.get(ref, '—')})."]
    th_pico = val.loc[(val["especificacao"] == "P3") & val["reproduz_pico"].notna(), "theta"]
    if picos.get("P3") and not picos.get("P1") and len(th_pico) and th_pico.iloc[0] == 0:
        L.append("P3 reproduz o pico de 2021–22 e P1 não, mas com θ = 0, isto é, sem o canal fiscal: a reprodução "
                 "vem da ausência de inércia própria (a inflação segue as expectativas), não da lacuna fiscal. "
                 "Não é evidência a favor da leitura fiscal da inflação recente.")
    elif picos.get("P3") and not picos.get("P1"):
        L.append("P3 reproduz o pico de 2021–22 e P1 não, com θ > 0: evidência a favor da leitura fiscal da "
                 "inflação recente.")
    elif not picos.any():
        L.append("Nenhuma especificação reproduz o pico de 2021–22: o pico tem componente de oferta e commodities "
                 "não modelado.")
    else:
        L.append("Reproduzem o pico: " + ", ".join(e for e, v in picos.items() if v) + ".")
    if "P3" in soma:
        L.append("Sobreajuste: P3 tem θ como parâmetro livre a mais; ver a coluna de erro com θ fixo em 0,5.")
        th = val.loc[val["especificacao"] == "P3", "theta"]
        if (th == 0).any():
            L.append("Em " + ("todos os episódios" if (th == 0).all() else "parte dos episódios")
                     + " o melhor ajuste de P3 tem θ = 0: nos dados brasileiros, o canal fiscal não melhora o ajuste e "
                       "P3 se reduz a uma Phillips achatada sem inércia.")

    # 7. alongamento
    if al is not None:
        dl = al["lft"]
        L += ["", "## 8. Alongamento da dívida", "",
              f"Decomposição em t0 (SGS, composição da DPMFi com operações de mercado aberto): LFT + compromissadas "
              f"= {_pct(dl['lft_total'])}, das quais LFT do Tesouro = {_pct(dl['lft_tesouro'])} e compromissadas do BCB = "
              f"{_pct(dl['compromissadas'])} (SGS 10632)."
              + (f" Conferência no estoque do Tesouro ({dl['tesouro_mes']}): LFT = {_pct(dl['tesouro_lft_mercado_share'])} "
                 "da DPMFi em mercado." if "tesouro_lft_mercado_share" in dl else ""),
              f"O alongamento reduz só a LFT do Tesouro; a meta de 40% para o total é alcançável (o piso é a fatia de "
              f"compromissadas, {_pct(dl['compromissadas'])}). Fatia mínima de LFT atingida (P3, λ = 0,9, cenário A): "
              f"{_pct(al['custo'].query('especificacao == \"P3\" and cenario == \"A\" and `lambda` == 0.9')['w_lft_min_along'].iloc[0])}.",
              "", "| Especificação | φ | Alongamento | Cenário | P(sucesso) máx. | λ\\*₅₀ | λ\\*₈₀ | Explosiva | Dívida ↑ | "
              "Dívida > tol. | Inflação > teto |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in al["tabela"].itertuples():
            L.append(f"| {r.especificacao} | {_fmt(r.phi)} | {r.alongamento}{' †' if r.todos_falham else ''} | {r.cenario} | "
                     f"{_pct(r.p_sucesso_max)} | {_fmt(r.lambda_star_50)} | {_fmt(r.lambda_star_80)} | "
                     f"{_pct(r.falha_inflacao_explosiva)} | {_pct(r.falha_divida_inclinacao)} | "
                     f"{_pct(r.falha_divida_nivel)} | {_pct(r.falha_inflacao)} |")
        er = al["erosao"]
        L += ["", "Erosão da dívida pela inflação (P3, trajetória determinística, soma em 10 anos, p.p. do PIB): "
              "total = redução do valor real da dívida não indexada (LFT, prefixados, cambial) pela inflação; não "
              "antecipada = parte acima da inflação embutida no custo de cada título.", "",
              "| φ | Alongamento | Cenário | λ | Erosão total | Não antecipada | Fração não antecipada | Dívida final | "
              "Inflação final |", "|---|---|---|---|---|---|---|---|---|"]
        for r in er.itertuples():
            frac = _pct(r.fracao_nao_antecipada) if r.erosao_total_pp > 0 else "— (deflação)"
            fim = "rompeu" if r.ruptura >= 0 else None
            L.append(f"| {_fmt(r.phi)} | {r.alongamento} | {r.cenario} | {_fmt(r._4, 1)} | {_fmt(r.erosao_total_pp, 1)} | "
                     f"{_fmt(r.erosao_nao_antecipada_pp, 1)} | {frac} | {fim or _fmt(r.d_final, 1)} | "
                     f"{fim or _fmt(r.pi_media_final, 1)} |")
        L += ["", "Erosão negativa: a inflação ficou abaixo da embutida no custo dos títulos (deflação ou desinflação "
              "não antecipada), o que aumenta a dívida real; nesses casos a fração não é calculada."]
        cu = al["custo"]
        L += ["", "Custo do alongamento com φ = 0 (a lacuna já está precificada: só custo, sem benefício): custo real "
              "efetivo médio da dívida (i_ef − π, média de 10 anos) e dívida final, trajetória determinística.", "",
              "| Especificação | Cenário | λ | Custo real sem → com | Δ custo (p.p. a.a.) | Dívida final sem → com | "
              "Duração final sem → com (anos) |", "|---|---|---|---|---|---|---|"]
        rv = lambda x, c=1: "rompeu" if not np.isfinite(x) else _fmt(x, c)  # noqa: E731
        for r in cu.itertuples():
            L.append(f"| {r.especificacao} | {r.cenario} | {_fmt(r._3, 1)} | {_fmt(r.custo_real_sem)} → "
                     f"{_fmt(r.custo_real_along)} | {_fmt(r.delta_custo_pp)} | {rv(r.d_final_sem)} → "
                     f"{rv(r.d_final_along)} | {rv(r.duracao_final_sem)} → {rv(r.duracao_final_along)} |")
        L += ["", "\"rompeu\": a trajetória determinística passou de 50% de inflação e foi encerrada; o custo real é a "
              "média até a ruptura."]
        L += [""] + al["respostas"] + ["", "Gráfico `14_alongamento`."]

    # 8. premissas
    datas = ini["datas_observacao"]
    L += ["", "## 9. Premissas e limitações", "", "### Condições iniciais", "",
          "| Variável | Valor | Data real da última observação |", "|---|---|---|"]
    rot_ini = {"i0": "Meta Selic (% a.a.)", "pi0": "IPCA 12m (%)", "pi_e0": "Focus IPCA 12m à frente (%)",
               "h0": "Hiato do produto (HP, %)", "g_potencial": "Crescimento potencial (% a.a.)",
               "d_gross0": "Dívida bruta do governo geral (% PIB)", "d_net0": "DLSP (% PIB)",
               "R0": "Reservas (US$ bi)", "E0": "Câmbio (R$/US$, média do trimestre)",
               "s0": "Primário do setor público, 12m (% PIB)", "r_long0": "NTN-B ~10 anos (% a.a.)",
               "r_long5_0": "NTN-B ~5 anos (% a.a.)"}
    for k, rot in rot_ini.items():
        if ini.get(k) is not None:
            L.append(f"| {rot} | {_fmt(ini[k])} | {datas.get(k, '')} |")
    if ini.get("focus_primario"):
        anos = sorted(ini["focus_primario"])[:5]
        L += ["", f"Focus na pesquisa de {ini.get('focus_data_pesquisa', '?')}: primário "
              + ", ".join(f"{a}: {_fmt(ini['focus_primario'][a])}" for a in anos)
              + "; DLSP " + ", ".join(f"{a}: {_fmt(ini['focus_dlsp'].get(a, np.nan), 1)}" for a in anos) + " (% PIB)."]
    L += ["", "### Juros, prêmio e term premium", "",
          f"- Juro real curto neutro {_fmt(p['r_neutro_base'], 1)}% e juro real longo neutro "
          f"{_fmt(p['r_long_neutro'], 1)}% (calibrado diretamente; grade 4,5 / 5,5 / 6,5); tp_lp derivado = "
          f"{_fmt(p['tp_lp'])} p.p. O prêmio médio p0 = {_fmt(p['p0'], 1)} não entra no nível de nenhum dos dois juros.",
          f"- Desvios do prêmio: fração ω = {_fmt(p['omega'], 1)} pela Taylor e 1 − ω pelo juro longo "
          "(variantes ω = 0,5 e 1).",
          f"- Term premium inicial (fecha a identidade do juro longo em t0): {_fmt(p['tp0'])} p.p.; converge para "
          f"tp_lp com τ = {p['tau_tp']:g} trimestres.",
          f"- Checagem (ANBIMA indisponível sem credenciais): inclinação NTN-B 10a − 5a em t0 = "
          f"{_fmt(ini['r_long0'] - ini['r_long5_0'])} p.p. (Tesouro Direto).",
          f"- Com meta de {_fmt(p['pi_meta'], 1)}%, a Selic de 7,5% é neutra só com r_neutro = 4,5 (variante neutro_45).",
          f"- Duração da dívida ({ini.get('duracao_metodo', 'prazo médio')}): NTN-B "
          f"{_fmt(p['dur_ipca'], 1)} anos (prazo médio do estoque {_fmt(ini.get('prazo_ipca_estoque_anos', np.nan), 1)}); "
          f"prefixados {_fmt(p['dur_pre'], 1)} anos (prazo {_fmt(ini.get('prazo_pre_estoque_anos', np.nan), 1)}); "
          f"LFT 0,25 ano. Estoque de {ini.get('duracao_mes_estoque', '?')}.",
          f"- Restrição de rolagem: LFT com juro real abaixo de {_fmt(p['r_min_rolagem'], 1)}% migra para NTN-B "
          f"(giro {_fmt(100 * p['giro_lft'], 1)}%/trimestre, banda {_fmt(p['banda_rolagem'], 1)} p.p.)."]
    if ctx.get("repressao"):
        rep = ctx["repressao"]
        lams = sorted({l for (_, _, l) in rep})
        L += ["", "Repressão financeira: fração do tempo com juro real da LFT abaixo de zero (trajetória "
              "determinística):", "", "| Especificação | Cenário | " + " | ".join(f"λ = {_fmt(l, 1)}" for l in lams) + " |",
              "|---|---|" + "---|" * len(lams)]
        for e in especs:
            for ch in cfg["cenarios"]:
                L.append(f"| {e} | {ch} | " + " | ".join(_pct(rep[(e, ch, l)]) for l in lams) + " |")
    L += ["", "### Parâmetros-chave", "", "| Parâmetro | Valor | Fonte |", "|---|---|---|"]
    for k in ("a1", "a2", "b1", "b2", "b3", "b2_p2", "b2_p3", "theta", "phi", "delta_min", "p2", "p2_p3", "p3",
              "kappa", "mu", "r_neutro_base", "r_long_neutro", "tp_lp", "omega", "tau_tp", "r_min_rolagem",
              "R_min"):
        L.append(f"| {k} | {f'{p[k]:.3g}'.replace('.', ',')} | {p['fontes'].get(k, 'padrão')} |")
    pac = cfg["pacote_fiscal"]
    cC = cfg["cenarios"]["C"]
    ef_res = reservas_choque.vendas_efetivas(p, cfg)["A_res100"]  # venda de C limitada pelo piso R_min
    L += ["", "### Cenários", "",
          f"- Pacote fiscal (A e C): {_fmt(sum(m['impacto_final'] for m in pac), 1)}% do PIB ao fim das rampas.",
          f"- B e C: Selic exógena até {_fmt(cC['i_alvo'], 1)}% em {cC['T_corte']} trimestres; venda programada de "
          f"até US$ {sum(cC['venda_reservas']):.0f} bi em reservas (efetiva: cerca de US$ {ef_res:.0f} bi, limitada "
          f"pelo piso de US$ {p['R_min']:.0f} bi). C: tolerância δ0 = {_fmt(cC.get('delta0', 0), 1)} p.p. que cai a "
          f"zero em {cC.get('T_delta', '—')} trimestres após o corte.",
          f"- Sucesso: dívida com inclinação ≤ 0 nos últimos {p['criterios']['janela_final']} trimestres e final ≤ "
          f"inicial + {p['criterios']['tolerancia_divida']:g} p.p.; inflação média final ≤ "
          f"{_fmt(p['pi_meta'] + p['criterios']['tolerancia_inflacao'], 1)}%; inflação ≤ "
          f"{p['criterios']['teto_explosivo']:g}% em todos os trimestres; reservas ≥ US$ {p['R_min']:.0f} bi. "
          f"Trajetórias com inflação acima de {p['pi_explosao']:g}% são encerradas."]
    if ctx["erros"]:
        L += ["", "### Problemas na coleta", ""] + [f"- {e}" for e in ctx["erros"]]
    L += ["", "### Limitações", "",
          "- λ_π e λ_fiscal são exógenos e constantes. Extensão sugerida: credibilidade adaptativa, "
          "λ[t] = λ[t−1] + ν (sucesso_parcial[t] − 0,5), separadamente para cada dimensão.",
          "- P3 é uma versão reduzida da FTPL: não resolve um equilíbrio com expectativas racionais; a lacuna é "
          "absorvida por inflação na proporção θ, e θ é calibrado, não derivado.",
          "- φ = 0 (a lacuna inicial já está precificada) é uma hipótese forte; com φ > 0 todos os cenários começam "
          "com pressão inflacionária adicional (variantes phi_025 e phi_05 na seção 5).",
          "- A restrição de rolagem é uma regra de comportamento, não um modelo de demanda por títulos.",
          "- O modelo continua semiestrutural e sem choques de oferta e de commodities.",
          "- Os resultados de P1 e P2 dependem de b1 e b3; os de P3, de θ, Δ_min e da duração da dívida "
          "(gráficos `6_sensibilidade_*`).",
          "- O piso de reservas (R_min = US$ 300 bi) corresponde a 100% da métrica ARA do FMI; a venda programada de "
          "até US$ 100 bi fica limitada a cerca de US$ 76 bi.",
          "- Duração de Macaulay calculada com taxas do Tesouro Direto do vértice mais próximo (não ANBIMA) e com "
          "o estoque total da DPMFi (mercado e carteira do BC).",
          "- O VP de P3 desconta o horizonte explícito ao juro longo corrente e o valor terminal ao juro longo neutro.",
          "- Inflação fiscal (P3): a lacuna entra como fração da dívida líquida e é medida contra a trajetória "
          "anunciada (com λ = 1 e sem choques, não há inflação fiscal); o valor terminal segue a fórmula literal "
          "s/max(r − g, Δ_min), e a perpetuidade 100·s/(r − g) é a variante `vt_perpetuidade` (ver README).",
          "- O critério principal de inflação é avaliado com teto e com banda simétrica; trajetórias deflacionárias "
          "só são reprovadas pela banda.",
          "- O critério de sucesso olha o fim do horizonte (últimos 8 trimestres) e não capta crises que se dissipam "
          "antes da janela final. O custo de cauda depende das métricas de trajetória (picos de dívida e de inflação, "
          "trimestres com inflação acima do teto) e dos choques persistente e no ano 7, no relatório de reservas.",
          "- O bootstrap mede apenas a incerteza do Monte Carlo, não a dos parâmetros. A incerteza de b3 entra pelas "
          "variantes estimada_b3_baixo e estimada_b3_alto; ω não é identificado nos dados, e sua incerteza entra pela "
          "grade ω ∈ {0; 0,38; 0,5; 1} (0,38 = 1 − b da verificação cruzada).",
          "- Estimação: o EMBI+ termina em jul/2024 (ω estimado até essa data); o DXY foi substituído pelo dólar amplo "
          "do Fed (DTWEXBGS, encadeado com DTWEXB antes de 2006); o IC-Br entra em US$ porque a versão em reais contém "
          "o próprio câmbio; hiato e desvio do Focus entram defasados porque reagem ao câmbio no próprio mês.",
          "- Alongamento: aplicado ao fim de cada trimestre, depois da emissão; a restrição de rolagem atua no "
          "trimestre seguinte sobre a LFT restante, de modo que as duas nunca movem o mesmo estoque. A emissão "
          "primária continua com a composição inicial e o teto devolve o excedente ao fim do trimestre.", ""]
    # síntese interpretativa, revisada à mão (a síntese numérica automática fica em ctx["sintese"])
    L += ["## 10. Síntese", ""] + SINTESE + [""]
    arq = saida / "relatorio.md"
    arq.write_text(rotular_secao5("\n".join(L), ef_res), encoding="utf-8")
    return arq


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--experimentos", default="config/experimentos.yaml")
    ap.add_argument("--calibracao", default="config/calibracao.yaml")
    ap.add_argument("--cenarios", default="config/cenarios.yaml")
    ap.add_argument("--mc", type=int, default=1000, help="simulações por (especificação, variante, cenário, λ)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--especificacoes", default="P1,P2,P3")
    ap.add_argument("--superficie", action="store_true", help="calcula a superfície λ_π × λ_fiscal")
    ap.add_argument("--monetizacao", action="store_true", help="LFT não rolada vira expansão monetária")
    ap.add_argument("--atualizar-dados", action="store_true")
    ap.add_argument("--offline", action="store_true", help="com --atualizar-dados, usa só data/raw")
    ap.add_argument("--retomar", action="store_true", help="reaproveita parquets parciais de rodadas anteriores")
    ap.add_argument("--sem-sensibilidade", action="store_true")
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--saida", default="outputs/v2_2")
    ap.add_argument("--boot-r", type=int, default=1000, help="réplicas do bootstrap pareado")
    ap.add_argument("--boot-seed", type=int, default=2026, help="semente do bootstrap (distinta da simulação)")
    ap.add_argument("--est-b", type=int, default=300, help="réplicas do bootstrap em blocos do ERPT")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    saida = RAIZ / args.saida
    saida.mkdir(parents=True, exist_ok=True)
    especs = [e.strip() for e in args.especificacoes.split(",")]

    calib = RAIZ / args.calibracao
    if args.atualizar_dados or "iniciais" not in (yaml.safe_load(calib.read_text(encoding="utf-8")) or {}):
        log.info("coletando dados")
        erros = dados.atualizar(calib, offline=args.offline)["erros_coleta"]
    else:
        erros = yaml.safe_load(calib.read_text(encoding="utf-8")).get("erros_coleta", [])
    p = modelo.carregar_calibracao(calib)
    if args.monetizacao:
        p["monetizacao"] = True
    cfg = yaml.safe_load((RAIZ / args.cenarios).read_text(encoding="utf-8"))
    exp = yaml.safe_load((RAIZ / args.experimentos).read_text(encoding="utf-8"))
    info = {k: {"nome": v["nome"], "cor": v["cor"]} for k, v in cfg["cenarios"].items()}
    grade = varredura.grade_lambda(0.01)
    choques = varredura.sortear_choques(p, args.mc, cfg["horizonte"], args.seed)
    t0 = time.time()
    p["b3_v1_trimestral"] = (yaml.safe_load(calib.read_text(encoding="utf-8")).get("estimados", {})
                             .get("b3", {}).get("estimado"))

    # Tarefa 3: estimação de b3 e ω (gera as variantes estimadas usadas nas demais tarefas)
    log.info("estimação de b3 e ω")
    est = estimacao.rodar(p, cfg, offline=args.offline, B=args.est_b)
    est["b3"].to_csv(saida / "estimacao_b3.csv", index=False, float_format="%.5f")
    est["calibracao_b3"].to_csv(saida / "calibracao_b3.csv", index=False, float_format="%.5f")
    om = est["omega"].copy()
    om["classificacao"] = om["classe"].map(estimacao.CLASSES_OMEGA)
    om = pd.concat([om, pd.DataFrame([{"amostra": "completa", "metodo": "canal do juro longo (b)", **est["canal_longo"],
                                       **{f"leitura_{k}": v for k, v in est["leitura_canal"].items()}}])])
    om.to_csv(saida / "estimacao_omega.csv", index=False, float_format="%.5f")
    (saida / "variantes_estimadas.yaml").write_text(yaml.safe_dump(est["variantes"], allow_unicode=True), encoding="utf-8")
    graficos.erpt_lp(est["b3"], saida)
    graficos.taylor_premio(est["omega"], saida)
    exp["variantes"].update(est["variantes"])
    # ω implícito na verificação cruzada pelo juro longo (b ≈ 1 − ω), com a mesma calibração da base
    exp["variantes"]["omega_038"] = {"omega": round(est["leitura_canal"]["omega_implicito"], 2)}
    # estresse do C_sem_piso com o repasse no limite superior do IC (comparado com A sob o mesmo b3)
    exp["variantes"]["C_sem_piso_b3_alto"] = {**est["variantes"]["estimada_b3_alto"], "cenario": "C",
                                              "politica_monetaria": "condicionada_sem_piso", "ref": "estimada_b3_alto"}
    refs = {v: d["ref"] for v, d in exp["variantes"].items() if isinstance(d, dict) and d.get("ref")}

    log.info("matriz de experimentos: %s × %d variantes (N=%d)", especs, len(exp["variantes"]), args.mc)
    df = varredura.rodar_matriz(p, cfg, exp, especs, grade, choques, saida / "parciais", args.retomar, args.n_jobs)
    df.to_parquet(saida / "resultados_lambda.parquet", index=False)
    ls = varredura.tabela_lambda_star(df)
    ls.to_csv(saida / "lambda_star.csv", index=False, float_format="%.4f")
    ordem = varredura.ordenar(ls, refs=refs)
    ordem.to_csv(saida / "ordenamento.csv", index=False)
    ordem_bil = varredura.ordenar(ls, refs=refs, sufixo="_bil")
    ordem_bil.to_csv(saida / "ordenamento_banda.csv", index=False)
    ordens_lim = {"70": varredura.ordenar(ls, "lambda_star_70_bil", refs, "_bil"),
                  "50": varredura.ordenar(ls, "lambda_star_50_bil", refs, "_bil")}
    log.info("matriz pronta em %.0f s", time.time() - t0)

    log.info("gráficos por especificação")
    log.info("checagem de consistência")
    cons = consistencia.tabela(p, cfg)
    cons.to_csv(saida / "consistencia.csv", index=False, float_format="%.4f")
    port = consistencia.portao(p, cfg)
    decs_pi, repressao = {}, {}
    for e in especs:
        pe = modelo.preparar({**copy.deepcopy(p), "especificacao": e})
        cens = varredura.preparar_cenarios(pe, cfg)
        m = df[(df["especificacao"] == e) & (df["variante"] == "base")]
        l = ls[(ls["especificacao"] == e) & (ls["variante"] == "base")]
        graficos.prob_sucesso(m, l, info, saida, e, f" ({e})")
        graficos.divida_final(m, info, pe, saida, e)
        graficos.inflacao_final(m, info, pe, saida, e)
        graficos.barras_lambda_star(l, info, saida, e)
        graficos.leques(varredura.leques(pe, cens, choques), info, saida, e)
        dec = varredura.decomposicao_divida(pe, cens, 0.5)
        dec.assign(especificacao=e).to_csv(saida / f"decomposicao_divida_{e}.csv", index=False, float_format="%.4f")
        graficos.decomposicao(dec, info, saida, e)
        decs_pi[e] = varredura.decomposicao_inflacao(pe, cens, 0.5)
        for ch, c in cens.items():
            lams = np.array([0.3, 0.5, 0.9])
            tr = modelo.simular(pe, c["cen"], lams, plano=c["plano"], guardar=("r_real_lft",))
            for k, lam in enumerate(lams):
                r = tr["r_real_lft"][k, 1:]
                r = r[np.isfinite(r)]
                repressao[(e, ch, float(lam))] = float((r < 0).mean()) if r.size else np.nan
    pd.concat([d.assign(especificacao=e) for e, d in decs_pi.items()]).to_csv(
        saida / "decomposicao_inflacao.csv", index=False, float_format="%.4f")
    graficos.prob_por_especificacao(df, ls, info, saida)
    for var in ("omega_05", "omega_1", "omega_038"):
        graficos.prob_por_especificacao(df, ls, info, saida, variante=var, nome=f"8_prob_sucesso_especificacoes_{var}")
    graficos.fronteira(df, info, saida)
    graficos.decomposicao_inflacao(decs_pi, info, saida)
    graficos.ordenamento(ordem, info, saida, [v for v in exp["variantes"] if not v.startswith("sens_")
                                              and "choque" not in v])

    if not args.sem_sensibilidade:
        log.info("sensibilidade")
        sens = varredura.sensibilidade(p, cfg, exp, especs, choques, args.n_jobs)
        linhas = []
        for e, por_param in sens.items():
            graficos.mapas_sensibilidade(por_param, info, saida, e, ROTULOS_SENS)
            for nome, s in por_param.items():
                for k, v in enumerate(s["valores"]):
                    for ch in cfg["cenarios"]:
                        pr = s[ch][k]
                        linhas.append({"especificacao": e, "parametro": nome, "valor": v, "cenario": ch,
                                       "lambda_star_80": s["grade"][np.argmax(pr >= 0.8)] if (pr >= 0.8).any()
                                       else np.nan})
        pd.DataFrame(linhas).to_csv(saida / "sensibilidade_lambda_star_80.csv", index=False, float_format="%.4f")

    areas, sup_trajs, comp_area, comp_area_bil, areas_bil, boot_a_bil = None, {}, None, None, None, None
    if args.superficie:
        log.info("superfície λ_π × λ_fiscal")
        sup, sup_trajs = varredura.superficie(p, cfg, exp, especs, choques, args.n_jobs)
        sup.to_parquet(saida / "superficie.parquet", index=False)
        areas = varredura.areas(sup)
        areas.to_csv(saida / "area_sucesso.csv", index=False, float_format="%.4f")
        areas_bil = varredura.areas(sup, col="p_sucesso_bil")
        areas_bil.to_csv(saida / "area_sucesso_banda.csv", index=False, float_format="%.4f")
        for v in exp["superficie"]["variantes"]:
            graficos.superficie(sup, areas, info, saida, v)

    # Tarefa 2: alongamento
    log.info("alongamento da dívida")
    along = {"lft": analises.decomposicao_lft_t0(p), "tabela": analises.tabela_alongamento(df, ls),
             "erosao": analises.erosao(p, cfg), "custo": analises.custo(p, cfg)}
    along["tabela"].to_csv(saida / "alongamento.csv", index=False, float_format="%.4f")
    along["erosao"].to_csv(saida / "alongamento_erosao.csv", index=False, float_format="%.4f")
    along["custo"].to_csv(saida / "alongamento_custo.csv", index=False, float_format="%.4f")
    graficos.alongamento(df, info, saida, [("phi_025", "Sem alongamento (φ = 0,25)"),
                                           ("phi_025_along_20", "Com along_20 (φ = 0,25)")])
    along["respostas"] = respostas_alongamento(along)

    log.info("diagnóstico da dívida de C")
    diag_c = analises.diagnostico_c(p, cfg, choques)
    diag_c["tabela"].to_csv(saida / "diagnostico_C.csv", index=False, float_format="%.4f")
    graficos.diagnostico_c(diag_c, info, saida)

    # Tarefa 1: bootstrap pareado (todas as variantes, incluindo as novas)
    log.info("bootstrap pareado (R=%d)", args.boot_r)
    trajs = analises.montar_diagonal(saida / "parciais", saida, especs, list(exp["variantes"]), list(cfg["cenarios"]))
    boot_d = bootstrap.rodar_diagonal(trajs, args.boot_r, args.boot_seed, refs)
    pares = []
    for e in especs:
        pares += [
            {"rotulo": "1. A_reservas × C_sem_piso", "especificacao": e, "ref": ("A_reservas", "A"), "alt": ("C_sem_piso", "C")},
            {"rotulo": "1. Valor das reservas em A (A × A_reservas)", "especificacao": e, "ref": ("base", "A"),
             "alt": ("A_reservas", "A")},
            {"rotulo": "1. A_reservas × C base", "especificacao": e, "ref": ("A_reservas", "A"), "alt": ("base", "C")},
            {"rotulo": "2. Piso no fim (C base × C_piso_corte)", "especificacao": e, "ref": ("base", "C"),
             "alt": ("C_piso_corte", "C")},
            {"rotulo": "2. Teto no corte (C_piso_corte × C_sem_piso)", "especificacao": e, "ref": ("C_piso_corte", "C"),
             "alt": ("C_sem_piso", "C")},
            {"rotulo": "2. A × C_piso_corte", "especificacao": e, "ref": ("base", "A"), "alt": ("C_piso_corte", "C")},
            {"rotulo": "4. Estresse b1 = 0,82: A × C_sem_piso", "especificacao": e, "ref": ("inercia_alta", "A"),
             "alt": ("C_sem_piso_inercia", "C")},
            {"rotulo": "4. Estresse b3 alto: A × C_sem_piso", "especificacao": e, "ref": ("estimada_b3_alto", "A"),
             "alt": ("C_sem_piso_b3_alto", "C")},
        ]
    comp = bootstrap.comparar(trajs, pares, args.boot_r, args.boot_seed)
    comp.to_csv(saida / "comparacoes_cruzadas.csv", index=False, float_format="%.4f")
    boot_d_bil = bootstrap.rodar_diagonal(trajs, args.boot_r, args.boot_seed, refs, chave="ok_bil")
    boot_d_bil.to_csv(saida / "bootstrap_diagonal_banda.csv", index=False, float_format="%.4f")
    comp_bil = bootstrap.comparar(trajs, pares, args.boot_r, args.boot_seed, chave="ok_bil")
    comp_bil.to_csv(saida / "comparacoes_cruzadas_banda.csv", index=False, float_format="%.4f")
    choque = {}
    for crit, chave in (("teto", "ok"), ("banda", "ok_bil")):
        pc, pdid = [], []
        for e in especs:
            for ano in (2, 3):
                sem = {"A": ("base", "A"), "A_reservas": ("A_reservas", "A"), "C_sem_piso": ("C_sem_piso", "C")}
                com = {"A": (f"A_choque{ano}", "A"), "A_reservas": (f"A_reservas_choque{ano}", "A"),
                       "C_sem_piso": (f"C_sem_piso_choque{ano}", "C")}
                for k in sem:
                    pc.append({"rotulo": f"ano {ano}: custo do choque para {k}", "especificacao": e,
                               "ref": sem[k], "alt": com[k]})
                pc += [{"rotulo": f"ano {ano}: A × A_reservas sob choque", "especificacao": e, "ref": com["A"],
                        "alt": com["A_reservas"]},
                       {"rotulo": f"ano {ano}: A × C_sem_piso sob choque", "especificacao": e, "ref": com["A"],
                        "alt": com["C_sem_piso"]},
                       {"rotulo": f"ano {ano}: A_reservas × C_sem_piso sob choque", "especificacao": e,
                        "ref": com["A_reservas"], "alt": com["C_sem_piso"]}]
                for k in ("A_reservas", "C_sem_piso"):
                    pdid.append({"rotulo": f"ano {ano}: custo do choque, {k} − A", "especificacao": e,
                                 "a": (sem["A"], com["A"]), "b": (sem[k], com[k])})
        choque[crit] = (bootstrap.comparar(trajs, pc, args.boot_r, args.boot_seed, chave=chave),
                        bootstrap.comparar_did(trajs, pdid, args.boot_r, args.boot_seed, chave=chave))
        choque[crit][0].to_csv(saida / f"parada_subita_{crit}.csv", index=False, float_format="%.4f")
        choque[crit][1].to_csv(saida / f"parada_subita_custo_cauda_{crit}.csv", index=False, float_format="%.4f")
    # dívida bruta × líquida para A, A_reservas e C_sem_piso, nas duas versões do critério de inflação
    divida_res = {}
    trio = {"A": ("base", "A"), "A_reservas": ("A_reservas", "A"), "C_sem_piso": ("C_sem_piso", "C")}
    for suf in ("", "_bil", "_liq", "_liq_bil"):
        pt = [{"rotulo": f"{a} × {b}", "especificacao": e, "ref": trio[a], "alt": trio[b]} for e in especs
              for a, b in (("A", "A_reservas"), ("A", "C_sem_piso"), ("A_reservas", "C_sem_piso"))]
        divida_res[suf] = bootstrap.comparar(trajs, pt, args.boot_r, args.boot_seed, chave=f"ok{suf}")
        divida_res[suf].assign(metrica=suf or "bruta_teto").to_csv(
            saida / f"divida_bruta_liquida{suf or '_bruta_teto'}.csv", index=False, float_format="%.4f")
    sens_res = {}
    sens_vars = sorted({v.replace("sens_A_reservas_", "") for v in exp["variantes"] if v.startswith("sens_A_reservas_")})
    for crit, chave in (("teto", "ok"), ("banda", "ok_bil")):
        ps = []
        for e in especs:
            for s in sens_vars:
                refA = (f"sens_A_{s}", "A") if f"sens_A_{s}" in exp["variantes"] else ("base", "A")
                ps += [{"rotulo": f"{s}: A × A_reservas", "especificacao": e, "ref": refA,
                        "alt": (f"sens_A_reservas_{s}", "A")},
                       {"rotulo": f"{s}: A × C_sem_piso", "especificacao": e, "ref": refA,
                        "alt": (f"sens_C_sem_piso_{s}", "C")},
                       {"rotulo": f"{s}: A_reservas × C_sem_piso", "especificacao": e,
                        "ref": (f"sens_A_reservas_{s}", "A"), "alt": (f"sens_C_sem_piso_{s}", "C")}]
        sens_res[crit] = bootstrap.comparar(trajs, ps, args.boot_r, args.boot_seed, chave=chave)
        sens_res[crit].to_csv(saida / f"sensibilidade_reservas_{crit}.csv", index=False, float_format="%.4f")
    boot_d.to_csv(saida / "bootstrap_diagonal.csv", index=False, float_format="%.4f")
    graficos.bootstrap_delta(boot_d, saida, [v for v in exp["variantes"] if not v.startswith("sens_")
                                             and "choque" not in v])
    boot_a = None
    if sup_trajs:
        analises.salvar_superficie(sup_trajs, saida, exp["superficie"]["variantes"], especs, list(cfg["cenarios"]),
                                   varredura.grade_lambda(exp["superficie"]["passo"]))
        boot_a = bootstrap.rodar_area(sup_trajs, args.boot_r, args.boot_seed)
        boot_a.to_csv(saida / "bootstrap_area.csv", index=False, float_format="%.4f")
        pares_area = [{"rotulo": r, "especificacao": e, "ref": a, "alt": b} for e in especs
                      for r, a, b in (("3. A base × C_sem_piso", ("base", "A"), ("C_sem_piso", "C")),
                                      ("3. A_reservas × C_sem_piso", ("A_reservas", "A"), ("C_sem_piso", "C")),
                                      ("3. A base × A_reservas", ("base", "A"), ("A_reservas", "A")))]
        comp_area = bootstrap.comparar_area(sup_trajs, pares_area, args.boot_r, args.boot_seed)
        comp_area.to_csv(saida / "comparacoes_area.csv", index=False, float_format="%.4f")
        comp_area_bil = bootstrap.comparar_area(sup_trajs, pares_area, args.boot_r, args.boot_seed, pos=2)
        comp_area_bil.to_csv(saida / "comparacoes_area_banda.csv", index=False, float_format="%.4f")
        boot_a_bil = bootstrap.rodar_area(sup_trajs, args.boot_r, args.boot_seed, pos=2)
        boot_a_bil.to_csv(saida / "bootstrap_area_banda.csv", index=False, float_format="%.4f")

    log.info("validação por especificação")
    val, val_df = validacao.validar(p, especs)
    val_df.to_csv(saida / "validacao.csv", index=False, float_format="%.4f")
    graficos.validacao(val, saida)

    ctx = dict(p=p, cfg=cfg, exp=exp, ls=ls, ordem=ordem, df=df, especs=especs, areas=areas, val_df=val_df,
               erros=erros, args=args, repressao=repressao, consistencia=cons, portao=port, est=est, along=along,
               boot_d=boot_d, boot_a=boot_a, diag_c=diag_c, comp=comp, comp_area=comp_area, refs=refs,
               ordem_bil=ordem_bil, boot_d_bil=boot_d_bil, ordens_lim=ordens_lim, choque=choque, divida_res=divida_res,
               sens_reservas=sens_res, comp_bil=comp_bil, comp_area_bil=comp_area_bil,
               areas_bil=areas_bil, boot_a_bil=boot_a_bil)
    ctx["sintese"] = sintese(ctx)
    arq = relatorio(ctx, saida)
    log.info("pronto em %.0f s: %s", time.time() - t0, arq)
    print(ls[ls["variante"] == "base"].to_string(index=False))


def _relacao_ac(ordem_txt: str) -> str:
    """"A", "C" (quem fica estritamente à frente) ou "=" (empate estatístico) numa ordem como "A ≈ C > B"."""
    if "A ≈ C" in ordem_txt or "C ≈ A" in ordem_txt:
        return "="
    partes = [x.strip(" †") for x in ordem_txt.split(" > ")]
    return "A" if partes.index("A") < partes.index("C") else "C"


def frase_robustez(ordens: dict) -> str:
    """Distingue inversão (A à frente numa especificação e C em outra) de mera diferença entre empate e ordem estrita."""
    rel = {e: _relacao_ac(o) for e, o in ordens.items() if o != "—"}
    estritos = {r for r in rel.values() if r != "="}
    b_ultimo = all(o.rstrip(" †").endswith("B") for o in ordens.values() if o != "—")
    empates = [e for e, r in rel.items() if r == "="]
    frente = [e for e, r in rel.items() if r != "="]
    if len(estritos) > 1:
        return ("**O ordenamento entre A e C se inverte entre especificações: a conclusão depende da teoria de "
                "inflação.**")
    if not estritos:
        txt = "**A e C empatam estatisticamente nas três especificações"
    else:
        quem = estritos.pop()
        txt = (f"**Nenhuma especificação inverte o ordenamento: A e C empatam em {', '.join(empates) or '—'} e "
               f"{quem} fica significativamente à frente em {', '.join(frente)}")
    return txt + ("; B é o último em todas.**" if b_ultimo else ".**")


VARIANTES_CRITERIO = ["base", "estimada", "omega_038", "omega_05", "omega_1", "theta_025", "theta_0", "pe_fiscal_05",
                      "pe_fiscal_0", "neutro_45",
                      "rlong_45", "rlong_65", "inercia_alta", "repasse_est", "C_lento", "C_sem_tolerancia", "C_piso_corte",
                      "C_sem_piso", "A_reservas", "along_20"]


def secao_criterio(ctx: dict) -> list[str]:
    """Ranking com os dois critérios de inflação lado a lado e veredito sobre a vantagem de A em P3."""
    ls, especs, df = ctx["ls"], ctx["especs"], ctx["df"]
    o, ob, bd, bdb = ctx["ordem"], ctx["ordem_bil"], ctx["boot_d"], ctx["boot_d_bil"]
    p = ctx["p"]
    lo, hi = p["pi_meta"] - p["criterios"]["tolerancia_inflacao"], p["pi_meta"] + p["criterios"]["tolerancia_inflacao"]
    L = ["## 2. Critério de inflação: só teto × banda simétrica", "",
         f"Só teto: inflação média dos últimos 8 trimestres ≤ {_fmt(hi, 1)}%. Banda simétrica: entre {_fmt(lo, 1)}% e "
         f"{_fmt(hi, 1)}% (intervalo de tolerância da meta). Os demais critérios são os mesmos. Ordens com \"A ≈ C\" "
         "quando o IC de 95% de Δλ\\*₈₀ (bootstrap pareado da mesma métrica) contém zero.", "",
         "| Variante | " + " | ".join(f"{e} teto | {e} banda" for e in especs) + " |",
         "|---|" + "---|---|" * len(especs)]
    for v in [v for v in VARIANTES_CRITERIO if v in ls["variante"].unique()]:
        L.append(f"| {v} | " + " | ".join(f"{_ordem_marcada(o, ls, e, v, bd)} | {_ordem_marcada(ob, ls, e, v, bdb, '_bil')}"
                                          for e in especs) + " |")
    olim = ctx.get("ordens_lim")
    if olim:
        L += ["", "Com a banda simétrica, nenhum cenário chega a 80% em boa parte das variantes de P1 e P2; por isso o "
              "ordenamento também é reportado nos limiares de 70% e 50% (\"A ≈ C\" pelo bootstrap do mesmo limiar):", "",
              "| Variante | " + " | ".join(f"{e} 80% | {e} 70% | {e} 50%" for e in especs) + " |",
              "|---|" + "---|---|---|" * len(especs)]
        for v in [v for v in VARIANTES_CRITERIO if v in ls["variante"].unique()]:
            L.append(f"| {v} | " + " | ".join(
                f"{_ordem_marcada(ob, ls, e, v, bdb, '_bil', '80')} | {_ordem_marcada(olim['70'], ls, e, v, bdb, '_bil', '70')}"
                f" | {_ordem_marcada(olim['50'], ls, e, v, bdb, '_bil', '50')}" for e in especs) + " |")
        L += ["", "Δλ\\* (C − A) com a banda, por limiar [IC 95%]:", "",
              "| Especificação | Variante | 80% | 70% | 50% |", "|---|---|---|---|---|"]
        for e in especs:
            for v in ("base", "estimada", "C_sem_piso", "C_piso_corte"):
                rb = _boot(bdb, e, v)
                if rb is not None:
                    L.append(f"| {e} | {v} | {_ic(rb, '80')} | {_ic(rb, '70')} | {_ic(rb, '50')} |")
    L += ["", "Δλ\\*₈₀ = λ\\*₈₀(C) − λ\\*₈₀(A) [IC 95%] e P(sucesso) máxima de A e C, com cada critério:", "",
          "| Especificação | Variante | Δλ\\*₈₀ teto | Δλ\\*₈₀ banda | P máx. A teto → banda | P máx. C teto → banda |",
          "|---|---|---|---|---|---|"]
    for e in especs:
        for v in ("base", "estimada", "omega_038", "theta_025", "theta_0", "pe_fiscal_05", "pe_fiscal_0", "C_sem_piso"):
            r, rb = _boot(bd, e, v), _boot(bdb, e, v)
            l = ls[(ls["especificacao"] == e) & (ls["variante"] == v)].set_index("cenario")
            lA = ls[(ls["especificacao"] == e) & (ls["variante"] == ("base" if "A" not in l.index else v))]
            lA = lA.set_index("cenario")
            if r is None or rb is None or "C" not in l.index:
                continue
            L.append(f"| {e} | {v} | {_ic(r)} | {_ic(rb)} | {_pct(lA.loc['A', 'p_sucesso_max'])} → "
                     f"{_pct(lA.loc['A', 'p_sucesso_max_bil'])} | {_pct(l.loc['C', 'p_sucesso_max'])} → "
                     f"{_pct(l.loc['C', 'p_sucesso_max_bil'])} |")
    # sucessos deflacionários (aceitos só pelo critério de teto)
    m = df[(df["variante"] == "base") & df["cenario"].isin(["A", "C"])]
    fr = m.groupby(["especificacao", "cenario"])["frac_sucesso_abaixo_banda"].agg(
        lambda x: np.average(x, weights=m.loc[x.index, "p_sucesso"] + 1e-12))
    L += ["", "Fração dos sucessos (critério de teto) com inflação média final abaixo de "
          f"{_fmt(lo, 1)}%, ponderada por P(sucesso) ao longo da grade de λ (variante base): "
          + "; ".join(f"{e}: A {_pct(fr.get((e, 'A'), np.nan))}, C {_pct(fr.get((e, 'C'), np.nan))}" for e in especs) + "."]
    # veredito
    vered = []
    for e in especs:
        a, b = _relacao_ac(_ordem_marcada(o, ls, e, "base", bd)), _relacao_ac(_ordem_marcada(ob, ls, e, "base", bdb, "_bil"))
        r, rb = _boot(bd, e, "base"), _boot(bdb, e, "base")
        vered.append((e, a, b, r, rb))
    for e, a, b, r, rb in vered:
        nome = {"A": "vantagem de A", "C": "vantagem de C", "=": "empate"}
        txt = f"- **{e}:** {nome[a]} com o teto, {nome[b]} com a banda"
        if a != b:
            txt += (". **O ranking muda com a banda: a vantagem de A " + ("era em parte artificial" if a == "A" else
                    "aparece só com a banda") + "**, sustentada por trajetórias com inflação abaixo da meta.")
        elif a == "A" and rb is not None and r is not None and rb["delta_80"] < r["delta_80"] - 0.02:
            txt += (f"; a vantagem de A diminui (Δλ\\*₈₀ de {_fmt(r['delta_80'])} para {_fmt(rb['delta_80'])}): "
                    "parte dela vinha de trajetórias deflacionárias.")
        else:
            txt += "; o ranking não depende do piso de inflação."
        L.append(txt)
    if ctx.get("comp_area_bil") is not None or ctx.get("areas_bil") is not None:
        ab = ctx.get("areas_bil")
        if ab is not None:
            L += ["", "Área de sucesso (≥ 80%) na superfície, banda simétrica: "
                  + "; ".join(f"{r.especificacao}/{r.variante}/{r.cenario}: {_pct(r.area_sucesso)}"
                              for r in ab[ab["variante"].isin(["base", "C_sem_piso", "A_reservas"])].itertuples()) + "."]
    return L + [""]


def _celula(r, rot):
    return (f"{_fmt(r[f'delta_{rot}'])} [{_fmt(r[f'ic_lo_{rot}'])}; {_fmt(r[f'ic_hi_{rot}'])}]"
            + (" ⚠" if r.get(f"pouco_confiavel_{rot}") else ""))


def ordem_trio(res: pd.DataFrame, espec: str, rot: str, pmax: dict) -> str:
    """Ordena A, A_reservas e C_sem_piso por λ* (censura 1,01 = não atinge; desempate pela P máx.), com "≈" entre
    vizinhos cujo IC de 95% da diferença pareada contém zero."""
    r = res[res["especificacao"] == espec]
    lam = {}
    for x in r.to_dict("records"):
        a, b = x["rotulo"].split(" × ")
        lam[a], lam[b] = x[f"ref_{rot}"], x[f"alt_{rot}"]
    if len(lam) < 3:
        return "—"
    ordem = sorted(lam, key=lambda k: (lam[k], -pmax.get(k, 0)))
    if all(v >= 1.01 for v in lam.values()):
        return " ≈ ".join(ordem) + " †"
    partes = [ordem[0]]
    for a, b in zip(ordem, ordem[1:]):
        x = r[r["rotulo"].isin([f"{a} × {b}", f"{b} × {a}"])].iloc[0]
        empate = x[f"ic_lo_{rot}"] <= 0 <= x[f"ic_hi_{rot}"]
        partes.append((" ≈ " if empate else " > ") + b)
    return "".join(partes)


def secao_divida_liquida(dr: dict, ls: pd.DataFrame, especs) -> list[str]:
    nomes = {"": "bruta, teto", "_bil": "bruta, banda", "_liq": "líquida, teto", "_liq_bil": "líquida, banda"}
    L = ["", "### Critério de dívida: bruta × líquida (A, A_reservas e C_sem_piso)", "",
         "Dívida líquida: inclinação da DLSP ≤ 0 nos últimos 8 trimestres e DLSP final ≤ inicial + 5 p.p.; inflação e "
         "reservas como no critério correspondente. A venda de reservas reduz a dívida bruta (resgata compromissadas), "
         "mas não a líquida no ato da venda: a comparação separa o efeito contábil do econômico. Ordem pelo λ\\* do "
         "limiar (1º = menor adesão necessária); \"≈\" quando o bootstrap pareado não distingue vizinhos; † quando "
         "nenhum dos três atinge o limiar.", "",
         "| Especificação | Limiar | " + " | ".join(f"Dívida {n}" for n in nomes.values()) + " |",
         "|---|---|" + "---|" * len(nomes)]
    trio = {"A": ("base", "A"), "A_reservas": ("A_reservas", "A"), "C_sem_piso": ("C_sem_piso", "C")}
    for e in especs:
        for rot in ("80", "70", "50"):
            cel = []
            for suf in nomes:
                pmax = {k: ls[(ls["especificacao"] == e) & (ls["variante"] == v) & (ls["cenario"] == c)]
                        [f"p_sucesso_max{suf}"].max() for k, (v, c) in trio.items()}
                cel.append(ordem_trio(dr[suf], e, rot, pmax))
            L.append(f"| {e} | {rot}% | " + " | ".join(cel) + " |")
    L += ["", "λ\\*₇₀ de cada estratégia (não atinge = sem 70% de sucesso em nenhum λ):", "",
          "| Especificação | Estratégia | " + " | ".join(nomes.values()) + " |", "|---|---|" + "---|" * len(nomes)]
    for e in especs:
        for k, (v, c) in trio.items():
            l = ls[(ls["especificacao"] == e) & (ls["variante"] == v) & (ls["cenario"] == c)]
            if len(l):
                L.append(f"| {e} | {k} | " + " | ".join(_fmt(l[f"lambda_star_70{s}"].iloc[0]) for s in nomes) + " |")
    return L + [""]


def secao_parada_subita(choque: dict) -> list[str]:
    """Custo do choque para cada cenário, comparação sob choque e diferença das diferenças (custo de cauda)."""
    L = ["", "### Parada súbita: custo de cauda da venda de reservas", "",
         "Choque não antecipado no ano 2 (trimestre 8) ou 3 (trimestre 12): depreciação de 30% no trimestre e prêmio "
         "de risco +3 p.p., com decaimento de 20% por trimestre; o BC defende o câmbio com até US$ 50 bi de reservas, "
         "que pode romper o piso R_min = US$ 300 bi (100% da ARA; o critério de reservas olha a janela final). A venda "
         "programada de até US$ 100 bi (A_reservas, C_sem_piso) é limitada pelo piso a cerca de US$ 76 bi; quem vendeu "
         "chega ao choque perto do piso, A com cerca de US$ 90 bi acima dele. Sem canal reservas → prêmio nesta seção "
         "(ver outputs/v2_2/reservas_choque). Δλ\\* = λ\\*(alternativa) − λ\\*(referência), bootstrap "
         "pareado; o \"custo do choque\" compara cada cenário com ele mesmo sem choque.", ""]
    for crit, (cmp_, did) in choque.items():
        lim = ("80", "70") if crit == "teto" else ("70", "50")
        L += [f"Critério de inflação: {'só teto' if crit == 'teto' else 'banda simétrica'} (limiares {lim[0]}% e "
              f"{lim[1]}%).", "", f"| Comparação | Especificação | Δλ\\*{lim[0]} [IC 95%] | Δλ\\*{lim[1]} [IC 95%] | "
              f"Leitura ({lim[0]}%) |", "|---|---|---|---|---|"]
        for r in cmp_.to_dict("records"):
            L.append(f"| {r['rotulo']} | {r['especificacao']} | {_celula(r, lim[0])} | {_celula(r, lim[1])} | "
                     f"{r[f'leitura_{lim[0]}']} |")
        L += ["", "Custo de cauda (diferença das diferenças: custo do choque do cenário − custo do choque de A; positivo "
              "= o cenário sofre mais):", "", f"| Comparação | Especificação | {lim[0]}% [IC 95%] | {lim[1]}% [IC 95%] |",
              "|---|---|---|---|"]
        for r in did.to_dict("records"):
            c = lambda rot: (f"{_fmt(r[f'did_{rot}'])} [{_fmt(r[f'ic_lo_{rot}'])}; {_fmt(r[f'ic_hi_{rot}'])}]"  # noqa: E731
                             + (" ⚠" if r[f"censura_{rot}"] > 0.2 else ""))
            L.append(f"| {r['rotulo']} | {r['especificacao']} | {c(lim[0])} | {c(lim[1])} |")
        sig = did[(did["ic_lo_" + lim[0]] > 0) & did["rotulo"].str.contains("A_reservas")]
        L += ["", ("**Há custo de cauda significativo da venda de reservas** em: "
                   + ", ".join(f"{r.especificacao} ({r.rotulo.split(':')[0]})" for r in sig.itertuples())
                   + ". Ele precisa entrar na conclusão." if len(sig) else
                   "**Com choques transitórios nos anos 2 e 3, não há custo de cauda mensurável da venda de "
                   "reservas**: A_reservas não sofre com o choque significativamente mais que A. Com choque persistente "
                   "ou no ano 7, a vantagem da venda desaparece (ver relatório de reservas, outputs/v2_2/reservas_choque, "
                   "seção 2). Esta seção não inclui o canal reservas → prêmio de risco; ele é testado no relatório de "
                   "reservas, com efeito pequeno com R_adequado = US$ 300 bi (100% da ARA) e moderado com US$ 363 bi."),
          ""]
    return L


def secao_sens_reservas(sens: dict) -> list[str]:
    nomes = {"c3_05": "c3 = 0,5", "c3_1": "c3 = 1", "c3_4": "c3 = 4", "rmin_250": "R_min = US$ 250 bi (anterior)",
             "rmin_350": "R_min = US$ 350 bi", "rend_2": "rendimento das reservas = 2%", "rend_6": "rendimento das reservas = 6%"}
    L = ["", "### Sensibilidade dos parâmetros das reservas (P1 e P3)", "",
         "Padrões: c3 = 2 (efeito da intervenção sobre o câmbio), R_min = US$ 300 bi, rendimento das reservas = 4% a.a. "
         "(contra o custo das compromissadas à Selic). Δλ\\* = λ\\*(alternativa) − λ\\*(referência), bootstrap pareado. "
         "Esta tabela usa a dívida bruta, em que o rendimento das reservas não entra; por isso as linhas com 2% e 6% "
         "saem quase idênticas. A sensibilidade ao rendimento pela dívida líquida, com tendência da depreciação, está "
         "no relatório de reservas (seção 1); c3 e R_min pela dívida líquida, na seção 3 dele.",
         "", "| Parâmetro | Comparação | Especificação | Teto 80% | Banda 70% | Banda 50% |", "|---|---|---|---|---|---|"]
    t, b = sens["teto"], sens["banda"]
    for r in t.to_dict("records"):
        rb = b[(b["rotulo"] == r["rotulo"]) & (b["especificacao"] == r["especificacao"])]
        rb = rb.iloc[0].to_dict() if len(rb) else None
        par, comp = r["rotulo"].split(": ")
        L.append(f"| {nomes.get(par, par)} | {comp} | {r['especificacao']} | {_celula(r, '80')} | "
                 f"{_celula(rb, '70') if rb else '—'} | {_celula(rb, '50') if rb else '—'} |")
    L += ["", "Nota: a venda de reservas reduz as compromissadas e, com elas, a dívida bruta; a dívida líquida não muda "
          "no ato da venda. Ainda assim, pela dívida líquida a vantagem se mantém e até aumenta (tabela \"Critério de "
          "dívida: bruta × líquida\" acima), porque vem do custo de carregamento: o rendimento das reservas mais a "
          "depreciação fica abaixo da Selic. A vantagem encolhe à medida que o carregamento se aproxima de zero "
          "(relatório de reservas, seção 1).", ""]
    return L


def secao_testes_sem_piso(comp: pd.DataFrame, comp_area, especs, comp_bil=None, comp_area_bil=None) -> list[str]:
    """Testes do C_sem_piso: reservas em A, decomposição piso/teto, superfície e estresse."""
    L = ["", "### Testes do C_sem_piso", "",
         "Δλ\\*₈₀ = λ\\*₈₀(alternativa) − λ\\*₈₀(referência), bootstrap pareado com os mesmos choques; negativo = a "
         "alternativa exige menos adesão.", "",
         "| Teste | Especificação | Referência | Alternativa | λ\\*₈₀ ref. | λ\\*₈₀ alt. | Δλ\\*₈₀ [IC 95%] | Δλ\\*₅₀ [IC 95%] | "
         "Leitura (80%) |", "|---|---|---|---|---|---|---|---|---|"]
    f80 = lambda x: _fmt(x) if x < 1.01 else "não atinge"  # noqa: E731
    for r in comp.itertuples():
        L.append(f"| {r.rotulo} | {r.especificacao} | {r.ref} | {r.alt} | {f80(r.ref_80)} | {f80(r.alt_80)} | "
                 f"{_fmt(r.delta_80)} [{_fmt(r.ic_lo_80)}; {_fmt(r.ic_hi_80)}]{' ⚠' if r.pouco_confiavel_80 else ''} | "
                 f"{_fmt(r.delta_50)} [{_fmt(r.ic_lo_50)}; {_fmt(r.ic_hi_50)}] | {r.leitura_80} |")
    if comp_bil is not None and len(comp_bil):
        L += ["", "Os mesmos testes com o critério de banda simétrica (1,5%–4,5%):", "",
              "| Teste | Especificação | λ\\*₈₀ ref. | λ\\*₈₀ alt. | Δλ\\*₈₀ [IC 95%] | Leitura (80%) |",
              "|---|---|---|---|---|---|"]
        for r in comp_bil.itertuples():
            L.append(f"| {r.rotulo} | {r.especificacao} | {f80(r.ref_80)} | {f80(r.alt_80)} | {_fmt(r.delta_80)} "
                     f"[{_fmt(r.ic_lo_80)}; {_fmt(r.ic_hi_80)}]{' ⚠' if r.pouco_confiavel_80 else ''} | {r.leitura_80} |")
    t1 = comp[comp["rotulo"] == "1. A_reservas × C_sem_piso"]
    if len(t1):
        emp = t1["leitura_80"].eq("empate estatístico")
        cfrente = t1["leitura_80"].eq("alternativa exige menos adesão")
        L += ["", "**Teste 1 (reservas):** "
              + ("A_reservas empata com C_sem_piso em todas as especificações: a vantagem vem das reservas, que podem "
                 "ser acrescentadas ao caminho ortodoxo." if emp.all() else
                 "C_sem_piso continua à frente de A_reservas em " + ", ".join(t1.loc[cfrente, "especificacao"])
                 + ": o alívio monetário temporário (até δ abaixo da Taylor) tem valor próprio, além das reservas."
                 + (f" Empate em {', '.join(t1.loc[emp, 'especificacao'])}." if emp.any() else "")
                 if cfrente.any() else
                 "A_reservas fica à frente de C_sem_piso em " + ", ".join(t1.loc[~emp, "especificacao"])
                 + ": somar a venda de reservas ao caminho ortodoxo domina a alternativa.")]
    t2a = comp[comp["rotulo"] == "2. Piso no fim (C base × C_piso_corte)"]
    t2b = comp[comp["rotulo"] == "2. Teto no corte (C_piso_corte × C_sem_piso)"]
    if len(t2a) and len(t2b):
        L += ["", "**Teste 2 (decomposição):** de C base para C_sem_piso, a parte atribuída a tirar o piso no fim é "
              + "; ".join(f"{r.especificacao}: {_fmt(r.delta_80)}" for r in t2a.itertuples())
              + " e a parte atribuída a trocar o piso pelo teto durante o corte é "
              + "; ".join(f"{r.especificacao}: {_fmt(r.delta_80)}" for r in t2b.itertuples()) + " (Δλ\\*₈₀)."]
    if comp_area is not None and len(comp_area):
        L += ["", "**Teste 3 (superfície λ_π × λ_fiscal):** ΔÁrea = Área(referência) − Área(alternativa).", "",
              "| Comparação | Especificação | Área ref. | Área alt. | ΔÁrea [IC 95%] | Leitura |", "|---|---|---|---|---|---|"]
        for crit, tab in (("teto", comp_area), ("banda", comp_area_bil)):
            if tab is None:
                continue
            for r in tab.itertuples():
                L.append(f"| {r.rotulo} ({crit}) | {r.especificacao} | {_pct(r.area_ref)} | {_pct(r.area_alt)} | "
                         f"{_fmt(100 * r.delta_area, 1)} p.p. [{_fmt(100 * r.ic_lo, 1)}; {_fmt(100 * r.ic_hi, 1)}] | "
                         f"{r.leitura} |")
    arq = RAIZ / "outputs" / "v2_2" / "theta_fino" / "theta_fino_bootstrap.csv"
    if arq.exists():
        tf = pd.read_csv(arq)
        if "sp_delta_80" in tf:
            L += ["", "**Teste 4 (grade fina de θ em P3):** Δλ\\*₈₀ contra A, com os dois critérios de inflação "
                  "(gráfico `theta_fino/19_theta_fino`).", "",
                  "| θ | C − A (teto) | C_sem_piso − A (teto) | C − A (banda) | C_sem_piso − A (banda) |",
                  "|---|---|---|---|---|"]
            ic = lambda r, pre: (f"{_fmt(getattr(r, pre + 'delta_80'))} [{_fmt(getattr(r, pre + 'ic_lo_80'))}; "  # noqa: E731
                                 f"{_fmt(getattr(r, pre + 'ic_hi_80'))}]" if hasattr(r, pre + "delta_80") else "—")
            for r in tf.itertuples():
                L.append(f"| {_fmt(r.theta)} | {ic(r, '')} | {ic(r, 'sp_')} | {ic(r, 'bil_')} | {ic(r, 'bil_sp_')} |")
    return L


def texto_magnitude(om: dict) -> str:
    if om["usado_no_modelo"]:
        return f"identificada: ψ = {_fmt(om['psi'])}, IC de Fieller {om['ic_texto']}, dentro da faixa admissível."
    if om["ic_tipo"] != "limitado":
        return (f"não identificada; o IC de Fieller é ilimitado ({om['ic_texto']}), então ω não é calibrado pelos "
                "dados.")
    fora = not 0 <= om["psi"] <= 1
    return (f"não identificada; o intervalo vai de {_fmt(om['ic_lo'])} a {_fmt(om['ic_hi'])}"
            + (f" e a estimativa pontual ({_fmt(om['psi'])}) cai fora da faixa admissível" if fora else "")
            + ", então ω não é calibrado pelos dados.")


def texto_sinal(oe: pd.DataFrame) -> str:
    """Evidência de ω > 0: regressões com IC limitado que exclui zero pela esquerda."""
    pos = oe[(oe["ic_tipo"] == "limitado") & (oe["ic_lo"] > 0)]
    total = int(oe["psi"].notna().sum())
    if pos.empty:
        return "nenhuma regressão exclui ω = 0 com 95% de confiança; não há evidência sobre o sinal."
    onde = "; ".join(f"{r.metodo} na amostra {r.amostra}" for r in pos.itertuples())
    forca = "fraca" if len(pos) <= total / 3 else "moderada"
    so = "só por " if len(pos) == 1 else "em "
    return (f"há evidência {forca}, {so}{onde} ({len(pos)} de {total} regressões), de que ω é positivo. Por isso, as "
            "variantes ω = 0,5 e ω = 1 aparecem no relatório com o mesmo destaque da base (ω = 0), e não como "
            "sensibilidade secundária.")


def respostas_alongamento(al: dict) -> list[str]:
    """Respostas explícitas: o alongamento reabre a válvula? A que velocidade? Qual o custo com φ = 0?"""
    tb = al["tabela"]
    p3 = tb[(tb["especificacao"] == "P3") & (tb["cenario"].isin(["A", "C"]))]
    pmax = lambda var: p3[p3["variante"] == var]["p_sucesso_max"].max()  # noqa: E731
    sem, com = pmax("phi_025"), pmax("phi_025_along_20")
    reabre = com >= 0.5
    linhas = [f"- **O alongamento reabre a válvula?** Com φ = 0,25, a maior P(sucesso) de A ou C vai de {_pct(sem)} "
              f"sem alongamento para {_pct(com)} com along_20"
              + (": sim, os cenários voltam a ter sucesso." if reabre else
                 ": não — os cenários continuam falhando, sobretudo por inflação acima do teto; a migração vai em "
                 "70% para NTN-B, que é indexada e não sofre erosão.")]
    vel = {v: pmax(v) for v in ("phi_025_along_12", "phi_025_along_20", "phi_025_along_28", "phi_025_along_pre",
                                "phi_025_along_50")}
    melhor = max(vel, key=lambda k: vel[k])
    linhas.append("- **Velocidade e composição:** P(sucesso) máx. de A/C com φ = 0,25 — "
                  + "; ".join(f"{k.replace('phi_025_', '')}: {_pct(v)}" for k, v in vel.items())
                  + f". Melhor caso: {melhor.replace('phi_025_', '')}"
                  + ("." if vel[melhor] >= 0.5 else ", ainda abaixo de 50%: nenhuma velocidade testada reabre a válvula."))
    cu = al["custo"][al["custo"]["cenario"] == "A"]
    linhas.append("- **Custo com φ = 0 (cenário A):** variação do custo real efetivo médio de "
                  + "; ".join(f"{r.especificacao} λ={_fmt(r._3, 1)}: {_fmt(r.delta_custo_pp)} p.p. a.a. "
                              f"(dívida final {_fmt(r.delta_d_final, 1):s} p.p.)" for r in cu.itertuples()) + ".")
    return linhas


def sintese(ctx: dict) -> list[str]:
    bd, ls, ordem, especs = ctx["boot_d"], ctx["ls"], ctx["ordem"], ctx["especs"]
    base = {e: _boot(bd, e, "base") for e in especs}
    empates = [e for e, r in base.items() if r is not None and r["leitura_80"] == "empate estatístico"]
    est = {e: _ordem_marcada(ordem, ls, e, "estimada", bd) for e in especs}
    L = [f"(a) **A e C são estatisticamente distinguíveis?** Na base, empate estatístico em λ\\*₈₀ em "
         f"{len(empates)} de {len(especs)} especificações ({', '.join(empates) or 'nenhuma'}); "
         + "; ".join(f"{e}: Δλ\\*₈₀ = {_ic(r)}" for e, r in base.items() if r is not None) + "."]
    ba = ctx.get("boot_a")
    if ba is not None and len(ba):
        b = ba[ba["variante"] == "base"]
        L.append("Na área de sucesso (base): " + "; ".join(f"{r.especificacao}: {r.leitura}" for r in b.itertuples()) + ".")
    L.append("(b) **Com os parâmetros estimados, quem fica à frente?** " + "; ".join(f"{e}: {o}" for e, o in est.items())
             + f" (b3 calibrado por especificação; ψ estimado = {_fmt(ctx['est']['omega_principal']['psi'])}, IC de "
             f"Fieller {ctx['est']['omega_principal']['ic_texto']}: {ctx['est']['omega_principal']['classe_texto']}; "
             + (f"ω = {_fmt(ctx['est']['omega_principal']['omega'])})." if ctx["est"]["omega_principal"]["usado_no_modelo"]
                else "a variante estimada usa ω = 0, e o efeito de ω fica na grade {0; 0,5; 1}).")
             + " Com a grade de ω, que tem o mesmo peso da base porque ω não é calibrado pelos dados: "
             + "; ".join(f"{e}: ω = 0 → {_ordem_marcada(ordem, ls, e, 'base', bd)}, ω = 0,5 → "
                         f"{_ordem_marcada(ordem, ls, e, 'omega_05', bd)}, ω = 1 → {_ordem_marcada(ordem, ls, e, 'omega_1', bd)}, "
                         f"ω = 0,38 (verificação cruzada) → {_ordem_marcada(ordem, ls, e, 'omega_038', bd)}"
                         for e in especs) + "."
             + (f" Em P3, com θ no intervalo sustentado pela validação: θ = 0,25 → "
                f"{_ordem_marcada(ordem, ls, 'P3', 'theta_025', bd)}; θ = 0 → {_ordem_marcada(ordem, ls, 'P3', 'theta_0', bd)}."
                if "P3" in especs else ""))
    tb, cu = ctx["along"]["tabela"], ctx["along"]["custo"]
    p3 = tb[(tb["especificacao"] == "P3") & tb["cenario"].isin(["A", "C"])]
    pmax = lambda v: p3.loc[p3["variante"] == v, "p_sucesso_max"].max()  # noqa: E731
    vel = {v.replace("phi_025_", ""): pmax(v) for v in ("phi_025_along_12", "phi_025_along_20", "phi_025_along_28",
                                                        "phi_025_along_pre", "phi_025_along_50")}
    cA = cu[cu["cenario"] == "A"]
    if ctx.get("boot_d_bil") is not None:
        L.append("(d) **Critério de inflação com banda simétrica (1,5%–4,5%):** "
                 + "; ".join(f"{e}: {_ordem_marcada(ctx['ordem'], ls, e, 'base', bd)} (teto) → "
                             f"{_ordem_marcada(ctx['ordem_bil'], ls, e, 'base', ctx['boot_d_bil'], '_bil')} (banda)"
                             for e in especs) + ". Ver seção 2.")
    L.append("(c) **O alongamento reabre a válvula da erosão inflacionária?** "
             + ("Sim" if max(vel.values()) >= 0.5 else "Não")
             + f": com φ = 0,25, a maior P(sucesso) de A ou C passa de {_pct(pmax('phi_025'))} para no máximo "
               f"{_pct(max(vel.values()))} ({', '.join(f'{k} {_pct(v)}' for k, v in vel.items())}); a inflação continua "
               "acima do teto porque 70% da LFT migra para NTN-B, que é indexada. Com φ = 0, o custo é pequeno: "
               f"entre {_fmt(cA['delta_custo_pp'].min())} e {_fmt(cA['delta_custo_pp'].max())} p.p. a.a. no custo real "
               f"da dívida e entre {_fmt(cA['delta_d_final'].min(), 1)} e {_fmt(cA['delta_d_final'].max(), 1)} p.p. do PIB "
               "na dívida final do cenário A.")
    return L


if __name__ == "__main__":
    main()
