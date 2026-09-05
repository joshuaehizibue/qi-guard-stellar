#!/usr/bin/env python3
"""
Master Dataset Build Runner.
Executes end-to-end ingestion, parsing, feature tensor generation, and catalog creation.
"""

import os
import sys
import json
import subprocess


def generate_catalog_markdown(dataset_dir: str):
    """Generates a comprehensive Markdown documentation file describing the dataset."""
    parsed_path = os.path.join(dataset_dir, "parsed", "vulnerabilities.json")
    meta_path = os.path.join(dataset_dir, "features", "metadata.json")
    train_path = os.path.join(dataset_dir, "features", "train_features.json")
    val_path = os.path.join(dataset_dir, "features", "val_features.json")

    with open(parsed_path, "r", encoding="utf-8") as f:
        vulns = json.load(f)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open(train_path, "r", encoding="utf-8") as f:
        train_samples = json.load(f)
    with open(val_path, "r", encoding="utf-8") as f:
        val_samples = json.load(f)

    catalog_path = os.path.join(dataset_dir, "DATASET_CATALOG.md")

    content = f"""# Soroban Security Portal ML Training Dataset Catalog

**Corpus Version:** `{meta['version']}`  
**Dataset Name:** `{meta['dataset_name']}`  
**Primary Source:** [Inferara/soroban-security-portal](https://github.com/Inferara/soroban-security-portal) / [Stellar Security Portal](https://stellarsecurityportal.com)  
**Total Samples:** `{meta['sample_count']}` (`{meta['train_count']}` Train / `{meta['val_count']}` Validation)  
**Positive / Vulnerable Ratio:** `{meta['positive_ratio'] * 100:.1f}%`  
**Qubit Compatibility:** `{meta['qubit_compatibility']} Qubits` (8-dimensional base feature space)

---

## 1. Vulnerability Classes Extracted From Real Audits

| ID | Finding Title | Category | Severity | Protocol / Target | Upstream Commit References |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for v in vulns:
        commits = ", ".join(f"`{c[:7]}`" for c in v.get("commits", [])[:2]) if v.get("commits") else "`main`"
        content += f"| **{v['id']}** | {v['title'][:45]}... | `{v['category']}` | **{v['severity']}** | {v['protocol']} | {commits} |\n"

    content += """
---

## 2. Feature Vector Specifications

### A. 8-Dimensional Base Features (`features_8d`)
*Directly mapped to PyTorch classical MLP encoder and PennyLane 8-qubit variational circuit (`n_qubits = 8`).*

| Index | Feature Dimension | Normalization Formula | Description |
| :---: | :--- | :--- | :--- |
| `[0]` | Byte Size | `min(1.0, byte_size / 5000.0)` | Normalized WASM bytecode binary size |
| `[1]` | Function Count | `min(1.0, fn_count / 50.0)` | Total declared & imported function count |
| `[2]` | Export Count | `min(1.0, export_count / 10.0)` | Number of exported contract entrypoints |
| `[3]` | Import Count | `min(1.0, import_count / 10.0)` | Host functions imported from `env` (e.g. `require_auth`) |
| `[4]` | Call Count | `min(1.0, call_count / 30.0)` | Internal & external call opcode frequency |
| `[5]` | Loop Density | `min(1.0, loop_count / 10.0)` | Unbounded loop instruction density |
| `[6]` | Finding Count | `min(1.0, findings / 5.0)` | Structural heuristic security findings |
| `[7]` | High Severity Flag | `1.0 if high else 0.0` | Binary indicator for critical authorization flaws |

### B. 16-Dimensional Extended Security Features (`features_16d`)
*Includes domain-specific Soroban contract semantics:*
- `[8]` Category ID normalized (`category_id / 10.0`)
- `[9]` Has authorization import check (`require_auth`)
- `[10]` Has signed `i128` without bound validations
- `[11]` State mutation indicator
- `[12]` Dynamic fee calculation logic (BPS overflow risk)
- `[13]` Unbounded loop / recursion indicator
- `[14]` Ground truth vulnerability label (`1.0` or `0.0`)
- `[15]` Structural complexity score

---

## 3. Data Split & File Layout

- **[`dataset/parsed/vulnerabilities.json`](parsed/vulnerabilities.json)**: Raw JSON structured audit records with code snippets and remediation instructions.
- **[`dataset/features/train_features.json`](features/train_features.json)**: 80% split for training classical PyTorch classifiers and optimizing PennyLane VQC parameters.
- **[`dataset/features/val_features.json`](features/val_features.json)**: 20% held-out test split for evaluating generalized precision, recall, and quantum delta.
- **[`dataset/features/metadata.json`](features/metadata.json)**: Hyperparameter and tensor configuration metadata.

---

## 4. How to Load and Train in Python

```python
import json
import torch

# Load training data
with open("dataset/features/train_features.json") as f:
    train_data = json.load(f)

# Extract 8-dim base features and binary labels
X_train = torch.tensor([item["features_8d"] for item in train_data], dtype=torch.float32)
y_train = torch.tensor([item["is_vulnerable"] for item in train_data], dtype=torch.float32).unsqueeze(1)

print(f"X_train shape: {X_train.shape}")  # (N, 8)
print(f"y_train shape: {y_train.shape}")  # (N, 1)

# Ready to pass to PyTorch MLP or PennyLane angle_embedding!
```
"""
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Done] Dataset Catalog generated at:\n  {catalog_path}")


def main():
    transforms_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.abspath(os.path.join(transforms_dir, ".."))

    print("=" * 70)
    print("  QI-GUARD DATASET PIPELINE: INFERARA SOROBAN SECURITY PORTAL")
    print("=" * 70)

    # Step 1: Extract taxonomy
    print("\n>>> Step 1: Extracting audit taxonomy & vulnerability records...")
    subprocess.run([sys.executable, os.path.join(transforms_dir, "extract_audit_taxonomy.py")], check=True)

    # Step 2: Generate feature matrix
    print("\n>>> Step 2: Generating feature matrices & fixtures...")
    subprocess.run([sys.executable, os.path.join(transforms_dir, "generate_feature_matrix.py")], check=True)

    # Step 3: Generate Catalog
    print("\n>>> Step 3: Generating Markdown documentation catalog...")
    generate_catalog_markdown(dataset_dir)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE: All datasets and features generated successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
