"""Confidence and Crop-Mismatch Utility Helpers.

Provides standard thresholding and warning generation for out-of-distribution /
non-target crop images when using single-crop models.
"""

from typing import Dict, Any, Optional

# Default confidence threshold below which single-crop classification is considered uncertain
CROP_CONFIDENCE_THRESHOLD = 0.40

UNCERTAIN_DISEASE_NAME = "Uncertain — result may not apply to this crop type"

MISMATCH_WARNING_MESSAGE = (
    "Yeh model currently sirf Tomato (Solanum lycopersicum) ke liye trained hai. "
    "Uploaded image kisi aur crop ki lag rahi hai — result unreliable ho sakta hai."
)


def check_crop_mismatch(confidence: float, threshold: float = CROP_CONFIDENCE_THRESHOLD) -> Dict[str, Any]:
    """Check if model prediction confidence indicates a possible crop mismatch.

    Parameters:
        confidence: Prediction probability (0.0 to 1.0).
        threshold: Minimum confidence threshold (default: 0.40).

    Returns:
        Dict with:
            - possible_crop_mismatch: bool
            - mismatch_warning: Optional[str]
            - display_disease_name: Optional[str] helper
    """
    is_mismatch = confidence < threshold
    return {
        "possible_crop_mismatch": is_mismatch,
        "mismatch_warning": MISMATCH_WARNING_MESSAGE if is_mismatch else None,
        "threshold": threshold,
    }
