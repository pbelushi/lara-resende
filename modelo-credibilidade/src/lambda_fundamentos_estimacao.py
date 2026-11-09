"""Canal de fundamentos na credibilidade: estimação no painel do Focus (Brasil, 2005–2025, trimestral).

logit(credibilidade_t) = a + β_s·(s − s_estab)_{t−1} + β_d·(d − 70)_{t−1} + β_R·reservas_{t−1} + e_t

- s − s_estab: primário do setor público consolidado (12 meses, % do PIB) menos o primário que estabiliza a
  dívida bruta em termos reais, (r − g)/(1 + g)·d, com r = Selic menos a expectativa de inflação do Focus (média
  de 4 trimestres) e g = crescimento tendencial. A versão nominal ((i − γ)/(1 + γ)·d, com γ observado) é
  reportada como robustez: ela sobe quando a inflação surpreende, o que contamina a relação com a credibilidade
  da meta. Nenhuma das duas depende da meta de primário (sem contaminação pelas revisões).
- d: dívida bruta do governo geral (% do PIB).
- reservas: reservas internacionais em % do PIB.

Credibilidades: índice de de Mendonça (meta de inflação) e índice de cumprimento esperado da meta de primário
(fiscal), do Focus, truncados em [0,05; 0,95] antes do logit. Duas especificações: nível com erros HAC
(4 defasagens) e primeiras diferenças (Δlogit sobre Δfundamentos), que elimina tendências comuns.

O logit é a escala em que o canal entra no simulador: λ_efetivo = logística(logit(λ_reputação) + Σ β·Δx).

Uso: python -m src.lambda_fundamentos_estimacao
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

from . import modelo
from .credibilidade_focus import SAIDA as S_PI
from .credibilidade_fiscal_focus import SAIDA as S_F
from .credibilidades_separadas import RAIZ

SAIDA = S_PI.parent / "lambda_fundamentos"
VARS = ["gap_s", "div", "res"]


def fundamentos() -> pd.DataFrame:
    p = pd.read_csv(RAIZ / "data" / "processed" / "trimestral.csv", index_col=0, parse_dates=True)
    i4 = p["selic"].rolling(4).mean()
    s_est = modelo.s_estabilizador(i4, p["gamma"], p["dbgg"])
    # versão real: juro real ex ante (Selic − expectativa do Focus) e crescimento tendencial; a versão nominal com o
    # γ observado sobe mecanicamente quando a inflação surpreende (γ alto → estabilizador baixo), o que mistura o
    # choque de inflação com o fundamento fiscal
    r4 = (p["selic"] - p["pi_e"]).rolling(4).mean()
    g_t = p["g_tend"]
    s_est_r = (r4 - g_t) / (100 + g_t) * p["dbgg"]
    f = pd.DataFrame({"s": p["s_spc"], "s_estab": s_est, "gap_s_nominal": p["s_spc"] - s_est,
                      "s_estab_real": s_est_r, "gap_s": p["s_spc"] - s_est_r, "div": p["dbgg"] - 70.0,
                      "res": 100 * p["reservas_bi"] * p["cambio"] / p["pib_12m_bi"]})
    f.index = f.index.to_period("Q").to_timestamp()
    return f


def credibilidades() -> pd.DataFrame:
    pi = pd.read_csv(S_PI / "credibilidade_focus_mensal.csv", index_col=0, parse_dates=True)
    fi = pd.read_csv(S_F / "credibilidade_fiscal_mensal.csv", index_col=0, parse_dates=True)
    c = pd.DataFrame({"meta": pi["icbc"], "fiscal": fi["icf"]}).resample("QS").mean()
    return c


def logit(x):
    x = np.clip(x, 0.05, 0.95)
    return np.log(x / (1 - x))


def ajustar(y, X, hac=4):
    m = pd.concat([y.rename("y"), X], axis=1).dropna()
    fit = sm.OLS(m["y"], sm.add_constant(m[X.columns])).fit(cov_type="HAC", cov_kwds={"maxlags": hac})
    return fit, len(m)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    f, c = fundamentos(), credibilidades()
    d = c.join(f, how="inner").loc["2005":"2025"]
    lag = f[VARS + ["gap_s_nominal", "s"]].shift(1).reindex(d.index)
    linhas = []
    for alvo in ("meta", "fiscal"):
        y = logit(d[alvo])
        for espec, (yy, XX) in {"nivel": (y, lag), "diferencas": (y.diff(), lag.diff())}.items():
            for conj in (VARS, ["gap_s"], ["gap_s", "div"], ["gap_s_nominal", "div", "res"], ["s", "div", "res"]):
                fit, n = ajustar(yy, XX[conj])
                linhas.append({"alvo": alvo, "especificacao": espec, "regressores": "+".join(conj), "n": n,
                               "r2": round(fit.rsquared, 3),
                               **{f"b_{k}": round(float(fit.params[k]), 4) for k in conj},
                               **{f"p_{k}": round(float(fit.pvalues[k]), 3) for k in conj}})
    e = pd.DataFrame(linhas)
    e.to_csv(SAIDA / "estimativas.csv", index=False)
    d.join(lag.add_suffix("_lag")).to_csv(SAIDA / "painel.csv")
    pd.set_option("display.width", 250)
    print(d[VARS + ["gap_s_nominal", "meta", "fiscal"]].iloc[::4].round(2).to_string())
    print(e.to_string(index=False))
    (SAIDA / "estimativas.json").write_text(json.dumps(linhas, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
