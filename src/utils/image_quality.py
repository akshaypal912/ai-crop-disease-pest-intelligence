"""Image Quality Validation Module."""
import io
import logging
from typing import Union, Dict, Any, Tuple
from pathlib import Path
from PIL import Image
from src.utils.prediction_status import MIN_IMAGE_RESOLUTION, MAX_IMAGE_RESOLUTION, MIN_IMAGE_SIZE_BYTES

logger = logging.getLogger(__name__)
SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "BMP", "TIFF"}
BLUR_THRESHOLD = 100.0

class ImageQualityValidator:
    def __init__(self, check_blur: bool = False):
        self.check_blur = check_blur
        self._cv2_available = False
        if check_blur:
            try:
                import cv2
                self._cv2_available = True
            except ImportError:
                logger.warning("OpenCV not available. Blur detection disabled.")
                self.check_blur = False
    
    def validate(self, image_input) -> Dict[str, Any]:
        errors, warnings, img_size, img_format = [], [], None, None
        try:
            img, load_error = self._load_image(image_input)
            if load_error:
                return {"valid": False, "errors": [load_error], "warnings": [], "image_size": None, "format": None}
            
            img_format = img.format if hasattr(img, 'format') else None
            img_size = img.size
            width, height = img_size
            
            min_w, min_h = MIN_IMAGE_RESOLUTION
            if width < min_w or height < min_h:
                errors.append(f"Resolution too low: {width}x{height}px. Min: {min_w}x{min_h}px.")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "image_size": img_size, "format": img_format}
    
    @staticmethod
    def _load_image(image_input):
        try:
            if isinstance(image_input, Image.Image):
                return image_input, None
            elif isinstance(image_input, (str, Path)):
                path = Path(image_input)
                if not path.exists():
                    return None, f"File not found: {path}"
                img = Image.open(path).convert("RGB")
                return img, None
            elif isinstance(image_input, bytes):
                if len(image_input) < MIN_IMAGE_SIZE_BYTES:
                    return None, "Image data too small"
                img = Image.open(io.BytesIO(image_input)).convert("RGB")
                return img, None
            else:
                return None, f"Unsupported type: {type(image_input)}"
        except Exception as e:
            return None, f"Load failed: {str(e)}"

_validator_instance = None

def get_image_quality_validator(check_blur: bool = False):
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ImageQualityValidator(check_blur=check_blur)
    return _validator_instance

def validate_image_quality(image_input, check_blur: bool = False):
    return get_image_quality_validator(check_blur=check_blur).validate(image_input)
