"""
utils/simulator.py
Generates realistic ICU patient vitals data for simulation and demonstration.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_vital_snapshot(patient_id: int = 1, risk_level: str = "normal") -> dict:
    """
    Generate a single snapshot of ICU vitals for a patient.

    Args:
        patient_id: Numeric patient identifier.
        risk_level: One of 'normal', 'warning', 'critical'.

    Returns:
        Dictionary with vital sign values.
    """
    rng = np.random.default_rng()

    if risk_level == "normal":
        heart_rate = rng.normal(75, 5)
        oxygen_level = rng.normal(97, 1)
        temperature = rng.normal(36.8, 0.3)
        blood_pressure = rng.normal(120, 8)
        respiratory_rate = rng.normal(16, 2)
    elif risk_level == "warning":
        heart_rate = rng.normal(100, 10)
        oxygen_level = rng.normal(93, 2)
        temperature = rng.normal(37.8, 0.4)
        blood_pressure = rng.normal(145, 10)
        respiratory_rate = rng.normal(22, 3)
    else:  # critical
        heart_rate = rng.normal(130, 15)
        oxygen_level = rng.normal(88, 3)
        temperature = rng.normal(39.0, 0.6)
        blood_pressure = rng.normal(170, 15)
        respiratory_rate = rng.normal(30, 4)

    return {
        "patient_id": patient_id,
        "timestamp": datetime.now(),
        "heart_rate": float(np.clip(heart_rate, 40, 200)),
        "oxygen_level": float(np.clip(oxygen_level, 70, 100)),
        "temperature": float(np.clip(temperature, 34.0, 42.0)),
        "blood_pressure": float(np.clip(blood_pressure, 60, 200)),
        "respiratory_rate": float(np.clip(respiratory_rate, 8, 45)),
    }


def generate_time_series(
    n_points: int = 60,
    interval_seconds: int = 2,
    risk_level: str = "normal",
) -> pd.DataFrame:
    """
    Generate a time-series DataFrame of ICU vitals.

    Args:
        n_points: Number of data points to generate.
        interval_seconds: Seconds between each point.
        risk_level: Baseline risk level for generation.

    Returns:
        DataFrame indexed by timestamp.
    """
    now = datetime.now()
    records = []
    for i in range(n_points):
        ts = now - timedelta(seconds=(n_points - i) * interval_seconds)
        snapshot = generate_vital_snapshot(risk_level=risk_level)
        snapshot["timestamp"] = ts
        records.append(snapshot)
    df = pd.DataFrame(records)
    df.set_index("timestamp", inplace=True)
    return df


def generate_patient_dataset(n_patients: int = 200, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic ICU patient dataset for training and analytics.

    Args:
        n_patients: Total number of patient records.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with vitals and computed risk score.
    """
    rng = np.random.default_rng(seed)

    heart_rate = rng.uniform(50, 160, n_patients)
    oxygen_level = rng.uniform(80, 100, n_patients)
    temperature = rng.uniform(35.0, 42.0, n_patients)
    blood_pressure = rng.uniform(80, 180, n_patients)
    respiratory_rate = rng.uniform(10, 40, n_patients)

    # Compute a continuous risk score in [0, 1]
    hr_score = np.abs(heart_rate - 75) / 85.0
    o2_score = (100.0 - oxygen_level) / 20.0
    temp_score = np.abs(temperature - 36.8) / 5.2
    bp_score = np.abs(blood_pressure - 120) / 100.0
    rr_score = np.abs(respiratory_rate - 16) / 24.0

    risk_score = np.clip(
        0.25 * hr_score
        + 0.30 * o2_score
        + 0.15 * temp_score
        + 0.15 * bp_score
        + 0.15 * rr_score,
        0.0,
        1.0,
    )

    df = pd.DataFrame(
        {
            "heart_rate": heart_rate,
            "oxygen_level": oxygen_level,
            "temperature": temperature,
            "blood_pressure": blood_pressure,
            "respiratory_rate": respiratory_rate,
            "risk_score": risk_score,
        }
    )
    return df


def classify_risk(risk_score: float) -> str:
    """
    Convert a continuous risk score to a categorical status.

    Args:
        risk_score: Float in [0, 1].

    Returns:
        'SAFE', 'WARNING', or 'CRITICAL'.
    """
    if risk_score < 0.35:
        return "SAFE"
    elif risk_score < 0.65:
        return "WARNING"
    return "CRITICAL"


FEATURE_COLUMNS = [
    "heart_rate",
    "oxygen_level",
    "temperature",
    "blood_pressure",
    "respiratory_rate",
]
