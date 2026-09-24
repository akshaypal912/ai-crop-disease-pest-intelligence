"""
Disease Risk Profiles — Per-disease environmental favourable-condition bands.

These ranges are derived from the existing Disease Knowledge Base (disease_kb.py)
and general plant pathology literature. They represent conditions described as
"favourable" for disease development in published sources.

IMPORTANT: These values are used as INPUTS to the heuristic risk scoring engine.
They are NOT quantitative epidemiological thresholds derived from controlled studies.
The risk engine explicitly labels outputs as contextual estimates, not validated
predictions. All bands should be reviewed and calibrated by a plant pathologist
before any advisory use.

References (general sources that informed the ranges):
  - Agrios, G.N. (2005). Plant Pathology (5th ed.). Elsevier.
  - USDA Plant Disease Handbooks (general guidance only).
  - Existing disease_kb.py knowledge entries in this codebase.
"""

from typing import Dict, Any

# Sentinel value used when a factor is not applicable
NOT_APPLICABLE = None

# ---------------------------------------------------------------------------
# Risk profile schema per disease
# ---------------------------------------------------------------------------
# temp_favourable_c     : (low, high) °C — range described as favourable
# humidity_favourable_pct: (low, high) % relative humidity
# rainfall_increases_risk: bool — whether recent rainfall notably increases risk
# growth_stage_weights  : higher weight on vulnerable growth stages
# ---------------------------------------------------------------------------

DISEASE_RISK_PROFILES: Dict[str, Dict[str, Any]] = {
    "Healthy": {
        "description": "No disease detected; baseline risk only.",
        "temp_favourable_c": NOT_APPLICABLE,
        "humidity_favourable_pct": NOT_APPLICABLE,
        "rainfall_increases_risk": False,
        "base_disease_score": 0.0,   # Healthy → no disease contribution
        "growth_stage_sensitive": False,
    },

    "Early Blight": {
        # Alternaria solani: warm + humid + wet foliage
        # Source: Agrios (2005); general extension literature
        "description": "Alternaria solani — warm, humid conditions with leaf wetness.",
        "temp_favourable_c": (24.0, 29.0),
        "humidity_favourable_pct": (80.0, 100.0),
        "rainfall_increases_risk": True,
        "base_disease_score": 0.5,   # Moderate baseline — manageable if caught early
        "growth_stage_sensitive": True,  # Worse at fruiting / late season
    },

    "Late Blight": {
        # Phytophthora infestans: cool + very high humidity + free moisture
        # Source: Agrios (2005); FAO Late Blight Management guides
        "description": "Phytophthora infestans — cool, very humid; rapid spread risk.",
        "temp_favourable_c": (15.0, 22.0),
        "humidity_favourable_pct": (90.0, 100.0),
        "rainfall_increases_risk": True,
        "base_disease_score": 0.75,  # Higher baseline — spreads very rapidly
        "growth_stage_sensitive": True,
    },

    "Leaf Mold": {
        # Passalora fulva: warm + very high humidity; common in greenhouses
        # Source: Agrios (2005); greenhouse management literature
        "description": "Passalora fulva — high humidity; common in enclosed/dense plantings.",
        "temp_favourable_c": (20.0, 24.0),
        "humidity_favourable_pct": (85.0, 100.0),
        "rainfall_increases_risk": False,  # Airborne; not strongly rainfall-driven
        "base_disease_score": 0.45,  # Moderate; foliage loss can be significant
        "growth_stage_sensitive": False,
    },
}

GROWTH_STAGE_VULNERABILITY: Dict[str, float] = {
    # Multiplier applied to the risk score for disease-sensitive growth stages.
    # Values are PROTOTYPE ESTIMATES and should be calibrated with agronomist input.
    "seedling":    0.7,   # Susceptible but limited economic impact on fruit
    "vegetative":  0.85,
    "flowering":   1.0,   # Infection at flowering → significant yield loss
    "fruiting":    1.1,   # Disease at fruiting → direct economic loss
    "ripening":    1.0,
    "unknown":     0.9,   # Conservative default
}


def get_disease_profile(disease_name: str) -> Dict[str, Any]:
    """
    Returns the risk profile for a given disease name.
    Falls back to a generic high-risk profile for unknown classes.
    """
    if disease_name in DISEASE_RISK_PROFILES:
        return DISEASE_RISK_PROFILES[disease_name]

    # Unknown disease class — conservative fallback
    return {
        "description": f"Unknown disease class '{disease_name}' — conservative risk assumed.",
        "temp_favourable_c": (18.0, 30.0),
        "humidity_favourable_pct": (75.0, 100.0),
        "rainfall_increases_risk": True,
        "base_disease_score": 0.6,
        "growth_stage_sensitive": True,
    }


def get_growth_stage_multiplier(growth_stage: str) -> float:
    """Returns the vulnerability multiplier for a given growth stage."""
    key = (growth_stage or "unknown").strip().lower()
    return GROWTH_STAGE_VULNERABILITY.get(key, GROWTH_STAGE_VULNERABILITY["unknown"])
