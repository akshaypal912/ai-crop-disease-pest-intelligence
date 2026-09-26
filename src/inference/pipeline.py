import io
from pathlib import Path
from typing import Dict, Any, Union
from PIL import Image
import torch
import torch.nn.functional as F

from src.utils.config import Config
from src.utils.confidence_utils import (
    check_crop_mismatch,
    UNCERTAIN_DISEASE_NAME,
    CROP_CONFIDENCE_THRESHOLD,
)
from src.preprocessing.transforms import get_val_test_transforms
from src.models.classifier import TomatoDiseaseClassifier


class DiseaseInferencePipeline:
    """
    Production-ready Inference Engine for Crop Disease Image Classification.
    Uses the exact same preprocessing transforms as validation & evaluation pipelines.
    Handles image bytes, file paths, and PIL Images with full error checking.
    Includes confidence thresholding to flag possible non-target crop mismatch.
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
        Runs inference on input image and returns structured result payload.
        
        Returns:
            Dict containing:
                - crop (str)
                - predicted_disease (str)
                - confidence (float)
                - class_probabilities (Dict[str, float])
                - possible_crop_mismatch (bool)
                - mismatch_warning (Optional[str])
                - raw_predicted_disease (str)
        """
        if self.model is None:
            raise RuntimeError("Model is not initialized or loaded.")
            
        pil_img = self.validate_and_load_image(image_input)
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1).squeeze(0)
            
        top_prob, top_idx = torch.max(probs, dim=0)
        conf_val = round(float(top_prob.item()), 4)
        raw_disease = self.class_names[top_idx.item()]
        
        prob_dict = {
            self.class_names[i]: round(float(probs[i].item()), 4)
            for i in range(len(self.class_names))
        }
        
        # Check for crop mismatch / low confidence threshold
        mismatch_info = check_crop_mismatch(conf_val, threshold=CROP_CONFIDENCE_THRESHOLD)
        is_mismatch = mismatch_info["possible_crop_mismatch"]
        
        display_disease = UNCERTAIN_DISEASE_NAME if is_mismatch else raw_disease
        
        return {
            "crop": self.crop_name,
            "predicted_disease": display_disease,
            "raw_predicted_disease": raw_disease,
            "confidence": conf_val,
            "class_probabilities": prob_dict,
            "possible_crop_mismatch": is_mismatch,
            "mismatch_warning": mismatch_info["mismatch_warning"],
        }


_pipeline_instance = None


def get_inference_pipeline(model_path: Union[str, Path] = Config.DEFAULT_MODEL_SAVE_PATH) -> DiseaseInferencePipeline:
    """Singleton getter for inference pipeline."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DiseaseInferencePipeline(model_path=model_path)
    return _pipeline_instance
