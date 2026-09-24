"""FastAPI Integration Tests — Unified Crop Disease & Pest Intelligence Platform.

Tests:
- /health endpoint (model_loaded, weather_configured, pest_model_available)
- /predict with valid image (disease, severity, pests, weather, risk, recommendations, alert)
- /predict without location → weather is null
- /predict with mocked pest detections
- /predict with High risk → active alert in response
- /predict invalid file types and empty buffers
- /predict resilience when optional modules (weather, pests) are unconfigured
"""

import sys
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app
from src.utils.config import Config

SAMPLE_IMAGE_PATH = Config.RAW_DATA_DIR / "Tomato___healthy" / "sample_Tomato___healthy_000.jpg"


@pytest.fixture
def client():
    return TestClient(app)


def _create_test_image_bytes():
    """Create a dummy RGB image in memory as bytes."""
    img = Image.fromarray(np.uint8(np.random.randint(50, 200, (150, 150, 3))))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# /health endpoint
# ---------------------------------------------------------------------------

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Tomato"
    assert data["version"] == "0.3.0"
    assert "weather_configured" in data
    assert "pest_model_available" in data
    assert isinstance(data["pest_model_available"], bool)
    assert isinstance(data["weather_configured"], bool)


# ---------------------------------------------------------------------------
# /predict: input validation & errors
# ---------------------------------------------------------------------------

def test_predict_invalid_file_type(client):
    text_content = b"This is plain text, not an image."
    response = client.post(
        "/predict",
        files={"file": ("test.txt", text_content, "text/plain")}
    )
    assert response.status_code == 400
    assert "Must be an image" in response.json()["detail"]


def test_predict_empty_file(client):
    response = client.post(
        "/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# /predict: Unified Pipeline Integration Tests
# ---------------------------------------------------------------------------

def test_predict_unified_response_schema(client, monkeypatch):
    """Verify the complete unified response schema with mocked/live components."""
    # Ensure sample or dummy image is used
    if SAMPLE_IMAGE_PATH.exists():
        img_bytes = SAMPLE_IMAGE_PATH.read_bytes()
    else:
        img_bytes = _create_test_image_bytes()

    response = client.post(
        "/predict",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()

    # 1. Top-level structure
    assert data["crop"] == "Tomato"
    assert "disease" in data
    assert "severity" in data
    assert "pests" in data
    assert "weather" in data
    assert "risk" in data
    assert "recommendations" in data
    assert "alert" in data

    # 2. Disease block
    disease = data["disease"]
    assert "name" in disease
    assert "confidence" in disease
    assert 0.0 <= disease["confidence"] <= 1.0
    assert "class_probabilities" in disease
    assert isinstance(disease["symptoms"], list)
    assert isinstance(disease["general_causes"], list)

    # 3. Severity block
    severity = data["severity"]
    assert severity["level"] in ("Low", "Moderate", "High", "Unknown")
    assert "affected_area_percentage" in severity

    # 4. Pests block
    assert isinstance(data["pests"], list)

    # 5. Weather block (null when no location provided)
    assert data["weather"] is None

    # 6. Risk block
    risk = data["risk"]
    assert risk["risk_level"] in ("Low", "Medium", "High", "Critical")
    assert 0.0 <= risk["risk_score"] <= 1.0
    assert isinstance(risk["factors"], list)

    # 7. Recommendations block
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    for rec in data["recommendations"]:
        assert "category" in rec
        assert "message" in rec

    # 8. Alert block
    alert = data["alert"]
    assert "active" in alert
    assert isinstance(alert["active"], bool)
    assert isinstance(alert["reasons"], list)


def test_predict_with_mocked_pests_and_high_risk_alert(client, monkeypatch):
    """Test unified pipeline when pests are detected and high risk triggers active alert."""
    if SAMPLE_IMAGE_PATH.exists():
        img_bytes = SAMPLE_IMAGE_PATH.read_bytes()
    else:
        img_bytes = _create_test_image_bytes()

    # Mock pest pipeline to return simulated detections
    class MockPestPipeline:
        @property
        def is_available(self): return True
        def predict(self, _):
            return {
                "status": "available",
                "pests": [
                    {"pest": "Aphid", "confidence": 0.94, "bounding_box": [12, 14, 80, 85]},
                    {"pest": "Whitefly", "confidence": 0.88, "bounding_box": [110, 60, 190, 140]},
                ],
                "message": "Detections complete",
            }

    # Mock risk engine to return High risk
    def mock_compute_risk(**kwargs):
        return {
            "risk_level": "High",
            "risk_score": 0.78,
            "factors": [
                "Disease detected: Early Blight",
                "Severe symptoms observed",
                "High humidity: 90%",
            ],
            "sub_scores": {"base_disease": 0.5, "severity": 0.4},
            "disclaimer": "Prototype risk disclaimer",
        }

    monkeypatch.setattr("api.main.get_pest_pipeline", lambda: MockPestPipeline())
    monkeypatch.setattr("api.main.compute_risk", mock_compute_risk)

    response = client.post(
        "/predict?growth_stage=flowering",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify pests are present in unified output
    assert len(data["pests"]) == 2
    assert data["pests"][0]["pest"] == "Aphid"
    assert data["pests"][1]["pest"] == "Whitefly"

    # Verify recommendations include pest advice
    rec_categories = [r["category"] for r in data["recommendations"]]
    rec_messages = " ".join([r["message"] for r in data["recommendations"]])
    assert "aphid" in rec_messages.lower() or "whitefly" in rec_messages.lower()

    # Verify alert is active due to High risk
    alert = data["alert"]
    assert alert["active"] is True
    assert alert["severity"] == "High"
    assert "High" in alert["title"]
    assert len(alert["reasons"]) == 3


def test_predict_weather_failure_resilience(client, monkeypatch):
    """Test that weather API failure or unconfigured key does not fail prediction."""
    if SAMPLE_IMAGE_PATH.exists():
        img_bytes = SAMPLE_IMAGE_PATH.read_bytes()
    else:
        img_bytes = _create_test_image_bytes()

    # Force weather service to return unavailable
    class MockWeatherSvc:
        @property
        def is_configured(self): return False
        def get_weather_by_city(self, _):
            return {"weather_available": False, "error": "API key not configured"}

    monkeypatch.setattr("api.main.get_weather_service", lambda: MockWeatherSvc())

    response = client.post(
        "/predict?city=London",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["weather"] is not None
    assert data["weather"]["weather_available"] is False
    # Core intelligence must still succeed
    assert data["crop"] == "Tomato"
    assert "disease" in data
    assert "risk" in data
    assert len(data["recommendations"]) > 0
