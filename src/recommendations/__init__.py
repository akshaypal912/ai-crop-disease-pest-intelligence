"""Recommendation engine package for crop disease and pest intelligence."""

from src.recommendations.recommendation_engine import (
    generate_recommendations,
    DISEASE_RECOMMENDATIONS,
    PEST_RECOMMENDATIONS,
)

__all__ = [
    "generate_recommendations",
    "DISEASE_RECOMMENDATIONS",
    "PEST_RECOMMENDATIONS",
]
