import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from typing import Dict, Any, List
from pathlib import Path

from src.utils.config import Config

def calculate_metrics(y_true: List[int], y_pred: List[int], class_names: List[str] = Config.TARGET_CLASSES) -> Dict[str, Any]:
    """
    Calculate comprehensive evaluation metrics.
    
    Args:
        y_true (List[int]): Ground truth class indices.
        y_pred (List[int]): Predicted class indices.
        class_names (List[str]): Target class string labels.
        
    Returns:
        Dict containing accuracy, precision, recall, f1_score, confusion_matrix, and per_class metrics.
    """
    acc = accuracy_score(y_true, y_pred)
    prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
    prec_weighted = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
    rec_weighted = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    
    # Per-class metrics breakdown
    prec_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
    rec_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
    f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
    
    per_class_df = pd.DataFrame({
        "Class": class_names,
        "Precision": prec_per_class,
        "Recall": rec_per_class,
        "F1-Score": f1_per_class
    })
    
    return {
        "accuracy": acc,
        "precision_macro": prec_macro,
        "precision_weighted": prec_weighted,
        "recall_macro": rec_macro,
        "recall_weighted": rec_weighted,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "confusion_matrix": cm,
        "per_class": per_class_df
    }

def print_classification_report(y_true: List[int], y_pred: List[int], class_names: List[str] = Config.TARGET_CLASSES):
    """Prints formatted classification report to stdout."""
    print("=" * 60)
    print("           TOMATO CROP DISEASE CLASSIFICATION REPORT")
    print("=" * 60)
    report = classification_report(y_true, y_pred, target_names=class_names, zero_division=0, digits=4)
    print(report)

def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str] = Config.TARGET_CLASSES,
    save_path: Path = None,
    show: bool = False
):
    """
    Plots and saves confusion matrix heatmap.
    """
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names
    )
    plt.title("Confusion Matrix - Tomato Crop Disease Classification")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"[INFO] Saved confusion matrix plot to: {save_path}")
        
    if show:
        plt.show()
    else:
        plt.close()
