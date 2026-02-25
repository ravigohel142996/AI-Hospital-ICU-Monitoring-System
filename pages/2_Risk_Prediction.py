"""
pages/2_Risk_Prediction.py
Slider-based patient risk prediction using the trained RandomForest model.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go

from utils.predictor import predict_risk
from utils.theme import apply_theme

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Risk Prediction | ICU System",
    page_icon="🔬",
    layout="wide",
)

apply_theme()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='color:#64b5f6;'>Patient Risk Prediction</h2>",
    unsafe_allow_html=True,
)
st.caption("Adjust patient vitals using the sliders below to compute AI-generated risk assessment.")
st.divider()

# ── Input sliders ──────────────────────────────────────────────────────────────
col_inputs, col_results = st.columns([1, 1])

with col_inputs:
    st.markdown("#### Patient Vital Parameters")

    heart_rate = st.slider(
        "Heart Rate (bpm)",
        min_value=50, max_value=160, value=75, step=1,
        help="Normal: 60–100 bpm",
    )
    oxygen_level = st.slider(
        "Oxygen Level (%)",
        min_value=80, max_value=100, value=97, step=1,
        help="Normal: 95–100%",
    )
    temperature = st.slider(
        "Temperature (°C)",
        min_value=35.0, max_value=42.0, value=36.8, step=0.1,
        help="Normal: 36.1–37.2 °C",
    )
    blood_pressure = st.slider(
        "Blood Pressure (mmHg)",
        min_value=80, max_value=180, value=120, step=1,
        help="Normal: 90–120 mmHg",
    )
    respiratory_rate = st.slider(
        "Respiratory Rate (br/min)",
        min_value=10, max_value=40, value=16, step=1,
        help="Normal: 12–20 br/min",
    )

    predict_btn = st.button("Run Risk Assessment", use_container_width=True)

# ── Prediction ─────────────────────────────────────────────────────────────────
with col_results:
    st.markdown("#### Risk Assessment Result")

    result = predict_risk(
        heart_rate=heart_rate,
        oxygen_level=oxygen_level,
        temperature=temperature,
        blood_pressure=blood_pressure,
        respiratory_rate=respiratory_rate,
    )
    risk_score = result["risk_score"]
    status = result["status"]

    STATUS_COLOR = {"SAFE": "#4caf50", "WARNING": "#ff9800", "CRITICAL": "#f44336"}
    STATUS_BG = {"SAFE": "#1b5e20", "WARNING": "#e65100", "CRITICAL": "#b71c1c"}
    color = STATUS_COLOR[status]
    bg = STATUS_BG[status]

    # Status card
    st.markdown(
        f"""
        <div class='pulse-badge' style='
            background: linear-gradient(135deg, {bg}55, {bg}22);
            border: 2px solid {color};
            border-radius: 10px;
            padding: 24px;
            text-align: center;
            margin-bottom: 16px;
        '>
            <div style='font-size: 14px; color: #90a4ae; letter-spacing: 2px; text-transform: uppercase;'>Risk Status</div>
            <div style='font-size: 42px; font-weight: 800; color: {color}; margin: 8px 0;'>{status}</div>
            <div style='font-size: 18px; color: #e0e6ed;'>Risk Score: <strong>{risk_score:.3f}</strong></div>
            <div style='font-size: 13px; color: #90a4ae; margin-top: 8px;'>
                {"Patient vitals within acceptable range." if status == "SAFE" else
                 "Some vitals are outside normal range. Close monitoring advised." if status == "WARNING" else
                 "Critical condition detected. Immediate medical intervention required."}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Gauge chart
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_score * 100,
            number={"suffix": "%", "font": {"color": "#e0e6ed", "size": 36}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#90a4ae",
                    "tickfont": {"color": "#90a4ae"},
                },
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "#112240",
                "bordercolor": "#1e3a5f",
                "steps": [
                    {"range": [0, 35], "color": "rgba(27, 94, 32, 0.20)"},
                    {"range": [35, 65], "color": "rgba(230, 81, 0, 0.20)"},
                    {"range": [65, 100], "color": "rgba(183, 28, 28, 0.20)"},
                ],
            },
            title={"text": "Risk Score", "font": {"color": "#64b5f6", "size": 14}},
        )
    )
    gauge.update_layout(
        paper_bgcolor="#0d1b2a",
        font_color="#e0e6ed",
        height=260,
        margin=dict(l=20, r=20, t=30, b=10),
    )
    st.plotly_chart(gauge, use_container_width=True)

# ── Vital deviation reference ──────────────────────────────────────────────────
st.divider()
st.markdown("#### Vital Deviation Analysis")

import pandas as pd

NORMAL = {
    "Heart Rate": (60, 100, heart_rate, "bpm"),
    "Oxygen Level": (95, 100, oxygen_level, "%"),
    "Temperature": (36.1, 37.2, temperature, "°C"),
    "Blood Pressure": (90, 120, blood_pressure, "mmHg"),
    "Respiratory Rate": (12, 20, respiratory_rate, "br/min"),
}

rows = []
for vital, (low, high, val, unit) in NORMAL.items():
    if val < low:
        deviation = "Below Normal"
        dev_color = "#ff9800"
    elif val > high:
        deviation = "Above Normal"
        dev_color = "#f44336"
    else:
        deviation = "Normal"
        dev_color = "#4caf50"
    rows.append({"Vital Sign": vital, "Value": f"{val} {unit}", "Normal Range": f"{low}–{high} {unit}", "Status": deviation})

deviations_df = pd.DataFrame(rows)
st.dataframe(deviations_df, use_container_width=True, hide_index=True)
