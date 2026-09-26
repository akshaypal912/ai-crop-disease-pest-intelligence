# AI-Based Crop Disease & Pest Intelligence Platform

An end-to-end, modular deep learning and agronomic intelligence solution for crop disease classification, pest detection, contextual severity estimation, weather-aware risk assessment, structured agricultural recommendations, real-time risk alerts, and an interactive farmer dashboard.

---

## 🌟 Application Flow Architecture

```
                             Farmer / User
                                  │
                                  ▼ (Uploads Image via UI)
                     Streamlit Farmer Dashboard
                                  │
                                  ▼ (HTTP POST /predict)
                          FastAPI Backend
                                  │
                                  ▼
                        Analysis Orchestrator
                                  │
  ┌───────────────────────────────┼───────────────────────────────┐
  ▼                               ▼                               ▼
Disease Model (CNN)      Severity Estimator           Pest Detection (YOLO)
[MobileNetV2 Transfer]   [HSV Segmentation]           [CONFIG REQUIRED]
→ Disease + Confidence   → Severity Level (Prototype) → Pests + Bounding Boxes
  │                               │                               │
  └──────────────┬────────────────┘                               │
                 ▼                                                │
       Disease Knowledge Base                                     │
       (Symptoms & Causes)                                        │
                 │                                                │
                 ▼                                                │
          Weather Service                                         │
       (OpenWeatherMap API)                                       │
                 │                                                │
                 ▼                                                │
            Risk Engine                                           │
       (Multi-Factor Heuristic)                                   │
                 │                                                │
  ┌──────────────┴────────────────────────────────────────────────┘
  ▼
Recommendation Engine (IPM, Cultural, Non-chemical Guidelines)
  │
  ▼
Alert Engine (High/Critical Real-Time Risk Notification)
  │
  ▼
Unified Crop Health Report
  │
  ▼ (JSON Response)
Streamlit Farmer Dashboard (Interactive Cards, Alerts, History & Visualization)
```

> ⚗️ **Prototype & Validation Notice**: Severity estimation and contextual risk scoring are prototype heuristics designed for agricultural decision-support; they are not scientifically calibrated on formal field-trial epidemiology datasets. Disease classification is trained on tomato leaf subsets and should be visually confirmed. All outputs carry explicit disclaimers.

---

## 🚀 Current Feature Status

| Feature / Subsystem | Status | Description |
|---------------------|--------|-------------|
| **Disease Classification** | **IMPLEMENTED** | MobileNetV2 fine-tuned on Tomato health classes (Healthy, Early Blight, Late Blight, Leaf Mold). |
| **Disease Severity Estimation** | **IMPLEMENTED (Prototype)** | OpenCV HSV colour-space segmentation with heuristic category thresholds (Low, Moderate, High). |
| **Weather Context** | **IMPLEMENTED (Optional)** | OpenWeatherMap API integration. Gracefully skipped when unconfigured. |
| **Risk Scoring Engine** | **IMPLEMENTED (Prototype)** | Multi-factor weighted index combining model confidence, severity heuristics, and environmental bands. |
| **Pest Detection** | **CONFIGURATION REQUIRED** | YOLOv8 pipeline and inference architecture fully implemented with graceful fallback. Requires placing trained `pest_yolov8.pt` weights in `src/models/pest_detection/weights/`. No fake predictions are generated. |
| **Structured Recommendations** | **IMPLEMENTED** | Source-attributed IPM, sanitation, cultural, and scouting guidelines without arbitrary chemical dosages. |
| **Real-Time Risk Alerts** | **IMPLEMENTED** | High and Critical risk alerts with contributing reason summaries. |
| **Farmer Web Dashboard** | **IMPLEMENTED** | Glassmorphism Streamlit interface with live API integration, pest bounding box overlay, weather grid, and session analysis history. |

---

## 📁 Repository Structure

```
ai-crop-disease-pest-intelligence/
├── api/
│   ├── __init__.py
│   └── main.py                        # Unified FastAPI REST API v0.3.0
├── app/
│   └── streamlit_app.py               # Upgraded Streamlit Farmer Dashboard
├── src/
│   ├── models/
│   │   ├── classifier.py              # MobileNetV2 disease model
│   │   └── pest_detection/            # YOLOv8 pest detection wrapper
│   │       ├── __init__.py
│   │       └── weights/               # (Place pest_yolov8.pt here)
│   ├── inference/
│   │   ├── pipeline.py                # Disease inference pipeline
│   │   └── pest/                      # Pest inference pipeline
│   │       ├── __init__.py
│   │       └── pipeline.py
│   ├── severity/
│   │   ├── __init__.py
│   │   └── estimator.py               # Prototype HSV colour segmentation
│   ├── weather/
│   │   ├── __init__.py
│   │   └── service.py                 # OpenWeatherMap integration
│   ├── risk_engine/
│   │   ├── __init__.py
│   │   ├── engine.py                  # Contextual risk scorer
│   │   └── disease_risk_profiles.py   # Environmental risk profiles
│   ├── recommendations/
│   │   ├── __init__.py
│   │   └── recommendation_engine.py   # Structured IPM recommendation engine
│   ├── alerts/
│   │   ├── __init__.py
│   │   └── engine.py                  # Real-time risk alert engine
│   ├── knowledge/
│   │   └── disease_kb.py              # Agricultural disease knowledge base
│   ├── preprocessing/                 # Transforms and data loaders
│   ├── training/                      # Model training routines
│   ├── evaluation/                    # Evaluation & confusion matrix
│   └── utils/                         # Config & dataset utilities
├── tests/
│   ├── test_pest_detection.py         # Pest detection tests
│   ├── test_recommendations.py        # Recommendation engine tests
│   ├── test_alerts.py                 # Alert engine tests
│   ├── test_api.py                    # Unified API tests
│   ├── test_severity.py               # Severity unit tests
│   ├── test_weather.py                # Weather service unit tests
│   ├── test_risk_engine.py            # Risk engine unit tests
│   ├── test_inference.py              # Disease inference tests
│   └── test_knowledge.py              # Knowledge base tests
├── docs/                              # System documentation
├── .env.example                       # Environment variable template
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start & Running the Platform

### 1. Installation

```bash
git clone https://github.com/akshaypal912/ai-crop-disease-pest-intelligence.git
cd ai-crop-disease-pest-intelligence

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Configuration (Optional)

```bash
copy .env.example .env
```

Edit `.env`:
```env
# Optional: Live weather context
OPENWEATHER_API_KEY=your_openweathermap_api_key_here

# Optional: Custom API URL for Streamlit frontend
API_BASE_URL=http://localhost:8000

# Optional: Path to custom YOLOv8 pest weights
PEST_MODEL_PATH=src/models/pest_detection/weights/pest_yolov8.pt
```

### 3. Running Backend (FastAPI REST API)

Start the FastAPI application:

```bash
uvicorn api.main:app --reload --port 8000
```

- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### 4. Running Frontend (Streamlit Dashboard)

In a separate terminal, launch the Streamlit farmer dashboard:

```bash
streamlit run app/streamlit_app.py
```

- **Farmer Dashboard URL**: `http://localhost:8501`

---

## 📡 API Response Structure

### `POST /predict?city=Mumbai&growth_stage=flowering`

```json
{
  "crop": "Tomato",
  "disease": {
    "name": "Early Blight",
    "confidence": 0.9142,
    "class_probabilities": {
      "Healthy": 0.0125,
      "Early Blight": 0.9142,
      "Late Blight": 0.0511,
      "Leaf Mold": 0.0222
    },
    "scientific_name": "Alternaria solani",
    "symptoms": ["Dark brown to black spots with concentric rings on lower leaves..."],
    "general_causes": ["Fungal pathogen Alternaria solani..."],
    "favorable_conditions": ["Warm temperatures (24-29°C), high humidity (>80%)..."],
    "general_preventive_information": ["Avoid overhead irrigation", "Practice crop rotation..."],
    "disclaimer": "NOTICE: This system provides informational guidance..."
  },
  "severity": {
    "level": "Moderate",
    "affected_area_percentage": 18.5,
    "estimation_method": "opencv_hsv_colour_segmentation",
    "prototype_disclaimer": "PROTOTYPE: Severity is a heuristic estimate..."
  },
  "pests": [
    {
      "pest": "Aphid",
      "confidence": 0.9234,
      "bounding_box": [12, 14, 80, 85]
    }
  ],
  "weather": {
    "weather_available": true,
    "location_name": "Mumbai",
    "country": "IN",
    "temperature_c": 28.5,
    "humidity_pct": 86.0,
    "rainfall_mm": 4.2,
    "condition": "Rain"
  },
  "risk": {
    "risk_level": "High",
    "risk_score": 0.74,
    "factors": [
      "Disease detected: Early Blight (base risk index: 0.50)",
      "Model confidence: 91.4%",
      "Moderate affected area: ~18.5%",
      "High humidity: 86%",
      "Recent rainfall: 4.2 mm",
      "Vulnerable growth stage: flowering"
    ]
  },
  "recommendations": [
    {
      "category": "Sanitation",
      "message": "Prune and safely discard lower infected leaves showing concentric lesions to reduce fungal inoculum.",
      "source": "University Agricultural Extension IPM Guidelines"
    },
    {
      "category": "Biological Control",
      "message": "Encourage natural predators such as lady beetles and hoverfly larvae for aphid suppression.",
      "source": "FAO Tomato Integrated Pest Management"
    },
    {
      "category": "Humidity Management",
      "message": "Elevated humidity (86%): Increase ventilation in covered structures to minimize spore transmission.",
      "source": "University Agricultural Extension IPM Guidelines"
    },
    {
      "category": "Urgent Action",
      "message": "Elevated crop health risk: Prioritize immediate scouting and seek qualified professional agronomic advice.",
      "source": "National Agricultural Extension Service"
    }
  ],
  "alert": {
    "active": true,
    "severity": "High",
    "title": "High Crop Health Alert",
    "reasons": [
      "Disease detected: Early Blight (base risk index: 0.50)",
      "High humidity: 86%",
      "Recent rainfall: 4.2 mm",
      "Vulnerable growth stage: flowering"
    ]
  }
}
```

---

## 🧪 Automated Testing

Run the entire automated test suite:

```bash
pytest tests/ -v
```

All 97 unit and integration tests validate the complete end-to-end pipeline:
- `test_pest_detection.py`: Graceful missing-weights fallback, input formats, mocked bounding boxes.
- `test_recommendations.py`: Multi-category generation, source metadata, chemical safety verification.
- `test_alerts.py`: High/Critical active triggers, Low/Medium inactive states.
- `test_api.py`: FastAPI `/health` and `/predict` integration, error handling, weather resilience.
- `test_severity.py`, `test_weather.py`, `test_risk_engine.py`, `test_inference.py`, `test_knowledge.py`.

---

## ⚠️ Current Scope & Limitations

1. **Pest Model Weights**: The pest detection pipeline is fully implemented and tested with mocks. Actual pest detection on physical images requires placing trained YOLOv8 weights (`pest_yolov8.pt`) in `src/models/pest_detection/weights/`. The system currently operates safely with graceful fallback.
2. **Prototype Estimates**: Severity percentages and risk index scores are heuristic approximations designed for contextual decision-support, not laboratory diagnoses.
3. **Pesticide Prescriptions**: Recommendation engine strictly limits guidance to non-chemical IPM, cultural, biological, and sanitation measures; chemical treatments require certified local agronomist consultation.
4. **Target Crop**: Currently focused on Tomato (*Solanum lycopersicum*).

---

## 📜 License

Licensed under the MIT License.
