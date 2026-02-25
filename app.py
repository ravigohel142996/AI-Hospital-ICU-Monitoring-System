"""
app.py
Dashboard Overview – main entry point for the Streamlit multi-page app.
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.simulator import generate_vital_snapshot, classify_risk
from utils.predictor import predict_risk
from utils.theme import apply_theme

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Hospital ICU Monitoring System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
apply_theme()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Navigation")
    st.markdown("Use the pages listed above to navigate.")
    st.markdown("---")
    st.markdown("**System Information**")
    st.markdown("Version: `1.0.0`")
    st.markdown("Model: `RandomForestRegressor`")
    st.markdown("Refresh: `Manual / Auto`")
    st.markdown("---")
    if st.button("Refresh Dashboard"):
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; color:#64b5f6; letter-spacing:2px;'>"
    "AI HOSPITAL ICU MONITORING SYSTEM"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#90a4ae; margin-top:-10px;'>"
    "Real-Time Patient Vitals &nbsp;|&nbsp; Risk Prediction &nbsp;|&nbsp; Clinical Analytics"
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Simulate current vitals ────────────────────────────────────────────────────
if "start_time" not in st.session_state:
    st.session_state["start_time"] = time.time()
if "active_patients" not in st.session_state:
    st.session_state["active_patients"] = 12

vitals = generate_vital_snapshot()
prediction = predict_risk(
    heart_rate=vitals["heart_rate"],
    oxygen_level=vitals["oxygen_level"],
    temperature=vitals["temperature"],
    blood_pressure=vitals["blood_pressure"],
    respiratory_rate=vitals["respiratory_rate"],
)
risk_score = prediction["risk_score"]
status = prediction["status"]

uptime_seconds = int(time.time() - st.session_state["start_time"])
uptime_str = f"{uptime_seconds // 3600:02d}:{(uptime_seconds % 3600) // 60:02d}:{uptime_seconds % 60:02d}"

STATUS_COLOR = {"SAFE": "#4caf50", "WARNING": "#ff9800", "CRITICAL": "#f44336"}
color = STATUS_COLOR[status]

# ── Status banner ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class='pulse-badge' style='
        background: linear-gradient(90deg, {color}22, {color}11);
        border-left: 4px solid {color};
        border-radius: 6px;
        padding: 10px 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    '>
        <span style='font-size:22px; color:{color}; font-weight:700;'>&#9679; SYSTEM STATUS: {status}</span>
        <span style='color:#90a4ae; font-size:14px;'>Risk Score: {risk_score:.2f} &nbsp;|&nbsp; Uptime: {uptime_str} &nbsp;|&nbsp; Active Patients: {st.session_state["active_patients"]}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Vitals metrics row ─────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Heart Rate", f"{vitals['heart_rate']:.0f} bpm", delta=None)
col2.metric("Oxygen Level", f"{vitals['oxygen_level']:.1f} %", delta=None)
col3.metric("Temperature", f"{vitals['temperature']:.1f} °C", delta=None)
col4.metric("Blood Pressure", f"{vitals['blood_pressure']:.0f} mmHg", delta=None)
col5.metric("Respiratory Rate", f"{vitals['respiratory_rate']:.0f} br/min", delta=None)

st.divider()

# ── Gauge chart + quick stats ──────────────────────────────────────────────────
col_gauge, col_stats = st.columns([1, 1])

with col_gauge:
    st.markdown("#### Patient Risk Score")
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=risk_score * 100,
            number={"suffix": "%", "font": {"color": "#e0e6ed", "size": 40}},
            delta={"reference": 35, "valueformat": ".1f"},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#90a4ae",
                    "tickfont": {"color": "#90a4ae"},
                },
                "bar": {"color": color, "thickness": 0.25},
                "bgcolor": "#112240",
                "bordercolor": "#1e3a5f",
                "steps": [
                    {"range": [0, 35], "color": "rgba(27, 94, 32, 0.27)"},
                    {"range": [35, 65], "color": "rgba(230, 81, 0, 0.40)"},
                    {"range": [65, 100], "color": "rgba(183, 28, 28, 0.27)"},
                ],
                "threshold": {
                    "line": {"color": "#ffffff", "width": 2},
                    "thickness": 0.75,
                    "value": risk_score * 100,
                },
            },
            title={"text": status, "font": {"color": color, "size": 18}},
        )
    )
    gauge.update_layout(
        paper_bgcolor="#0d1b2a",
        font_color="#e0e6ed",
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(gauge, use_container_width=True)

with col_stats:
    st.markdown("#### System Overview")

    def stat_card(label: str, value: str, sub: str = "") -> str:
        return (
            f"<div style='background:#112240; border:1px solid #1e3a5f; border-radius:8px;"
            f"padding:14px 18px; margin-bottom:10px;'>"
            f"<span style='color:#90a4ae; font-size:12px; text-transform:uppercase; letter-spacing:1px;'>{label}</span><br>"
            f"<span style='color:#e0e6ed; font-size:22px; font-weight:600;'>{value}</span>"
            f"{'<br><span style=color:#546e7a;font-size:12px>' + sub + '</span>' if sub else ''}"
            f"</div>"
        )

    st.markdown(
        stat_card("Active Patients", str(st.session_state["active_patients"]), "Currently in ICU"),
        unsafe_allow_html=True,
    )
    st.markdown(
        stat_card("System Uptime", uptime_str, "HH:MM:SS"),
        unsafe_allow_html=True,
    )
    st.markdown(
        stat_card("Last Updated", pd.Timestamp.now().strftime("%H:%M:%S"), "Auto-simulated vitals"),
        unsafe_allow_html=True,
    )

st.divider()

# ── Normal ranges reference ────────────────────────────────────────────────────
st.markdown("#### Normal Vital Ranges Reference")
ref_data = {
    "Vital Sign": ["Heart Rate", "Oxygen Level", "Temperature", "Blood Pressure", "Respiratory Rate"],
    "Normal Range": ["60–100 bpm", "95–100 %", "36.1–37.2 °C", "90–120 mmHg", "12–20 br/min"],
    "Warning Range": ["50–60 or 100–120 bpm", "90–95 %", "37.2–38.5 °C", "120–160 mmHg", "20–30 br/min"],
    "Critical Range": ["< 50 or > 120 bpm", "< 90 %", "> 38.5 °C or < 35 °C", "> 160 mmHg", "> 30 br/min"],
}
st.dataframe(
    pd.DataFrame(ref_data),
    use_container_width=True,
    hide_index=True,
)
