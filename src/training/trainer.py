import time
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple

from src.utils.config import Config
from src.utils.seed import set_seed
from src.models.classifier import TomatoDiseaseClassifier

class Trainer:
    """
    Modular Trainer for Tomato Crop Disease Image Classification models.
    Handles device placement, optimization, learning rate decay, loss tracking,
    validation scoring, and model checkpointing.
    """
    
    def __init__(
        self,
        model: TomatoDiseaseClassifier,
        train_loader: DataLoader,
        val_loader: DataLoader,
        lr: float = Config.LEARNING_RATE,
        weight_decay: float = Config.WEIGHT_DECAY,
        device: str = None
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.model.to(self.device)
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="min", factor=0.5, patience=2
        )
        
        self.history: Dict[str, List[float]] = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }

    def train_epoch(self) -> Tuple[float, float]:
        """Runs a single training epoch."""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in self.train_loader:
            images, labels = images.to(self.device), labels.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data).item()
            total += labels.size(0)
            
        epoch_loss = running_loss / total if total > 0 else 0.0
        epoch_acc = correct / total if total > 0 else 0.0
        return epoch_loss, epoch_acc

    def validate_epoch(self) -> Tuple[float, float]:
        """Runs a single validation epoch."""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in self.val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                running_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct += torch.sum(preds == labels.data).item()
                total += labels.size(0)
                
        epoch_loss = running_loss / total if total > 0 else 0.0
        epoch_acc = correct / total if total > 0 else 0.0
        return epoch_loss, epoch_acc

    def train(
        self,
        epochs: int = Config.EPOCHS,
        save_path: Path = Config.DEFAULT_MODEL_SAVE_PATH,
        patience: int = 5
    ) -> Dict[str, List[float]]:
        """
        Executes full training pipeline with checkpoint saving and early stopping.
        
        Args:
            epochs (int): Max number of epochs.
            save_path (Path): Path to save best model weights.
            patience (int): Early stopping patience epochs.
        """
        print(f"[INFO] Starting model training on device: '{self.device}'")
        best_val_loss = float("inf")
        patience_counter = 0
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        
        for epoch in range(1, epochs + 1):
            train_loss, train_acc = self.train_epoch()
            val_loss, val_acc = self.validate_epoch()
            
            self.history["train_loss"].append(train_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_loss"].append(val_loss)
            self.history["val_acc"].append(val_acc)
            
            self.scheduler.step(val_loss)
            current_lr = self.optimizer.param_groups[0]['lr']
            
            print(
                f"Epoch {epoch:02d}/{epochs:02d} | "
                f"Train Loss: {train_loss:.4f} - Train Acc: {train_acc*100:.2f}% | "
                f"Val Loss: {val_loss:.4f} - Val Acc: {val_acc*100:.2f}% | "
                f"LR: {current_lr:.6f}"
            )
            
            # Checkpoint best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                checkpoint = {
                    "epoch": epoch,
                    "model_state_dict": self.model.state_dict(),
                    "optimizer_state_dict": self.optimizer.state_dict(),
                    "val_loss": val_loss,
                    "val_acc": val_acc,
                    "model_name": self.model.model_name,
                    "class_names": self.model.class_names
                }
                torch.save(checkpoint, save_path)
                print(f"  [+] Saved best model checkpoint to {save_path}")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"[INFO] Early stopping triggered after {epoch} epochs.")
                    break
                    
        elapsed = time.time() - start_time
        print(f"[INFO] Training finished in {elapsed:.2f} seconds. Best Val Loss: {best_val_loss:.4f}")
        return self.history
