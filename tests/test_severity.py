"""
Tests for src/severity/estimator.py

Tests:
- Mostly green image → Low severity
- Mostly brown/yellow image → Moderate or High severity
- Healthy class passthrough → 0% / Low (no CV2 processing)
- Return schema completeness
- _pct_to_category thresholds
"""

import io
import sys
from pathlib import Path
import pytest
import numpy as np
from PIL import Image

# Ensure project root is on path when running from any directory
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.severity.estimator import SeverityEstimator, estimate_severity, SEVERITY_THRESHOLDS


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_solid_rgb_image(r: int, g: int, b: int, size: int = 128) -> Image.Image:
    """Create a solid-colour PIL image for testing."""
    arr = np.full((size, size, 3), [r, g, b], dtype=np.uint8)
    return Image.fromarray(arr, mode="RGB")


def _image_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Unit Tests — SeverityEstimator
# ---------------------------------------------------------------------------

class TestSeverityEstimatorSchema:
    """Tests that return dict always contains all required keys."""

    REQUIRED_KEYS = {
        "severity",
        "affected_area_percentage",
        "estimation_method",
        "prototype_disclaimer",
    }

    def _check_schema(self, result: dict):
        for key in self.REQUIRED_KEYS:
            assert key in result, f"Missing key in severity result: '{key}'"
        assert result["severity"] in ("Low", "Moderate", "High", "Unknown"), (
            f"Unexpected severity value: {result['severity']}"
        )
        assert isinstance(result["prototype_disclaimer"], str)
        assert len(result["prototype_disclaimer"]) > 10

    def test_healthy_passthrough_schema(self):
        img = _make_solid_rgb_image(80, 160, 60)  # green
        estimator = SeverityEstimator()
        result = estimator.estimate(img, predicted_disease="Healthy")
        self._check_schema(result)

    def test_disease_image_schema(self):
        img = _make_solid_rgb_image(80, 160, 60)
        estimator = SeverityEstimator()
        result = estimator.estimate(img, predicted_disease="Early Blight")
        self._check_schema(result)

    def test_bytes_input_schema(self):
        img = _make_solid_rgb_image(80, 160, 60)
        estimator = SeverityEstimator()
        result = estimator.estimate(_image_to_bytes(img), predicted_disease="Late Blight")
        self._check_schema(result)


class TestSeverityHealthyPassthrough:
    """Healthy class should always return 0% / Low regardless of pixel content."""

    def test_healthy_returns_zero_pct(self):
        img = _make_solid_rgb_image(150, 80, 40)  # brownish — would score high otherwise
        estimator = SeverityEstimator()
        result = estimator.estimate(img, predicted_disease="Healthy")
        assert result["severity"] == "Low"
        assert result["affected_area_percentage"] == 0.0
        assert result["estimation_method"] == "healthy_class_passthrough"

    def test_healthy_case_insensitive(self):
        img = _make_solid_rgb_image(80, 160, 60)
        estimator = SeverityEstimator()
        result = estimator.estimate(img, predicted_disease="healthy")
        assert result["severity"] == "Low"
        assert result["affected_area_percentage"] == 0.0


class TestSeverityGreenImage:
    """Mostly green image should produce Low severity."""

    def test_green_image_low_severity(self):
        # Solid green → very high proportion of healthy leaf pixels
        img = _make_solid_rgb_image(50, 180, 50)  # vivid green
        estimator = SeverityEstimator()
        if not estimator._cv2_available:
            pytest.skip("opencv-python not installed — skipping colour analysis tests")
        result = estimator.estimate(img, predicted_disease="Early Blight")
        assert result["severity"] == "Low", (
            f"Expected Low for green image, got {result['severity']} "
            f"({result['affected_area_percentage']}%)"
        )
        assert result["affected_area_percentage"] is not None
        assert result["affected_area_percentage"] < SEVERITY_THRESHOLDS["Moderate"][0]


class TestSeverityBrownImage:
    """Mostly brown/yellow image should produce Moderate or High severity."""

    def test_brown_image_elevated_severity(self):
        # Brown/necrotic colour (HSV hue ~10, high saturation, mid value)
        img = _make_solid_rgb_image(160, 80, 20)  # rust/brown
        estimator = SeverityEstimator()
        if not estimator._cv2_available:
            pytest.skip("opencv-python not installed — skipping colour analysis tests")
        result = estimator.estimate(img, predicted_disease="Early Blight")
        assert result["severity"] in ("Moderate", "High"), (
            f"Expected Moderate or High for brown image, got {result['severity']} "
            f"({result['affected_area_percentage']}%)"
        )

    def test_yellow_image_elevated_severity(self):
        # Yellow/chlorotic colour
        img = _make_solid_rgb_image(220, 200, 30)  # yellow
        estimator = SeverityEstimator()
        if not estimator._cv2_available:
            pytest.skip("opencv-python not installed — skipping colour analysis tests")
        result = estimator.estimate(img, predicted_disease="Leaf Mold")
        assert result["severity"] in ("Moderate", "High"), (
            f"Expected Moderate or High for yellow image, got {result['severity']} "
            f"({result['affected_area_percentage']}%)"
        )


class TestPctToCategory:
    """Unit tests for _pct_to_category static method."""

    def test_zero_is_low(self):
        assert SeverityEstimator._pct_to_category(0.0) == "Low"

    def test_nine_is_low(self):
        assert SeverityEstimator._pct_to_category(9.9) == "Low"

    def test_ten_is_moderate(self):
        assert SeverityEstimator._pct_to_category(10.0) == "Moderate"

    def test_twenty_five_is_moderate(self):
        assert SeverityEstimator._pct_to_category(25.0) == "Moderate"

    def test_thirty_is_high(self):
        assert SeverityEstimator._pct_to_category(30.0) == "High"

    def test_hundred_is_high(self):
        assert SeverityEstimator._pct_to_category(100.0) == "High"


class TestEstimateSeverityConvenienceFunction:
    """Tests for the module-level estimate_severity() convenience function."""

    def test_returns_dict(self):
        img = _make_solid_rgb_image(80, 160, 60)
        result = estimate_severity(img, predicted_disease="Healthy")
        assert isinstance(result, dict)

    def test_healthy_shortcut(self):
        img = _make_solid_rgb_image(80, 160, 60)
        result = estimate_severity(img, "Healthy")
        assert result["severity"] == "Low"
        assert result["affected_area_percentage"] == 0.0
