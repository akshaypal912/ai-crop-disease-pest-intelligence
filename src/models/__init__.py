"""
Model definitions and transfer learning classifiers for crop disease intelligence.
"""
from .classifier import TomatoDiseaseClassifier, get_model

__all__ = ["TomatoDiseaseClassifier", "get_model"]
