# API Reference

> **Version**: 0.2.0  
> **Base URL**: `http://localhost:8000`

---

## Authentication

No authentication required for local development. Set `OPENWEATHER_API_KEY` in the environment (or `.env` file) to enable weather context.

---

## Endpoints

### `GET /health`

Check service health and component availability.

**Response**
```json
{
  "status": "healthy",
  "crop": "Tomato",
  "model_loaded": true,
  "version": "0.2.0",
  "weather_configured": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"healthy"` or `"degraded: <reason>"` |
| `crop` | string | Target crop name |
| `model_loaded` | boolean | Whether ML model checkpoint is loaded |
| `version` | string | API version |
| `weather_configured` | boolean | `true` if `OPENWEATHER_API_KEY` is set |

---

### `POST /predict`

Upload a leaf image to classify disease, estimate severity, fetch weather context (optional), and compute a contextual risk score.

**Content-Type**: `multipart/form-data`

**Parameters**

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| `file` | form-data | image file | ✅ Yes | Leaf image (JPEG, PNG, WEBP) |
| `lat` | query | float | No | Latitude for weather lookup |
| `lon` | query | float | No | Longitude for weather lookup |
| `city` | query | string | No | City name for weather (used if lat/lon absent) |
| `growth_stage` | query | string | No | `seedling` / `vegetative` / `flowering` / `fruiting` / `ripening` |

> **Note**: Weather lookup is only performed if a location parameter is provided **and** `OPENWEATHER_API_KEY` is configured. If either is absent, `weather` is `null` and the endpoint continues normally.

**Example cURL (image-only)**
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "accept: application/json" \
     -F "file=@leaf_sample.jpg"
```

**Example cURL (with weather + growth stage)**
```bash
curl -X POST "http://localhost:8000/predict?city=Mumbai&growth_stage=flowering" \
     -H "accept: application/json" \
     -F "file=@leaf_sample.jpg"
```

---

**Full Response Schema**

```json
{
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 0.9142,
  "class_probabilities": {
    "Healthy": 0.0125,
    "Early Blight": 0.9142,
    "Late Blight": 0.0511,
    "Leaf Mold": 0.0222
  },
  "scientific_name": "Alternaria solani",
  "symptoms": ["..."],
  "general_causes": ["..."],
  "favorable_conditions": ["..."],
  "general_preventive_information": ["..."],
  "disclaimer": "NOTICE: ...",

  "severity": {
    "severity": "Moderate",
    "affected_area_percentage": 18.5,
    "estimation_method": "opencv_hsv_colour_segmentation",
    "prototype_disclaimer": "PROTOTYPE: ..."
  },

  "weather": {
    "weather_available": true,
    "location_name": "Mumbai",
    "country": "IN",
    "temperature_c": 31.2,
    "humidity_pct": 88,
    "rainfall_mm": 4.5,
    "wind_speed_ms": 3.1,
    "condition": "Rain",
    "description": "moderate rain",
    "error": null
  },

  "risk": {
    "risk_level": "High",
    "risk_score": 0.71,
    "factors": [
      "Disease detected: Early Blight (base risk index: 0.50 — prototype value)",
      "Model confidence: 91.4% (high confidence in prediction)",
      "Moderate affected area: ~18.5% of visible leaf area (heuristic estimate)",
      "High humidity: 88% (within or above disease-favourable band ≥80%)",
      "Temperature 31.2°C within disease-favourable range (24–29°C)",
      "Recent rainfall: 4.5 mm (may facilitate spore splash or spread)",
      "Vulnerable growth stage: flowering (yield-critical period — risk elevated)"
    ],
    "sub_scores": {
      "base_disease": 0.5,
      "model_confidence": 0.9142,
      "severity": 0.185,
      "humidity": 1.0,
      "temperature": 0.76,
      "rainfall": 0.45
    },
    "disclaimer": "PROTOTYPE CONTEXTUAL ESTIMATE: ..."
  }
}
```

**Response when weather unavailable (no location / no API key)**
```json
{
  "...": "...",
  "weather": null,
  "risk": {
    "risk_level": "Medium",
    "risk_score": 0.45,
    "factors": ["..."],
    "sub_scores": {
      "humidity": 0.0,
      "temperature": 0.0,
      "rainfall": 0.0,
      "..."
    }
  }
}
```

---

### Error Responses

| Status | Condition | Example detail |
|--------|-----------|----------------|
| `400` | Non-image file type | `"Invalid file content type 'text/plain'. Must be an image."` |
| `400` | Empty file | `"Uploaded file is empty (0 bytes)."` |
| `400` | Corrupted image | `"Invalid or corrupted image: ..."` |
| `503` | Model not found | `"Model checkpoint unavailable: ..."` |
| `500` | Unexpected server error | `"Inference execution failure: ..."` |

---

## Severity Field — Methodology

The `severity` object is produced by a **prototype heuristic estimator**:

1. The image is converted to HSV colour space (OpenCV).
2. Separate pixel masks are built for:
   - **Healthy green leaf tissue** (HSV hue 35–90, moderate S/V)
   - **Disease-indicator colouration**: yellow chlorosis, brown necrosis, dark lesions
3. `affected_area_percentage = disease_pixels / (green_pixels + disease_pixels) × 100`
4. Mapped to category: Low (< 10%), Moderate (10–30%), High (≥ 30%)

> ⚠️ **These thresholds are prototype estimates.** They have not been validated against standardised disease-severity scales (e.g., Horsfall-Barratt) or field assessments. The `estimation_method` field indicates what algorithm was used, and `prototype_disclaimer` always accompanies the output.

**Severity levels**

| Level | Affected Area (%) | Note |
|-------|-----------------|------|
| Low | 0 – 9.9 | Minimal visible symptoms |
| Moderate | 10 – 29.9 | Noticeable lesions |
| High | ≥ 30 | Extensive damage visible |

---

## Risk Field — Methodology

The `risk` object is produced by a **prototype heuristic scoring engine**:

1. Each factor is scored independently on [0, 1]:
   - **base_disease**: severity of the detected disease from risk profiles
   - **model_confidence**: classifier certainty
   - **severity**: linear mapping of affected area percentage
   - **humidity**: proximity to disease-favourable humidity band
   - **temperature**: proximity to disease-favourable temperature band
   - **rainfall**: recent rainfall effect for splash-transmitted diseases
2. Weighted average applied (see `FACTOR_WEIGHTS` in `engine.py`).
3. Growth stage multiplier applied on top.
4. `risk_score` mapped to `risk_level`:

| Level | Score Range | Meaning |
|-------|------------|---------|
| Low | 0.00 – 0.29 | Minimal concern |
| Medium | 0.30 – 0.54 | Monitor closely |
| High | 0.55 – 0.79 | Take preventive action |
| Critical | ≥ 0.80 | Immediate intervention advised |

> ⚠️ The weights, thresholds, and disease profiles are PROTOTYPE VALUES. They require calibration with validated agricultural / epidemiological data before any official advisory use. All outputs are clearly labelled as contextual estimates.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHER_API_KEY` | Optional | API key from openweathermap.org. Without it, weather context is disabled and the app runs in image-only mode. |

See `.env.example` for setup instructions.

---

## Interactive Documentation

When the FastAPI server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
