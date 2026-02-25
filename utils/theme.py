"""Shared Streamlit theme utilities for consistent UI styling."""

import streamlit as st


def apply_theme() -> None:
    """Inject global CSS for a high-contrast, animated dashboard theme."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg-1: #06142b;
            --bg-2: #0a2244;
            --bg-3: #12386b;
            --surface: rgba(12, 30, 56, 0.86);
            --surface-hover: rgba(19, 45, 80, 0.95);
            --text-main: #f5f9ff;
            --text-soft: #c9defa;
            --primary: #6fc3ff;
            --accent: #00e5ff;
            --border: rgba(111, 195, 255, 0.33);
        }

        .stApp {
            background:
                radial-gradient(circle at 20% 20%, rgba(0, 229, 255, 0.18), transparent 42%),
                radial-gradient(circle at 80% 10%, rgba(111, 195, 255, 0.20), transparent 36%),
                linear-gradient(145deg, var(--bg-1) 0%, var(--bg-2) 52%, var(--bg-3) 100%);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            animation: fadeInPage 0.8s ease-out;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #081a36 0%, #0d2a50 100%);
            border-right: 1px solid var(--border);
        }

        h1, h2, h3, h4 {
            color: var(--primary) !important;
            letter-spacing: 0.2px;
        }

        p, span, label, li, .stCaption {
            color: var(--text-soft) !important;
        }

        .stMarkdown, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
            color: var(--text-main) !important;
        }

        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, var(--surface) 0%, rgba(14, 39, 71, 0.95) 100%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            animation: floatIn 0.6s ease both;
        }

        div[data-testid="metric-container"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.35);
            border-color: rgba(0, 229, 255, 0.7);
            background: linear-gradient(135deg, var(--surface-hover) 0%, rgba(22, 56, 96, 0.95) 100%);
        }

        .stButton > button {
            background: linear-gradient(90deg, #0aa2ff, #1ee0ff);
            color: #03213f;
            font-weight: 700;
            border: none;
            border-radius: 999px;
            transition: all 0.25s ease;
            box-shadow: 0 6px 18px rgba(10, 162, 255, 0.35);
        }

        .stButton > button:hover {
            transform: translateY(-1px) scale(1.01);
            box-shadow: 0 10px 20px rgba(30, 224, 255, 0.4);
            filter: brightness(1.05);
        }

        .stDataFrame, div[data-testid="stPlotlyChart"], .st-emotion-cache-1r6slb0 {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(111, 195, 255, 0.2);
            animation: floatIn 0.8s ease both;
        }

        [data-testid="stMetricValue"] {
            color: #f8fcff !important;
            font-weight: 700 !important;
            text-shadow: 0 0 12px rgba(111, 195, 255, 0.22);
        }

        [data-testid="stMetricLabel"] {
            color: #a4cfff !important;
            font-weight: 600 !important;
        }

        .pulse-badge {
            animation: pulseGlow 1.7s infinite;
        }

        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.32); }
            70% { box-shadow: 0 0 0 14px rgba(0, 229, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 229, 255, 0); }
        }

        @keyframes fadeInPage {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes floatIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
