"""
train_model.py
Trains the ICU risk RandomForestRegressor model and saves it to models/.
Also exports the synthetic patient dataset to data/.
Run once before starting the Streamlit app:
    python train_model.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

from utils.simulator import generate_patient_dataset, FEATURE_COLUMNS

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def train_and_save():
    print("Generating synthetic ICU patient dataset...")
    df = generate_patient_dataset(n_patients=500, seed=42)

    csv_path = os.path.join(DATA_DIR, "icu_patient_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path}  ({len(df)} rows)")

    X = df[FEATURE_COLUMNS].values
    y = df["risk_score"].values

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    print(f"Cross-validated R² scores: {scores.round(4)}")
    print(f"Mean R²: {scores.mean():.4f}  |  Std: {scores.std():.4f}")

    model_path = os.path.join(MODELS_DIR, "icu_risk_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    train_and_save()
