"""Pest detection model package.

Provides an interface to object detection models for agricultural pests (e.g., YOLOv8).
Gracefully handles missing weights, missing dependencies, and unconfigured environments.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Supported default pest classes for tomato/crop intelligence
SUPPORTED_PEST_CLASSES = [
    "Aphid",
    "Armyworm",
    "Beetle",
    "Bollworm",
    "Caterpillar",
    "Grasshopper",
    "Mite",
    "Mosquito",
    "Sawfly",
    "Stem Borer",
    "Tomato Hornworm",
    "Whitefly",
]

# Weights path configuration
DEFAULT_WEIGHTS_DIR = Path(__file__).parent / "weights"
DEFAULT_WEIGHTS_PATH = DEFAULT_WEIGHTS_DIR / "pest_yolov8.pt"


def get_weights_path() -> Path:
    """Return the configured path to the pest detection model weights."""
    env_path = os.getenv("PEST_MODEL_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_WEIGHTS_PATH


def is_pest_model_available() -> bool:
    """Check if the pest detection model library and weights are both present."""
    weights_path = get_weights_path()
    if not weights_path.exists():
        return False
    try:
        import ultralytics  # noqa: F401
        return True
    except ImportError:
        return False


# Global singleton cache
_pest_model_instance = None


def get_pest_detector():
    """Return the singleton YOLO model for pest detection if available.

    Raises:
        FileNotFoundError: if model weights are missing.
        RuntimeError: if the ultralytics library is not installed.
    """
    global _pest_model_instance
    if _pest_model_instance is not None:
        return _pest_model_instance

    weights_path = get_weights_path()
    if not weights_path.exists():
        raise FileNotFoundError(
            f"Pest detection weights not found at {weights_path}. "
            "Please download or train a YOLOv8 pest detection model and place it in the weights directory, "
            "or specify PEST_MODEL_PATH in your environment."
        )

    try:
        from ultralytics import YOLO
    except ImportError as e:
        raise RuntimeError(
            "Ultralytics YOLO library is required for pest detection. "
            "Install it via `pip install ultralytics`"
        ) from e

    _pest_model_instance = YOLO(str(weights_path))
    return _pest_model_instance


def reset_pest_detector():
    """Reset the singleton detector instance (useful for testing)."""
    global _pest_model_instance
    _pest_model_instance = None


def detect_pests(image_path: str) -> Dict[str, Any]:
    """Run pest detection on a single image file path.

    Parameters:
        image_path: Path to the image file on disk.

    Returns:
        Dict with keys:
            - status: "available" | "unavailable" | "error"
            - pests: List of dicts with 'pest', 'confidence', 'bounding_box'
            - message: Informational status message
    """
    if not is_pest_model_available():
        return {
            "status": "unavailable",
            "pests": [],
            "message": "Pest detection model is not configured (missing weights or ultralytics library).",
        }

    try:
        model = get_pest_detector()
        results = model(image_path)
        detections: List[Dict[str, Any]] = []

        for result in results:
            if not hasattr(result, "boxes") or result.boxes is None:
                continue

            for cls_id, conf, box in zip(
                result.boxes.cls.tolist(),
                result.boxes.conf.tolist(),
                result.boxes.xyxy.tolist(),
            ):
                # Map class index to class name
                if hasattr(model, "names") and int(cls_id) in model.names:
                    pest_name = model.names[int(cls_id)]
                elif int(cls_id) < len(SUPPORTED_PEST_CLASSES):
                    pest_name = SUPPORTED_PEST_CLASSES[int(cls_id)]
                else:
                    pest_name = f"Pest_Class_{int(cls_id)}"

                detections.append(
                    {
                        "pest": str(pest_name),
                        "confidence": round(float(conf), 4),
                        "bounding_box": [int(round(coord)) for coord in box],
                    }
                )

        return {
            "status": "available",
            "pests": detections,
            "message": f"Successfully detected {len(detections)} pest instances.",
        }

    except Exception as e:
        return {
            "status": "error",
            "pests": [],
            "message": f"Pest detection failed during inference: {str(e)}",
        }
