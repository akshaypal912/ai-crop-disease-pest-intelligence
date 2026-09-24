from torchvision import transforms
from src.utils.config import Config

def get_train_transforms(image_size=Config.IMAGE_SIZE):
    """
    Returns image transformation pipeline for training with data augmentation.
    
    Args:
        image_size (tuple): Target image dimensions (height, width). Default (224, 224).
    """
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=Config.NORM_MEAN, std=Config.NORM_STD)
    ])

def get_val_test_transforms(image_size=Config.IMAGE_SIZE):
    """
    Returns deterministic image transformation pipeline for validation and testing.
    
    Args:
        image_size (tuple): Target image dimensions (height, width). Default (224, 224).
    """
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=Config.NORM_MEAN, std=Config.NORM_STD)
    ])
