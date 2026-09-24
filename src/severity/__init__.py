"""
Severity Estimation Module — Prototype heuristic-based leaf disease severity estimation.

NOTE: All thresholds in this module are PROTOTYPE ESTIMATES based on colour-space
segmentation heuristics. They have NOT been validated against agricultural field data
or peer-reviewed disease-severity scales (e.g., Horsfall-Barratt). Use for
exploratory purposes only; calibrate thresholds with domain expert guidance.
"""

from .estimator import SeverityEstimator, estimate_severity

__all__ = ["SeverityEstimator", "estimate_severity"]
