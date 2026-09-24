import random
import numpy as np
import torch
from .config import Config

def set_seed(seed: int = Config.SEED):
    """
    Set random seed across all libraries to ensure full reproducibility.
    
    Args:
        seed (int): The random seed integer. Default is from Config.SEED (42).
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    # Ensure deterministic CUDNN behavior if running on GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    print(f"[INFO] Random seed set to: {seed}")
