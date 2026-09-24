import argparse
from pathlib import Path
import torch

from src.utils.config import Config
from src.utils.seed import set_seed
from src.preprocessing.dataset import get_dataloaders
from src.models.classifier import TomatoDiseaseClassifier
from src.evaluation.metrics import (
    calculate_metrics,
    print_classification_report,
    plot_confusion_matrix
)

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate Tomato Crop Disease Image Classifier")
    parser.add_argument("--model_path", type=str, default=str(Config.DEFAULT_MODEL_SAVE_PATH), help="Path to saved model checkpoint")
    parser.add_argument("--batch_size", type=int, default=Config.BATCH_SIZE, help="Batch size")
    parser.add_argument("--seed", type=int, default=Config.SEED, help="Random seed for reproducibility")
    parser.add_argument("--plot_path", type=str, default=str(Config.MODELS_DIR / "confusion_matrix.png"), help="Path to save confusion matrix plot")
    return parser.parse_args()

def main():
    args = parse_args()
    set_seed(args.seed)
    
    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Saved model checkpoint not found at: {model_path}. Please run train.py first.")
        
    print(f"[INFO] Loading model checkpoint from: {model_path}")
    checkpoint = torch.load(model_path, map_location="cpu")
    
    model_name = checkpoint.get("model_name", Config.DEFAULT_MODEL_NAME)
    class_names = checkpoint.get("class_names", Config.TARGET_CLASSES)
    
    model = TomatoDiseaseClassifier(num_classes=len(class_names), model_name=model_name, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    
    _, _, test_loader = get_dataloaders(batch_size=args.batch_size, seed=args.seed)
    
    y_true = []
    y_pred = []
    
    print(f"[INFO] Running inference on test split ({len(test_loader.dataset)} samples)...")
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            
            y_true.extend(labels.cpu().numpy().tolist())
            y_pred.extend(preds.cpu().numpy().tolist())
            
    # Calculate metrics
    metrics = calculate_metrics(y_true, y_pred, class_names=class_names)
    
    print_classification_report(y_true, y_pred, class_names=class_names)
    
    print(f"Overall Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"Macro Precision:   {metrics['precision_macro']:.4f}")
    print(f"Macro Recall:      {metrics['recall_macro']:.4f}")
    print(f"Macro F1-Score:    {metrics['f1_macro']:.4f}")
    print("\nPer-Class Performance Breakdown:")
    print(metrics['per_class'].to_string(index=False))
    
    plot_confusion_matrix(metrics['confusion_matrix'], class_names=class_names, save_path=Path(args.plot_path))

if __name__ == "__main__":
    main()
