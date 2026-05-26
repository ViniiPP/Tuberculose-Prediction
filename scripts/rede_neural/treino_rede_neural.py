"""
Treino da Rede Neural com MLPClassifier (scikit-learn)
Múltiplas camadas, regularização L2 e early stopping
Avalia em teste1, retreina com treino+teste1, avalia em teste2
Salva métricas e gráficos em resultados/rede_neural/
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    f1_score, precision_score, recall_score, accuracy_score,
    confusion_matrix, ConfusionMatrixDisplay,
)

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from pipeline.preditores import TODOS_PREDITORES, ALVO
from pipeline.preprocessor import TuberculosePreprocessor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT_DIR = os.path.join(ROOT, "resultados", "rede_neural")
os.makedirs(OUT_DIR, exist_ok=True)


def carregar(nome):
    df = pd.read_csv(os.path.join(ROOT, nome), low_memory=False)
    X = df[TODOS_PREDITORES]
    y = df[ALVO].values
    return X, y


def threshold_otimo(y_true, probs):
    thresholds = np.arange(0.10, 0.90, 0.01)
    melhor_f1, melhor_t = 0, 0.5
    for t in thresholds:
        preds = (probs >= t).astype(int)
        f = f1_score(y_true, preds, zero_division=0)
        if f > melhor_f1:
            melhor_f1, melhor_t = f, t
    return melhor_t


def avaliar(nome_etapa, modelo, X_arr, y_arr, threshold):
    probs = modelo.predict_proba(X_arr)[:, 1]
    preds = (probs >= threshold).astype(int)

    metricas = {
        "etapa": nome_etapa,
        "acuracia": accuracy_score(y_arr, preds),
        "precisao": precision_score(y_arr, preds, zero_division=0),
        "recall": recall_score(y_arr, preds, zero_division=0),
        "f1": f1_score(y_arr, preds, zero_division=0),
        "roc_auc": roc_auc_score(y_arr, probs),
        "threshold": threshold,
    }
    print(f"\n=== {nome_etapa} ===")
    print(classification_report(y_arr, preds, target_names=["Conclui", "Abandona"]))
    print(f"ROC-AUC: {metricas['roc_auc']:.4f} | Threshold: {threshold:.2f}")

    fpr, tpr, _ = roc_curve(y_arr, probs)
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"AUC = {metricas['roc_auc']:.3f}", linewidth=2)
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("Taxa de Falso Positivo")
    plt.ylabel("Taxa de Verdadeiro Positivo")
    plt.title(f"Curva ROC — Rede Neural — {nome_etapa}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"roc_{nome_etapa}.png"), dpi=150)
    plt.close()

    cm = confusion_matrix(y_arr, preds)
    disp = ConfusionMatrixDisplay(cm, display_labels=["Conclui", "Abandona"])
    fig, ax = plt.subplots(figsize=(5, 4))
    disp.plot(ax=ax, colorbar=False)
    ax.set_title(f"Matriz de Confusão — {nome_etapa}")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"confusao_{nome_etapa}.png"), dpi=150)
    plt.close()

    return metricas


def salvar_curva_loss(modelo, nome):
    if not hasattr(modelo, "loss_curve_"):
        return
    plt.figure(figsize=(8, 4))
    plt.plot(modelo.loss_curve_, label="Treino")
    if hasattr(modelo, "validation_fraction") and modelo.early_stopping:
        plt.plot(modelo.validation_scores_, label="Validação")
    plt.xlabel("Época")
    plt.ylabel("Loss")
    plt.title(f"Curva de Aprendizado — {nome}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"curva_aprendizado_{nome}.png"), dpi=150)
    plt.close()


def main():
    print("Carregando dados...")
    X_treino_raw, y_treino = carregar("treino.csv")
    X_teste1_raw, y_teste1 = carregar("teste1.csv")
    X_teste2_raw, y_teste2 = carregar("teste2.csv")

    print("Pré-processando (fase 1)...")
    prep = TuberculosePreprocessor()
    X_treino = prep.fit_transform(X_treino_raw, y_treino)
    X_teste1 = prep.transform(X_teste1_raw)
    X_teste2 = prep.transform(X_teste2_raw)

    modelo = MLPClassifier(
        hidden_layer_sizes=(128, 64, 32),
        activation="relu",
        alpha=1e-4,             # regularização L2
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=15,
        max_iter=300,
        random_state=42,
        verbose=True,
    )

    print("\nTreinando rede neural...")
    modelo.fit(X_treino, y_treino)
    salvar_curva_loss(modelo, "fase1")

    probs_treino = modelo.predict_proba(X_treino)[:, 1]
    t_otimo = threshold_otimo(y_treino, probs_treino)
    print(f"\nThreshold ótimo: {t_otimo:.2f}")

    resultados = []
    resultados.append(avaliar("treino", modelo, X_treino, y_treino, t_otimo))
    resultados.append(avaliar("teste1", modelo, X_teste1, y_teste1, t_otimo))

    print("\nRetreino com treino + teste1...")
    X_treino_raw2 = pd.concat([X_treino_raw, X_teste1_raw])
    y_treino2 = np.concatenate([y_treino, y_teste1])

    prep2 = TuberculosePreprocessor()
    X_retreino = prep2.fit_transform(X_treino_raw2, y_treino2)
    X_teste2_proc = prep2.transform(X_teste2_raw)

    modelo2 = MLPClassifier(
        hidden_layer_sizes=(128, 64, 32),
        activation="relu",
        alpha=1e-4,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=15,
        max_iter=300,
        random_state=42,
        verbose=True,
    )
    modelo2.fit(X_retreino, y_treino2)
    salvar_curva_loss(modelo2, "fase2_retreino")

    probs_retreino = modelo2.predict_proba(X_retreino)[:, 1]
    t_final = threshold_otimo(y_treino2, probs_retreino)

    resultados.append(avaliar("teste2_final", modelo2, X_teste2_proc, y_teste2, t_final))

    df_res = pd.DataFrame(resultados)
    df_res.to_csv(os.path.join(OUT_DIR, "metricas.csv"), index=False)
    print(f"\nResultados salvos em: {OUT_DIR}")
    print(df_res.to_string(index=False))


if __name__ == "__main__":
    main()
