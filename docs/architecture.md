# System Architecture

> **Version**: 0.2.0 — Contextual Crop-Health Intelligence  
> **Last updated**: Phase 3 implementation

---

## Overview

The AI Crop Disease & Pest Intelligence Platform is a modular, layered Python application built for tomato leaf disease classification and contextual crop-health risk assessment. It is composed of independently testable subsystems that feed results sequentially.

---

## High-Level Data Flow

```
                        ┌─────────────────────────┐
                        │     Uploaded Leaf Image  │
                        └────────────┬────────────┘
                                     │
               ┌─────────────────────┼──────────────────────┐
               │                     │                        │
               ▼                     ▼                        ▼
  ┌──────────────────────┐  ┌─────────────────┐   ┌──────────────────────┐
  │  Disease Classifier   │  │ Severity        │   │  Weather Service      │
  │  (MobileNetV2 CNN)    │  │ Estimator       │   │  (OpenWeatherMap API) │
  │                       │  │ [PROTOTYPE]      │   │  [OPTIONAL]           │
  │  → disease class      │  │ → severity level │   │  → temperature        │
  │  → confidence score   │  │ → affected %     │   │  → humidity           │
  │  → class probs        │  │                  │   │  → rainfall           │
  └──────────┬───────────┘  └────────┬─────────┘   └──────────┬───────────┘
             │                       │                          │
             └──────────────┬────────┘                         │
                            │                                  │
                            ▼                                  │
               ┌────────────────────────┐                      │
               │  Disease Knowledge     │                      │
               │  Base                  │                      │
               │  → symptoms            │                      │
               │  → causes              │                      │
               │  → preventive info     │                      │
               └────────────┬───────────┘                      │
                            │                                  │
                            └──────────────┬───────────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────┐
                            │  Risk Engine              │
                            │  (Heuristic Scoring)      │
                            │  [PROTOTYPE]              │
                            │                           │
                            │  → risk_level             │
                            │  → risk_score (0–1)       │
                            │  → contributing factors   │
                            └────────────┬──────────────┘
                                         │
                    ┌────────────────────┼─────────────────────┐
                    │                    │                       │
                    ▼                    ▼                       ▼
         ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐
         │  FastAPI REST    │  │  Streamlit Web App  │  │  CLI / Scripts   │
         │  (POST /predict) │  │  (Farmer Interface) │  │  (train, eval)   │
         └──────────────────┘  └────────────────────┘  └──────────────────┘
```

---

## Component Descriptions

### 1. Disease Classifier (`src/inference/pipeline.py`)
- **Model**: MobileNetV2 pre-trained on ImageNet, fine-tuned on PlantVillage tomato subsets.
- **Classes**: Healthy, Early Blight, Late Blight, Leaf Mold.
- **Output**: `predicted_disease`, `confidence`, `class_probabilities`.
- **Type**: Deep learning model inference — output is a *model prediction*, not a laboratory diagnosis.

### 2. Severity Estimator (`src/severity/estimator.py`)
- **Method**: OpenCV HSV colour-space pixel segmentation.
- **Logic**: Builds a green-leaf mask and a disease-indicator mask (brown/yellow/dark), computes ratio.
- **Output**: `severity` (Low/Moderate/High), `affected_area_percentage`.
- ⚠️ **PROTOTYPE**: Thresholds are heuristic estimates. Not validated against standardised severity scales.
- **Graceful degradation**: Returns `Unknown` if OpenCV unavailable or processing fails.

### 3. Weather Service (`src/weather/service.py`)
- **API**: OpenWeatherMap Current Weather endpoint.
- **Auth**: `OPENWEATHER_API_KEY` environment variable — never hard-coded.
- **Output**: temperature, humidity, rainfall, wind speed, condition.
- **Fallback**: If API key absent or request fails, returns `{weather_available: false}`. Pipeline continues normally.

### 4. Disease Knowledge Base (`src/knowledge/disease_kb.py`)
- Static structured lookup of symptoms, causes, favourable conditions, and management practices.
- Sourced from general plant pathology literature; all entries include the professional disclaimer.

### 5. Risk Engine (`src/risk_engine/engine.py`)
- Combines classifier output, severity estimate, and weather data into a weighted composite score.
- **Sub-scorers** (each independently replaceable):
  - Base disease score (from `disease_risk_profiles.py`)
  - Model confidence weighting
  - Severity percentage
  - Humidity alignment with disease-favourable band
  - Temperature alignment with disease-favourable band
  - Rainfall influence
  - Growth stage multiplier
- **Output**: `risk_level` (Low/Medium/High/Critical), `risk_score` (0–1), `factors` (list of strings).
- ⚠️ **PROTOTYPE**: All weights and thresholds require calibration with agricultural field data.
- **Output type**: *Contextual estimate*, not an epidemiological forecast.

---

## Repository Structure

```
ai-crop-disease-pest-intelligence/
├── api/
│   ├── __init__.py
│   └── main.py                        # FastAPI v0.2.0 — POST /predict, GET /health
├── app/
│   └── streamlit_app.py               # Streamlit farmer interface (v0.2.0)
├── src/
│   ├── severity/
│   │   ├── __init__.py
│   │   └── estimator.py               # Prototype heuristic severity estimation
│   ├── weather/
│   │   ├── __init__.py
│   │   └── service.py                 # OpenWeatherMap integration (key from env)
│   ├── risk_engine/
│   │   ├── __init__.py
│   │   ├── engine.py                  # Modular weighted risk scorer
│   │   └── disease_risk_profiles.py   # Per-disease favourable condition bands
│   ├── inference/
│   │   └── pipeline.py                # MobileNetV2 inference engine
│   ├── knowledge/
│   │   └── disease_kb.py              # Structured disease knowledge base
│   ├── preprocessing/                 # Transforms, dataset loaders
│   ├── models/                        # Classifier definitions
│   ├── training/                      # Training loop, schedulers
│   ├── evaluation/                    # Metrics, confusion matrix
│   └── utils/                         # Config, seed, dataset generator
├── tests/
│   ├── test_severity.py               # Severity unit tests
│   ├── test_weather.py                # Weather service tests (mocked)
│   ├── test_risk_engine.py            # Risk engine unit + schema tests
│   ├── test_api.py                    # FastAPI integration tests (v0.2.0)
│   ├── test_inference.py              # Inference pipeline unit tests
│   └── test_knowledge.py              # Knowledge base tests
├── docs/
│   ├── architecture.md                # This document
│   ├── model.md                       # Model card
│   └── api.md                         # API reference
├── .env.example                       # Environment variable template
└── requirements.txt
```

---

## Design Principles

1. **Graceful degradation**: Every optional component (weather, severity) can fail or be absent without crashing the core inference path.
2. **Transparency**: All prototype estimates are labelled as such with explicit disclaimers in code, API responses, and UI.
3. **Modularity**: Each sub-scorer in the risk engine is independently replaceable when better calibration data becomes available.
4. **No hard-coded secrets**: API keys are read from environment variables only.

---

## Phase Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1–2 | ✅ Complete | Disease classification, knowledge base, FastAPI, Streamlit |
| 3 | ✅ Complete | Severity estimation, weather integration, risk engine |
| 4 | 🔜 Planned | Pest detection (pending annotated dataset) |
| 5 | 🔜 Planned | Multi-crop support |
