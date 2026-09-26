"""
Severity Estimator — Prototype heuristic leaf-disease severity estimation.

Pipeline:
    PIL Image / bytes
        ↓  RGB → HSV + LAB colour-space conversion (OpenCV)
        ↓  Green-leaf mask  (healthy leaf area)
        ↓  Disease-indicator mask  (brown / yellow / dark spot pixels)
        ↓  affected_area_percentage = diseased / (green + diseased) × 100
        ↓  Severity category (Low / Moderate / High)

IMPORTANT — PROTOTYPE DISCLAIMER:
    The colour thresholds used here are heuristic estimates derived from general
    knowledge of leaf colouration. They have NOT been validated against:
      • Horsfall-Barratt severity scales
      • Annotated lesion segmentation datasets
      • Expert field assessments
    Do NOT use these estimates for official agricultural advisory, regulatory
    reporting, or chemical application decisions without independent validation.
"""

import io
import logging
from typing import Union, Dict, Any, Optional

import numpy as np
from PIL import Image

from src.utils.prediction_status import PredictionStatus, should_compute_severity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prototype Heuristic Thresholds (NOT scientifically validated)
# ---------------------------------------------------------------------------
# Severity categories based on estimated percentage of visible leaf area
# showing disease-indicator colouration. These boundaries are PLACEHOLDER
# values intended for prototype demonstration only.
SEVERITY_THRESHOLDS = {
    "Low":      (0.0,  10.0),   # 0 – 10 % affected
    "Moderate": (10.0, 30.0),   # 10 – 30 % affected
    "High":     (30.0, 100.0),  # > 30 % affected
}

# HSV colour ranges for the disease-indicator mask (brown, yellow, dark spots).
# These are tuned for typical tomato leaf pathology appearance under standard
# outdoor lighting. Performance may degrade under artificial light, deep shadow,
# or non-tomato crops. Values in OpenCV convention: H ∈ [0,179], S/V ∈ [0,255].
_DISEASE_COLOUR_MASKS_HSV = [
    # Yellow / chlorotic regions (hue ~15–35, high saturation)
    {"lower": np.array([15,  60,  80], dtype=np.uint8),
     "upper": np.array([35, 255, 255], dtype=np.uint8),
     "label": "yellow_chlorosis"},
    # Brown / necrotic regions (hue ~5–18, moderate-high saturation, low-mid value)
    {"lower": np.array([5,  50,  30], dtype=np.uint8),
     "upper": np.array([18, 255, 180], dtype=np.uint8),
     "label": "brown_necrosis"},
    # Dark spots / black lesions (any hue, low saturation, very low value)
    {"lower": np.array([0,   0,   0], dtype=np.uint8),
     "upper": np.array([179, 80,  50], dtype=np.uint8),
     "label": "dark_lesion"},
]

# HSV range for healthy green leaf tissue.
_GREEN_LEAF_MASK_HSV = {
    "lower": np.array([35, 40,  40], dtype=np.uint8),
    "upper": np.array([90, 255, 255], dtype=np.uint8),
}


class SeverityEstimator:
    """
    Prototype heuristic disease-severity estimator.

    Uses OpenCV colour-space analysis to estimate the fraction of the visible
    leaf area that exhibits disease-indicator colouration (brown, yellow, dark).
    Results are labelled as prototype estimates; see module docstring for caveats.
    """

    def __init__(self):
        try:
            import cv2  # noqa: F401
            self._cv2_available = True
        except ImportError:
            logger.warning(
                "opencv-python not found. SeverityEstimator will return "
                "fallback values. Install opencv-python to enable severity analysis."
            )
            self._cv2_available = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate(
        self,
        image_input: Union[str, bytes, io.BytesIO, "Image.Image"],
        predicted_disease: Optional[str] = None,
        prediction_status: Optional[PredictionStatus] = None,
    ) -> Dict[str, Any]:
        """
        Estimate disease severity from a leaf image with status awareness.

        Args:
            image_input: PIL Image, raw bytes, BytesIO, or file path.
            predicted_disease: The predicted disease class name. If "Healthy",
                severity is returned as 0% / Low without pixel analysis.
            prediction_status: The prediction status from inference pipeline.
                If uncertain/invalid, returns UNRELIABLE status.

        Returns:
            {
                "status": "PROTOTYPE" | "UNRELIABLE" | "UNAVAILABLE",
                "level": "Low" | "Moderate" | "High" | None,
                "visible_affected_area_percentage": float | None,
                "method": str | None,
                "message": str,
            }
        """
        # Check if diagnosis is uncertain - do not estimate severity
        if prediction_status and not should_compute_severity(prediction_status):
            return {
                "status": "UNRELIABLE",
                "level": None,
                "visible_affected_area_percentage": None,
                "method": None,
                "message": (
                    "Severity estimation unreliable due to uncertain or invalid diagnosis. "
                    "A confident disease identification is required for meaningful severity analysis."
                ),
            }

        # Short-circuit for healthy predictions
        if predicted_disease and predicted_disease.lower() == "healthy":
            return {
                "status": "PROTOTYPE",
                "level": "Low",
                "visible_affected_area_percentage": 0.0,
                "method": "healthy_class_passthrough",
                "message": "Healthy classification: no visible disease symptoms expected.",
            }

        if not self._cv2_available:
            return self._fallback_result()

        try:
            pil_img = self._load_pil(image_input)
            affected_pct = self._compute_affected_percentage(pil_img)
            severity = self._pct_to_category(affected_pct)
            return {
                "status": "PROTOTYPE",
                "level": severity,
                "visible_affected_area_percentage": round(affected_pct, 2),
                "method": "opencv_hsv_colour_segmentation",
                "message": (
                    "PROTOTYPE: Visible affected-area estimate from colour-space analysis. "
                    "This is a heuristic estimate and not a validated epidemiological severity measurement."
                ),
            }
        except Exception as exc:
            logger.warning("Severity estimation failed: %s. Returning fallback.", exc)
            return self._fallback_result()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_pil(self, image_input) -> "Image.Image":
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        if isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input)).convert("RGB")
        if isinstance(image_input, io.BytesIO):
            image_input.seek(0)
            return Image.open(image_input).convert("RGB")
        # Assume file path
        return Image.open(image_input).convert("RGB")

    def _compute_affected_percentage(self, pil_img: "Image.Image") -> float:
        """
        Core colour-segmentation logic.

        Converts the image to HSV, builds separate masks for green leaf tissue
        and disease-indicator colouration, then computes:
            affected% = disease_pixels / (green_pixels + disease_pixels) × 100

        Returns 0.0 if no leaf-like pixels are detected (e.g., background-only image).
        """
        import cv2  # imported here so module loads without cv2

        # Resize for consistent, fast processing (does not affect ratio calculation)
        img_resized = pil_img.resize((256, 256), Image.LANCZOS)
        bgr = cv2.cvtColor(np.array(img_resized), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        # Build disease-indicator mask (union of all disease colour ranges)
        disease_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for mask_def in _DISEASE_COLOUR_MASKS_HSV:
            m = cv2.inRange(hsv, mask_def["lower"], mask_def["upper"])
            disease_mask = cv2.bitwise_or(disease_mask, m)

        # Build green-leaf mask
        green_mask = cv2.inRange(
            hsv, _GREEN_LEAF_MASK_HSV["lower"], _GREEN_LEAF_MASK_HSV["upper"]
        )

        # Morphological cleanup to remove isolated noise pixels
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)

        disease_px = int(np.sum(disease_mask > 0))
        green_px = int(np.sum(green_mask > 0))
        leaf_px = disease_px + green_px

        if leaf_px == 0:
            return 0.0

        return (disease_px / leaf_px) * 100.0

    @staticmethod
    def _pct_to_category(affected_pct: float) -> str:
        """
        Map an affected-area percentage to a severity category.

        Thresholds are PROTOTYPE ESTIMATES — see SEVERITY_THRESHOLDS constant.
        """
        if affected_pct < SEVERITY_THRESHOLDS["Moderate"][0]:
            return "Low"
        if affected_pct < SEVERITY_THRESHOLDS["High"][0]:
            return "Moderate"
        return "High"

    @staticmethod
    def _build_result(severity: str, affected_pct: float, method: str) -> Dict[str, Any]:
        return {
            "severity": severity,
            "affected_area_percentage": affected_pct,
            "estimation_method": method,
            "prototype_disclaimer": (
                "PROTOTYPE: Severity values are heuristic estimates from colour-space "
                "pixel analysis. They have not been validated against standardised "
                "disease-severity scales or field assessments. Do not use for official "
                "agricultural advisory or treatment decisions."
            ),
        }

    @staticmethod
    def _fallback_result() -> Dict[str, Any]:
        return {
            "status": "UNAVAILABLE",
            "level": None,
            "visible_affected_area_percentage": None,
            "method": "unavailable",
            "message": (
                "Severity estimation unavailable: opencv-python not installed "
                "or image processing failed."
            ),
        }


# ---------------------------------------------------------------------------
# Module-level singleton + convenience function
# ---------------------------------------------------------------------------

_estimator_instance: Optional[SeverityEstimator] = None


def get_severity_estimator() -> SeverityEstimator:
    """Singleton getter for SeverityEstimator."""
    global _estimator_instance
    if _estimator_instance is None:
        _estimator_instance = SeverityEstimator()
    return _estimator_instance


def estimate_severity(
    image_input: Union[str, bytes, io.BytesIO, "Image.Image"],
    predicted_disease: Optional[str] = None,
    prediction_status: Optional[PredictionStatus] = None,
) -> Dict[str, Any]:
    """
    Convenience function. Calls SeverityEstimator.estimate() on the singleton instance.
    
    Args:
        image_input: Image in various formats
        predicted_disease: Predicted disease name
        prediction_status: Prediction status from inference pipeline
    """
    return get_severity_estimator().estimate(image_input, predicted_disease, prediction_status)
