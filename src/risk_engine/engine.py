"""
Risk Engine — Contextual crop-health risk scoring with data sufficiency validation.

Combines model prediction confidence, disease identity, severity estimate,
and optional weather context into a composite risk score and level.

Key Design Improvements:
1. Data Sufficiency Checks: Returns INSUFFICIENT_DATA when required inputs missing
2. Separates diagnostic confidence from environmental risk
3. Transparency: Explicitly states when weather or diagnosis unavailable
4. Conservative: Does not fabricate risk scores when evidence insufficient
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .disease_risk_profiles import get_disease_profile, get_growth_stage_multiplier
from src.utils.prediction_status import PredictionStatus, should_provide_diagnosis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Risk Level Thresholds (PROTOTYPE — not validated against field outcomes)
# ---------------------------------------------------------------------------
RISK_LEVEL_THRESHOLDS = [
    (0.80, "Critical"),
    (0.55, "High"),
    (0.30, "Medium"),
    (0.00, "Low"),
]

RISK_ENGINE_DISCLAIMER = (
    "PROTOTYPE CONTEXTUAL ESTIMATE: The risk score is produced by a heuristic "
    "rule-based engine combining model prediction, colour-based severity estimation, "
    "and weather context. It has NOT been validated against field outcomes or "
    "epidemiological data. Do not use as the sole basis for agricultural treatment "
    "or management decisions. Consult a qualified agronomist or plant pathologist."
)

FACTOR_WEIGHTS: Dict[str, float] = {
    "severity":            0.50,  # Estimated affected leaf area
    "base_disease":        0.30,  # Identity / virulence of detected disease
    "uncertainty_penalty": 0.20,  # Penalty for diagnostic uncertainty (added, not multiplied)
}


@dataclass
class RiskInput:
    """Structured input container for the risk engine."""
    disease: str
    confidence: float                    # 0.0 – 1.0
    severity_pct: Optional[float] = None # 0.0 – 100.0; None if estimation unavailable
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    rainfall_mm: Optional[float] = None
    growth_stage: Optional[str] = None
    location: Optional[str] = None


@dataclass
class RiskOutput:
    """Structured output from the risk engine."""
    risk_level: str
    risk_score: float
    factors: List[str] = field(default_factory=list)
    sub_scores: Dict[str, float] = field(default_factory=dict)
    disclaimer: str = RISK_ENGINE_DISCLAIMER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "risk_score": round(self.risk_score, 4),
            "factors": self.factors,
            "sub_scores": {k: round(v, 4) for k, v in self.sub_scores.items()},
            "disclaimer": self.disclaimer,
        }


class RiskEngine:
    """
    Modular heuristic risk engine for contextual crop-health assessment.
    """

    def compute(self, inputs: RiskInput) -> RiskOutput:
        """
        Compute composite risk from the provided inputs.
        """
        profile = get_disease_profile(inputs.disease)
        factors: List[str] = []
        sub_scores: Dict[str, float] = {}

        # --- 1. Base disease score -----------------------------------------
        base = profile["base_disease_score"]
        sub_scores["base_disease"] = base
        if inputs.disease not in ("Healthy", "Uncertain — result may not apply to this crop type") and base > 0:
            factors.append(
                f"Disease detected: {inputs.disease} "
                f"(base risk index: {base:.2f} — prototype value)"
            )

        # --- 2. Uncertainty penalty ----------------------------------------
        # Low confidence adds an uncertainty penalty instead of multiplying/diluting
        if inputs.disease == "Healthy":
            uncertainty_penalty = max(0.0, (1.0 - inputs.confidence) * 0.3)
        else:
            uncertainty_penalty = max(0.0, (1.0 - inputs.confidence) * 1.0)

        sub_scores["uncertainty_penalty"] = uncertainty_penalty
        sub_scores["model_confidence"] = inputs.confidence

        if inputs.confidence > 0.70:
            factors.append(
                f"Model confidence: {inputs.confidence * 100:.1f}% "
                f"(high confidence in prediction)"
            )
        elif inputs.confidence < 0.40 and inputs.disease != "Healthy":
            factors.append(
                f"Model confidence: {inputs.confidence * 100:.1f}% "
                f"(low confidence — result uncertain)"
            )

        # --- 3. Severity ---------------------------------------------------
        severity_score = self._score_severity(inputs.severity_pct, factors)
        sub_scores["severity"] = severity_score

        # --- 4. Weather factors (or explicit fallback note) ----------------
        has_weather = not (
            inputs.temperature_c is None and
            inputs.humidity_pct is None and
            inputs.rainfall_mm is None
        )

        if has_weather:
            humidity_score = self._score_humidity(
                inputs.humidity_pct, profile["humidity_favourable_pct"], factors
            )
            sub_scores["humidity"] = humidity_score

            temp_score = self._score_temperature(
                inputs.temperature_c, profile["temp_favourable_c"], factors
            )
            sub_scores["temperature"] = temp_score

            rainfall_score = self._score_rainfall(
                inputs.rainfall_mm, profile["rainfall_increases_risk"], factors
            )
            sub_scores["rainfall"] = rainfall_score

            # Blended score with environmental terms
            base_risk = (
                FACTOR_WEIGHTS["severity"] * severity_score +
                FACTOR_WEIGHTS["base_disease"] * base +
                FACTOR_WEIGHTS["uncertainty_penalty"] * uncertainty_penalty
            )
            weather_addition = (
                0.15 * humidity_score +
                0.10 * temp_score +
                0.10 * rainfall_score
            )
            weighted = min(1.0, base_risk + weather_addition)
        else:
            sub_scores["humidity"] = 0.0
            sub_scores["temperature"] = 0.0
            sub_scores["rainfall"] = 0.0
            factors.append("Environmental risk not included (weather data unavailable)")

            # Standard 3-term additive formula
            weighted = (
                FACTOR_WEIGHTS["severity"] * severity_score +
                FACTOR_WEIGHTS["base_disease"] * base +
                FACTOR_WEIGHTS["uncertainty_penalty"] * uncertainty_penalty
            )

        # --- 5. Growth stage multiplier -----------------------------------
        growth_mult = get_growth_stage_multiplier(inputs.growth_stage or "unknown")
        if inputs.growth_stage and inputs.growth_stage.lower() in ("flowering", "fruiting"):
            factors.append(
                f"Vulnerable growth stage: {inputs.growth_stage} "
                f"(yield-critical period — risk elevated)"
            )

        final_score = min(1.0, max(0.0, weighted * growth_mult))
        risk_level = self._score_to_level(final_score)

        # --- 6. Hard safety clamping rule ---------------------------------
        # If severity is High (>= 30%) and confidence < 0.50, risk must NEVER be Low
        is_high_severity = (inputs.severity_pct is not None and inputs.severity_pct >= 30.0)
        is_low_conf = (inputs.confidence < 0.50)

        if is_high_severity and is_low_conf and inputs.disease != "Healthy":
            if risk_level == "Low":
                risk_level = "Medium"
                final_score = max(final_score, 0.35)
            factors.append("Low model confidence combined with high severity — risk elevated as precaution")

        # Healthy with high confidence short-circuits to Low
        if inputs.disease == "Healthy" and inputs.confidence >= 0.80 and not is_high_severity:
            final_score = min(final_score, 0.20)
            risk_level = "Low"
            if not factors:
                factors.append("No disease detected — plant appears healthy.")

        return RiskOutput(
            risk_level=risk_level,
            risk_score=final_score,
            factors=factors,
            sub_scores=sub_scores,
        )

    # -----------------------------------------------------------------------
    # Private sub-scorers
    # -----------------------------------------------------------------------

    @staticmethod
    def _score_severity(severity_pct: Optional[float], factors: List[str]) -> float:
        """Linear severity score; returns 0 if severity unavailable."""
        if severity_pct is None:
            factors.append("Severity estimation unavailable — factor excluded from scoring.")
            return 0.0
        score = min(severity_pct / 100.0, 1.0)
        if severity_pct >= 30.0:
            factors.append(
                f"High affected area: ~{severity_pct:.1f}% of visible leaf area "
                f"shows disease-indicator colouration (heuristic estimate)"
            )
        elif severity_pct >= 10.0:
            factors.append(
                f"Moderate affected area: ~{severity_pct:.1f}% of visible leaf area "
                f"(heuristic estimate)"
            )
        return score

    @staticmethod
    def _score_humidity(
        humidity_pct: Optional[float],
        favourable_band: Optional[tuple],
        factors: List[str],
    ) -> float:
        """Score humidity: 1.0 if within favourable band, 0.0 if below, linear otherwise."""
        if humidity_pct is None:
            return 0.0
        if favourable_band is None:
            return 0.0

        low, high = favourable_band
        if humidity_pct >= low:
            factors.append(
                f"High humidity: {humidity_pct:.0f}% "
                f"(within or above disease-favourable band ≥{low:.0f}%)"
            )
            return 1.0
        elif humidity_pct >= low * 0.75:
            return (humidity_pct - low * 0.75) / (low - low * 0.75)
        return 0.0

    @staticmethod
    def _score_temperature(
        temperature_c: Optional[float],
        favourable_band: Optional[tuple],
        factors: List[str],
    ) -> float:
        """Score temperature: 1.0 if within favourable band, falls off outside."""
        if temperature_c is None:
            return 0.0
        if favourable_band is None:
            return 0.0

        low, high = favourable_band
        if low <= temperature_c <= high:
            factors.append(
                f"Temperature {temperature_c:.1f}°C within disease-favourable range "
                f"({low:.0f}–{high:.0f}°C)"
            )
            return 1.0
        margin = 5.0
        if temperature_c < low:
            dist = low - temperature_c
        else:
            dist = temperature_c - high
        if dist <= margin:
            return max(0.0, 1.0 - dist / margin)
        return 0.0

    @staticmethod
    def _score_rainfall(
        rainfall_mm: Optional[float],
        rainfall_increases_risk: bool,
        factors: List[str],
    ) -> float:
        """Score rainfall influence."""
        if rainfall_mm is None:
            return 0.0
        if not rainfall_increases_risk:
            return 0.0
        if rainfall_mm >= 10.0:
            factors.append(
                f"Recent rainfall: {rainfall_mm:.1f} mm "
                f"(may facilitate spore splash or spread)"
            )
            return 1.0
        if rainfall_mm > 0:
            factors.append(
                f"Trace rainfall: {rainfall_mm:.1f} mm detected."
            )
            return rainfall_mm / 10.0
        return 0.0

    @staticmethod
    def _score_to_level(score: float) -> str:
        """Map composite score to risk level label."""
        for threshold, level in RISK_LEVEL_THRESHOLDS:
            if score >= threshold:
                return level
        return "Low"


# ---------------------------------------------------------------------------
# Module-level singleton + convenience function
# ---------------------------------------------------------------------------

_engine_instance: Optional[RiskEngine] = None


def get_risk_engine() -> RiskEngine:
    """Singleton getter for RiskEngine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RiskEngine()
    return _engine_instance


def compute_risk(
    disease: str,
    confidence: float,
    severity_pct: Optional[float] = None,
    temperature_c: Optional[float] = None,
    humidity_pct: Optional[float] = None,
    rainfall_mm: Optional[float] = None,
    growth_stage: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function. Calls RiskEngine.compute() on the singleton instance.
    
    NOTE: This function does not validate data sufficiency. 
    For status-aware risk computation, use compute_risk_with_validation().
    """
    inp = RiskInput(
        disease=disease,
        confidence=confidence,
        severity_pct=severity_pct,
        temperature_c=temperature_c,
        humidity_pct=humidity_pct,
        rainfall_mm=rainfall_mm,
        growth_stage=growth_stage,
        location=location,
    )
    result = get_risk_engine().compute(inp)
    return result.to_dict()


def compute_risk_with_validation(
    disease: Optional[str],
    confidence: float,
    prediction_status: PredictionStatus,
    severity_pct: Optional[float] = None,
    weather_available: bool = False,
    temperature_c: Optional[float] = None,
    humidity_pct: Optional[float] = None,
    rainfall_mm: Optional[float] = None,
    growth_stage: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Status-aware risk computation with data sufficiency validation.
    
    Returns INSUFFICIENT_DATA when required inputs are missing or diagnosis is uncertain.
    Separates diagnostic confidence from environmental risk.
    
    Args:
        disease: Predicted disease name (may be None if uncertain)
        confidence: Model confidence (NOT a calibrated probability)
        prediction_status: Prediction status from inference pipeline
        severity_pct: Visible affected area percentage (None if unavailable)
        weather_available: Whether weather data is available
        temperature_c: Temperature in Celsius
        humidity_pct: Humidity percentage
        rainfall_mm: Rainfall in millimeters
        growth_stage: Crop growth stage
        location: Location identifier
        
    Returns:
        Dict containing:
            - status: "AVAILABLE" | "INSUFFICIENT_DATA"
            - risk_level: str | None
            - risk_score: float | None
            - factors: List[str]
            - diagnostic_confidence: str
            - environmental_context: str
            - message: str
    """
    # Check data sufficiency
    has_confident_diagnosis = should_provide_diagnosis(prediction_status)
    has_weather = weather_available
    
    factors = []
    
    # Case 1: Diagnosis is uncertain/invalid
    if not has_confident_diagnosis:
        return {
            "status": "INSUFFICIENT_DATA",
            "risk_level": None,
            "risk_score": None,
            "factors": [
                f"Diagnostic confidence insufficient: {prediction_status}",
                "A confident disease identification is required for reliable risk assessment.",
            ],
            "diagnostic_confidence": "INSUFFICIENT",
            "environmental_context": "NOT_APPLICABLE",
            "message": (
                "Risk assessment unavailable due to uncertain diagnosis. "
                "Upload clearer images or seek professional diagnosis."
            ),
        }
    
    # Case 2: Diagnosis confident but no weather data
    if not has_weather:
        # Can compute partial risk based on disease and severity only
        factors.append("Environmental risk not included (weather data unavailable)")
        
        # Use the basic compute() but flag it as incomplete
        result = compute_risk(
            disease=disease or "Unknown",
            confidence=confidence,
            severity_pct=severity_pct,
            temperature_c=None,
            humidity_pct=None,
            rainfall_mm=None,
            growth_stage=growth_stage,
            location=location,
        )
        
        result["status"] = "PARTIAL"
        result["diagnostic_confidence"] = "SUFFICIENT"
        result["environmental_context"] = "UNAVAILABLE"
        result["message"] = (
            "Risk assessment based on disease and severity only. "
            "Environmental conditions not factored due to missing weather data."
        )
        result["factors"].insert(0, "Environmental risk not included (weather data unavailable)")
        
        return result
    
    # Case 3: Full context available
    result = compute_risk(
        disease=disease or "Unknown",
        confidence=confidence,
        severity_pct=severity_pct,
        temperature_c=temperature_c,
        humidity_pct=humidity_pct,
        rainfall_mm=rainfall_mm,
        growth_stage=growth_stage,
        location=location,
    )
    
    result["status"] = "AVAILABLE"
    result["diagnostic_confidence"] = "SUFFICIENT"
    result["environmental_context"] = "AVAILABLE"
    result["message"] = "Risk assessment based on complete diagnostic and environmental data."
    
    return result
