"""Unit Tests for Pest Detection Module and Inference Pipeline.

Tests:
- Missing YOLO weights handling (graceful fallback)
- Model availability checks
- Pest detection output schema
- Mocked detector inference with valid bounding boxes
- Pipeline input handling (bytes, PIL Image, invalid formats)
- Malformed detector output handling
"""

import sys
from pathlib import Path
import pytest
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.pest_detection import (
    is_pest_model_available,
    detect_pests,
    get_pest_detector,
    reset_pest_detector,
    SUPPORTED_PEST_CLASSES,
)
from src.inference.pest.pipeline import (
    PestInferencePipeline,
    get_pest_pipeline,
    reset_pest_pipeline,
    predict_pests,
)


@pytest.fixture(autouse=True)
def clean_pest_state():
    reset_pest_pipeline()
    reset_pest_detector()
    yield
    reset_pest_pipeline()
    reset_pest_detector()


# ---------------------------------------------------------------------------
# Missing Weights / Unconfigured Environment
# ---------------------------------------------------------------------------

class TestMissingWeights:
    def test_is_model_available_false_when_weights_missing(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PEST_MODEL_PATH", str(tmp_path / "non_existent.pt"))
        assert is_pest_model_available() is False

    def test_detect_pests_graceful_fallback(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PEST_MODEL_PATH", str(tmp_path / "non_existent.pt"))
        dummy_img = tmp_path / "test.jpg"
        dummy_img.write_bytes(b"dummy")

        result = detect_pests(str(dummy_img))
        assert result["status"] == "unavailable"
        assert result["pests"] == []
        assert "not configured" in result["message"].lower()

    def test_get_pest_detector_raises_file_not_found(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PEST_MODEL_PATH", str(tmp_path / "non_existent.pt"))
        with pytest.raises(FileNotFoundError):
            get_pest_detector()


# ---------------------------------------------------------------------------
# Pipeline Input Types & Error Handling
# ---------------------------------------------------------------------------

class TestPipelineInputHandling:
    def test_empty_bytes_input(self):
        pipeline = PestInferencePipeline()
        result = pipeline.predict(b"")
        assert result["status"] == "error"
        assert result["pests"] == []
        assert "empty" in result["message"].lower()

    def test_invalid_type_input(self):
        pipeline = PestInferencePipeline()
        result = pipeline.predict(12345)  # type: ignore
        assert result["status"] == "error"
        assert "unsupported" in result["message"].lower()

    def test_missing_file_path(self):
        pipeline = PestInferencePipeline()
        result = pipeline.predict("non_existent_file_path_1234.jpg")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_pil_image_fallback_when_unconfigured(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PEST_MODEL_PATH", str(tmp_path / "missing.pt"))
        pipeline = PestInferencePipeline()
        img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
        result = pipeline.predict(img)
        assert result["status"] == "unavailable"
        assert result["pests"] == []


# ---------------------------------------------------------------------------
# Mocked Detection Execution
# ---------------------------------------------------------------------------

class DummyBox:
    def __init__(self, cls, conf, xyxy):
        self._cls = cls
        self._conf = conf
        self._xyxy = xyxy

    @property
    def cls(self):
        class ArrayWrap:
            def __init__(self, data): self._data = data
            def tolist(self): return self._data
        return ArrayWrap(self._cls)

    @property
    def conf(self):
        class ArrayWrap:
            def __init__(self, data): self._data = data
            def tolist(self): return self._data
        return ArrayWrap(self._conf)

    @property
    def xyxy(self):
        class ArrayWrap:
            def __init__(self, data): self._data = data
            def tolist(self): return self._data
        return ArrayWrap(self._xyxy)


class DummyResult:
    def __init__(self, boxes):
        self.boxes = boxes


class DummyYOLOModel:
    def __init__(self):
        self.names = {0: "Aphid", 1: "Whitefly", 2: "Tomato Hornworm"}

    def __call__(self, image_path):
        boxes = DummyBox(
            cls=[0, 1],
            conf=[0.9234, 0.8711],
            xyxy=[[10, 20, 110, 120], [150, 80, 220, 190]]
        )
        return [DummyResult(boxes)]


class TestMockedPestInference:
    def test_mocked_pest_detection_output_schema(self, monkeypatch, tmp_path):
        # Create a fake weights file so availability passes
        fake_weights = tmp_path / "fake_yolo.pt"
        fake_weights.write_bytes(b"fake model")
        monkeypatch.setenv("PEST_MODEL_PATH", str(fake_weights))

        # Mock get_pest_detector to return our DummyYOLOModel
        dummy_model = DummyYOLOModel()
        monkeypatch.setattr("src.models.pest_detection.is_pest_model_available", lambda: True)
        monkeypatch.setattr("src.models.pest_detection.get_pest_detector", lambda: dummy_model)

        img = Image.fromarray(np.zeros((300, 300, 3), dtype=np.uint8))
        result = predict_pests(img)

        assert result["status"] == "available"
        assert len(result["pests"]) == 2

        # Check first detection
        det1 = result["pests"][0]
        assert det1["pest"] == "Aphid"
        assert det1["confidence"] == 0.9234
        assert det1["bounding_box"] == [10, 20, 110, 120]

        # Check second detection
        det2 = result["pests"][1]
        assert det2["pest"] == "Whitefly"
        assert det2["confidence"] == 0.8711
        assert det2["bounding_box"] == [150, 80, 220, 190]

    def test_malformed_detector_output_handled_gracefully(self, monkeypatch, tmp_path):
        # Model returning empty/None results
        class BrokenModel:
            def __call__(self, image_path):
                return [DummyResult(None)]

        monkeypatch.setattr("src.models.pest_detection.is_pest_model_available", lambda: True)
        monkeypatch.setattr("src.models.pest_detection.get_pest_detector", lambda: BrokenModel())

        img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
        result = predict_pests(img)

        assert result["status"] == "available"
        assert result["pests"] == []
