import os
from pathlib import Path

class Config:
    """Central configuration management for Tomato crop disease classification."""
    
    # Global Parameters
    SEED: int = 42
    CROP_NAME: str = "Tomato"
    
    # Target Classes (4 core classes required for Phase 1)
    TARGET_CLASSES = [
        "Healthy",
        "Early Blight",
        "Late Blight",
        "Leaf Mold"
    ]
    
    # Class mapping directory folder names <-> clean label names
    CLASS_FOLDER_MAP = {
        "Tomato___healthy": "Healthy",
        "Tomato___Early_blight": "Early Blight",
        "Tomato___Late_blight": "Late Blight",
        "Tomato___Leaf_mold": "Leaf Mold",
        # Clean folder names fallback
        "Healthy": "Healthy",
        "Early_Blight": "Early Blight",
        "Late_Blight": "Late Blight",
        "Leaf_Mold": "Leaf Mold",
    }
    
    NUM_CLASSES: int = len(TARGET_CLASSES)
    
    # Image Preprocessing Hyperparameters
    IMAGE_SIZE: tuple = (224, 224)
    IMAGE_CHANNELS: int = 3
    
    # ImageNet Normalization
    NORM_MEAN: list = [0.485, 0.456, 0.406]
    NORM_STD: list = [0.229, 0.224, 0.225]
    
    # Data Split Ratios
    TRAIN_RATIO: float = 0.70
    VAL_RATIO: float = 0.15
    TEST_RATIO: float = 0.15
    
    # Training Hyperparameters
    BATCH_SIZE: int = 32
    NUM_WORKERS: int = 2
    LEARNING_RATE: float = 1e-3
    WEIGHT_DECAY: float = 1e-4
    EPOCHS: int = 10
    
    # Model Selection
    DEFAULT_MODEL_NAME: str = "mobilenet_v2" # Supported: 'mobilenet_v2', 'resnet18', 'efficientnet_b0'
    
    # Project File System Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    SAMPLE_DATA_DIR: Path = DATA_DIR / "sample"
    SPLITS_CSV_PATH: Path = DATA_DIR / "splits.csv"
    MODELS_DIR: Path = BASE_DIR / "models"
    DEFAULT_MODEL_SAVE_PATH: Path = MODELS_DIR / "tomato_disease_mobilenetv2.pt"

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist locally."""
        for d in [cls.DATA_DIR, cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR, cls.SAMPLE_DATA_DIR, cls.MODELS_DIR]:
            d.mkdir(parents=True, exist_ok=True)
