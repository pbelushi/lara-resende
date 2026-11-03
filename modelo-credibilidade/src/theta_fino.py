"""Grade fina de θ em P3 e decomposição da inflação de A e C (por que a vantagem de A cresce e depois se inverte).

Uso: python -m src.theta_fino  (grava em outputs/v2_2/theta_fino/)
"""
from __future__ import annotations

import copy
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import bootstrap, graficos, metricas, modelo, varredura

RAIZ = Path(__file__).resolve().parents[1]
THETAS = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.5)
LAMS_DECOMP = (0.5, 0.6, 0.7)
COMPS = ("expectativa", "fiscal", "hiato", "cambio", "choque")
log = logging.getLogger(__name__)


AJUSTE_SEM_PISO = {"politica_monetaria": "condicionada_sem_piso"}


def _p3(p: dict, theta: float) -> dict:
    return modelo.preparar({**copy.deepcopy(p), "especificacao": "P3", "theta": theta})


def grade(p: dict, cfg: dict, choques: np.ndarray, R: int = 1000, seed: int = 2026) -> tuple[pd.DataFrame, pd.DataFrame]:
    """λ*, P(sucesso) e bootstrap pareado A × C para cada θ."""
    g = varredura.grade_lambda(0.01)
    resumo, curvas = [], []
    for th in THETAS:
        q = _p3(p, th)
        cens = varredura.preparar_cenarios(q, cfg)
        cens["C_sem_piso"] = varredura.preparar_cenarios(q, cfg, ["C"], AJUSTE_SEM_PISO)["C"]
        mc, oks_m, _ = varredura.diagonal(q, cens, g, choques, trajetorias=True)
        oks, oksb = oks_m[""], oks_m["_bil"]
        mc["theta"] = th
        curvas.append(mc)
        bt = bootstrap.diagonal(oks["A"], oks["C"], g, bootstrap.indices(choques.shape[0], R, seed))
        linha = {"theta": th, **{f"{k}": v for k, v in bt.items()}, "leitura_80": bootstrap.leitura_diagonal(bt, "80"),
                 "leitura_50": bootstrap.leitura_diagonal(bt, "50")}
        bs = bootstrap.diagonal(oks["A"], oks["C_sem_piso"], g, bootstrap.indices(choques.shape[0], R, seed))
        linha.update({f"sp_{k}": v for k, v in bs.items()})
        linha["sp_leitura_80"] = bootstrap.leitura_diagonal(bs, "80")
        # banda simétrica [1,5; 4,5]
        bb = bootstrap.diagonal(oksb["A"], oksb["C"], g, bootstrap.indices(choques.shape[0], R, seed))
        linha.update({f"bil_{k}": v for k, v in bb.items()})
        bsb = bootstrap.diagonal(oksb["A"], oksb["C_sem_piso"], g, bootstrap.indices(choques.shape[0], R, seed))
        linha.update({f"bil_sp_{k}": v for k, v in bsb.items()})
        for ch in ("A", "B", "C", "C_sem_piso"):
            m = mc[mc["cenario"] == ch]
            linha[f"pmax_{ch}"] = m["p_sucesso"].max()
            linha[f"l80_{ch}"] = metricas.lambda_star_prob(m["lambda"].values, m["p_sucesso"].values, 0.8)
            linha[f"bil_l80_{ch}"] = metricas.lambda_star_prob(m["lambda"].values, m["p_sucesso_bil"].values, 0.8)
            linha[f"bil_pmax_{ch}"] = m["p_sucesso_bil"].max()
        resumo.append(linha)
        log.info("θ = %.2f: Δλ*80 = %+.2f [%+.2f; %+.2f]", th, bt["delta_80"], bt["ic_lo_80"], bt["ic_hi_80"])
    return pd.DataFrame(resumo), pd.concat(curvas, ignore_index=True)


def decomposicao(p: dict, cfg: dict, choques: np.ndarray, thetas=(0.5, 0.25, 0.0)) -> pd.DataFrame:
    """Média (sobre trajetórias não rompidas) de cada componente da inflação na janela final e no horizonte todo,
    com a inflação média final, o sucesso e as falhas por critério; A e C, λ ∈ LAMS_DECOMP."""
    N = choques.shape[0]
    n = p["criterios"]["janela_final"]
    linhas = []
    for th in thetas:
        q = _p3(p, th)
        cens = varredura.preparar_cenarios(q, cfg, ["A", "C"])
        cens["C_sem_piso"] = varredura.preparar_cenarios(q, cfg, ["C"], AJUSTE_SEM_PISO)["C"]
        for ch, c in cens.items():
            for lam in LAMS_DECOMP:
                tr = modelo.simular(q, c["cen"], np.full(N, lam), choques=choques, plano=c["plano"])
                ok, det = metricas.sucesso(tr, q)
                vivo = tr["ruptura"] < 0
                pif = np.nanmean(tr["pi"][:, -n:], axis=1)
                piso_meta = q["pi_meta"] - q["criterios"]["tolerancia_inflacao"]
                linha = {"theta": th, "cenario": ch, "lambda": lam, "p_sucesso": ok.mean(),
                         # sucessos com inflação média final abaixo de meta − 1,5 (o critério só tem teto)
                         "frac_sucesso_deflacionario": float((ok & (pif < piso_meta)).sum() / max(ok.sum(), 1)),
                         "p_sucesso_bilateral": float((ok & (pif >= piso_meta)).mean()),
                         "pi_final": np.nanmean(tr["pi"][vivo, -n:]), "pi_meio": np.nanmean(tr["pi"][vivo, 1:]),
                         "d_final": np.nanmean(tr["d_gross"][vivo, -1]),
                         "custo_real": np.nanmean(tr["i_ef"][vivo, 1:] - tr["pi"][vivo, 1:]),
                         "selic_media": np.nanmean(tr["i"][vivo, 1:]), "prem_medio": np.nanmean(tr["prem"][vivo, 1:]),
                         **{f"falha_{k}": v for k, v in metricas.falhas(det).items()}}
                for comp in COMPS:
                    x = tr[f"comp_{comp}"][vivo]
                    linha[f"{comp}_final"] = np.nanmean(x[:, -n:])
                    linha[f"{comp}_todo"] = np.nanmean(x[:, 1:])
                linhas.append(linha)
    return pd.DataFrame(linhas)


def grafico(resumo: pd.DataFrame, curvas: pd.DataFrame, info: dict, saida: Path):
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    ax = axs[0]
    ax.fill_between(resumo["theta"], resumo["ic_lo_80"], resumo["ic_hi_80"], color="#9bb3cf", alpha=0.5, lw=0,
                    label="IC 95% (bootstrap pareado)")
    ax.plot(resumo["theta"], resumo["delta_80"], "o-", color=graficos.TINTA, label="Δλ*₈₀ = λ*₈₀(C) − λ*₈₀(A)")
    ax.axhline(0, color=graficos.TINTA_SEC, lw=0.8)
    ax.set_xlabel("θ (fração da lacuna absorvida por inflação)")
    ax.set_ylabel("Δλ*₈₀ (positivo: vantagem de A)")
    ax.set_title("Vantagem de A sobre C ao longo de θ (P3)", loc="left", color=graficos.TINTA, fontsize=9)
    ax.plot(resumo["theta"], resumo["sp_delta_80"], "s--", color="#009E73", label="Δλ*₈₀ de C_sem_piso − A")
    ax.legend(fontsize=7.5)
    ax = axs[1]
    for ch, ls in (("A", "-"), ("C", ":"), ("C_sem_piso", "--")):
        cor = info.get(ch, {"cor": "#56B4E9"})["cor"] if ch != "C_sem_piso" else "#56B4E9"
        nome = info[ch]["nome"] if ch in info else "C sem piso"
        ax.plot(resumo["theta"], resumo[f"l80_{ch}"], ls, marker="o", color=cor, label=nome)
    ax.set_xlabel("θ")
    ax.set_ylabel("λ*₈₀")
    ax.legend(fontsize=7.5)
    ax.set_title("Adesão mínima para 80% de sucesso", loc="left", color=graficos.TINTA, fontsize=9)
    fig.tight_layout()
    return graficos._salvar(fig, saida, "19_theta_fino")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    saida = RAIZ / "outputs" / "v2_2" / "theta_fino"
    saida.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)  # mesmos choques da rodada principal
    resumo, curvas = grade(p, cfg, choques)
    resumo.to_csv(saida / "theta_fino_bootstrap.csv", index=False, float_format="%.4f")
    curvas.to_csv(saida / "theta_fino_curvas.csv", index=False, float_format="%.4f")
    dec = decomposicao(p, cfg, choques)
    dec.to_csv(saida / "theta_decomposicao_inflacao.csv", index=False, float_format="%.4f")
    info = {k: {"nome": v["nome"], "cor": v["cor"]} for k, v in cfg["cenarios"].items()}
    grafico(resumo, curvas, info, saida)
    log.info("pronto")


if __name__ == "__main__":
    main()
