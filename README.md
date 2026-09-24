# AI-Based Crop Disease & Pest Intelligence Platform

An end-to-end, modular deep learning and agronomic intelligence solution for crop disease classification, pest detection, contextual severity estimation, weather-aware risk assessment, structured agricultural recommendations, and real-time risk alerts.

---

## 🌟 Unified Intelligence Architecture

```
                                 Uploaded Leaf Image
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  ▼                       ▼                       ▼
       ┌──────────────────────┐┌──────────────────────┐┌──────────────────────┐
       │ Disease Classifier   ││ Severity Estimator   ││ Pest Detection (YOLO)│
       │ (MobileNetV2 CNN)    ││ (HSV Segmentation)   ││ [CONFIG REQUIRED]    │
       │ → disease + conf     ││ [PROTOTYPE]          ││ → pest + bbox + conf │
       └──────────┬───────────┘└──────────┬───────────┘└──────────┬───────────┘
                  │                       │                       │
                  └──────────────┬────────┘                       │
                                 ▼                                │
                      ┌──────────────────────┐                    │
                      │ Disease KB           │                    │
                      │ (Symptoms, Causes)   │                    │
                      └──────────┬───────────┘                    │
                                 │                                │
                                 ▼                                │
                      ┌──────────────────────┐                    │
                      │ Weather Service      │                    │
                      │ (OpenWeatherMap API) │                    │
                      │ [OPTIONAL]           │                    │
                      └──────────┬───────────┘                    │
                                 │                                │
                                 ▼                                │
                      ┌──────────────────────┐                    │
                      │ Risk Engine          │                    │
                      │ (Heuristic Scoring)  │                    │
                      │ [PROTOTYPE]          │                    │
                      └──────────┬───────────┘                    │
                                 │                                │
                  ┌──────────────┴────────────────────────────────┘
                  ▼
       ┌──────────────────────────────────────────────────────────────┐
       │ Recommendation Engine (IPM, Cultural, Non-chemical Guidelines)│
       └──────────────────────────────┬───────────────────────────────┘
                                      ▼
       ┌──────────────────────────────────────────────────────────────┐
       │ Alert Engine (High/Critical Real-Time Risk Notification)     │
       └──────────────────────────────┬───────────────────────────────┘
                                      ▼
                      Unified Crop Health Report
```

> ⚗️ **Prototype & Validation Notice**: Severity estimation and risk engine scoring are heuristic decision-support prototypes and are not scientifically calibrated on formal field-trial epidemiology datasets. Outputs carry explicit disclaimers.

---

## 📁 Repository Structure

```
ai-crop-disease-pest-intelligence/
├── api/
│   ├── __init__.py
│   └── main.py                        # Unified FastAPI REST API v0.3.0
├── app/
│   └── streamlit_app.py               # Streamlit Farmer Interface
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
│   ├── test_pest_detection.py         # Pest detection tests (NEW)
│   ├── test_recommendations.py        # Recommendation engine tests (NEW)
│   ├── test_alerts.py                 # Alert engine tests (NEW)
│   ├── test_api.py                    # Unified API tests (UPDATED)
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

## 🚀 Component Status & Readiness

| Subsystem | Status | Description |
|-----------|--------|-------------|
| **Disease Classification** | **IMPLEMENTED** | MobileNetV2 trained on 4 classes (Healthy, Early Blight, Late Blight, Leaf Mold). |
| **Severity Estimation** | **IMPLEMENTED (Prototype)** | OpenCV HSV colour-space segmentation with heuristic category mapping. |
| **Weather Context** | **IMPLEMENTED (Optional)** | OpenWeatherMap API integration. Graceful fallback if unconfigured. |
| **Risk Engine** | **IMPLEMENTED (Prototype)** | Multi-factor weighted contextual risk index (0.0 to 1.0). |
| **Pest Detection** | **CONFIGURATION REQUIRED** | Pipeline & detector architecture fully implemented; requires placing trained `pest_yolov8.pt` weights in `src/models/pest_detection/weights/`. Gracefully returns empty list if weights are missing. |
| **Recommendation Engine** | **IMPLEMENTED** | Rule-based, source-attributed IPM guidance without unsafe chemical dosages. |
| **Alert Engine** | **IMPLEMENTED** | Automated alert payload generator for High and Critical risk levels. |

---

## ⚡ Quick Start

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
# Optional: Weather integration
OPENWEATHER_API_KEY=your_openweathermap_api_key_here

# Optional: Custom path to trained YOLOv8 pest model weights
PEST_MODEL_PATH=src/models/pest_detection/weights/pest_yolov8.pt
```

### 3. Start the Unified API

```bash
uvicorn api.main:app --reload --port 8000
```

- **Interactive API Docs (Swagger)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`

---

## 📡 Unified API Response Example

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
    "humidity_pct": 86,
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

## 🧪 Testing

Run the full automated test suite (97 tests):

```bash
pytest tests/ -v
```

Run specific test modules:

```bash
# Pest detection tests
pytest tests/test_pest_detection.py -v

# Recommendation engine tests
pytest tests/test_recommendations.py -v

# Alert engine tests
pytest tests/test_alerts.py -v

# API integration tests
pytest tests/test_api.py -v
```

---

## ⚠️ Current Scope & Limitations

1. **Pest Model Weights**: The pest detection architecture is implemented and unit-tested with mocks and graceful fallbacks. Actual pest inference on real images requires downloading or training YOLOv8 weights (`pest_yolov8.pt`).
2. **Prototype Estimates**: Severity percentages and risk scores are heuristic indices designed to demonstrate contextual intelligence workflows, not certified agronomic diagnostics.
3. **Chemical Safety**: The recommendation engine strictly limits advice to non-chemical IPM, cultural, biological, and sanitation measures; pesticide prescriptions require certified local extension consultation.
4. **Single-Crop Focus**: Currently focused on Tomato (*Solanum lycopersicum*).

---

## 📜 License

Licensed under the MIT License.
