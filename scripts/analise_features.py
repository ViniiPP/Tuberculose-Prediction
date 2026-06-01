"""
Análise de features: SHAP values, Permutation Importance
Validação Cruzada e Curva de Calibração
Execute APÓS o pipeline_final.py ter sido rodado
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib
import shap
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score, accuracy_score
)

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.preditores import TODOS_PREDITORES, ALVO
from pipeline.preprocessor import TuberculosePreprocessor

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA  = os.path.join(ROOT, "resultados", "analise")
os.makedirs(SAIDA, exist_ok=True)

PASTA_MODELO = os.path.join(ROOT, "pipeline", "modelo")


def carregar_dados():
    dfs = []
    for arquivo in ["treino.csv", "teste1.csv", "teste2.csv"]:
        df = pd.read_csv(os.path.join(ROOT, arquivo), low_memory=False)
        dfs.append(df)
    total = pd.concat(dfs, ignore_index=True)
    return total[TODOS_PREDITORES], total[ALVO].values


def nomes_features(preprocessador):
    nomes = []
    ct = preprocessador._transformador
    for nome, transformador, colunas in ct.transformers_:
        if nome == "ohe":
            enc = transformador.named_steps["encoder"]
            nomes.extend(enc.get_feature_names_out(colunas).tolist())
        else:
            nomes.extend(colunas if isinstance(colunas, list) else [colunas])
    return nomes


def validacao_cruzada(modelo_base, X_proc, y):
    print("\n=== Validação Cruzada (5-fold) ===")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    metricas = {
        "ROC-AUC": "roc_auc",
        "F1": "f1",
        "Precisão": "precision",
        "Recall": "recall",
    }

    resultados = {}

    for nome_metrica, scoring in metricas.items():
        scores = cross_val_score(
            modelo_base,
            X_proc,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=-1
        )

        resultados[nome_metrica] = scores
        print(f"  {nome_metrica}: {scores.mean():.4f} ± {scores.std():.4f}")

    nomes_metricas = list(resultados.keys())
    medias = [resultados[nome].mean() for nome in nomes_metricas]
    desvios = [resultados[nome].std() for nome in nomes_metricas]

    fig, ax = plt.subplots(figsize=(10, 6))

    cores = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6"]

    barras = ax.bar(
        nomes_metricas,
        medias,
        yerr=desvios,
        capsize=8,
        color=cores,
        edgecolor="#1E293B",
        linewidth=1.2,
        alpha=0.9
    )

    ax.set_title(
        "Validação Cruzada — 5-fold (Desempenho do Modelo)",
        fontsize=13,
        fontweight="bold",
        pad=15
    )

    ax.set_ylabel("Score médio", fontsize=10, labelpad=8)
    ax.set_ylim(0, 1)
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    for barra, media, desvio in zip(barras, medias, desvios):
        altura = barra.get_height()

        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura + 0.025,
            f"{media:.3f}\n±{desvio:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold"
        )

    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA, "validacao_cruzada.png"), dpi=150)
    plt.close()

    print("  Gráfico salvo.")
    return resultados


def permutation_importance_plot(modelo, X_proc, y, nomes, amostra=20000):
    print(f"\n=== Permutation Importance (amostra={amostra}) ===")
    if len(X_proc) > amostra:
        np.random.seed(42)
        idx = np.random.choice(len(X_proc), amostra, replace=False)
        X_sub = X_proc[idx]
        y_sub = y[idx]
    else:
        X_sub = X_proc
        y_sub = y

    resultado = permutation_importance(
        modelo, X_sub, y_sub,
        n_repeats=5, random_state=42,
        scoring="roc_auc", n_jobs=-1
    )
    idx = np.argsort(resultado.importances_mean)[::-1][:20]

    fig, ax = plt.subplots(figsize=(10, 6.5))
    importancias = resultado.importances_mean[list(reversed(idx))]
    norm = plt.Normalize(importancias.min() if len(importancias) > 0 else 0, importancias.max() if len(importancias) > 0 else 1)
    cmap = plt.cm.Blues
    cores = cmap(0.3 + 0.5 * norm(importancias))

    ax.barh(
        [nomes[i] for i in reversed(idx)],
        importancias,
        xerr=resultado.importances_std[list(reversed(idx))],
        color=cores, edgecolor='#1E293B', linewidth=0.8, alpha=0.9
    )
    ax.set_xlabel("Redução média no ROC-AUC", fontsize=10, labelpad=8)
    ax.set_title("Permutation Importance — Top 20 Features", fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA, "permutation_importance.png"), dpi=150)
    plt.close()
    print("  Gráfico salvo.")

    # CSV com todas as importâncias
    df_imp = pd.DataFrame({
        "feature":    nomes,
        "importancia": resultado.importances_mean,
        "desvio":     resultado.importances_std,
    }).sort_values("importancia", ascending=False)
    df_imp.to_csv(os.path.join(SAIDA, "permutation_importance.csv"), index=False)
    print("  Top 5 features:")
    print(df_imp.head(5).to_string(index=False))
    return df_imp


def shap_analysis(modelo, X_proc, nomes, amostra=2000):
    print(f"\n=== SHAP Values (amostra={amostra}) ===")
    idx_amostra = np.random.choice(len(X_proc), min(amostra, len(X_proc)), replace=False)
    X_amostra = X_proc[idx_amostra]

    # Extrai o estimador base do CalibratedClassifierCV
    modelo_base = modelo.calibrated_classifiers_[0].estimator
    tipo = type(modelo_base).__name__

    try:
        if "Forest" in tipo or "Gradient" in tipo or "Tree" in tipo:
            explicador = shap.TreeExplainer(modelo_base)
        else:
            explicador = shap.KernelExplainer(
                modelo.predict_proba, shap.sample(X_amostra, 100)
            )

        valores_shap = explicador.shap_values(X_amostra)
        if isinstance(valores_shap, list):
            valores_shap = valores_shap[1]

        # Summary
        plt.figure(figsize=(11, 7.5))
        plt.clf()
        shap.summary_plot(valores_shap, X_amostra,
                          feature_names=nomes, show=False, max_display=20)
        plt.title("SHAP Values — Impacto de cada feature", fontsize=12, fontweight='bold', pad=15)
        plt.savefig(os.path.join(SAIDA, "shap_beeswarm.png"), dpi=150, bbox_inches="tight")
        plt.close()

        # Bar plot
        plt.figure(figsize=(10, 6.5))
        plt.clf()
        shap.summary_plot(valores_shap, X_amostra,
                          feature_names=nomes, plot_type="bar",
                          show=False, max_display=20)
        plt.title("SHAP — Importância Global das Features", fontsize=12, fontweight='bold', pad=15)
        plt.savefig(os.path.join(SAIDA, "shap_barras.png"), dpi=150, bbox_inches="tight")
        plt.close()
        print("  Gráficos SHAP salvos.")
    except Exception as e:
        print(f"  Aviso SHAP: {e}")


def calibration_curve_plot(modelo, X_proc, y):
    print("\n=== Curva de Calibração ===")
    probs = modelo.predict_proba(X_proc)[:, 1]
    frac_pos, media_pred = calibration_curve(y, probs, n_bins=10, strategy="uniform")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Curva de calibração
    axes[0].plot(media_pred, frac_pos, "s-", label="Modelo Calibrado", color="#2563EB", linewidth=2, markersize=6)
    axes[0].plot([0, 1], [0, 1], "k--", label="Perfeitamente calibrado", alpha=0.7)
    axes[0].set_xlabel("Probabilidade prevista", fontsize=10, labelpad=8)
    axes[0].set_ylabel("Fração de positivos reais", fontsize=10, labelpad=8)
    axes[0].set_title("Curva de Calibração", fontsize=11, fontweight='bold', pad=12)
    axes[0].legend(loc="upper left")
    axes[0].grid(linestyle=":", alpha=0.5)
    axes[0].set_xlim(-0.02, 1.02)
    axes[0].set_ylim(-0.02, 1.02)

    # Histograma de probabilidades tricolor
    n, bins, patches = axes[1].hist(probs, bins=30, edgecolor="white", linewidth=0.5, alpha=0.8)
    for i in range(len(patches)):
        bin_center = bins[i]
        if bin_center < 0.30:
            patches[i].set_facecolor('#10B981') # Baixo
        elif bin_center < 0.60:
            patches[i].set_facecolor('#F59E0B') # Médio
        else:
            patches[i].set_facecolor('#EF4444') # Alto

    axes[1].axvline(0.30, color="#D97706", linestyle="--", linewidth=1.5, label="Limite médio (30%)")
    axes[1].axvline(0.60, color="#DC2626", linestyle="--", linewidth=1.5, label="Limite alto (60%)")
    axes[1].set_xlabel("Probabilidade prevista", fontsize=10, labelpad=8)
    axes[1].set_ylabel("Contagem", fontsize=10, labelpad=8)
    axes[1].set_title("Distribuição das Probabilidades", fontsize=11, fontweight='bold', pad=12)
    axes[1].legend(loc="upper right")
    axes[1].grid(linestyle=":", alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA, "calibracao.png"), dpi=150)
    plt.close()
    print("  Gráfico salvo.")
    print(f"  Prob. média: {probs.mean():.3f} | Desvio: {probs.std():.3f}")
    print(f"  % baixo (<30%): {(probs<0.30).mean()*100:.1f}%")
    print(f"  % médio (30-60%): {((probs>=0.30)&(probs<0.60)).mean()*100:.1f}%")
    print(f"  % alto (>=60%): {(probs>=0.60).mean()*100:.1f}%")


def main():
    print("Carregando dados e modelo...")
    X_raw, y = carregar_dados()

    preprocessador = joblib.load(os.path.join(PASTA_MODELO, "preprocessador.joblib"))
    modelo         = joblib.load(os.path.join(PASTA_MODELO, "modelo_final.joblib"))
    nome_modelo    = joblib.load(os.path.join(PASTA_MODELO, "nome_modelo.joblib"))
    print(f"Modelo carregado: {nome_modelo}")

    X_proc = preprocessador.transform(X_raw)
    nomes  = nomes_features(preprocessador)
    print(f"Features: {X_proc.shape[1]}")

    modelo_base = modelo.calibrated_classifiers_[0].estimator
    validacao_cruzada(modelo_base, X_proc, y)
    df_imp = permutation_importance_plot(modelo, X_proc, y, nomes)
    shap_analysis(modelo, X_proc, nomes)
    calibration_curve_plot(modelo, X_proc, y)

    print(f"\nTodos os resultados salvos em: {SAIDA}")


if __name__ == "__main__":
    main()
