"""Alert Generation Engine for Crop Health Risks.

Evaluates contextual risk outcomes to determine whether an actionable alert
should be raised. Raises active alerts for "High" and "Critical" risk levels,
summarising key contributing reasons from the risk assessment.
"""

from typing import Dict, Any, List, Optional, Union


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
