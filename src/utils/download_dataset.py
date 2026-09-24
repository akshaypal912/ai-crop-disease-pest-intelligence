import os
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from src.utils.config import Config
from src.utils.seed import set_seed

def create_sample_dataset(output_dir: Path = Config.RAW_DATA_DIR, num_images_per_class: int = 40):
    """
    Generates synthetic sample leaf image dataset for testing and offline execution.
    Each image will simulate leaf structures with visual pattern variations corresponding to class types.
    """
    set_seed(Config.SEED)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    classes_info = {
        "Tomato___healthy": {"bg": (34, 139, 34), "spots": None},          # Forest Green
        "Tomato___Early_blight": {"bg": (107, 142, 35), "spots": (139, 69, 19)}, # Olive Green + Concentric Brown spots
        "Tomato___Late_blight": {"bg": (85, 107, 47), "spots": (47, 79, 79)},   # Dark Green + Dark Water-soaked lesions
        "Tomato___Leaf_mold": {"bg": (154, 205, 50), "spots": (218, 165, 32)}   # Yellowish Green + Pale Velvet spots
    }
    
    print(f"[INFO] Generating sample dataset in: {output_dir}")
    for class_name, info in classes_info.items():
        class_folder = output_dir / class_name
        class_folder.mkdir(parents=True, exist_ok=True)
        
        for i in range(num_images_per_class):
            # Base green canvas with slight noise
            img = Image.new("RGB", (256, 256), color=info["bg"])
            draw = ImageDraw.Draw(img)
            
            # Draw leaf vein outlines
            draw.line([(128, 250), (128, 10)], fill=(20, 80, 20), width=4)
            draw.line([(128, 180), (50, 100)], fill=(20, 80, 20), width=2)
            draw.line([(128, 180), (200, 100)], fill=(20, 80, 20), width=2)
            draw.line([(128, 100), (30, 40)], fill=(20, 80, 20), width=2)
            draw.line([(128, 100), (220, 40)], fill=(20, 80, 20), width=2)
            
            # If disease class, draw representative spots/lesions
            if info["spots"] is not None:
                np.random.seed(Config.SEED + i)
                num_spots = np.random.randint(5, 15)
                for _ in range(num_spots):
                    cx, cy = np.random.randint(30, 220), np.random.randint(30, 220)
                    r = np.random.randint(8, 25)
                    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=info["spots"], outline=(50, 25, 0))
            
            img_path = class_folder / f"sample_{class_name}_{i:03d}.jpg"
            img.save(img_path)
            
    print(f"[INFO] Successfully created {num_images_per_class * len(classes_info)} sample images across 4 target tomato classes.")

if __name__ == "__main__":
    Config.ensure_directories()
    create_sample_dataset()
