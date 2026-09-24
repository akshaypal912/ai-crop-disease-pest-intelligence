import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from PIL import Image
from typing import Dict, Any, Union
from pathlib import Path

from src.utils.config import Config
from src.preprocessing.transforms import get_val_test_transforms

class TomatoDiseaseClassifier(nn.Module):
    """
    Transfer Learning Classifier for Tomato Crop Disease Intelligence.
    Supports MobileNetV2, EfficientNet-B0, and ResNet18 backbones.
    """
    
    def __init__(
        self,
        num_classes: int = Config.NUM_CLASSES,
        model_name: str = Config.DEFAULT_MODEL_NAME,
        pretrained: bool = True
    ):
        super(TomatoDiseaseClassifier, self).__init__()
        self.num_classes = num_classes
        self.model_name = model_name.lower()
        self.class_names = Config.TARGET_CLASSES
        
        # Load backbone architecture
        if self.model_name == "mobilenet_v2":
            weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
            self.backbone = models.mobilenet_v2(weights=weights)
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier[1] = nn.Linear(in_features, num_classes)
            
        elif self.model_name == "efficientnet_b0":
            weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
            self.backbone = models.efficientnet_b0(weights=weights)
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier[1] = nn.Linear(in_features, num_classes)
            
        elif self.model_name == "resnet18":
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            self.backbone = models.resnet18(weights=weights)
            in_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Linear(in_features, num_classes)
            
        else:
            raise ValueError(f"Unsupported model architecture: {model_name}. Choose 'mobilenet_v2', 'efficientnet_b0', or 'resnet18'.")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning raw class logits."""
        return self.backbone(x)

    def predict(self, x: torch.Tensor) -> Dict[str, Any]:
        """
        Run inference on a single image tensor batch or tensor.
        
        Args:
            x (torch.Tensor): Preprocessed image tensor shape (1, 3, H, W) or (3, H, W).
            
        Returns:
            Dict containing:
                - predicted_disease (str)
                - confidence (float)
                - probabilities (Dict[str, float])
        """
        self.eval()
        if x.dim() == 3:
            x = x.unsqueeze(0)
            
        with torch.no_grad():
            logits = self.forward(x)
            probs = F.softmax(logits, dim=1).squeeze(0)
            
        top_prob, top_idx = torch.max(probs, dim=0)
        
        prob_dict = {
            self.class_names[i]: float(probs[i].item())
            for i in range(len(self.class_names))
        }
        
        return {
            "predicted_disease": self.class_names[top_idx.item()],
            "confidence": float(top_prob.item()),
            "probabilities": prob_dict
        }

    def predict_file(self, image_path: Union[str, Path], device: str = "cpu") -> Dict[str, Any]:
        """
        Run inference directly on an image file path.
        """
        self.to(device)
        self.eval()
        
        transform = get_val_test_transforms()
        image = Image.open(image_path).convert("RGB")
        tensor = transform(image).unsqueeze(0).to(device)
        
        return self.predict(tensor)

def get_model(
    model_name: str = Config.DEFAULT_MODEL_NAME,
    num_classes: int = Config.NUM_CLASSES,
    pretrained: bool = True
) -> TomatoDiseaseClassifier:
    """Factory function for instantiating tomato disease classifier."""
    return TomatoDiseaseClassifier(num_classes=num_classes, model_name=model_name, pretrained=pretrained)
