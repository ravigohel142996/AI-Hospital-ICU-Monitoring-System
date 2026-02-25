"""
pages/1_Live_Monitoring.py
Real-time streaming ICU patient vitals with auto-refresh.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.simulator import generate_vital_snapshot, classify_risk
from utils.predictor import predict_risk
from utils.theme import apply_theme

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Live Monitoring | ICU System",
    page_icon="📡",
    layout="wide",
)

apply_theme()

# ── Session state for streaming buffer ────────────────────────────────────────
BUFFER_SIZE = 60  # keep last 60 data points (~2 min at 2 s intervals)

if "live_data" not in st.session_state:
    st.session_state["live_data"] = pd.DataFrame(
        columns=["timestamp", "heart_rate", "oxygen_level", "temperature",
                 "blood_pressure", "respiratory_rate"]
    )

if "stream_running" not in st.session_state:
    st.session_state["stream_running"] = True

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='color:#64b5f6;'>Live ICU Patient Monitoring</h2>",
    unsafe_allow_html=True,
)
st.caption("Streaming synthetic patient vitals — refreshed every 2 seconds")

# ── Controls ───────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 4])
with col_ctrl1:
    risk_sim = st.selectbox("Simulate Patient State", ["normal", "warning", "critical"], index=0)
with col_ctrl2:
    auto_refresh = st.toggle("Auto Refresh", value=True)

st.divider()

# ── Append new data point ──────────────────────────────────────────────────────
snapshot = generate_vital_snapshot(risk_level=risk_sim)
new_row = pd.DataFrame([{
    "timestamp": snapshot["timestamp"],
    "heart_rate": snapshot["heart_rate"],
    "oxygen_level": snapshot["oxygen_level"],
    "temperature": snapshot["temperature"],
    "blood_pressure": snapshot["blood_pressure"],
    "respiratory_rate": snapshot["respiratory_rate"],
}])
st.session_state["live_data"] = pd.concat(
    [st.session_state["live_data"], new_row], ignore_index=True
).tail(BUFFER_SIZE)

df = st.session_state["live_data"]

# ── Current vitals ─────────────────────────────────────────────────────────────
latest = df.iloc[-1]
prediction = predict_risk(
    heart_rate=latest["heart_rate"],
    oxygen_level=latest["oxygen_level"],
    temperature=latest["temperature"],
    blood_pressure=latest["blood_pressure"],
    respiratory_rate=latest["respiratory_rate"],
)
status = prediction["status"]
risk_score = prediction["risk_score"]
STATUS_COLOR = {"SAFE": "#4caf50", "WARNING": "#ff9800", "CRITICAL": "#f44336"}
color = STATUS_COLOR[status]

# ── Status badge ───────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='pulse-badge' style='background:{color}22; border-left:4px solid {color}; border-radius:6px;"
    f"padding:8px 16px; margin-bottom:12px;'>"
    f"<span style='color:{color}; font-size:18px; font-weight:700;'>&#9679; {status}</span>"
    f"&nbsp;&nbsp;<span style='color:#90a4ae;'>Risk Score: {risk_score:.2f}</span></div>",
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Heart Rate", f"{latest['heart_rate']:.0f} bpm")
m2.metric("Oxygen Level", f"{latest['oxygen_level']:.1f} %")
m3.metric("Temperature", f"{latest['temperature']:.1f} °C")
m4.metric("Blood Pressure", f"{latest['blood_pressure']:.0f} mmHg")
m5.metric("Resp. Rate", f"{latest['respiratory_rate']:.0f} br/min")

st.divider()

# ── Chart helpers ──────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    xaxis=dict(gridcolor="#1e3a5f", showgrid=True),
    yaxis=dict(gridcolor="#1e3a5f", showgrid=True),
    margin=dict(l=40, r=20, t=40, b=40),
    height=220,
)


def line_chart(x, y, name: str, color: str, fill_color: str, yrange=None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x, y=y, name=name, mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=fill_color,
        )
    )
    layout = dict(CHART_LAYOUT)
    layout["title"] = dict(text=name, font=dict(color="#64b5f6", size=14))
    if yrange:
        layout["yaxis"] = dict(range=yrange, gridcolor="#1e3a5f", showgrid=True)
    fig.update_layout(**layout)
    return fig


# ── Charts ─────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    fig_hr = line_chart(
        df["timestamp"], df["heart_rate"],
        "Heart Rate (bpm)", "rgb(100, 181, 246)", "rgba(100, 181, 246, 0.08)", yrange=[40, 200]
    )
    st.plotly_chart(fig_hr, use_container_width=True)

with c2:
    fig_o2 = line_chart(
        df["timestamp"], df["oxygen_level"],
        "Oxygen Level (%)", "rgb(76, 175, 80)", "rgba(76, 175, 80, 0.08)", yrange=[75, 100]
    )
    st.plotly_chart(fig_o2, use_container_width=True)

with c3:
    fig_temp = line_chart(
        df["timestamp"], df["temperature"],
        "Temperature (°C)", "rgb(255, 152, 0)", "rgba(255, 152, 0, 0.08)", yrange=[34, 42]
    )
    st.plotly_chart(fig_temp, use_container_width=True)

# ── Data table ─────────────────────────────────────────────────────────────────
st.markdown("#### Recent Readings")
display_df = df.copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
display_df.columns = ["Time", "Heart Rate", "SpO2 %", "Temp °C", "BP mmHg", "RR br/min"]
st.dataframe(display_df.tail(10).iloc[::-1], use_container_width=True, hide_index=True)

# ── Auto-refresh ───────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(2)
    st.rerun()
