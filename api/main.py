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
from src.inference.pipeline import get_inference_pipeline
from src.knowledge.disease_kb import get_knowledge_base
from src.severity.estimator import estimate_severity
from src.weather.service import get_weather_service
from src.risk_engine.engine import compute_risk, compute_risk_with_validation
from src.inference.pest.pipeline import get_pest_pipeline
from src.recommendations import generate_recommendations
from src.alerts import generate_alert, generate_alert_with_validation
from src.utils.prediction_status import PredictionStatus

app = FastAPI(
    title="AI Crop Disease & Pest Intelligence Platform API",
    description=(
        "REST API for automated tomato crop disease classification, pest detection (YOLO), "
        "disease severity estimation (prototype), weather-contextual risk scoring, "
        "structured agricultural recommendations, and real-time risk alerts."
    ),
    version="0.3.0"
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
    pest_model_available: bool


class DiseaseResult(BaseModel):
    name: Optional[str]  # May be None if uncertain
    confidence: float
    prediction_status: str  # Status enum name
    status_message: Optional[str] = None  # Human-readable status explanation
    class_probabilities: Dict[str, float] = {}
    scientific_name: Optional[str] = None
    symptoms: List[str] = []
    general_causes: List[str] = []
    favorable_conditions: List[str] = []
    general_preventive_information: List[str] = []
    disclaimer: Optional[str] = None


class SeverityResult(BaseModel):
    status: str = "UNAVAILABLE"                        # PROTOTYPE | UNRELIABLE | UNAVAILABLE
    level: Optional[str] = None                        # Low | Moderate | High | None
    visible_affected_area_percentage: Optional[float] = None
    method: Optional[str] = None
    message: Optional[str] = None


class PestDetectionItem(BaseModel):
    pest: str
    confidence: float
    bounding_box: List[int]


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
    factors: List[str] = []
    sub_scores: Dict[str, float] = {}
    disclaimer: Optional[str] = None


class RecommendationItem(BaseModel):
    category: str
    message: str
    source: Optional[str] = None


class AlertResult(BaseModel):
    active: bool = False
    severity: Optional[str] = None
    title: Optional[str] = None
    reasons: List[str] = []


class PredictionResponse(BaseModel):
    # ── Core platform intelligence ───────────────────────────────────────────
    crop: str
    disease: DiseaseResult
    severity: SeverityResult
    pests: List[PestDetectionItem] = []
    weather: Optional[WeatherResult] = None
    risk: RiskResult
    recommendations: List[RecommendationItem] = []
    alert: AlertResult


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Check API service health, deep learning models, weather configuration, and pest detection readiness.
    """
    try:
        pipeline = get_inference_pipeline()
        is_disease_model_loaded = pipeline.model is not None
    except Exception as e:
        is_disease_model_loaded = False

    pest_pipeline = get_pest_pipeline()
    is_pest_available = pest_pipeline.is_available

    status_str = "healthy" if is_disease_model_loaded else "degraded: disease model unavailable"

    return HealthResponse(
        status=status_str,
        crop=Config.CROP_NAME,
        model_loaded=is_disease_model_loaded,
        version="0.3.0",
        weather_configured=get_weather_service().is_configured,
        pest_model_available=is_pest_available,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict_crop_intelligence(
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
    Unified crop health analysis pipeline:
    Image → Disease Classification → Severity Estimation → Weather → Risk Engine
    → Pest Detection → Recommendations → Alert Generation → Unified Health Report.
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

    # 4. Run Disease Classification Inference
    try:
        disease_pipeline = get_inference_pipeline()
        inference_result = disease_pipeline.predict(image_bytes)
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Disease model checkpoint unavailable: {str(fnf_err)}"
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted image: {str(val_err)}"
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease inference execution failure: {str(err)}"
        )

    # Extract prediction status and disease info
    predicted_disease = inference_result.get("predicted_disease")  # May be None
    confidence = inference_result["confidence"]
    prediction_status = inference_result["prediction_status"]  # PredictionStatus enum
    status_message = inference_result.get("status_message", "")

    # 5. Retrieve Knowledge Base Information (only if diagnosis is confident)
    kb = get_knowledge_base()
    if predicted_disease:
        disease_info = kb.get_disease_info(predicted_disease)
    else:
        disease_info = {}
    
    preventive_info = (
        disease_info.get("preventive_measures", []) +
        disease_info.get("general_management_practices", [])
    )

    disease_result = DiseaseResult(
        name=predicted_disease,
        confidence=confidence,
        prediction_status=prediction_status.name,
        status_message=status_message,
        class_probabilities=inference_result.get("class_probabilities", {}),
        scientific_name=disease_info.get("scientific_name", "N/A") if predicted_disease else None,
        symptoms=disease_info.get("symptoms", []),
        general_causes=disease_info.get("general_causes", []),
        favorable_conditions=disease_info.get("favorable_conditions", []),
        general_preventive_information=preventive_info,
        disclaimer=disease_info.get("disclaimer", ""),
    )
        symptoms=disease_info.get("symptoms", []),
        general_causes=disease_info.get("general_causes", []),
        favorable_conditions=disease_info.get("favorable_conditions", []),
        general_preventive_information=preventive_info,
        disclaimer=disease_info.get("disclaimer", ""),
    )

    # 6. Severity Estimation (status-aware — skips when diagnosis uncertain)
    try:
        severity_raw = estimate_severity(
            image_bytes, 
            predicted_disease, 
            prediction_status=prediction_status
        )
        severity_result = SeverityResult(**severity_raw)
    except Exception as sev_err:
        severity_result = SeverityResult(
            status="UNAVAILABLE",
            level=None,
            visible_affected_area_percentage=None,
            method="error",
            message=f"Severity estimation error: {str(sev_err)}",
        )

    # 7. Weather Context (optional — gracefully fallback if unavailable)
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

    # 8. Contextual Risk Assessment (status-aware with validation)
    try:
        risk_dict = compute_risk_with_validation(
            disease=predicted_disease,
            confidence=confidence,
            prediction_status=prediction_status,
            severity_pct=severity_result.visible_affected_area_percentage,
            weather_available=weather_for_risk.get("weather_available", False),
            temperature_c=weather_for_risk.get("temperature_c"),
            humidity_pct=weather_for_risk.get("humidity_pct"),
            rainfall_mm=weather_for_risk.get("rainfall_mm"),
            growth_stage=growth_stage,
            location=city or (f"{lat},{lon}" if lat is not None else None),
        )
        risk_result = RiskResult(**risk_dict)
    except Exception as risk_err:
        risk_result = RiskResult(
            risk_level="Medium",
            risk_score=0.5,
            factors=[f"Risk computation error fallback: {str(risk_err)}"],
            sub_scores={},
            disclaimer="Fallback risk result due to computation exception.",
        )

    # 9. Pest Detection Pipeline (independent, graceful fallback)
    detected_pests_list: List[PestDetectionItem] = []
    pests_for_recs: List[Dict[str, Any]] = []

    try:
        pest_pipeline = get_pest_pipeline()
        pest_output = pest_pipeline.predict(image_bytes)
        raw_pests = pest_output.get("pests", [])
        if isinstance(raw_pests, list):
            for p in raw_pests:
                if isinstance(p, dict) and "pest" in p and "confidence" in p and "bounding_box" in p:
                    detected_pests_list.append(PestDetectionItem(**p))
                    pests_for_recs.append(p)
    except Exception:
        # Pest detection failure must never disrupt disease analysis
        detected_pests_list = []
        pests_for_recs = []

    # 10. Structured Recommendation Engine (status-aware)
    try:
        raw_recs = generate_recommendations(
            crop=inference_result.get("crop", Config.CROP_NAME),
            disease=predicted_disease,
            pests=pests_for_recs,
            severity=severity_result.model_dump(),
            weather=weather_result.model_dump() if weather_result else None,
            risk_level=risk_result.risk_level,
            prediction_status=prediction_status,
        )
        recommendations_list = [RecommendationItem(**r) for r in raw_recs]
    except Exception:
        recommendations_list = [
            RecommendationItem(
                category="General Guidance",
                message="Maintain routine crop inspection and consult local agricultural extension services.",
                source="Standard Agricultural Good Practices"
            )
        ]

    # 11. Real-Time Alert Engine (status-aware with suppression)
    try:
        alert_dict = generate_alert_with_validation(
            risk_result.model_dump(),
            prediction_status=prediction_status
        )
        alert_result = AlertResult(**alert_dict)
    except Exception:
        alert_result = AlertResult(active=False, severity=None, title=None, reasons=[])

    return PredictionResponse(
        crop=inference_result["crop"],
        disease=disease_result,
        severity=severity_result,
        pests=detected_pests_list,
        weather=weather_result,
        risk=risk_result,
        recommendations=recommendations_list,
        alert=alert_result,
    )


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _build_weather_result(raw: Dict[str, Any]) -> WeatherResult:
    """Convert raw weather dict to typed WeatherResult."""
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
