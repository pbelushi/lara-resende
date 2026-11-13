"""Pacote aprovado pelo Senado com a base do PLOA 2027: soma ao pacote (0,346% do PIB) a diferença de ~0,61 p.p. entre
o primário do governo central projetado no PLOA 2027 antes do pacote (0,13% do PIB; MPO, audiência na CMO, nov/2026)
e o do cenário sem ajuste do modelo (≈ -0,48% no governo central em 2027). Uso: python -m src.pacote_senado_2026_base_oficial
"""
import copy, numpy as np, pandas as pd, yaml
from src import modelo, varredura
from src import recessivo as R
from src.busca_contra_mercado import HOSTIL
from src.credibilidades_separadas import RAIZ, simular_combo
from src.lambda_dinamico_aplicacao import CENTRAL
from src.pacote_governo_2026 import PIB27
from src.pacote_governo_2026_diagnostico import medir
from src.pacote_senado_2026 import combo_senado
N=1000
p=modelo.carregar_calibracao(RAIZ/"config"/"calibracao.yaml")
cfg=yaml.safe_load((RAIZ/"config"/"cenarios.yaml").read_text(encoding="utf-8"))
for k in ("R","s"):
    if k not in R.GUARDAR: R.GUARDAR=R.GUARDAR+(k,)
ch=varredura.sortear_choques(p,N,cfg["horizonte"],42)
lpb=np.random.default_rng(2027).uniform(0.2,0.5,N); lph=np.random.default_rng(2027).uniform(0.0,0.3,N)
G=[("baixa, regra central",lpb,(0.2,0.35,0.5),CENTRAL,0.0),("hostil",lph,(0,0.15,0.3),HOSTIL,0.0),("hostil, θ = 0,32",lph,(0,0.15,0.3),HOSTIL,0.32)]
rows=[]
for tot in (0.346, 0.956):
  c=combo_senado(tot*PIB27/100)
  for g,lp,lfs,regra,th in G:
    v=[]
    for lf in lfs:
      q0=copy.deepcopy(p); q0["dinamica_lambda"],q0["indexacao_meta"]=regra,th
      tr,q,_=simular_combo(c,q0,cfg,"P2",ch,lp,np.full(N,lf)); v.append(medir(tr,q))
    rows.append({"total":tot,"grupo":g,**pd.DataFrame(v).mean().round(3).to_dict()})
d=pd.DataFrame(rows); d.to_csv(RAIZ/"outputs"/"v2_2"/"pacote_senado_2026"/"base_oficial.csv",index=False); print(d.to_string(index=False))
