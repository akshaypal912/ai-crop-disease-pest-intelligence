"""Prediction Status Enums and Constants for Uncertainty-Aware System.

Defines structured status states for diagnostic predictions, severity estimation,
risk assessment, and pest detection to explicitly communicate uncertainty and
insufficient data conditions.
"""

from enum import Enum
from typing import Dict, Any


# ═══════════════════════════════════════════════════════════════════════════
# Prediction Status Enums
# ═══════════════════════════════════════════════════════════════════════════

class PredictionStatus(str, Enum):
    """Diagnostic prediction confidence states."""
    SUPPORTED_HIGH_CONFIDENCE = "SUPPORTED_HIGH_CONFIDENCE"
    SUPPORTED_LOW_CONFIDENCE = "SUPPORTED_LOW_CONFIDENCE"
    UNSUPPORTED_OR_UNCERTAIN = "UNSUPPORTED_OR_UNCERTAIN"
    INVALID_IMAGE = "INVALID_IMAGE"


class SeverityStatus(str, Enum):
    """Severity estimation reliability states."""
    RELIABLE = "RELIABLE"
    PROTOTYPE = "PROTOTYPE"
    UNRELIABLE = "UNRELIABLE"
    UNAVAILABLE = "UNAVAILABLE"


class RiskStatus(str, Enum):
    """Risk assessment data completeness states."""
    AVAILABLE = "AVAILABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNAVAILABLE = "UNAVAILABLE"


class PestStatus(str, Enum):
    """Pest detection model availability states."""
    DETECTED = "DETECTED"
    NO_PEST_DETECTED = "NO_PEST_DETECTED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    ERROR = "ERROR"


class WeatherStatus(str, Enum):
    """Weather data availability states."""
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


# ═══════════════════════════════════════════════════════════════════════════
# Confidence Thresholds (Engineering Estimates — Not Scientifically Calibrated)
# ═══════════════════════════════════════════════════════════════════════════

# High-confidence threshold: model output above this is considered reliable
CONFIDENCE_THRESHOLD_HIGH = 0.70

# Minimum confidence threshold: below this, prediction is considered uncertain
CONFIDENCE_THRESHOLD_LOW = 0.40

# Image quality thresholds
MIN_IMAGE_RESOLUTION = (50, 50)  # Minimum width x height in pixels
MAX_IMAGE_RESOLUTION = (8000, 8000)  # Maximum reasonable resolution
MIN_IMAGE_SIZE_BYTES = 100  # Minimum file size in bytes


# ═══════════════════════════════════════════════════════════════════════════
# Status Messages & Labels
# ═══════════════════════════════════════════════════════════════════════════

STATUS_MESSAGES: Dict[PredictionStatus, str] = {
    PredictionStatus.SUPPORTED_HIGH_CONFIDENCE: (
        "High-confidence diagnosis within the supported disease classes."
    ),
    PredictionStatus.SUPPORTED_LOW_CONFIDENCE: (
        "Low-confidence diagnosis. The image may not clearly match the trained disease patterns. "
        "Consider uploading a clearer image or seeking professional diagnosis."
    ),
    PredictionStatus.UNSUPPORTED_OR_UNCERTAIN: (
        "The image does not confidently match the supported Tomato disease classes. "
        "This may be a different crop, a non-leaf image, or an unsupported condition. "
        "Please upload a clear image of a Tomato leaf."
    ),
    PredictionStatus.INVALID_IMAGE: (
        "Image quality is insufficient for reliable analysis. "
        "Please ensure the image is clear, properly lit, and in a supported format."
    ),
}


SEVERITY_STATUS_MESSAGES: Dict[SeverityStatus, str] = {
    SeverityStatus.RELIABLE: (
        "Severity estimation based on validated methodology."
    ),
    SeverityStatus.PROTOTYPE: (
        "PROTOTYPE: Visible affected-area estimate from colour-space analysis. "
        "This is a heuristic estimate and not a validated epidemiological severity measurement."
    ),
    SeverityStatus.UNRELIABLE: (
        "Severity estimation unreliable due to low diagnostic confidence or image quality issues."
    ),
    SeverityStatus.UNAVAILABLE: (
        "Severity estimation unavailable. OpenCV not installed or processing failed."
    ),
}


RISK_STATUS_MESSAGES: Dict[RiskStatus, str] = {
    RiskStatus.AVAILABLE: (
        "Risk assessment based on available diagnostic, severity, and environmental data."
    ),
    RiskStatus.INSUFFICIENT_DATA: (
        "Insufficient data for reliable risk assessment. "
        "Missing one or more of: confident diagnosis, severity estimate, or environmental context."
    ),
    RiskStatus.UNAVAILABLE: (
        "Risk assessment unavailable due to system error."
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

def determine_prediction_status(confidence: float, image_valid: bool = True) -> PredictionStatus:
    """Determine prediction status from model confidence and image validity.
    
    Args:
        confidence: Model's maximum softmax probability (0.0 to 1.0)
        image_valid: Whether the image passed quality checks
        
    Returns:
        PredictionStatus enum value
    """
    if not image_valid:
        return PredictionStatus.INVALID_IMAGE
    
    if confidence >= CONFIDENCE_THRESHOLD_HIGH:
        return PredictionStatus.SUPPORTED_HIGH_CONFIDENCE
    elif confidence >= CONFIDENCE_THRESHOLD_LOW:
        return PredictionStatus.SUPPORTED_LOW_CONFIDENCE
    else:
        return PredictionStatus.UNSUPPORTED_OR_UNCERTAIN


def should_provide_diagnosis(status: PredictionStatus) -> bool:
    """Check if a definitive disease name should be provided."""
    return status in (
        PredictionStatus.SUPPORTED_HIGH_CONFIDENCE,
        PredictionStatus.SUPPORTED_LOW_CONFIDENCE,
    )


def should_compute_severity(status: PredictionStatus) -> bool:
    """Check if severity estimation should be attempted."""
    return status in (
        PredictionStatus.SUPPORTED_HIGH_CONFIDENCE,
        PredictionStatus.SUPPORTED_LOW_CONFIDENCE,
    )


def should_compute_full_risk(
    prediction_status: PredictionStatus,
    weather_available: bool,
) -> bool:
    """Check if full risk assessment can be computed."""
    has_diagnosis = should_provide_diagnosis(prediction_status)
    return has_diagnosis and weather_available


def get_status_message(status: PredictionStatus) -> str:
    """Get human-readable message for a prediction status."""
    return STATUS_MESSAGES.get(status, "Unknown prediction status.")

