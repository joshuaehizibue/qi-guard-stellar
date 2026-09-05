# QI-Guard Soroban Security Dataset

> **Dedicated Machine Learning Dataset & Feature Extraction Pipeline**  
> Grounded in real-world Soroban vulnerability audit findings and compiled contracts from the [Soroban Security Portal](https://github.com/Inferara/soroban-security-portal).

---

## Directory Layout

```
dataset/
├── raw/                         # Raw cached audit markdown and downloaded WASM fixtures
│   ├── trustless_work_-_runtime_verification.md
│   └── fixtures/                # Real compiled Soroban WASM binaries (.wasm)
├── parsed/                      # Structured JSON vulnerability taxonomy & code snippets
│   └── vulnerabilities.json
├── features/                    # Ready-to-train normalized feature tensors
│   ├── train_features.json      # 80% Training set (8-dim base & 16-dim extended)
│   ├── val_features.json        # 20% Validation set
│   └── metadata.json            # Dataset versioning, category maps & dimensions
├── transforms/                  # Transformation scripts
│   ├── extract_audit_taxonomy.py  # Ingests markdown audits into structured records
│   ├── generate_feature_matrix.py # Computes 8D/16D tensors from bytecode + findings
│   └── build_dataset.py           # Master CLI runner
├── DATASET_CATALOG.md           # Full catalog with finding details, tables, and dimensions
└── README.md
```

---

## Running the Transformation Pipeline

To re-run all transformations from scratch:

```bash
python3 dataset/transforms/build_dataset.py
```

This single command will:
1. Ingest raw audit reports and download compiled Soroban contract fixtures.
2. Parse findings, extract code snippets, severities, and Git commit pairs.
3. Compute 8D and 16D feature vectors matching QI-Guard's model architecture.
4. Export balanced `train_features.json` and `val_features.json` splits.
5. Re-generate `DATASET_CATALOG.md`.

---

## Loading into PyTorch or PennyLane

```python
import json
import torch

with open("dataset/features/train_features.json") as f:
    train_samples = json.load(f)

# 8-dimensional base vectors for PyTorch MLP and PennyLane 8-qubit circuit
X = torch.tensor([s["features_8d"] for s in train_samples], dtype=torch.float32)
y = torch.tensor([s["is_vulnerable"] for s in train_samples], dtype=torch.float32)

print(f"Features: {X.shape}, Labels: {y.shape}")
```
