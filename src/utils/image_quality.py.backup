"""Image Quality Validation Module.

Pre-flight validation checks for image inputs before disease classification:
- File size validation
- Image format validation  
- Resolution validation
- Basic corruption detection
- Optional blur detection (if OpenCV available)

Returns structured validation results with specific failure reasons.
"""

import io
import logging
from typing import Union, Dict, Any, Tuple
from pathlib import Path
from PIL import Image

from src.utils.prediction_status import (
    MIN_IMAGE_RESOLUTION,
    MAX_IMAGE_RESOLUTION,
    MIN_IMAGE_SIZE_BYTES,
)

logger = logging.getLogger(__name__)

# Supported image formats
SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "BMP", "TIFF"}

# Blur detection threshold (Laplacian variance)
# Lower values indicate more blur; threshold is heuristic
BLUR_THRESHOLD = 100.0
