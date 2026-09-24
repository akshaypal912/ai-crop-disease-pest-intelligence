"""Pest inference pipeline.

Provides a modular interface for running pest object detection on images
(supplied as raw bytes, file paths, or PIL Images).
Ensures zero dependency interference with the disease classification model.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Union
from PIL import Image
import io

from src.models.pest_detection import (
    detect_pests,
    is_pest_model_available,
    reset_pest_detector,
)


class PestInferencePipeline:
    """Orchestrates pest detection on images with graceful error handling and resource cleanup."""

    def __init__(self):
        self._is_available = is_pest_model_available()

    @property
    def is_available(self) -> bool:
        """Check if pest detection model weights and dependencies are available."""
        return is_pest_model_available()

    def predict(self, image_input: Union[bytes, str, Path, Image.Image]) -> Dict[str, Any]:
        """Run pest detection on the provided image input.

        Parameters:
            image_input: Raw image bytes, filesystem path, Path object, or PIL Image.

        Returns:
            Dict containing:
                - "status": "available" | "unavailable" | "error"
                - "pests": List of detection dicts (pest, confidence, bounding_box)
                - "message": Informational status message
        """
        temp_file_path = None

        try:
            # Handle Path or str (already a path on disk)
            if isinstance(image_input, (str, Path)):
                path_str = str(image_input)
                if not os.path.exists(path_str):
                    return {
                        "status": "error",
                        "pests": [],
                        "message": f"Image file not found: {path_str}",
                    }
                return detect_pests(path_str)

            # Handle PIL Image
            elif isinstance(image_input, Image.Image):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    temp_file_path = tmp.name
                    # Convert RGBA/P to RGB before saving as JPEG
                    if image_input.mode not in ("RGB", "L"):
                        rgb_img = image_input.convert("RGB")
                    else:
                        rgb_img = image_input
                    rgb_img.save(temp_file_path, format="JPEG")
                return detect_pests(temp_file_path)

            # Handle raw bytes
            elif isinstance(image_input, bytes):
                if len(image_input) == 0:
                    return {
                        "status": "error",
                        "pests": [],
                        "message": "Empty image bytes provided for pest detection.",
                    }
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    temp_file_path = tmp.name
                    tmp.write(image_input)
                    tmp.flush()
                return detect_pests(temp_file_path)

            else:
                return {
                    "status": "error",
                    "pests": [],
                    "message": f"Unsupported image input type: {type(image_input)}",
                }

        finally:
            # Always clean up temporary files
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass


# Singleton instance
_pipeline_instance: Union[PestInferencePipeline, None] = None


def get_pest_pipeline() -> PestInferencePipeline:
    """Return the singleton PestInferencePipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = PestInferencePipeline()
    return _pipeline_instance


def reset_pest_pipeline():
    """Reset the singleton pipeline and detector (useful for tests)."""
    global _pipeline_instance
    _pipeline_instance = None
    reset_pest_detector()


def predict_pests(image_input: Union[bytes, str, Path, Image.Image]) -> Dict[str, Any]:
    """Convenience function to run pest detection on an image input."""
    pipeline = get_pest_pipeline()
    return pipeline.predict(image_input)
