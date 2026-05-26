"""
Treino do modelo baseline: Regressão Logística com regularização L2
Avalia em teste1, depois retreina com treino+teste1 e avalia em teste2
Salva métricas e gráficos em resultados/regressao_logistica/
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    f1_score, precision_score, recall_score, accuracy_score,
    confusion_matrix, ConfusionMatrixDisplay,
)
from sklearn.model_selection import learning_curve

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from pipeline.preditores import TODOS_PREDITORES, ALVO
from pipeline.preprocessor import TuberculosePreprocessor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT_DIR = os.path.join(ROOT, "resultados", "regressao_logistica")
os.makedirs(OUT_DIR, exist_ok=True)


def carregar(nome):
    caminho = os.path.join(ROOT, nome)
    df = pd.read_csv(caminho, low_memory=False)
    X = df[TODOS_PREDITORES]
    y = df[ALVO]
    return X, y


def threshold_otimo(y_true, probs):
    # Encontra o threshold que maximiza o F1.
    thresholds = np.arange(0.10, 0.90, 0.01)
    melhor_f1, melhor_t = 0, 0.5
    for t in thresholds:
        preds = (probs >= t).astype(int)
        f = f1_score(y_true, preds, zero_division=0)
        if f > melhor_f1:
            melhor_f1, melhor_t = f, t
    return melhor_t


def avaliar(nome_etapa, modelo, X, y, threshold, salvar=True):
    probs = modelo.predict_proba(X)[:, 1]
    preds = (probs >= threshold).astype(int)

    metricas = {
        "etapa": nome_etapa,
        "acuracia": accuracy_score(y, preds),
        "precisao": precision_score(y, preds, zero_division=0),
        "recall": recall_score(y, preds, zero_division=0),
        "f1": f1_score(y, preds, zero_division=0),
        "roc_auc": roc_auc_score(y, probs),
        "threshold": threshold,
    }
    print(f"\n=== {nome_etapa} ===")
    print(classification_report(y, preds, target_names=["Conclui", "Abandona"]))
    print(f"ROC-AUC: {metricas['roc_auc']:.4f} | Threshold usado: {threshold:.2f}")

    if salvar:
        # Curva ROC
        fpr, tpr, _ = roc_curve(y, probs)
        plt.figure(figsize=(7, 5))
        plt.plot(fpr, tpr, label=f"AUC = {metricas['roc_auc']:.3f}", linewidth=2)
        plt.plot([0, 1], [0, 1], "k--")
        plt.xlabel("Taxa de Falso Positivo")
        plt.ylabel("Taxa de Verdadeiro Positivo")
        plt.title(f"Curva ROC — {nome_etapa}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, f"roc_{nome_etapa}.png"), dpi=150)
        plt.close()

        # Matriz de confusão
        cm = confusion_matrix(y, preds)
        disp = ConfusionMatrixDisplay(cm, display_labels=["Conclui", "Abandona"])
        fig, ax = plt.subplots(figsize=(5, 4))
        disp.plot(ax=ax, colorbar=False)
        ax.set_title(f"Matriz de Confusão — {nome_etapa}")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, f"confusao_{nome_etapa}.png"), dpi=150)
        plt.close()

    return metricas


def curva_aprendizado(pipe, X, y):
    tamanhos, train_sc, val_sc = learning_curve(
        pipe, X, y,
        cv=5, scoring="roc_auc",
        train_sizes=np.linspace(0.1, 1.0, 8),
        n_jobs=-1,
    )
    plt.figure(figsize=(8, 5))
    plt.plot(tamanhos, train_sc.mean(axis=1), label="Treino")
    plt.plot(tamanhos, val_sc.mean(axis=1), label="Validação (CV)")
    plt.fill_between(tamanhos, train_sc.mean(1) - train_sc.std(1),
                     train_sc.mean(1) + train_sc.std(1), alpha=0.15)
    plt.fill_between(tamanhos, val_sc.mean(1) - val_sc.std(1),
                     val_sc.mean(1) + val_sc.std(1), alpha=0.15)
    plt.xlabel("Tamanho do conjunto de treino")
    plt.ylabel("ROC-AUC")
    plt.title("Curva de Aprendizado — Regressão Logística")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "curva_aprendizado.png"), dpi=150)
    plt.close()


def main():
    print("Carregando dados...")
    X_treino, y_treino = carregar("treino.csv")
    X_teste1, y_teste1 = carregar("teste1.csv")
    X_teste2, y_teste2 = carregar("teste2.csv")

    pipe = Pipeline([
        ("prep", TuberculosePreprocessor()),
        ("clf", LogisticRegression(C=0.1, max_iter=1000,
                                   class_weight="balanced", random_state=42)),
    ])

    print("\nTreinando modelo...")
    pipe.fit(X_treino, y_treino)

    curva_aprendizado(pipe, X_treino, y_treino)

    probs_treino = pipe.predict_proba(X_treino)[:, 1]
    t_otimo = threshold_otimo(y_treino, probs_treino)
    print(f"\nThreshold ótimo (F1 no treino): {t_otimo:.2f}")

    resultados = []
    resultados.append(avaliar("treino", pipe, X_treino, y_treino, t_otimo))
    resultados.append(avaliar("teste1", pipe, X_teste1, y_teste1, t_otimo))

    print("\nRetreino com treino + teste1...")
    X_retreino = pd.concat([X_treino, X_teste1])
    y_retreino = pd.concat([y_treino, y_teste1])
    pipe.fit(X_retreino, y_retreino)

    probs_retreino = pipe.predict_proba(X_retreino)[:, 1]
    t_final = threshold_otimo(y_retreino, probs_retreino)

    resultados.append(avaliar("teste2_final", pipe, X_teste2, y_teste2, t_final))

    df_res = pd.DataFrame(resultados)
    df_res.to_csv(os.path.join(OUT_DIR, "metricas.csv"), index=False)
    print(f"\nResultados salvos em: {OUT_DIR}")
    print(df_res.to_string(index=False))


if __name__ == "__main__":
    main()
