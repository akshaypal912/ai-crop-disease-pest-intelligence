import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Load .env file if present (development convenience; no-op in production)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.utils.config import Config
from src.inference.pipeline import get_inference_pipeline, DiseaseInferencePipeline
from src.knowledge.disease_kb import get_knowledge_base, DiseaseKnowledgeBase
from src.severity.estimator import estimate_severity
from src.weather.service import get_weather_service, reset_weather_service
from src.risk_engine.engine import compute_risk

app = FastAPI(
    title="AI Crop Disease & Pest Intelligence Platform API",
    description=(
        "REST API for automated tomato crop disease classification, disease severity "
        "estimation (prototype), weather-contextual risk scoring, and agricultural "
        "decision support. Version 0.2.0 adds contextual crop-health intelligence."
    ),
    version="0.2.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    crop: str
    model_loaded: bool
    version: str
    weather_configured: bool


class SeverityResult(BaseModel):
    severity: str                          # Low | Moderate | High | Unknown
    affected_area_percentage: Optional[float]
    estimation_method: str
    prototype_disclaimer: str


class WeatherResult(BaseModel):
    weather_available: bool
    location_name: Optional[str] = None
    country: Optional[str] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    rainfall_mm: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None


class RiskResult(BaseModel):
    risk_level: str                        # Low | Medium | High | Critical
    risk_score: float                      # 0.0 – 1.0
    factors: List[str]
    sub_scores: Dict[str, float]
    disclaimer: str


class PredictionResponse(BaseModel):
    # ── Core classification ──────────────────────────────────────────────────
    crop: str
    disease: str
    confidence: float
    class_probabilities: Dict[str, float]
    # ── Disease knowledge ────────────────────────────────────────────────────
    scientific_name: str
    symptoms: List[str]
    general_causes: List[str]
    favorable_conditions: List[str]
    general_preventive_information: List[str]
    disclaimer: str
    # ── Contextual intelligence (new in v0.2.0) ──────────────────────────────
    severity: SeverityResult
    weather: Optional[WeatherResult] = None
    risk: RiskResult


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Check API service health, deep learning model state, and weather service availability.
    """
    try:
        pipeline = get_inference_pipeline()
        is_loaded = pipeline.model is not None
    except Exception as e:
        return HealthResponse(
            status=f"degraded: {str(e)}",
            crop=Config.CROP_NAME,
            model_loaded=False,
            version="0.2.0",
            weather_configured=get_weather_service().is_configured,
        )

    return HealthResponse(
        status="healthy",
        crop=Config.CROP_NAME,
        model_loaded=is_loaded,
        version="0.2.0",
        weather_configured=get_weather_service().is_configured,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict_crop_disease(
    file: UploadFile = File(...),
    lat: Optional[float] = Query(
        default=None,
        description="Latitude for weather lookup (requires OPENWEATHER_API_KEY)."
    ),
    lon: Optional[float] = Query(
        default=None,
        description="Longitude for weather lookup (requires OPENWEATHER_API_KEY)."
    ),
    city: Optional[str] = Query(
        default=None,
        description="City name for weather lookup (used when lat/lon not provided)."
    ),
    growth_stage: Optional[str] = Query(
        default=None,
        description=(
            "Current crop growth stage for risk scoring. "
            "One of: seedling, vegetative, flowering, fruiting, ripening."
        ),
    ),
):
    """
    Upload a leaf image to predict crop disease, estimate severity, fetch weather
    context (optional), and compute a contextual risk score.

    **New in v0.2.0**:
    - `severity` — heuristic affected-area estimate (prototype; see disclaimer).
    - `weather` — current weather if location params provided and API key set.
    - `risk` — composite contextual risk score combining all available signals.

    Weather is optional: if location params or API key are absent, the endpoint
    continues in image-only mode and `weather` will be `null`.
    """
    # 1. Validate file presence
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided in upload request."
        )

    # 2. Check content type header if provided
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file content type '{file.content_type}'. Must be an image (JPEG, PNG, etc.)."
        )

    # 3. Read image bytes
    try:
        image_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file buffer: {str(e)}"
        )

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    # 4. Run Model Inference Engine
    try:
        pipeline = get_inference_pipeline()
        inference_result = pipeline.predict(image_bytes)
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model checkpoint unavailable: {str(fnf_err)}"
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted image: {str(val_err)}"
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failure: {str(err)}"
        )

    predicted_disease = inference_result["predicted_disease"]
    confidence = inference_result["confidence"]

    # 5. Retrieve Disease Knowledge Base Information
    kb = get_knowledge_base()
    disease_info = kb.get_disease_info(predicted_disease)
    preventive_info = (
        disease_info.get("preventive_measures", []) +
        disease_info.get("general_management_practices", [])
    )

    # 6. Severity Estimation (prototype — always attempted)
    try:
        severity_raw = estimate_severity(image_bytes, predicted_disease)
    except Exception:
        severity_raw = {
            "severity": "Unknown",
            "affected_area_percentage": None,
            "estimation_method": "error",
            "prototype_disclaimer": "Severity estimation failed.",
        }

    severity_result = SeverityResult(**severity_raw)

    # 7. Weather (optional — gracefully skipped if not configured / not requested)
    weather_result: Optional[WeatherResult] = None
    weather_for_risk: Dict[str, Any] = {}

    weather_svc = get_weather_service()
    if lat is not None and lon is not None:
        raw_weather = weather_svc.get_weather(lat, lon)
        weather_result = _build_weather_result(raw_weather)
        weather_for_risk = raw_weather
    elif city:
        raw_weather = weather_svc.get_weather_by_city(city)
        weather_result = _build_weather_result(raw_weather)
        weather_for_risk = raw_weather

    # 8. Risk Engine
    risk_dict = compute_risk(
        disease=predicted_disease,
        confidence=confidence,
        severity_pct=severity_raw.get("affected_area_percentage"),
        temperature_c=weather_for_risk.get("temperature_c"),
        humidity_pct=weather_for_risk.get("humidity_pct"),
        rainfall_mm=weather_for_risk.get("rainfall_mm"),
        growth_stage=growth_stage,
        location=city or (f"{lat},{lon}" if lat is not None else None),
    )
    risk_result = RiskResult(**risk_dict)

    return PredictionResponse(
        crop=inference_result["crop"],
        disease=predicted_disease,
        confidence=confidence,
        class_probabilities=inference_result["class_probabilities"],
        scientific_name=disease_info.get("scientific_name", "N/A"),
        symptoms=disease_info.get("symptoms", []),
        general_causes=disease_info.get("general_causes", []),
        favorable_conditions=disease_info.get("favorable_conditions", []),
        general_preventive_information=preventive_info,
        disclaimer=disease_info.get("disclaimer", ""),
        severity=severity_result,
        weather=weather_result,
        risk=risk_result,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_weather_result(raw: Dict[str, Any]) -> WeatherResult:
    """Convert raw weather dict to typed WeatherResult (strips extra fields)."""
    return WeatherResult(
        weather_available=raw.get("weather_available", False),
        location_name=raw.get("location_name"),
        country=raw.get("country"),
        temperature_c=raw.get("temperature_c"),
        humidity_pct=raw.get("humidity_pct"),
        rainfall_mm=raw.get("rainfall_mm"),
        wind_speed_ms=raw.get("wind_speed_ms"),
        condition=raw.get("condition"),
        description=raw.get("description"),
        error=raw.get("error"),
    )
