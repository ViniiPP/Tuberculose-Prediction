"""
Pipeline final de produção.
Treina o modelo HistGradientBoosting, aplica calibração e salva. Treina com todos os dados (treino + teste1 + teste2)
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.preditores import TODOS_PREDITORES, ALVO, THRESHOLD_BAIXO, THRESHOLD_ALTO
from pipeline.preprocessor import TuberculosePreprocessor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_MODELO = os.path.join(ROOT, "pipeline", "modelo")
os.makedirs(PASTA_MODELO, exist_ok=True)


def carregar(nome):
    df = pd.read_csv(os.path.join(ROOT, nome), low_memory=False)
    return df[TODOS_PREDITORES], df[ALVO].values


def nivel_risco(prob):
    if prob >= THRESHOLD_ALTO:
        return "alto"
    if prob >= THRESHOLD_BAIXO:
        return "medio"
    return "baixo"


def main():
    print("Carregando todos os dados...")
    X_treino, y_treino = carregar("treino.csv")
    X_teste1, y_teste1 = carregar("teste1.csv")
    X_teste2, y_teste2 = carregar("teste2.csv")

    X_total = pd.concat([X_treino, X_teste1, X_teste2])
    y_total = np.concatenate([y_treino, y_teste1, y_teste2])
    print(f"Total: {len(y_total)} amostras | LTFU: {y_total.sum()} ({y_total.mean()*100:.1f}%)")

    print("\nPré-processando...")
    preprocessador = TuberculosePreprocessor()
    X_proc = preprocessador.fit_transform(X_total, y_total)
    print(f"Features: {X_proc.shape[1]}")

    nome_modelo = "HistGradientBoosting"
    modelo_base = HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_depth=6,
        class_weight="balanced",
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
    )
    print(f"\n>> Usando modelo: {nome_modelo}")

    print("\nTreinando modelo final com calibração...")
    modelo_calibrado = CalibratedClassifierCV(modelo_base, cv=5, method="isotonic")
    modelo_calibrado.fit(X_proc, y_total)

    probs_finais = modelo_calibrado.predict_proba(X_proc)[:, 1]
    auc_final = roc_auc_score(y_total, probs_finais)
    print(f"ROC-AUC (treino completo): {auc_final:.4f}")

    niveis = [nivel_risco(p) for p in probs_finais]
    for nivel in ["baixo", "medio", "alto"]:
        n = niveis.count(nivel)
        print(f"  {nivel.capitalize()}: {n} ({n/len(niveis)*100:.1f}%)")

    joblib.dump(preprocessador,   os.path.join(PASTA_MODELO, "preprocessador.joblib"))
    joblib.dump(modelo_calibrado, os.path.join(PASTA_MODELO, "modelo_final.joblib"))
    joblib.dump(nome_modelo,      os.path.join(PASTA_MODELO, "nome_modelo.joblib"))
    print(f"\nModelo '{nome_modelo}' salvo em: {PASTA_MODELO}")


def predict(dados: dict) -> dict:
    preprocessador = joblib.load(os.path.join(ROOT, "pipeline", "modelo", "preprocessador.joblib"))
    modelo         = joblib.load(os.path.join(ROOT, "pipeline", "modelo", "modelo_final.joblib"))

    df   = pd.DataFrame([dados])[TODOS_PREDITORES]
    X    = preprocessador.transform(df)
    prob = float(modelo.predict_proba(X)[0, 1])

    return {
        "probabilidade":     round(prob, 4),
        "probabilidade_pct": round(prob * 100, 1),
        "nivel_risco":       nivel_risco(prob),
    }


if __name__ == "__main__":
    main()
