"""Alert Generation Engine for Crop Health Risks.

Evaluates contextual risk outcomes to determine whether an actionable alert
should be raised. Raises active alerts for "High" and "Critical" risk levels,
summarising key contributing reasons from the risk assessment.

Key Behavior:
- Suppresses alerts when diagnosis is uncertain or evidence is insufficient
- Only raises alerts for confident, high-risk assessments
- Provides clear messaging about why alerts are or aren't triggered
"""

from typing import Dict, Any, List, Optional, Union
from src.utils.prediction_status import PredictionStatus, should_provide_diagnosis


def generate_alert(risk: Union[Dict[str, Any], Any, None]) -> Dict[str, Any]:
    """Generate an alert payload based on the risk engine assessment.

    Parameters:
        risk: Risk assessment dict or object containing 'risk_level' and 'factors'.
              May be None if risk evaluation was unavailable.

    Returns:
        Dict with keys:
            - active: bool (True for High/Critical risk, False otherwise)
            - severity: Optional[str] ("High" | "Critical" | None)
            - title: Optional[str] (Human-readable alert title | None)
            - reasons: List[str] (List of contributing factors / warning reasons)
    """
    inactive_alert: Dict[str, Any] = {
        "active": False,
        "severity": None,
        "title": None,
        "reasons": [],
    }

    if not risk:
        return inactive_alert

    # Handle dict input
    if isinstance(risk, dict):
        risk_level = risk.get("risk_level")
        factors = risk.get("factors", [])
    # Handle object with attributes
    elif hasattr(risk, "risk_level"):
        risk_level = getattr(risk, "risk_level", None)
        factors = getattr(risk, "factors", [])
    elif isinstance(risk, str):
        risk_level = risk
        factors = []
    else:
        return inactive_alert

    if not isinstance(risk_level, str):
        return inactive_alert

    level_norm = risk_level.strip().capitalize()

    if level_norm in ("High", "Critical"):
        # Format reasons list: use factors if provided, or supply standard reasons
        reasons_list: List[str] = []
        if isinstance(factors, list) and len(factors) > 0:
            reasons_list = [str(f) for f in factors]
        else:
            reasons_list = [
                f"Elevated risk score classified as {level_norm}",
                "Favorable environmental and crop conditions for rapid pathogen progression",
            ]

        title = f"{level_norm} Crop Health Alert"

        return {
            "active": True,
            "severity": level_norm,
            "title": title,
            "reasons": reasons_list,
        }

    return inactive_alert


def generate_alert_with_validation(
    risk: Union[Dict[str, Any], Any, None],
    prediction_status: Optional[PredictionStatus] = None,
) -> Dict[str, Any]:
    """Generate an alert with data sufficiency validation.
    
    Suppresses alerts when:
    - Diagnosis is uncertain or invalid
    - Risk assessment is unavailable due to insufficient data
    
    Parameters:
        risk: Risk assessment dict or object containing 'risk_level' and 'factors'.
              May be None if risk evaluation was unavailable.
        prediction_status: Prediction status from inference pipeline.
        
    Returns:
        Dict with keys:
            - active: bool (True only for confident High/Critical risk)
            - severity: Optional[str] ("High" | "Critical" | None)
            - title: Optional[str]
            - reasons: List[str]
            - suppressed: bool (True if alert was suppressed due to uncertainty)
            - suppression_reason: Optional[str]
    """
    inactive_alert: Dict[str, Any] = {
        "active": False,
        "severity": None,
        "title": None,
        "reasons": [],
        "suppressed": False,
        "suppression_reason": None,
    }
    
    # Check if diagnosis is uncertain - suppress alerts
    if prediction_status and not should_provide_diagnosis(prediction_status):
        return {
            "active": False,
            "severity": None,
            "title": None,
            "reasons": [],
            "suppressed": True,
            "suppression_reason": (
                f"Alert suppressed: Diagnosis uncertain ({prediction_status.name}). "
                "Alerts are only triggered for confident disease identifications."
            ),
        }
    
    # Check if risk assessment indicates insufficient data
    if isinstance(risk, dict):
        risk_status = risk.get("status")
        if risk_status == "INSUFFICIENT_DATA":
            return {
                "active": False,
                "severity": None,
                "title": None,
                "reasons": [],
                "suppressed": True,
                "suppression_reason": (
                    "Alert suppressed: Risk assessment unavailable due to insufficient data. "
                    "Alerts require confident diagnosis and sufficient environmental context."
                ),
            }
    
    # Use standard alert generation logic for confident assessments
    standard_alert = generate_alert(risk)
    
    # Add suppression tracking (not suppressed if we reached here)
    standard_alert["suppressed"] = False
    standard_alert["suppression_reason"] = None
    
    return standard_alert
