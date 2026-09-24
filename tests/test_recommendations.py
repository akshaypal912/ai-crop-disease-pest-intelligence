"""Unit Tests for Recommendation Engine.

Tests:
- Output schema verification (category, message, optional source)
- Disease-specific recommendations
- Pest-specific recommendations
- Severity-based recommendations
- Weather context recommendations
- Combined multi-factor recommendations
- Fallback when no conditions matched
- Safety verification (no unsafe chemical dosage instructions)
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.recommendations import generate_recommendations


class TestRecommendationSchema:
    def test_basic_schema(self):
        recs = generate_recommendations(disease="Early Blight")
        assert isinstance(recs, list)
        assert len(recs) > 0
        for r in recs:
            assert "category" in r
            assert "message" in r
            assert isinstance(r["category"], str)
            assert isinstance(r["message"], str)
            if "source" in r:
                assert isinstance(r["source"], str)

    def test_disclaimer_always_present(self):
        recs = generate_recommendations(disease="Healthy")
        categories = [r["category"] for r in recs]
        assert "Disclaimer" in categories


class TestDiseaseRecommendations:
    def test_early_blight_recs(self):
        recs = generate_recommendations(disease="Early Blight")
        categories = {r["category"] for r in recs}
        assert "Sanitation" in categories or "Cultural Control" in categories
        # Verify source metadata exists
        sources = [r.get("source") for r in recs if "source" in r]
        assert len(sources) > 0

    def test_late_blight_recs(self):
        recs = generate_recommendations(disease="Late Blight")
        categories = {r["category"] for r in recs}
        assert "Monitoring" in categories or "Sanitation" in categories

    def test_healthy_recs(self):
        recs = generate_recommendations(disease="Healthy")
        messages = " ".join([r["message"] for r in recs])
        assert "Preventive Scouting" in [r["category"] for r in recs] or "scouting" in messages.lower()


class TestPestRecommendations:
    def test_aphid_recommendations(self):
        pests = [{"pest": "Aphid", "confidence": 0.92, "bounding_box": [10, 10, 50, 50]}]
        recs = generate_recommendations(disease="Healthy", pests=pests)
        messages = " ".join([r["message"] for r in recs])
        assert "aphid" in messages.lower() or "predator" in messages.lower()

    def test_multiple_pests_recommendations(self):
        pests = [
            {"pest": "Aphid", "confidence": 0.90, "bounding_box": [10, 10, 50, 50]},
            {"pest": "Whitefly", "confidence": 0.85, "bounding_box": [60, 60, 100, 100]},
        ]
        recs = generate_recommendations(pests=pests)
        messages = " ".join([r["message"] for r in recs])
        assert "aphid" in messages.lower()
        assert "whitefly" in messages.lower() or "sticky" in messages.lower()


class TestSeverityAndWeatherRecommendations:
    def test_high_severity_advises_expert_consultation(self):
        severity = {"level": "High", "affected_area_percentage": 45.0}
        recs = generate_recommendations(disease="Early Blight", severity=severity)
        categories = {r["category"] for r in recs}
        assert "Expert Consultation" in categories or "Severe Symptom Response" in categories

    def test_high_humidity_weather_recommendation(self):
        weather = {"weather_available": True, "humidity_pct": 92, "rainfall_mm": 0.0}
        recs = generate_recommendations(disease="Leaf Mold", weather=weather)
        categories = {r["category"] for r in recs}
        assert "Humidity Management" in categories

    def test_high_rainfall_weather_recommendation(self):
        weather = {"weather_available": True, "humidity_pct": 70, "rainfall_mm": 12.5}
        recs = generate_recommendations(weather=weather)
        categories = {r["category"] for r in recs}
        assert "Rainfall Precaution" in categories


class TestSafetyAndFallbacks:
    def test_no_unsafe_dosages_in_recommendations(self):
        """Ensure no fabricated chemical measurements/concentrations exist."""
        all_diseases = ["Early Blight", "Late Blight", "Leaf Mold", "Healthy", "Unknown"]
        all_pests = [
            [{"pest": "Aphid", "confidence": 0.9, "bounding_box": [0, 0, 10, 10]}],
            [{"pest": "Whitefly", "confidence": 0.9, "bounding_box": [0, 0, 10, 10]}],
            [{"pest": "Tomato Hornworm", "confidence": 0.9, "bounding_box": [0, 0, 10, 10]}],
        ]

        for d in all_diseases:
            for p in all_pests:
                recs = generate_recommendations(disease=d, pests=p)
                for r in recs:
                    msg = r["message"].lower()
                    # Check for unsafe chemical dosage strings
                    assert "g/l" not in msg
                    assert "ml/l" not in msg
                    assert "ppm" not in msg
                    assert "kg/ha" not in msg
                    assert "% concentration" not in msg

    def test_empty_inputs_returns_fallback(self):
        recs = generate_recommendations()
        assert len(recs) >= 1
        categories = [r["category"] for r in recs]
        assert "General Crop Care" in categories or "Disclaimer" in categories
