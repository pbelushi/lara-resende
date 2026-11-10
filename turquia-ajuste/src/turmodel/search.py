"""
Busca aleatória de políticas para a Turquia a partir de set/2021, com a credibilidade abalada (λ0 calibrado).

Pergunta: dado o ponto de partida de 2021 (inflação de 19%, juro real zero, reservas líquidas negativas, λ baixo),
a melhor saída era o aperto anticíclico tradicional ou havia espaço para uma solução heterodoxa diferente da adotada?
Sem reservas, não há âncora cambial: o câmbio flutua em todos os cenários alternativos.

Espaço sorteado:
- juros: juro real ex ante de r0 (início) a r1 (após `meses`), de −5% a +20%, mais uma reação de 0 a 1 ponto por
  ponto de inflação acima da âncora; a taxa nominal segue a inflação esperada;
- âncora anunciada: meta de 5% imediata ou trajetória de desinflação de 19% para 5% em 12 a 60 meses;
- fiscal: ajuste de 0 a 5% do PIB (em relação ao observado), multiplicador de 0,3 (qualidade) a 1,0 (demanda),
  início e rampa, parcela via impostos indiretos (que sobe preços);
- preços administrados reajustados pela âncora (θ de 0 a 0,4);
- salário mínimo: reajuste por regra entre a inflação passada (θw = 0) e a âncora (θw = 1), com ganho real de 0 a 5%;
- reservas: o banco central compra dólares para impedir apreciação real acima de 0 a 1% ao mês em relação à
  trajetória da âncora (recompõe reservas e evita a espiral deflacionária de câmbio).

Resultados por combinação: inflação em 12 meses (dez/22, dez/23, dez/24, set/26), pico, probabilidades, PIB acumulado
em relação à política observada (mesmos choques), salário mínimo real, reservas e dívida.
Sucesso: pico de inflação ≤ 30% e inflação entre 0% e 10% em set/2026 (deflação não conta como sucesso).

Uso:  PYTHONPATH=src python -m turmodel.search
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from .model import MESES, ROOT, T, idx, politica_observada, simulate

OUT = ROOT / "outputs" / "busca"
VARIANTES = ("A_inercia_baixa", "B_inercia_alta")
LAMBDA0 = (0.0, 0.3)     # a calibração dá λ0 entre 0 e 0,12; as alternativas partem de λ0 ~ U(0; 0,3)
MESES_MINIMO = [idx(m) for m in ("2022-01", "2022-07", "2023-01", "2023-07", "2024-01", "2025-01", "2026-01")]


def carregar(variante: str) -> dict:
    return yaml.safe_load((ROOT / "config" / f"params_calibrated_{variante}.yaml").read_text(encoding="utf-8"))


def ancora(t_dis: int) -> np.ndarray:
    if t_dis <= 0:
        return np.full(T + 1, 5.0)
    return np.interp(np.arange(T + 1), [0, t_dis], [19.0, 5.0])


def politica(c: dict) -> dict:
    adj = np.zeros(T + 1)
    if c["ajuste"] > 0:
        adj = np.clip((np.arange(T + 1) - c["inicio"] + 1) / c["rampa"], 0, 1) * c["ajuste"]
    theta = np.clip(np.arange(T + 1) / 6, 0, 1) * c["theta"]
    return {"nome": c.get("nome", ""), "real": {"r0": c["r0"], "r1": c["r1"], "meses": c["meses"], "reacao": c["reacao"]},
            "adj": adj, "mult": c["mult"], "tax": c["tax"], "theta": theta, "anchor": ancora(c["t_dis"]),
            "wage": {"modo": "regra", "meses": MESES_MINIMO, "theta_w": c["theta_w"], "ganho": c["ganho"]},
            "jump": np.r_[0.0, c.get("salto", 0.0), np.zeros(T - 1)], "kkm": np.zeros(T + 1),
            "compra_reservas": c["compra"]}


def sortear(rng: np.random.Generator) -> dict:
    return {"r0": float(rng.uniform(-5, 20)), "r1": float(rng.uniform(-5, 12)), "meses": int(rng.integers(6, 37)),
            "reacao": float(rng.uniform(0, 1.0)), "t_dis": int(rng.choice([0, 12, 24, 36, 48, 60])),
            "ajuste": float(rng.uniform(0, 5)) if rng.random() < 0.7 else 0.0, "inicio": int(rng.integers(1, 7)),
            "rampa": int(rng.integers(1, 19)), "mult": float(rng.uniform(0.3, 1.0)),
            "tax": float(rng.uniform(0, 0.5)) if rng.random() < 0.4 else 0.0,
            "theta": float(rng.uniform(0, 0.4)) if rng.random() < 0.6 else 0.0,
            "theta_w": float(rng.uniform(0, 1)), "ganho": float(rng.uniform(0, 0.05)),
            "compra": float(rng.uniform(0, 0.01))}


REFERENCIAS = {
    # aperto anticíclico tradicional: juro real alto e contração de demanda (corte de gasto de multiplicador alto)
    "ref_anticiclica": {"r0": 10.0, "r1": 6.0, "meses": 24, "reacao": 0.5, "t_dis": 36, "ajuste": 2.0, "inicio": 1, "rampa": 6,
                        "mult": 0.9, "tax": 0.0, "theta": 0.0, "theta_w": 0.0, "ganho": 0.0, "compra": 0.005},
    # só juros: aperto monetário sem ajuste fiscal
    "ref_so_juros": {"r0": 10.0, "r1": 6.0, "meses": 24, "reacao": 0.5, "t_dis": 36, "ajuste": 0.0, "inicio": 1, "rampa": 6,
                     "mult": 0.6, "tax": 0.0, "theta": 0.0, "theta_w": 0.0, "ganho": 0.0, "compra": 0.005},
    # heterodoxa: ajuste de qualidade (baixo multiplicador), juro real pouco acima do neutro e queda gradual da taxa
    # nominal com a inflação, administrados e salário mínimo reajustados pela trajetória anunciada
    "ref_heterodoxa": {"r0": 3.0, "r1": 2.0, "meses": 24, "reacao": 0.5, "t_dis": 36, "ajuste": 3.0, "inicio": 1, "rampa": 6,
                       "mult": 0.35, "tax": 0.0, "theta": 0.25, "theta_w": 0.5, "ganho": 0.0, "compra": 0.005},
    # heterodoxa sem política de rendas: só ajuste de qualidade e juro real perto do neutro
    "ref_fiscal_qualidade": {"r0": 3.0, "r1": 2.0, "meses": 24, "reacao": 0.5, "t_dis": 36, "ajuste": 3.0, "inicio": 1, "rampa": 6,
                             "mult": 0.35, "tax": 0.0, "theta": 0.0, "theta_w": 0.0, "ganho": 0.0, "compra": 0.005},
    # juro real zero mantido (não corta nem sobe em termos reais) com ajuste de qualidade
    "ref_juro_real_zero": {"r0": 0.0, "r1": 0.0, "meses": 12, "reacao": 0.5, "t_dis": 36, "ajuste": 3.0, "inicio": 1, "rampa": 6,
                           "mult": 0.35, "tax": 0.0, "theta": 0.25, "theta_w": 0.5, "ganho": 0.0, "compra": 0.005},
}


def metricas(X: dict, O: dict) -> dict:
    yoy = X["yoy"]
    fim, pico = yoy[:, T], yoy[:, 1:].max(axis=1)
    pib = (X["ly"][:, 1:] - O["ly"][:, 1:]).sum(axis=1) / 12 * 100          # pontos do PIB de um ano, set/21–set/26
    pib24 = (X["ly"][:, 1:idx("2023-08") + 1] - O["ly"][:, 1:idx("2023-08") + 1]).sum(axis=1) / 12 * 100
    ok = (pico <= 30) & (fim <= 10) & (fim >= 0)
    med = lambda v: float(np.median(v))  # noqa: E731
    return {"p_sucesso": float(ok.mean()), "p_fim_le_10": float((fim <= 10).mean()),
            "p_fim_banda": float(((fim <= 10) & (fim >= 0)).mean()), "p_deflacao": float((fim < 0).mean()),
            "p_pico_le_30": float((pico <= 30).mean()), "p_fim_le_15": float((fim <= 15).mean()),
            "infl_dez22": med(yoy[:, idx("2022-12")]), "infl_dez23": med(yoy[:, idx("2023-12")]),
            "infl_dez24": med(yoy[:, idx("2024-12")]), "infl_set26": med(fim), "infl_pico": med(pico),
            "pib_vs_obs": med(pib), "pib_vs_obs_2a": med(pib24), "hiato_min": med(X["y"].min(axis=1)),
            "cambio_set26": med(np.exp(np.minimum(X["e"][:, T], 20.0))), "salario_min_real_set26": med(X["w_real"][:, T] - O["w_real"][:, T]) * 100,
            "reservas_min": med(X["R"].min(axis=1)), "reservas_set26": med(X["R"][:, T]), "divida_set26": med(X["d"][:, T]),
            "juro_nominal_medio_1a": med(X["i"][:, 1:13].mean(axis=1)), "juro_real_medio": med(X["r"][:, 1:].mean(axis=1)),
            "lambda_set26": med(X["lam"][:, T])}


def avaliar(itens, variante: str, n: int, seed: int = 7):
    p = carregar(variante)
    obs = politica_observada(p)
    base = simulate(p, obs, n=1, stochastic=False)
    O = simulate(p, obs, n=n, seed=seed, base=None)
    out = []
    lam0 = np.random.default_rng(2027).uniform(*LAMBDA0, n)      # credibilidade inicial abalada, por trajetória
    for cid, c in itens:
        X = simulate(p, {**politica(c), "lambda0": lam0}, n=n, seed=seed, base=base)
        out.append({"id": cid, "variante": variante, **c, **metricas(X, O)})
    return out


def rodar(combos: dict, variante: str, n: int, jobs: int = 2, lote: int = 100) -> pd.DataFrame:
    it = list(combos.items())
    res = Parallel(n_jobs=jobs)(delayed(avaliar)(it[i:i + lote], variante, n) for i in range(0, len(it), lote))
    return pd.DataFrame([x for r in res for x in r])


def observada(variante: str, n: int = 1000) -> dict:
    p = carregar(variante)
    O = simulate(p, politica_observada(p), n=n, seed=7)
    return {"id": "observada", "variante": variante, **metricas(O, O)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n1", type=int, default=6000)
    ap.add_argument("--N1", type=int, default=200)
    ap.add_argument("--final", type=int, default=30)
    ap.add_argument("--seed", type=int, default=41)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    combos = {f"c{i:05d}": sortear(rng) for i in range(a.n1)}
    combos.update(REFERENCIAS)
    tri = pd.concat([rodar(combos, v, a.N1) for v in VARIANTES])
    tri.to_csv(OUT / "triagem.csv", index=False)
    # finalistas: robustas nas duas variantes (pior caso de sucesso) e fronteira sucesso × PIB
    piv = tri.pivot_table(index="id", columns="variante", values=["p_sucesso", "pib_vs_obs", "p_fim_le_15"])
    piv.columns = [f"{x}_{y[0]}" for x, y in piv.columns]
    piv["suc_min"] = piv[["p_sucesso_A", "p_sucesso_B"]].min(axis=1)
    piv["pib_min"] = piv[["pib_vs_obs_A", "pib_vs_obs_B"]].min(axis=1)
    fin = list(piv.sort_values("suc_min", ascending=False).head(a.final // 2).index)
    teto = piv["suc_min"].max()
    for frac in (0.6, 0.8, 0.9):
        fin += list(piv[piv["suc_min"] >= frac * teto].sort_values("pib_min", ascending=False).head(5).index)
    fin += list(REFERENCIAS)
    fin = list(dict.fromkeys(fin))
    f = pd.concat([rodar({k: combos[k] for k in fin}, v, 1000, lote=5) for v in VARIANTES])
    f = pd.concat([f, pd.DataFrame([observada(v) for v in VARIANTES])])
    f.to_csv(OUT / "finalistas.csv", index=False)
    (OUT / "combinacoes.json").write_text(json.dumps(combos), encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    cols = ["id", "variante", "p_sucesso", "p_fim_le_15", "infl_pico", "infl_dez23", "infl_set26", "pib_vs_obs",
            "salario_min_real_set26", "juro_nominal_medio_1a", "juro_real_medio", "r0", "r1", "ajuste", "mult", "theta",
            "theta_w", "t_dis"]
    print(f.sort_values(["variante", "p_sucesso"], ascending=[True, False])[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
