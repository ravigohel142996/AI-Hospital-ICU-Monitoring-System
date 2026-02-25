"""
pages/4_Model_Insights.py
Displays model metadata, accuracy, and feature importance chart.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score

from utils.predictor import load_model, get_feature_importances, get_model_info
from utils.simulator import generate_patient_dataset, FEATURE_COLUMNS
from utils.theme import apply_theme

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Model Insights | ICU System",
    page_icon="🧠",
    layout="wide",
)

apply_theme()

# ── Load model data ────────────────────────────────────────────────────────────
@st.cache_data
def compute_cv_scores():
    df = generate_patient_dataset(n_patients=500, seed=42)
    X = df[FEATURE_COLUMNS].values
    y = df["risk_score"].values
    model = load_model()
    scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    return scores


model_info = get_model_info()
importances_df = get_feature_importances()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#64b5f6;'>Model Insights</h2>", unsafe_allow_html=True)
st.caption("Details about the trained RandomForestRegressor ICU risk model.")
st.divider()

# ── Model configuration metrics ────────────────────────────────────────────────
st.markdown("#### Model Configuration")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Model Type", model_info["type"])
m2.metric("Estimators", str(model_info["n_estimators"]))
m3.metric("Max Depth", str(model_info["max_depth"]) if model_info["max_depth"] else "Unlimited")
m4.metric("Random State", str(model_info["random_state"]))

st.divider()

# ── Accuracy ───────────────────────────────────────────────────────────────────
st.markdown("#### Model Performance (Cross-Validation)")

with st.spinner("Computing cross-validation scores…"):
    cv_scores = compute_cv_scores()

mean_r2 = cv_scores.mean()
std_r2 = cv_scores.std()

a1, a2, a3 = st.columns(3)
a1.metric("Mean R² Score", f"{mean_r2:.4f}")
a2.metric("Std Deviation", f"{std_r2:.4f}")
a3.metric("CV Folds", "5")

# CV fold bar chart
cv_fig = go.Figure()
cv_fig.add_trace(
    go.Bar(
        x=[f"Fold {i+1}" for i in range(len(cv_scores))],
        y=cv_scores,
        marker_color=["#4caf50" if s >= 0.85 else "#ff9800" for s in cv_scores],
        text=[f"{s:.4f}" for s in cv_scores],
        textposition="outside",
        textfont=dict(color="#e0e6ed"),
    )
)
cv_fig.add_hline(
    y=mean_r2, line_color="#64b5f6", line_dash="dash",
    annotation_text=f"Mean R² = {mean_r2:.4f}",
    annotation_font_color="#64b5f6",
)
cv_fig.update_layout(
    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    xaxis=dict(gridcolor="#1e3a5f"),
    yaxis=dict(gridcolor="#1e3a5f", range=[0, 1.05], title="R² Score"),
    height=280,
    showlegend=False,
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(cv_fig, use_container_width=True)

st.divider()

# ── Feature importances ────────────────────────────────────────────────────────
st.markdown("#### Feature Importance")

FEATURE_LABELS = {
    "heart_rate": "Heart Rate",
    "oxygen_level": "Oxygen Level",
    "temperature": "Temperature",
    "blood_pressure": "Blood Pressure",
    "respiratory_rate": "Respiratory Rate",
}

importances_df["label"] = importances_df["feature"].map(FEATURE_LABELS)
importances_df = importances_df.sort_values("importance", ascending=True)

imp_fig = go.Figure()
imp_fig.add_trace(
    go.Bar(
        x=importances_df["importance"],
        y=importances_df["label"],
        orientation="h",
        marker_color="#64b5f6",
        text=[f"{v:.4f}" for v in importances_df["importance"]],
        textposition="outside",
        textfont=dict(color="#e0e6ed"),
    )
)
imp_fig.update_layout(
    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    xaxis=dict(gridcolor="#1e3a5f", title="Importance Score"),
    yaxis=dict(gridcolor="#1e3a5f"),
    height=320,
    showlegend=False,
    margin=dict(l=160, r=40, t=20, b=40),
)
st.plotly_chart(imp_fig, use_container_width=True)

st.divider()

# ── Raw importance table ───────────────────────────────────────────────────────
st.markdown("#### Feature Importance Table")
table_df = importances_df[["label", "importance"]].sort_values("importance", ascending=False).copy()
table_df.columns = ["Feature", "Importance Score"]
table_df["Importance Score"] = table_df["Importance Score"].round(6)
st.dataframe(table_df, use_container_width=True, hide_index=True)

st.divider()

# ── Model notes ────────────────────────────────────────────────────────────────
st.markdown("#### Model Notes")
st.markdown(
    """
    <div style='background:#112240; border:1px solid #1e3a5f; border-radius:8px; padding:16px;'>
        <ul style='color:#90a4ae; line-height:2;'>
            <li><strong style='color:#64b5f6;'>Algorithm:</strong> RandomForestRegressor — ensemble of decision trees trained on ICU vitals.</li>
            <li><strong style='color:#64b5f6;'>Target:</strong> Continuous risk score in [0, 1] derived from clinical vital thresholds.</li>
            <li><strong style='color:#64b5f6;'>Features:</strong> Heart Rate, Oxygen Level, Temperature, Blood Pressure, Respiratory Rate.</li>
            <li><strong style='color:#64b5f6;'>Training Data:</strong> 500 synthetic ICU patient records with realistic vital distributions.</li>
            <li><strong style='color:#64b5f6;'>Risk Thresholds:</strong> SAFE &lt; 0.35 &le; WARNING &lt; 0.65 &le; CRITICAL.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)
