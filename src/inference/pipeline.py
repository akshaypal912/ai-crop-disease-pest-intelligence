import io
from pathlib import Path
from typing import Dict, Any, Union, Optional
from PIL import Image
import torch
import torch.nn.functional as F

from src.utils.config import Config
from src.utils.prediction_status import (
    PredictionStatus,
    determine_prediction_status,
    should_provide_diagnosis,
    get_status_message,
    CONFIDENCE_THRESHOLD_HIGH,
    CONFIDENCE_THRESHOLD_LOW,
)
from src.utils.image_quality import validate_image_quality
from src.preprocessing.transforms import get_val_test_transforms
from src.models.classifier import TomatoDiseaseClassifier


class DiseaseInferencePipeline:
    """
    Uncertainty-Aware Disease Inference Engine.
    
    Integrates image quality validation, confidence thresholding, and structured
    prediction status to avoid forcing out-of-distribution images into disease classes.
    
    Pipeline:
        Image Input → Quality Validation → Model Inference → Status Determination → Structured Output
    
    Returns explicit UNSUPPORTED/UNCERTAIN status instead of forcing classification.
    """
    
    def __init__(self, model_path: Union[str, Path] = Config.DEFAULT_MODEL_SAVE_PATH, device: str = None):
        self.model_path = Path(model_path)
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.transform = get_val_test_transforms()
        self.model = None
        self.crop_name = Config.CROP_NAME
        self.class_names = Config.TARGET_CLASSES
        
        self.load_model()

    def load_model(self):
        """Loads model checkpoint from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found at: {self.model_path}. "
                f"Please train the model first using `python train.py`."
            )
            
        checkpoint = torch.load(self.model_path, map_location="cpu")
        model_name = checkpoint.get("model_name", Config.DEFAULT_MODEL_NAME)
        self.class_names = checkpoint.get("class_names", Config.TARGET_CLASSES)
        
        self.model = TomatoDiseaseClassifier(
            num_classes=len(self.class_names),
            model_name=model_name,
            pretrained=False
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

    def validate_and_load_image(self, image_input: Union[str, Path, bytes, io.BytesIO, Image.Image]) -> Image.Image:
        """
        Validates input image, format, and corruption state before returning PIL Image.
        """
        try:
            if isinstance(image_input, (str, Path)):
                path = Path(image_input)
                if not path.exists():
                    raise FileNotFoundError(f"Image file does not exist: {path}")
                img = Image.open(path)
            elif isinstance(image_input, bytes):
                if len(image_input) == 0:
                    raise ValueError("Received empty image file buffer (0 bytes).")
                img = Image.open(io.BytesIO(image_input))
            elif isinstance(image_input, io.BytesIO):
                img = Image.open(image_input)
            elif isinstance(image_input, Image.Image):
                img = image_input
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")

            # Verify image content integrity
            img.verify()
            
            # Reopen after verify() closes image handle
            if isinstance(image_input, (str, Path)):
                img = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, bytes):
                img = Image.open(io.BytesIO(image_input)).convert("RGB")
            elif isinstance(image_input, io.BytesIO):
                image_input.seek(0)
                img = Image.open(image_input).convert("RGB")
            else:
                img = image_input.convert("RGB")
                
            return img

        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise e
            raise ValueError(f"Invalid or corrupted image file: {str(e)}")

    def predict(self, image_input: Union[str, Path, bytes, io.BytesIO, Image.Image]) -> Dict[str, Any]:
        """
        Runs inference on input image with uncertainty-aware prediction status.
        
        Pipeline:
            1. Image quality validation (resolution, format, corruption)
            2. Model inference (if quality OK)
            3. Confidence-based status determination
            4. Conditional disease name (only if confident)
        
        Returns:
            Dict containing:
                - prediction_status (PredictionStatus): Confidence/validity state
                - status_message (str): Human-readable explanation
                - crop (str): Target crop name
                - disease (Optional[str]): Disease name (None if uncertain)
                - model_confidence (float): Raw model confidence (NOT calibrated probability)
                - class_probabilities (Dict[str, float]): All class scores
                - raw_predicted_class (str): Top class before filtering
                - quality_warnings (List[str]): Image quality issues
        """
        if self.model is None:
            raise RuntimeError("Model is not initialized or loaded.")
        
        # Step 1: Image Quality Validation
        quality_result = validate_image_quality(image_input, check_blur=False)
        
        if not quality_result["valid"]:
            # Image failed quality checks - return INVALID_IMAGE status
            return {
                "prediction_status": PredictionStatus.INVALID_IMAGE,
                "status_message": get_status_message(PredictionStatus.INVALID_IMAGE),
                "crop": self.crop_name,
                "disease": None,
                "model_confidence": 0.0,
                "class_probabilities": {},
                "raw_predicted_class": None,
                "quality_errors": quality_result.get("errors", []),
                "quality_warnings": quality_result.get("warnings", []),
            }
        
        # Step 2: Load and preprocess image
        try:
            pil_img = self.validate_and_load_image(image_input)
            tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        except Exception as e:
            return {
                "prediction_status": PredictionStatus.INVALID_IMAGE,
                "status_message": f"Image loading failed: {str(e)}",
                "crop": self.crop_name,
                "disease": None,
                "model_confidence": 0.0,
                "class_probabilities": {},
                "raw_predicted_class": None,
                "quality_errors": [str(e)],
                "quality_warnings": [],
            }
        
        # Step 3: Model Inference
        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1).squeeze(0)
            
        top_prob, top_idx = torch.max(probs, dim=0)
        conf_val = round(float(top_prob.item()), 4)
        raw_predicted_class = self.class_names[top_idx.item()]
        
        prob_dict = {
            self.class_names[i]: round(float(probs[i].item()), 4)
            for i in range(len(self.class_names))
        }
        
        # Step 4: Determine Prediction Status based on confidence
        prediction_status = determine_prediction_status(conf_val, image_valid=True)
        status_message = get_status_message(prediction_status)
        
        # Step 5: Conditional Disease Name
        # Only provide disease name if confidence meets minimum threshold
        if should_provide_diagnosis(prediction_status):
            disease_name = raw_predicted_class
        else:
            disease_name = None
        
        return {
            "prediction_status": prediction_status,
            "status_message": status_message,
            "crop": self.crop_name,
            "disease": disease_name,
            "model_confidence": conf_val,
            "class_probabilities": prob_dict,
            "raw_predicted_class": raw_predicted_class,
            "quality_warnings": quality_result.get("warnings", []),
            "confidence_threshold_high": CONFIDENCE_THRESHOLD_HIGH,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
        }


_pipeline_instance = None


def get_inference_pipeline(model_path: Union[str, Path] = Config.DEFAULT_MODEL_SAVE_PATH) -> DiseaseInferencePipeline:
    """Singleton getter for inference pipeline."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DiseaseInferencePipeline(model_path=model_path)
    return _pipeline_instance
