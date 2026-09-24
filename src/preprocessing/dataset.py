import os
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

from src.utils.config import Config
from src.utils.seed import set_seed
from src.preprocessing.transforms import get_train_transforms, get_val_test_transforms

def is_image_valid(image_path: Path) -> bool:
    """Checks if an image file is readable and non-corrupt using PIL."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        # Verify again by loading fully (verify() closes file pointer)
        with Image.open(image_path) as img:
            img.load()
        return True
    except Exception:
        return False

def create_splits(
    data_dir: Path = Config.RAW_DATA_DIR,
    output_csv: Path = Config.SPLITS_CSV_PATH,
    seed: int = Config.SEED
) -> pd.DataFrame:
    """
    Scans image dataset directory, detects corrupt files, and creates stratified 
    Train/Val/Test splits with zero data leakage.
    
    Args:
        data_dir (Path): Input directory containing subfolders per class.
        output_csv (Path): Output CSV path to save the splits manifest.
        seed (int): Fixed random state seed.
        
    Returns:
        pd.DataFrame: Split manifest DataFrame.
    """
    set_seed(seed)
    image_paths = []
    class_names = []
    label_indices = []
    
    class_to_idx = {cls_name: i for i, cls_name in enumerate(Config.TARGET_CLASSES)}
    
    print(f"[INFO] Scanning dataset directory: {data_dir}")
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")
        
    for folder_name in os.listdir(data_dir):
        folder_path = data_dir / folder_name
        if not folder_path.is_dir():
            continue
            
        # Map raw folder name to standardized target class
        std_class_name = Config.CLASS_FOLDER_MAP.get(folder_name, folder_name)
        if std_class_name not in class_to_idx:
            print(f"[WARNING] Skipping unmapped folder: {folder_name}")
            continue
            
        label_idx = class_to_idx[std_class_name]
        
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                img_path = folder_path / file_name
                if is_image_valid(img_path):
                    image_paths.append(str(img_path.resolve()))
                    class_names.append(std_class_name)
                    label_indices.append(label_idx)
                else:
                    print(f"[WARNING] Skipping corrupt image file: {img_path}")

    if len(image_paths) == 0:
        raise ValueError(f"No valid images found under {data_dir}. Run dataset generator or download PlantVillage.")

    df = pd.DataFrame({
        "image_path": image_paths,
        "class_name": class_names,
        "label": label_indices
    })
    
    # 1st split: Train vs (Val + Test)
    train_df, temp_df = train_test_split(
        df,
        test_size=(Config.VAL_RATIO + Config.TEST_RATIO),
        stratify=df["label"],
        random_state=seed,
        shuffle=True
    )
    
    # 2nd split: Val vs Test (50/50 of temp)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        stratify=temp_df["label"],
        random_state=seed,
        shuffle=True
    )
    
    train_df = train_df.copy()
    val_df = val_df.copy()
    test_df = test_df.copy()
    
    train_df["split"] = "train"
    val_df["split"] = "val"
    test_df["split"] = "test"
    
    full_df = pd.concat([train_df, val_df, test_df], axis=0).reset_index(drop=True)
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    full_df.to_csv(output_csv, index=False)
    print(f"[INFO] Created reproducible split manifest saved to: {output_csv}")
    print(f"[INFO] Train samples: {len(train_df)} | Val samples: {len(val_df)} | Test samples: {len(test_df)}")
    
    return full_df

class CropDiseaseDataset(Dataset):
    """PyTorch Dataset for Tomato Crop Disease Images."""
    
    def __init__(self, df: pd.DataFrame, transform=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_path = row["image_path"]
        label = row["label"]
        
        image = Image.open(image_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
            
        return image, torch.tensor(label, dtype=torch.long)

def seed_worker(worker_id):
    """Seed worker initializer for PyTorch DataLoader reproducibility."""
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    import random
    random.seed(worker_seed)

def get_dataloaders(
    splits_csv: Path = Config.SPLITS_CSV_PATH,
    batch_size: int = Config.BATCH_SIZE,
    num_workers: int = Config.NUM_WORKERS,
    seed: int = Config.SEED
):
    """
    Factory function producing PyTorch DataLoaders for train, val, and test splits.
    """
    if not splits_csv.exists():
        print(f"[INFO] Splits CSV not found. Generating new split manifest...")
        df = create_splits(seed=seed)
    else:
        df = pd.read_csv(splits_csv)
        
    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "val"]
    test_df = df[df["split"] == "test"]
    
    train_dataset = CropDiseaseDataset(train_df, transform=get_train_transforms())
    val_dataset = CropDiseaseDataset(val_df, transform=get_val_test_transforms())
    test_dataset = CropDiseaseDataset(test_df, transform=get_val_test_transforms())
    
    g = torch.Generator()
    g.manual_seed(seed)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        worker_init_fn=seed_worker,
        generator=g
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        worker_init_fn=seed_worker,
        generator=g
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        worker_init_fn=seed_worker,
        generator=g
    )
    
    return train_loader, val_loader, test_loader
