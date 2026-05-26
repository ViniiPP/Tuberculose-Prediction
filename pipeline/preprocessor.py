"""
Pipeline de pré-processamento compatível com scikit-learn.
Uso: pipe = Pipeline([("prep", TuberculosePreprocessor()), ("clf", modelo)])
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.experimental import enable_iterative_imputer 
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, OrdinalEncoder, TargetEncoder, OneHotEncoder

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.preditores import (
    PREDITORES_NUMERICOS,
    PREDITORES_CATEGORICOS,
    PREDITORES_ORDINAIS,
    PREDITORES_BINARIOS,
)

COL_TARGET_ENC = ["SG_UF_NOT"]
COL_OHE = [c for c in PREDITORES_CATEGORICOS if c not in COL_TARGET_ENC]

# 9 = ignorado → NaN
# Variáveis binárias: 1=Sim → 1, 2=Não → 0  (encoding intuitivo, evita inversão de sinal)
_MAPA_BINARIO = {"1": 1, "2": 0, 1: 1, 2: 0}
_IGNORADOS = {9, "9"}


def _limpar_binarios(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for col in PREDITORES_BINARIOS:
        if col not in X.columns:
            continue
        X[col] = X[col].replace(_IGNORADOS, np.nan)
        X[col] = X[col].map(lambda v: _MAPA_BINARIO.get(v, np.nan) if not (isinstance(v, float) and np.isnan(v)) else np.nan)
        X[col] = pd.to_numeric(X[col], errors="coerce")
    return X


def _limpar_numericos(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for col in PREDITORES_NUMERICOS + PREDITORES_ORDINAIS:
        if col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce")
    return X


class TuberculosePreprocessor(BaseEstimator, TransformerMixin):
    """
    Transforma dados brutos do SINAN em features numéricas para os modelos.
    - Binários: 1=Sim→1, 2=Não→0, 9=Ignorado→NaN
    - Numéricos: IterativeImputer + RobustScaler
    - Categóricos: OneHotEncoder (baixa cardinalidade) / TargetEncoder (UF)
    - Ordinais: OrdinalEncoder
    """

    def __init__(self):
        self._transformador = None
        self._mapa_raras = {}

    def fit(self, X, y=None):
        X = _limpar_binarios(X)
        X = _limpar_numericos(X)
        self._mapa_raras = self._calcular_raras(X)
        X = self._aplicar_raras(X)

        pipe_numerico = Pipeline([
            ("imputer", IterativeImputer(max_iter=10, random_state=42)),
            ("scaler",  RobustScaler()),
        ])
        pipe_binario = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ])
        pipe_ohe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(sparse_output=False, handle_unknown="ignore")),
        ])
        pipe_ordinal = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ])
        pipe_target = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", TargetEncoder()),
        ])

        self._transformador = ColumnTransformer([
            ("numerico", pipe_numerico, PREDITORES_NUMERICOS),
            ("binario",  pipe_binario,  PREDITORES_BINARIOS),
            ("ohe",      pipe_ohe,      COL_OHE),
            ("ordinal",  pipe_ordinal,  PREDITORES_ORDINAIS),
            ("target",   pipe_target,   COL_TARGET_ENC),
        ], remainder="drop")

        self._transformador.fit(X, y)
        return self

    def transform(self, X, y=None):
        X = _limpar_binarios(X)
        X = _limpar_numericos(X)
        X = self._aplicar_raras(X)
        return self._transformador.transform(X)

    def fit_transform(self, X, y=None, **params):
        return self.fit(X, y).transform(X)

    def _calcular_raras(self, X: pd.DataFrame) -> dict:
        mapa = {}
        for col in COL_OHE:
            if col in X.columns:
                freq = X[col].astype(str).value_counts(normalize=True)
                mapa[col] = set(freq[freq < 0.01].index.tolist())
        return mapa

    def _aplicar_raras(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        for col, raras in self._mapa_raras.items():
            if col in X.columns and raras:
                X[col] = X[col].astype(str).apply(
                    lambda v: "__raro__" if v in raras else v
                )
        return X
