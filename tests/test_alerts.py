"""Unit Tests for Alert Generation Engine.

Tests:
- High risk triggers active alert
- Critical risk triggers active alert
- Medium risk remains inactive
- Low risk remains inactive
- Unknown / None / malformed inputs handled gracefully
- Reasons extraction from risk assessment factors
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.alerts import generate_alert


class TestAlertGeneration:
    def test_high_risk_triggers_active_alert(self):
        risk = {
            "risk_level": "High",
            "risk_score": 0.72,
            "factors": [
                "Disease detected: Early Blight",
                "High humidity: 88%",
                "Recent rainfall: 5.2 mm",
            ],
        }
        alert = generate_alert(risk)
        assert alert["active"] is True
        assert alert["severity"] == "High"
        assert "High" in alert["title"]
        assert len(alert["reasons"]) == 3
        assert "Early Blight" in alert["reasons"][0]

    def test_critical_risk_triggers_active_alert(self):
        risk = {
            "risk_level": "Critical",
            "risk_score": 0.88,
            "factors": [
                "Disease detected: Late Blight",
                "High humidity: 95%",
                "Vulnerable flowering stage",
            ],
        }
        alert = generate_alert(risk)
        assert alert["active"] is True
        assert alert["severity"] == "Critical"
        assert "Critical" in alert["title"]
        assert len(alert["reasons"]) == 3

    def test_medium_risk_is_inactive(self):
        risk = {
            "risk_level": "Medium",
            "risk_score": 0.45,
            "factors": ["Disease detected: Early Blight", "Moderate humidity"],
        }
        alert = generate_alert(risk)
        assert alert["active"] is False
        assert alert["severity"] is None
        assert alert["title"] is None
        assert alert["reasons"] == []

    def test_low_risk_is_inactive(self):
        risk = {
            "risk_level": "Low",
            "risk_score": 0.12,
            "factors": ["Healthy crop tissue", "Optimal humidity"],
        }
        alert = generate_alert(risk)
        assert alert["active"] is False
        assert alert["severity"] is None
        assert alert["title"] is None
        assert alert["reasons"] == []

    def test_none_input_returns_inactive(self):
        alert = generate_alert(None)
        assert alert["active"] is False
        assert alert["severity"] is None
        assert alert["reasons"] == []

    def test_empty_dict_returns_inactive(self):
        alert = generate_alert({})
        assert alert["active"] is False
        assert alert["reasons"] == []

    def test_string_level_input(self):
        alert = generate_alert("High")
        assert alert["active"] is True
        assert alert["severity"] == "High"
