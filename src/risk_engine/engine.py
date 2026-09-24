"""
Risk Engine — Contextual crop-health risk scoring.

Combines model prediction confidence, disease identity, severity estimate,
and optional weather context into a composite risk score and level.

IMPORTANT — TRANSPARENCY NOTES:

  1. model_prediction  : The deep learning classifier output (disease + confidence).
     This is a machine learning estimate, not a laboratory diagnosis.

  2. contextual_estimate: The risk score produced here. It is a HEURISTIC,
     rule-based scoring aggregate. Weights and thresholds are PROTOTYPE VALUES
     that require calibration with validated agricultural data before any
     field-advisory use.

  3. agricultural_evidence: Disease-ecology information from the knowledge base,
     derived from general plant pathology literature. See disease_risk_profiles.py
     for sourcing notes.

The engine is deliberately modular so that each sub-scorer can be replaced or
calibrated independently as better data becomes available.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .disease_risk_profiles import get_disease_profile, get_growth_stage_multiplier

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

# ---------------------------------------------------------------------------
# Sub-scorer weight configuration (PROTOTYPE — requires calibration)
# ---------------------------------------------------------------------------
# Each sub-score is in [0, 1]. The final risk_score is a weighted average.
# Weights reflect the assumed relative importance of each factor in this
# prototype. They have not been derived from statistical modelling of disease
# spread data and MUST be reviewed before operational use.
FACTOR_WEIGHTS: Dict[str, float] = {
    "base_disease":   0.25,  # Identity / severity of the disease itself
    "model_confidence": 0.15,  # How certain the ML model is
    "severity":       0.25,  # Estimated affected leaf area
    "humidity":       0.15,  # Current humidity vs. favourable band
    "temperature":    0.10,  # Current temperature vs. favourable band
    "rainfall":       0.10,  # Recent rainfall indicator
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

    Each factor is scored independently (0–1) then combined as a weighted
    average. The design intentionally separates concerns so individual
    sub-scorers can be replaced with calibrated models in future phases.
    """

    def compute(self, inputs: RiskInput) -> RiskOutput:
        """
        Compute composite risk from the provided inputs.

        Args:
            inputs: RiskInput dataclass with disease prediction + context.

        Returns:
            RiskOutput with risk_level, risk_score, factors, and disclaimer.
        """
        profile = get_disease_profile(inputs.disease)
        factors: List[str] = []
        sub_scores: Dict[str, float] = {}

        # --- 1. Base disease score -----------------------------------------
        base = profile["base_disease_score"]
        sub_scores["base_disease"] = base
        if inputs.disease != "Healthy" and base > 0:
            factors.append(
                f"Disease detected: {inputs.disease} "
                f"(base risk index: {base:.2f} — prototype value)"
            )

        # --- 2. Model confidence -------------------------------------------
        # High confidence in a disease prediction increases weight on the score.
        # For Healthy, confidence reduces the overall risk.
        if inputs.disease == "Healthy":
            conf_score = max(0.0, 1.0 - inputs.confidence)
        else:
            conf_score = inputs.confidence
        sub_scores["model_confidence"] = conf_score
        if conf_score > 0.70:
            factors.append(
                f"Model confidence: {inputs.confidence * 100:.1f}% "
                f"(high confidence in prediction)"
            )
        elif conf_score < 0.40 and inputs.disease != "Healthy":
            factors.append(
                f"Model confidence: {inputs.confidence * 100:.1f}% "
                f"(low confidence — result uncertain)"
            )

        # --- 3. Severity ---------------------------------------------------
        severity_score = self._score_severity(inputs.severity_pct, factors)
        sub_scores["severity"] = severity_score

        # --- 4. Humidity ---------------------------------------------------
        humidity_score = self._score_humidity(
            inputs.humidity_pct, profile["humidity_favourable_pct"], factors
        )
        sub_scores["humidity"] = humidity_score

        # --- 5. Temperature -----------------------------------------------
        temp_score = self._score_temperature(
            inputs.temperature_c, profile["temp_favourable_c"], factors
        )
        sub_scores["temperature"] = temp_score

        # --- 6. Rainfall ---------------------------------------------------
        rainfall_score = self._score_rainfall(
            inputs.rainfall_mm, profile["rainfall_increases_risk"], factors
        )
        sub_scores["rainfall"] = rainfall_score

        # --- Weighted aggregate -------------------------------------------
        weighted = (
            FACTOR_WEIGHTS["base_disease"]     * sub_scores["base_disease"] +
            FACTOR_WEIGHTS["model_confidence"] * sub_scores["model_confidence"] +
            FACTOR_WEIGHTS["severity"]         * sub_scores["severity"] +
            FACTOR_WEIGHTS["humidity"]         * sub_scores["humidity"] +
            FACTOR_WEIGHTS["temperature"]      * sub_scores["temperature"] +
            FACTOR_WEIGHTS["rainfall"]         * sub_scores["rainfall"]
        )

        # --- Growth stage multiplier -------------------------------------
        growth_mult = get_growth_stage_multiplier(inputs.growth_stage or "unknown")
        if inputs.growth_stage and inputs.growth_stage.lower() in ("flowering", "fruiting"):
            factors.append(
                f"Vulnerable growth stage: {inputs.growth_stage} "
                f"(yield-critical period — risk elevated)"
            )

        final_score = min(1.0, max(0.0, weighted * growth_mult))
        risk_level = self._score_to_level(final_score)

        # Healthy with high confidence short-circuits to Low
        if inputs.disease == "Healthy" and inputs.confidence >= 0.80:
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
            return 0.0  # Weather not provided; exclude factor
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
        # Partial score within ±5°C of the band
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

    Returns dict suitable for JSON serialisation.
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
