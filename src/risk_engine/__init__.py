"""
Risk Engine Module — Contextual crop-health risk scoring.

Combines model prediction, severity estimate, and weather context into a
composite risk score. All weights and thresholds are PROTOTYPE VALUES whose
assumptions must be calibrated using validated agricultural data before any
field-advisory use.

Clearly distinguishes:
  - model_prediction   : output of the deep learning classifier
  - contextual_estimate: risk score derived from heuristic rules
  - agricultural_note  : known disease ecology from the knowledge base
"""

from .engine import RiskEngine, compute_risk

__all__ = ["RiskEngine", "compute_risk"]
