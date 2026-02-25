"""
utils/predictor.py
Loads the trained ICU risk model and exposes a clean prediction interface.
"""

import os
import numpy as np
import pandas as pd
import joblib

from utils.simulator import FEATURE_COLUMNS, classify_risk

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "icu_risk_model.pkl")
_MODEL_CACHE = None


def load_model():
    """
    Load the RandomForestRegressor model from disk (cached after first load).

    Returns:
        Trained sklearn model object.
    """
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = joblib.load(_MODEL_PATH)
    return _MODEL_CACHE


def predict_risk(
    heart_rate: float,
    oxygen_level: float,
    temperature: float,
    blood_pressure: float,
    respiratory_rate: float,
) -> dict:
    """
    Predict patient risk from vital signs.

    Args:
        heart_rate: Heart rate in bpm.
        oxygen_level: Peripheral oxygen saturation (%).
        temperature: Body temperature (°C).
        blood_pressure: Systolic blood pressure (mmHg).
        respiratory_rate: Breaths per minute.

    Returns:
        Dictionary with keys:
            - risk_score (float, 0–1)
            - status (str: 'SAFE' | 'WARNING' | 'CRITICAL')
    """
    model = load_model()
    features = np.array(
        [[heart_rate, oxygen_level, temperature, blood_pressure, respiratory_rate]]
    )
    risk_score = float(np.clip(model.predict(features)[0], 0.0, 1.0))
    return {
        "risk_score": risk_score,
        "status": classify_risk(risk_score),
    }


def get_feature_importances() -> pd.DataFrame:
    """
    Return a DataFrame of feature importances from the trained model.

    Returns:
        DataFrame with columns ['feature', 'importance'].
    """
    model = load_model()
    importances = model.feature_importances_
    df = pd.DataFrame(
        {"feature": FEATURE_COLUMNS, "importance": importances}
    ).sort_values("importance", ascending=False)
    return df


def get_model_info() -> dict:
    """
    Return metadata about the trained model.

    Returns:
        Dictionary with model type, n_estimators, max_depth, etc.
    """
    model = load_model()
    return {
        "type": type(model).__name__,
        "n_estimators": model.n_estimators,
        "max_depth": model.max_depth,
        "random_state": model.random_state,
    }
