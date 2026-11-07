"""Busca aleatória de combinações de ajuste com sucesso sob adesão baixa (λ ≤ 0,3) e baixo custo social.

Cada combinação sorteia: tamanho total do pacote, composição entre os dez itens de config/recessivo.yaml (com teto
por item), início e rampa do pacote, regra monetária (Taylor ou alívio condicionado sem piso, com alvo, prazo e
tolerância), venda de reservas (total e prazo) e alongamento da dívida. Cada combinação roda com os mesmos choques
(common random numbers) e é comparada com a referência sem ajuste (S) na mesma adesão.

Fase 1: sorteio amplo, só P2 (especificação de referência), N trajetórias reduzido.
Fase 2: mutações locais em torno das melhores combinações da fase 1.
Fase 3: as finalistas rodam com N = 1000 em P1, P2 e P3.

Uso: python -m src.busca_aleatoria [--n1 6000] [--n2 1500] [--N1 200] [--final 40] [--jobs 2]
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from . import metricas, modelo, politicas, recessivo as R, varredura

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "outputs" / "v2_2" / "busca_aleatoria"
R.GUARDAR = R.GUARDAR + ("R",)
ITENS = list(R.CONF["itens"])
# teto de cada item (% do PIB em vigor ao fim da rampa): premissa da busca, ordem de grandeza do espaço fiscal
TETO = {"renuncias": 2.5, "beneficios": 1.0, "subsidios": 0.6, "verbas_teto": 0.2, "prev_militar": 0.4,
        "emendas": 0.5, "custeio": 0.8, "pisos": 1.2, "investimento": 1.0, "transferencias": 1.5}
LAMS = [0.1, 0.2, 0.3]
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------- sorteio

def alocar(total: float, pesos: np.ndarray) -> dict:
    """Distribui `total` pelos itens na proporção dos pesos, respeitando o teto de cada item (water-filling)."""
    teto = np.array([TETO[k] for k in ITENS])
    x = np.zeros(len(ITENS))
    livre = np.ones(len(ITENS), bool) & (pesos > 0)
    resto = min(total, teto[pesos > 0].sum())
    while resto > 1e-9 and livre.any():
        w = pesos * livre
        add = resto * w / w.sum()
        novo = np.minimum(x + add, teto)
        resto -= (novo - x).sum()
        x = novo
        livre &= x < teto - 1e-9
    return {k: float(v) for k, v in zip(ITENS, x) if v > 1e-6}


def sortear(rng: np.random.Generator) -> dict:
    pesos = rng.dirichlet(np.full(len(ITENS), 0.6))
    pesos[rng.random(len(ITENS)) < 0.3] = 0.0  # combinações esparsas: cerca de 30% dos itens fora
    if pesos.sum() == 0:
        pesos[rng.integers(len(ITENS))] = 1.0
    c = {"total": float(rng.uniform(0.5, 6.0)), "pesos": (pesos / pesos.sum()).tolist(),
         "inicio": int(rng.integers(1, 5)), "rampa": int(rng.integers(1, 17)),
         "regra": str(rng.choice(["taylor", "condicionada_sem_piso"])),
         "i_alvo": float(rng.uniform(6.5, 11.0)), "T_corte": int(rng.integers(4, 13)),
         "delta0": float(rng.uniform(0.0, 2.0)), "T_delta": int(rng.integers(1, 17)),
         "reservas": float(rng.choice([0.0, rng.uniform(0, 100)])), "T_res": int(rng.integers(1, 9)),
         "along": bool(rng.random() < 0.4), "w_lft": float(rng.uniform(0.30, 0.55)), "T_along": int(rng.integers(8, 29))}
    return c


def mutar(c: dict, rng: np.random.Generator, escala: float = 0.15) -> dict:
    m = copy.deepcopy(c)
    p = np.array(m["pesos"]) * np.exp(rng.normal(0, 0.5, len(ITENS)))
    if rng.random() < 0.3:
        p[rng.integers(len(ITENS))] = rng.random() * p.max()
    m["pesos"] = (p / p.sum()).tolist()
    m["total"] = float(np.clip(m["total"] * np.exp(rng.normal(0, escala)), 0.5, 6.0))
    m["inicio"] = int(np.clip(m["inicio"] + rng.integers(-1, 2), 1, 4))
    m["rampa"] = int(np.clip(m["rampa"] + rng.integers(-3, 4), 1, 16))
    m["i_alvo"] = float(np.clip(m["i_alvo"] + rng.normal(0, 0.5), 6.5, 11.0))
    m["T_corte"] = int(np.clip(m["T_corte"] + rng.integers(-2, 3), 4, 12))
    m["delta0"] = float(np.clip(m["delta0"] + rng.normal(0, 0.3), 0, 2))
    m["T_delta"] = int(np.clip(m["T_delta"] + rng.integers(-3, 4), 1, 16))
    m["reservas"] = float(np.clip(m["reservas"] + rng.normal(0, 10), 0, 100))
    m["T_res"] = int(np.clip(m["T_res"] + rng.integers(-1, 2), 1, 8))
    if rng.random() < 0.1:
        m["regra"] = "taylor" if m["regra"] != "taylor" else "condicionada_sem_piso"
    if rng.random() < 0.1:
        m["along"] = not m["along"]
    m["w_lft"] = float(np.clip(m["w_lft"] + rng.normal(0, 0.03), 0.30, 0.55))
    m["T_along"] = int(np.clip(m["T_along"] + rng.integers(-3, 4), 8, 28))
    return m


# ---------------------------------------------------------------------------------------------- avaliação

def pacote_de(c: dict, T: int) -> tuple[list[dict], dict]:
    aloc = alocar(c["total"], np.array(c["pesos"]))
    pac = []
    for k, v in aloc.items():
        it = R.CONF["itens"][k]
        pac.append({"nome": it["nome"], "chave": k, "tipo": it["tipo"], "canal": it["canal"],
                    "multiplicador": it["m"], "trilha": politicas.rampa(c["inicio"], c["rampa"], v, T),
                    "impacto_final": v})
    return pac, aloc


def avaliar(c: dict, p_base: dict, cfg: dict, espec: str, choques: np.ndarray, lams, trS_cache: dict) -> list[dict]:
    T = cfg["horizonte"]
    pac, aloc = pacote_de(c, T)
    extra = {"alongamento": True, "w_lft_alvo": c["w_lft"], "T_along": c["T_along"], "s_ipca": 0.7} if c["along"] else {}
    q = R.preparar_espec(p_base, espec, extra)
    qS = R.preparar_espec(p_base, espec)
    k = c["T_res"]
    ajustes = {"politica_monetaria": c["regra"], "pacote_fiscal": True,
               "venda_reservas": [c["reservas"] / k] * k if c["reservas"] > 0 else []}
    chave = "A"
    if c["regra"] != "taylor":
        chave = "C"
        ajustes.update({"i_alvo": c["i_alvo"], "T_corte": c["T_corte"], "delta0": c["delta0"],
                        "T_delta": c["T_delta"], "piso_final": None})
    cc = copy.deepcopy(cfg)
    cc["pacote_fiscal"] = pac
    cen = varredura.preparar_cenarios(q, cc, [chave], ajustes)[chave]
    lams = np.asarray(lams, float)
    N = choques.shape[0]
    tr = modelo.simular(q, cen["cen"], np.repeat(lams, N), choques=np.tile(choques, (len(lams), 1, 1)),
                        plano=cen["plano"], guardar=R.GUARDAR)
    tr = {kk: v.reshape(len(lams), N, -1) for kk, v in tr.items() if kk != "ruptura"} | {
        "ruptura": tr["ruptura"].reshape(len(lams), N)}
    if espec not in trS_cache:
        trS_cache[espec] = R.simular(qS, cfg, "S", lams, choques, None)
    trS = trS_cache[espec]
    m = R.atividade(tr, trS, q)
    linhas = []
    mult = sum(R.CONF["itens"][kk]["m"] * v for kk, v in aloc.items()) / max(sum(aloc.values()), 1e-9)
    for i, lam in enumerate(lams):
        sub = {kk: v[i] for kk, v in tr.items()}
        ok = {suf: metricas.sucesso(sub, q, bilateral=b, divida=d)[0] for suf, (b, d) in metricas.METRICAS.items()}
        v = m["valida"][i]
        linhas.append({
            "especificacao": espec, "lambda": float(lam),
            **{f"p{suf}": float(o.mean()) for suf, o in ok.items()},
            "dif_1-8": float(np.nanmean(np.where(v, m["dif_1-8"][i], np.nan))) if v.any() else np.nan,
            "dif_1-16": float(np.nanmean(np.where(v, m["dif_1-16"][i], np.nan))) if v.any() else np.nan,
            "p_recessao_1-16": float(m["recessao_1-16"][i].mean()),
            "frac_valida": float(v.mean()),
            "pi_final_med": float(np.nanmedian(sub["pi"][:, -8:].mean(axis=1))),
            "d_final_med": float(np.nanmedian(sub["d_gross"][:, -1])),
            "total_efetivo": float(sum(aloc.values())), "mult_medio": float(mult),
            **{f"x_{kk}": float(aloc.get(kk, 0.0)) for kk in ITENS},
        })
    return linhas


def _avaliar_lote(lote, p_base, cfg, espec, choques, lams):
    if "R" not in R.GUARDAR:  # workers do joblib não executam o topo do módulo quando rodado com -m
        R.GUARDAR = R.GUARDAR + ("R",)
    cache: dict = {}
    out = []
    for cid, c in lote:
        try:
            for l in avaliar(c, p_base, cfg, espec, choques, lams, cache):
                out.append({"id": cid, **l, **{f"c_{k}": v for k, v in c.items() if k != "pesos"}})
        except Exception as e:  # noqa: BLE001 — registra e segue
            log.warning("combinação %s falhou: %s", cid, e)
    return out


def rodar(combos: dict, p_base, cfg, espec, choques, lams, jobs: int, lote: int = 50) -> pd.DataFrame:
    itens = list(combos.items())
    lotes = [itens[i:i + lote] for i in range(0, len(itens), lote)]
    res = Parallel(n_jobs=jobs)(delayed(_avaliar_lote)(l, p_base, cfg, espec, choques, lams) for l in lotes)
    return pd.DataFrame([x for r in res for x in r])


def pontuar(df: pd.DataFrame, chave: str = "p_bil") -> pd.DataFrame:
    """Uma linha por combinação: sucesso médio em λ = 0,1–0,3 e em 0,3, custo em atividade a λ = 0,3."""
    g = df.groupby("id")
    s = pd.DataFrame({"p_med": g[chave].mean(), "p_03": df[df["lambda"] == 0.3].set_index("id")[chave],
                      "p_01": df[df["lambda"] == 0.1].set_index("id")[chave],
                      "dif16_03": df[df["lambda"] == 0.3].set_index("id")["dif_1-16"],
                      "dif16_01": df[df["lambda"] == 0.1].set_index("id")["dif_1-16"]})
    return s


def fronteira(s: pd.DataFrame, x: str = "p_med", y: str = "dif16_03") -> pd.Index:
    """Combinações não dominadas (maior sucesso e maior atividade)."""
    v = s[[x, y]].dropna().sort_values([x, y], ascending=False)
    melhor, keep = -np.inf, []
    for i, r in v.iterrows():
        if r[y] > melhor:
            keep.append(i)
            melhor = r[y]
    return pd.Index(keep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n1", type=int, default=6000)
    ap.add_argument("--n2", type=int, default=1500)
    ap.add_argument("--N1", type=int, default=200)
    ap.add_argument("--final", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    SAIDA.mkdir(parents=True, exist_ok=True)
    p = modelo.carregar_calibracao(RAIZ / "config" / "calibracao.yaml")
    cfg = yaml.safe_load((RAIZ / "config" / "cenarios.yaml").read_text(encoding="utf-8"))
    choques = varredura.sortear_choques(p, 1000, cfg["horizonte"], 42)
    rng = np.random.default_rng(a.seed)
    # referências: pacote base em A e C sem piso, para comparação
    combos = {f"r{i:05d}": sortear(rng) for i in range(a.n1)}
    log.info("fase 1: %d combinações", len(combos))
    d1 = rodar(combos, p, cfg, "P2", choques[:a.N1], LAMS, a.jobs)
    d1.to_csv(SAIDA / "fase1.csv", index=False)
    s1 = pontuar(d1)
    # fase 2: mutações em torno das 60 melhores (sucesso médio, desempate por atividade) e da fronteira
    top = s1.sort_values(["p_med", "dif16_03"], ascending=False).head(60).index.union(fronteira(s1))
    filhos = {}
    for j in range(a.n2):
        pai = top[j % len(top)]
        filhos[f"m{j:05d}"] = mutar(combos[pai], rng, 0.15 if j < a.n2 // 2 else 0.3)
    combos.update(filhos)
    log.info("fase 2: %d mutações", len(filhos))
    d2 = rodar(filhos, p, cfg, "P2", choques[:a.N1], LAMS, a.jobs)
    d2.to_csv(SAIDA / "fase2.csv", index=False)
    s12 = pontuar(pd.concat([d1, d2]))
    # finalistas: melhores por sucesso, fronteira sucesso × atividade e melhores com sucesso ≥ 50% e menor custo
    fin = list(s12.sort_values(["p_med", "dif16_03"], ascending=False).head(a.final // 2).index)
    fin += [i for i in fronteira(s12) if i not in fin]
    bons = s12[s12["p_03"] >= 0.5].sort_values("dif16_03", ascending=False)
    fin += [i for i in bons.index if i not in fin][: a.final // 2]
    fin = fin[: int(a.final * 1.5)]
    log.info("fase 3: %d finalistas em P1, P2, P3 com N = 1000", len(fin))
    lams_f = [0.1, 0.15, 0.2, 0.25, 0.3]
    d3 = pd.concat([rodar({i: combos[i] for i in fin}, p, cfg, e, choques, lams_f, a.jobs, lote=4)
                    for e in ("P1", "P2", "P3_theta05")])
    d3.to_csv(SAIDA / "fase3_finalistas.csv", index=False)
    (SAIDA / "combinacoes.json").write_text(json.dumps(combos), encoding="utf-8")
    (SAIDA / "execucao.json").write_text(json.dumps({"n1": a.n1, "n2": a.n2, "N1": a.N1, "seed": a.seed,
                                                     "tetos": TETO, "lams_triagem": LAMS, "lams_final": lams_f}),
                                         encoding="utf-8")
    log.info("pronto: %s", SAIDA)


if __name__ == "__main__":
    main()
