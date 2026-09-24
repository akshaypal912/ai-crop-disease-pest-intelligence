"""
Tests for src/risk_engine/engine.py and src/risk_engine/disease_risk_profiles.py

Tests:
- Healthy disease + high confidence → Low risk
- High-severity disease + high humidity → High or Critical risk
- Missing weather → engine runs; weather factors excluded (score still valid)
- Return schema completeness
- Individual sub-scorer edge cases
- Disease risk profile lookup + fallback
- Growth stage multiplier
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.risk_engine.engine import (
    RiskEngine, RiskInput, RiskOutput, compute_risk,
    RISK_ENGINE_DISCLAIMER, FACTOR_WEIGHTS
)
from src.risk_engine.disease_risk_profiles import (
    get_disease_profile, get_growth_stage_multiplier,
    DISEASE_RISK_PROFILES, GROWTH_STAGE_VULNERABILITY
)

# ---------------------------------------------------------------------------
# Required output schema keys
# ---------------------------------------------------------------------------
REQUIRED_OUTPUT_KEYS = {"risk_level", "risk_score", "factors", "sub_scores", "disclaimer"}
VALID_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_healthy_input(**kwargs) -> RiskInput:
    defaults = {
        "disease": "Healthy",
        "confidence": 0.95,
        "severity_pct": 0.0,
    }
    defaults.update(kwargs)
    return RiskInput(**defaults)


def make_disease_input(**kwargs) -> RiskInput:
    defaults = {
        "disease": "Early Blight",
        "confidence": 0.91,
        "severity_pct": 25.0,
        "temperature_c": 27.0,
        "humidity_pct": 85.0,
        "rainfall_mm": 12.0,
        "growth_stage": "fruiting",
    }
    defaults.update(kwargs)
    return RiskInput(**defaults)


# ---------------------------------------------------------------------------
# Schema Tests
# ---------------------------------------------------------------------------

class TestRiskOutputSchema:

    def test_output_dict_has_required_keys(self):
        result = compute_risk(disease="Healthy", confidence=0.9)
        for key in REQUIRED_OUTPUT_KEYS:
            assert key in result, f"Missing key: '{key}'"

    def test_risk_level_is_valid(self):
        result = compute_risk(disease="Healthy", confidence=0.9)
        assert result["risk_level"] in VALID_RISK_LEVELS

    def test_risk_score_in_range(self):
        result = compute_risk(disease="Early Blight", confidence=0.85, severity_pct=20.0)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_factors_is_list_of_strings(self):
        result = compute_risk(disease="Late Blight", confidence=0.88, severity_pct=35.0)
        assert isinstance(result["factors"], list)
        for f in result["factors"]:
            assert isinstance(f, str)

    def test_sub_scores_has_all_factor_keys(self):
        result = compute_risk(disease="Early Blight", confidence=0.85, severity_pct=20.0)
        for key in FACTOR_WEIGHTS:
            assert key in result["sub_scores"], f"sub_scores missing factor key: '{key}'"

    def test_disclaimer_is_non_empty_string(self):
        result = compute_risk(disease="Healthy", confidence=0.9)
        assert isinstance(result["disclaimer"], str)
        assert len(result["disclaimer"]) > 20


# ---------------------------------------------------------------------------
# Risk Level Tests
# ---------------------------------------------------------------------------

class TestRiskLevels:

    def test_healthy_high_confidence_returns_low(self):
        engine = RiskEngine()
        inp = make_healthy_input(confidence=0.95)
        out = engine.compute(inp)
        assert out.risk_level == "Low", (
            f"Expected Low for healthy + high confidence, got {out.risk_level}"
        )

    def test_healthy_low_confidence_has_higher_score(self):
        engine = RiskEngine()
        inp_high = make_healthy_input(confidence=0.95)
        inp_low = make_healthy_input(confidence=0.35)
        out_high = engine.compute(inp_high)
        out_low = engine.compute(inp_low)
        assert out_low.risk_score >= out_high.risk_score, (
            "Low-confidence healthy should have >= risk score than high-confidence healthy"
        )

    def test_severe_disease_adverse_weather_elevated_risk(self):
        engine = RiskEngine()
        inp = make_disease_input(
            disease="Late Blight",
            confidence=0.92,
            severity_pct=45.0,
            temperature_c=18.0,   # Late blight favourable
            humidity_pct=95.0,    # Very high
            rainfall_mm=20.0,
            growth_stage="fruiting",
        )
        out = engine.compute(inp)
        assert out.risk_level in ("High", "Critical"), (
            f"Expected High or Critical for severe Late Blight + adverse weather, "
            f"got {out.risk_level} (score={out.risk_score:.3f})"
        )

    def test_low_severity_dry_weather_lower_risk(self):
        engine = RiskEngine()
        inp = make_disease_input(
            disease="Early Blight",
            confidence=0.75,
            severity_pct=3.0,       # Very low severity
            temperature_c=15.0,     # Out of Early Blight favourable band
            humidity_pct=50.0,      # Low humidity
            rainfall_mm=0.0,
            growth_stage="vegetative",
        )
        out = engine.compute(inp)
        assert out.risk_level in ("Low", "Medium"), (
            f"Expected Low or Medium for low-severity dry conditions, "
            f"got {out.risk_level} (score={out.risk_score:.3f})"
        )

    def test_risk_score_range_all_inputs(self):
        engine = RiskEngine()
        for disease in ["Healthy", "Early Blight", "Late Blight", "Leaf Mold"]:
            inp = RiskInput(
                disease=disease,
                confidence=0.85,
                severity_pct=20.0,
                temperature_c=24.0,
                humidity_pct=80.0,
                rainfall_mm=5.0,
                growth_stage="flowering",
            )
            out = engine.compute(inp)
            assert 0.0 <= out.risk_score <= 1.0, (
                f"Risk score out of [0,1] for {disease}: {out.risk_score}"
            )


# ---------------------------------------------------------------------------
# Missing Weather Tests
# ---------------------------------------------------------------------------

class TestMissingWeather:

    def test_no_weather_engine_runs_without_exception(self):
        """Risk engine must work when no weather data is provided."""
        engine = RiskEngine()
        inp = RiskInput(
            disease="Early Blight",
            confidence=0.88,
            severity_pct=20.0,
            # No temperature, humidity, rainfall
        )
        try:
            out = engine.compute(inp)
            assert isinstance(out, RiskOutput)
        except Exception as exc:
            pytest.fail(f"RiskEngine raised exception with no weather: {exc}")

    def test_no_weather_sub_scores_are_zero(self):
        engine = RiskEngine()
        inp = RiskInput(disease="Early Blight", confidence=0.88, severity_pct=20.0)
        out = engine.compute(inp)
        assert out.sub_scores.get("humidity") == 0.0
        assert out.sub_scores.get("temperature") == 0.0
        assert out.sub_scores.get("rainfall") == 0.0

    def test_no_severity_sub_score_is_zero(self):
        engine = RiskEngine()
        inp = RiskInput(disease="Early Blight", confidence=0.88, severity_pct=None)
        out = engine.compute(inp)
        assert out.sub_scores.get("severity") == 0.0

    def test_compute_risk_convenience_no_weather(self):
        result = compute_risk(disease="Late Blight", confidence=0.80)
        assert isinstance(result, dict)
        assert result["risk_level"] in VALID_RISK_LEVELS


# ---------------------------------------------------------------------------
# Growth Stage Tests
# ---------------------------------------------------------------------------

class TestGrowthStage:

    def test_flowering_stage_increases_risk_vs_unknown(self):
        engine = RiskEngine()
        base = RiskInput(disease="Early Blight", confidence=0.85, severity_pct=20.0,
                         humidity_pct=85.0, temperature_c=27.0, rainfall_mm=10.0)
        base.growth_stage = None
        base_out = engine.compute(base)

        bloom = RiskInput(disease="Early Blight", confidence=0.85, severity_pct=20.0,
                          humidity_pct=85.0, temperature_c=27.0, rainfall_mm=10.0,
                          growth_stage="flowering")
        bloom_out = engine.compute(bloom)
        assert bloom_out.risk_score >= base_out.risk_score

    def test_unknown_growth_stage_uses_fallback(self):
        mult = get_growth_stage_multiplier("unknown")
        assert 0.5 <= mult <= 1.5


# ---------------------------------------------------------------------------
# Disease Risk Profile Tests
# ---------------------------------------------------------------------------

class TestDiseaseRiskProfiles:

    def test_all_known_diseases_have_profiles(self):
        from src.utils.config import Config
        for cls in Config.TARGET_CLASSES:
            profile = get_disease_profile(cls)
            assert "base_disease_score" in profile
            assert 0.0 <= profile["base_disease_score"] <= 1.0

    def test_unknown_disease_returns_fallback_profile(self):
        profile = get_disease_profile("Unknown_Disease_XYZ")
        assert "base_disease_score" in profile
        assert profile["base_disease_score"] > 0  # Conservative

    def test_healthy_profile_has_zero_base_score(self):
        profile = get_disease_profile("Healthy")
        assert profile["base_disease_score"] == 0.0

    def test_growth_stage_multipliers_in_range(self):
        for stage, mult in GROWTH_STAGE_VULNERABILITY.items():
            assert 0.0 < mult <= 2.0, (
                f"Growth stage multiplier out of reasonable range for '{stage}': {mult}"
            )
