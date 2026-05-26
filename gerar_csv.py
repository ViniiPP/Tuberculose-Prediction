
# Gera o arquivo resultados_modelo.csv para uso no dashboard de apresentação
# Execute APÓS rodar pipeline/pipeline_final.py

import sys
import os
import pandas as pd
import numpy as np
import joblib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline.preditores import TODOS_PREDITORES, ALVO, THRESHOLD_BAIXO, THRESHOLD_ALTO, THRESHOLD_CLASSIFICACAO

prep   = joblib.load("pipeline/modelo/preprocessador.joblib")
modelo = joblib.load("pipeline/modelo/modelo_final.joblib")

df   = pd.read_csv("teste2.csv")
X    = prep.transform(df[TODOS_PREDITORES])
y    = df[ALVO].values
prob = modelo.predict_proba(X)[:, 1]

def nivel_risco(p):
    if p >= THRESHOLD_ALTO:
        return "alto"
    if p >= THRESHOLD_BAIXO:
        return "medio"
    return "baixo"

resultado = pd.DataFrame({
    "id":                range(1, len(df) + 1),
    "probabilidade_ltfu": prob.round(4),
    "nivel_risco":        [nivel_risco(p) for p in prob],
    "predicao_modelo":    ["abandona" if p >= THRESHOLD_CLASSIFICACAO else "conclui" for p in prob],
    "resultado_real":     ["abandona" if r == 1 else "conclui" for r in y],
})

resultado.to_csv("resultados_modelo.csv", index=False)
print(f"Salvo: resultados_modelo.csv ({len(resultado)} pacientes)")
