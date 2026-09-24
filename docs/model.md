# Model Card — Tomato Disease Classifier

> **Version**: 0.1.0  
> **Architecture**: MobileNetV2 (Transfer Learning — ImageNet)  
> **Crop**: Tomato (*Solanum lycopersicum*)

---

## Model Overview

The disease classifier is a MobileNetV2 convolutional neural network pre-trained on ImageNet and fine-tuned on a subset of the PlantVillage dataset covering four tomato leaf health classes.

The model is designed as a decision-support tool for farmers. Its output is a **probabilistic model prediction**, not a laboratory diagnosis.

---

## Supported Classes

| Class | Scientific Name | Description |
|-------|----------------|-------------|
| Healthy | *Solanum lycopersicum* | No disease detected |
| Early Blight | *Alternaria solani* | Fungal — warm/humid; target-ring lesions |
| Late Blight | *Phytophthora infestans* | Oomycete — cool/wet; rapid spread |
| Leaf Mold | *Passalora fulva* | Fungal — high humidity; velvety mold |

---

## Architecture

| Attribute | Value |
|-----------|-------|
| Base model | MobileNetV2 (ImageNet pre-trained) |
| Fine-tuning | Final classifier head replaced; full model fine-tuned |
| Input size | 224 × 224 × 3 (RGB) |
| Normalisation | ImageNet mean/std (0.485, 0.456, 0.406 / 0.229, 0.224, 0.225) |
| Output | Softmax probability over 4 classes |
| Optimiser | Adam (lr=1e-3, weight_decay=1e-4) |
| Default epochs | 10 |
| Batch size | 32 |

---

## Training Data

- **Source**: PlantVillage dataset (public, Kaggle / official release)
- **Split**: 70% train / 15% validation / 15% test (stratified, reproducible seed=42)
- **Augmentations** (train only): random horizontal flip, rotation, colour jitter
- **Preprocessing** (all splits): resize → centre crop → normalise

---

## Inference Pipeline

```
Input (bytes / file path / PIL Image)
    ↓
Validation & format checking
    ↓
Resize to 224×224, normalize
    ↓
MobileNetV2 forward pass (torch.no_grad())
    ↓
Softmax → class probabilities
    ↓
argmax → predicted_disease + confidence
```

---

## Limitations

1. **Single crop**: Trained only on tomato leaves. Do not use for other crops.
2. **Supported diseases**: Only 4 classes — out-of-distribution inputs (e.g., pest damage, nutrient deficiency) will be assigned the nearest trained class.
3. **Image quality**: Best on close-up, well-lit leaf images. Performance degrades under severe blur, extreme backgrounds, or artificial lighting.
4. **Not a diagnosis**: Model confidence is a probabilistic estimate, not a laboratory confirmation. Always verify with an agronomist before treatment.

---

## Re-training

```bash
python train.py --epochs 10 --batch_size 32
```

Checkpoint saved to `models/tomato_disease_mobilenetv2.pt`.

Evaluation:
```bash
python evaluate.py
```
