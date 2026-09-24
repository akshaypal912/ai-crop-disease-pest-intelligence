import argparse
from pathlib import Path
import torch

from src.utils.config import Config
from src.utils.seed import set_seed
from src.utils.download_dataset import create_sample_dataset
from src.preprocessing.dataset import create_splits, get_dataloaders
from src.models.classifier import get_model
from src.training.trainer import Trainer

def parse_args():
    parser = argparse.ArgumentParser(description="Train Tomato Crop Disease Image Classifier")
    parser.add_argument("--data_dir", type=str, default=str(Config.RAW_DATA_DIR), help="Path to raw dataset folder")
    parser.add_argument("--epochs", type=int, default=Config.EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=Config.BATCH_SIZE, help="Batch size")
    parser.add_argument("--lr", type=float, default=Config.LEARNING_RATE, help="Learning rate")
    parser.add_argument("--model_name", type=str, default=Config.DEFAULT_MODEL_NAME, choices=["mobilenet_v2", "resnet18", "efficientnet_b0"], help="Backbone model")
    parser.add_argument("--output_model", type=str, default=str(Config.DEFAULT_MODEL_SAVE_PATH), help="Path to save model checkpoint")
    parser.add_argument("--seed", type=int, default=Config.SEED, help="Random seed for reproducibility")
    return parser.parse_args()

def main():
    args = parse_args()
    set_seed(args.seed)
    
    data_dir = Path(args.data_dir)
    if not data_dir.exists() or len(list(data_dir.glob("*/*"))) == 0:
        print(f"[INFO] Dataset not found in {data_dir}. Generating sample dataset for pipeline execution...")
        create_sample_dataset(output_dir=data_dir)
        
    print(f"[INFO] Preparing data splits...")
    create_splits(data_dir=data_dir, seed=args.seed)
    
    train_loader, val_loader, _ = get_dataloaders(batch_size=args.batch_size, seed=args.seed)
    
    print(f"[INFO] Initializing model: '{args.model_name}'...")
    model = get_model(model_name=args.model_name, num_classes=Config.NUM_CLASSES, pretrained=True)
    
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        lr=args.lr
    )
    
    trainer.train(
        epochs=args.epochs,
        save_path=Path(args.output_model)
    )

if __name__ == "__main__":
    main()
