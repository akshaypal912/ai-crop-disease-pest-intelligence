"""
FastAPI Integration Tests — Updated for v0.2.0

Tests:
- /health endpoint (now includes weather_configured field)
- /predict with valid image → includes severity + risk in response
- /predict without location → weather field is null
- /predict with invalid file type → 400
- /predict with empty file → 400
- /predict response schema completeness
"""

import os
import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app
from src.utils.config import Config

SAMPLE_IMAGE_PATH = Config.RAW_DATA_DIR / "Tomato___healthy" / "sample_Tomato___healthy_000.jpg"


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# /health endpoint
# ---------------------------------------------------------------------------

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Tomato"
    assert "version" in data
    # v0.2.0: weather_configured field must be present
    assert "weather_configured" in data
    assert isinstance(data["weather_configured"], bool)


def test_health_endpoint_version(client):
    response = client.get("/health")
    data = response.json()
    assert data["version"] == "0.2.0"


# ---------------------------------------------------------------------------
# /predict: invalid inputs
# ---------------------------------------------------------------------------

def test_predict_endpoint_invalid_file_type(client):
    text_content = b"This is plain text content, not an image file."
    response = client.post(
        "/predict",
        files={"file": ("test.txt", text_content, "text/plain")}
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Must be an image" in detail or "Invalid" in detail


def test_predict_endpoint_empty_file(client):
    empty_content = b""
    response = client.post(
        "/predict",
        files={"file": ("empty.jpg", empty_content, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# /predict: valid image (requires sample data and trained model)
# ---------------------------------------------------------------------------

def test_predict_endpoint_valid_image_base_schema(client):
    """Core schema test — severity + risk fields must be present."""
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")

    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": ("test_leaf.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()

    # ── Core classification fields (unchanged from v0.1) ─────────────────────
    assert data["crop"] == "Tomato"
    assert data["disease"] in Config.TARGET_CLASSES
    assert 0.0 <= data["confidence"] <= 1.0
    assert "class_probabilities" in data
    assert "scientific_name" in data
    assert isinstance(data["symptoms"], list)
    assert isinstance(data["general_causes"], list)
    assert isinstance(data["favorable_conditions"], list)
    assert isinstance(data["general_preventive_information"], list)
    assert len(data["disclaimer"]) > 0

    # ── New v0.2.0: Severity ──────────────────────────────────────────────────
    assert "severity" in data, "severity field missing from response"
    sev = data["severity"]
    assert "severity" in sev
    assert sev["severity"] in ("Low", "Moderate", "High", "Unknown")
    assert "affected_area_percentage" in sev
    assert "estimation_method" in sev
    assert "prototype_disclaimer" in sev
    assert isinstance(sev["prototype_disclaimer"], str)

    # ── New v0.2.0: Risk ──────────────────────────────────────────────────────
    assert "risk" in data, "risk field missing from response"
    risk = data["risk"]
    assert risk["risk_level"] in ("Low", "Medium", "High", "Critical")
    assert 0.0 <= risk["risk_score"] <= 1.0
    assert isinstance(risk["factors"], list)
    assert isinstance(risk["sub_scores"], dict)
    assert "disclaimer" in risk


def test_predict_endpoint_weather_is_null_without_location(client):
    """Without lat/lon/city params, weather must be null."""
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")

    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": ("test_leaf.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["weather"] is None, (
        f"Expected weather=null when no location params provided, got: {data['weather']}"
    )


def test_predict_endpoint_risk_score_in_range(client):
    """Risk score must always be in [0, 1]."""
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")

    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": ("test_leaf.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    risk_score = response.json()["risk"]["risk_score"]
    assert 0.0 <= risk_score <= 1.0


def test_predict_endpoint_growth_stage_param(client):
    """growth_stage query param should be accepted without error."""
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")

    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/predict?growth_stage=flowering",
            files={"file": ("test_leaf.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    # flowering stage factor may appear in risk factors
    data = response.json()
    assert "risk" in data


def test_predict_endpoint_missing_weather_config_still_works(client, monkeypatch):
    """Even if OPENWEATHER_API_KEY is absent, predict must succeed."""
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")

    # Ensure weather key is not set
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    # Force re-init of weather service singleton to pick up env change
    from src.weather import service as ws_mod
    ws_mod._service_instance = None

    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/predict?city=Mumbai",
            files={"file": ("test_leaf.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    # weather should be either null or show weather_available=false
    if data["weather"] is not None:
        assert data["weather"]["weather_available"] is False
