"""
pages/3_Analytics.py
Statistical analysis, correlation heatmap, and risk trend charts.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from utils.simulator import classify_risk

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analytics | ICU System",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%); color: #e0e6ed; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 100%); border-right: 1px solid #1e3a5f; }
    h1, h2, h3 { color: #64b5f6; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load dataset ───────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "icu_patient_data.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


df = load_data()
df["status"] = df["risk_score"].apply(classify_risk)

VITAL_COLS = ["heart_rate", "oxygen_level", "temperature", "blood_pressure", "respiratory_rate"]
VITAL_LABELS = {
    "heart_rate": "Heart Rate (bpm)",
    "oxygen_level": "Oxygen Level (%)",
    "temperature": "Temperature (°C)",
    "blood_pressure": "Blood Pressure (mmHg)",
    "respiratory_rate": "Respiratory Rate (br/min)",
}
COLORS = ["#64b5f6", "#4caf50", "#ff9800", "#e91e63", "#ab47bc"]

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#64b5f6;'>Clinical Analytics</h2>", unsafe_allow_html=True)
st.caption(f"Analyzing {len(df)} synthetic ICU patient records.")
st.divider()

# ── Summary stats ──────────────────────────────────────────────────────────────
st.markdown("#### Dataset Summary Statistics")
summary = df[VITAL_COLS + ["risk_score"]].describe().round(3)
summary.index.name = "Statistic"
st.dataframe(summary, use_container_width=True)

st.divider()

# ── Vital distributions ────────────────────────────────────────────────────────
st.markdown("#### Vital Sign Distributions")

dist_cols = st.columns(3)
for i, col in enumerate(VITAL_COLS[:3]):
    with dist_cols[i]:
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df[col],
                nbinsx=30,
                marker_color=COLORS[i],
                opacity=0.8,
                name=VITAL_LABELS[col],
            )
        )
        fig.update_layout(
            paper_bgcolor="#0d1b2a",
            plot_bgcolor="#0d1b2a",
            font_color="#90a4ae",
            title=dict(text=VITAL_LABELS[col], font=dict(color="#64b5f6", size=13)),
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f", title="Count"),
            margin=dict(l=30, r=20, t=40, b=30),
            height=230,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

dist_cols2 = st.columns(2)
for i, col in enumerate(VITAL_COLS[3:]):
    with dist_cols2[i]:
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df[col],
                nbinsx=30,
                marker_color=COLORS[i + 3],
                opacity=0.8,
                name=VITAL_LABELS[col],
            )
        )
        fig.update_layout(
            paper_bgcolor="#0d1b2a",
            plot_bgcolor="#0d1b2a",
            font_color="#90a4ae",
            title=dict(text=VITAL_LABELS[col], font=dict(color="#64b5f6", size=13)),
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f", title="Count"),
            margin=dict(l=30, r=20, t=40, b=30),
            height=230,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Correlation heatmap ────────────────────────────────────────────────────────
st.markdown("#### Correlation Heatmap")
corr = df[VITAL_COLS + ["risk_score"]].corr().round(3)
labels = [VITAL_LABELS.get(c, c) for c in corr.columns]

heatmap = go.Figure(
    go.Heatmap(
        z=corr.values,
        x=labels,
        y=labels,
        colorscale="RdBu",
        zmid=0,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#e0e6ed"},
        colorbar=dict(tickfont=dict(color="#90a4ae")),
    )
)
heatmap.update_layout(
    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    height=440,
    margin=dict(l=40, r=20, t=20, b=40),
    xaxis=dict(tickfont=dict(color="#90a4ae")),
    yaxis=dict(tickfont=dict(color="#90a4ae")),
)
st.plotly_chart(heatmap, use_container_width=True)

st.divider()

# ── Risk score trends ──────────────────────────────────────────────────────────
st.markdown("#### Risk Score Distribution by Status")

status_counts = df["status"].value_counts()
STATUS_COLOR = {"SAFE": "#4caf50", "WARNING": "#ff9800", "CRITICAL": "#f44336"}

pie = go.Figure(
    go.Pie(
        labels=status_counts.index.tolist(),
        values=status_counts.values.tolist(),
        marker_colors=[STATUS_COLOR.get(s, "#90a4ae") for s in status_counts.index],
        textfont=dict(color="#e0e6ed"),
        hole=0.4,
    )
)
pie.update_layout(
    paper_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    height=320,
    legend=dict(font=dict(color="#e0e6ed")),
    margin=dict(l=20, r=20, t=20, b=20),
)

scatter_fig = go.Figure()
for s, c in STATUS_COLOR.items():
    sub = df[df["status"] == s]
    scatter_fig.add_trace(
        go.Scatter(
            x=sub["heart_rate"],
            y=sub["oxygen_level"],
            mode="markers",
            name=s,
            marker=dict(color=c, size=5, opacity=0.7),
        )
    )
scatter_fig.update_layout(
    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    title=dict(text="Heart Rate vs Oxygen Level by Risk Status", font=dict(color="#64b5f6", size=13)),
    xaxis=dict(title="Heart Rate (bpm)", gridcolor="#1e3a5f"),
    yaxis=dict(title="Oxygen Level (%)", gridcolor="#1e3a5f"),
    height=320,
    legend=dict(font=dict(color="#e0e6ed")),
    margin=dict(l=40, r=20, t=40, b=40),
)

col_pie, col_scatter = st.columns([1, 2])
with col_pie:
    st.plotly_chart(pie, use_container_width=True)
with col_scatter:
    st.plotly_chart(scatter_fig, use_container_width=True)

# ── Risk score histogram ────────────────────────────────────────────────────────
st.divider()
st.markdown("#### Risk Score Trend")
risk_hist = go.Figure()
risk_hist.add_trace(
    go.Histogram(
        x=df["risk_score"],
        nbinsx=40,
        marker_color="#64b5f6",
        opacity=0.8,
    )
)
risk_hist.add_vline(x=0.35, line_color="#ff9800", line_dash="dash",
                    annotation_text="Warning Threshold", annotation_font_color="#ff9800")
risk_hist.add_vline(x=0.65, line_color="#f44336", line_dash="dash",
                    annotation_text="Critical Threshold", annotation_font_color="#f44336")
risk_hist.update_layout(
    paper_bgcolor="#0d1b2a",
    plot_bgcolor="#0d1b2a",
    font_color="#90a4ae",
    xaxis=dict(title="Risk Score", gridcolor="#1e3a5f"),
    yaxis=dict(title="Count", gridcolor="#1e3a5f"),
    height=280,
    showlegend=False,
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(risk_hist, use_container_width=True)
