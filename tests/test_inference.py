import os
import io
import pytest
from pathlib import Path
from PIL import Image

from src.utils.config import Config
from src.inference.pipeline import DiseaseInferencePipeline, get_inference_pipeline

SAMPLE_IMAGE_PATH = Config.RAW_DATA_DIR / "Tomato___healthy" / "sample_Tomato___healthy_000.jpg"

def test_inference_pipeline_initialization():
    pipeline = get_inference_pipeline()
    assert pipeline is not None
    assert pipeline.model is not None
    assert pipeline.crop_name == "Tomato"

def test_predict_with_valid_file_path():
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")
        
    pipeline = get_inference_pipeline()
    result = pipeline.predict(SAMPLE_IMAGE_PATH)
    
    assert "crop" in result
    assert result["crop"] == "Tomato"
    assert "predicted_disease" in result
    assert result["predicted_disease"] in Config.TARGET_CLASSES
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert "class_probabilities" in result
    assert len(result["class_probabilities"]) == len(Config.TARGET_CLASSES)

def test_predict_with_bytes_input():
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")
        
    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
        
    pipeline = get_inference_pipeline()
    result = pipeline.predict(image_bytes)
    
    assert result["crop"] == "Tomato"
    assert result["predicted_disease"] in Config.TARGET_CLASSES

def test_predict_with_pil_image_input():
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    pipeline = get_inference_pipeline()
    result = pipeline.predict(img)
    
    assert result["crop"] == "Tomato"
    assert result["predicted_disease"] in Config.TARGET_CLASSES

def test_predict_invalid_corrupted_image():
    pipeline = get_inference_pipeline()
    invalid_bytes = b"this_is_not_an_image_file_buffer"
    
    with pytest.raises(ValueError) as exc_info:
        pipeline.predict(invalid_bytes)
        
    assert "Invalid or corrupted image" in str(exc_info.value) or "cannot identify image file" in str(exc_info.value)

def test_predict_empty_buffer():
    pipeline = get_inference_pipeline()
    empty_bytes = b""
    
    with pytest.raises(ValueError) as exc_info:
        pipeline.predict(empty_bytes)
        
    assert "empty" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

def test_missing_model_file():
    non_existent_path = Path("models/non_existent_checkpoint_12345.pt")
    with pytest.raises(FileNotFoundError):
        DiseaseInferencePipeline(model_path=non_existent_path)
