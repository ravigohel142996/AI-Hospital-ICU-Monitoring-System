# AI Hospital ICU Monitoring System

A production-level AI-powered ICU patient monitoring dashboard built with **Python**, **Streamlit**, and **Scikit-learn**.

## Features

- **Dashboard Overview** – Real-time vitals display, system status (SAFE / WARNING / CRITICAL), risk gauge chart
- **Live Monitoring** – Simulated streaming ICU vitals with interactive Plotly charts (auto-refresh every 2 s)
- **Risk Prediction** – Slider-based patient vitals input, RandomForest risk score prediction
- **Analytics** – Vital distribution histograms, correlation heatmap, risk score trends
- **Model Insights** – Feature importances, cross-validation scores, model configuration

## Project Structure

```
├── app.py                     # Dashboard Overview (main page)
├── train_model.py             # One-time model training script
├── requirements.txt
├── pages/
│   ├── 1_Live_Monitoring.py
│   ├── 2_Risk_Prediction.py
│   ├── 3_Analytics.py
│   └── 4_Model_Insights.py
├── utils/
│   ├── simulator.py           # ICU vitals data generator
│   └── predictor.py           # Model loader & prediction interface
├── models/
│   └── icu_risk_model.pkl     # Trained RandomForestRegressor
├── data/
│   └── icu_patient_data.csv   # Synthetic patient dataset (500 records)
├── assets/
└── notebooks/
    └── model_training.ipynb
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train and save the model (generates models/ and data/ files)
python train_model.py

# 3. Launch the Streamlit app
streamlit run app.py
```

## Tech Stack

| Component | Library |
|-----------|---------|
| UI Framework | Streamlit |
| Charts | Plotly |
| ML Model | Scikit-learn RandomForestRegressor |
| Data | Pandas, NumPy |
| Model Serialization | Joblib |

## Risk Classification

| Score Range | Status |
|-------------|--------|
| 0.00 – 0.34 | SAFE (green) |
| 0.35 – 0.64 | WARNING (orange) |
| 0.65 – 1.00 | CRITICAL (red) |
