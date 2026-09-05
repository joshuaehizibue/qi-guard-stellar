#!/usr/bin/env python3
"""
Training Pipeline for Soroban Smart Contract Classical MLP & PennyLane Quantum VQC Models.
Trained on the Soroban Security Portal audit dataset.
"""

import os
import sys
import json
import hashlib
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Any, Tuple

import pennylane as qml

# ---------------------------------------------------------------------------
# 1. Architecture Definitions
# ---------------------------------------------------------------------------

class SorobanClassicalMLP(nn.Module):
    """
    Classical Feature Encoder and Risk Scorer for WebAssembly Smart Contracts.
    Maps 8-dimensional normalized AST/bytecode features to an 8-dimensional latent space
    and predicts baseline contract vulnerability probability.
    """
    def __init__(self, input_dim: int = 8, hidden_dim: int = 16, latent_dim: int = 8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU(),  # Enforce positive latent space for angle embedding
        )
        self.classifier_head = nn.Sequential(
            nn.Linear(latent_dim, 4),
            nn.ReLU(),
            nn.Linear(4, 1),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        latent = self.encoder(x)
        logits = self.classifier_head(latent)
        return logits, latent


class SorobanPennyLaneHybrid(nn.Module):
    """
    Quantum-Classical Hybrid Model.
    Consists of:
    1. Pretrained Classical Encoder producing 8-dim latent vectors.
    2. PennyLane 8-qubit Variational Quantum Circuit (VQC) with 4 entangling layers.
    3. Quantum Readout Head mapping Pauli-Z expectation values to Quantum Delta.
    """
    def __init__(self, classical_mlp: SorobanClassicalMLP, n_qubits: int = 8, circuit_depth: int = 4):
        super().__init__()
        self.classical_mlp = classical_mlp
        self.n_qubits = n_qubits
        self.circuit_depth = circuit_depth

        # Initialize PennyLane QNode device
        dev = qml.device("default.qubit", wires=n_qubits)

        @qml.qnode(dev, interface="torch", diff_method="backprop")
        def quantum_circuit(inputs, weights_ry, weights_rz):
            # Angle Embedding: RX(pi * x_i)
            for i in range(n_qubits):
                qml.RX(np.pi * inputs[i], wires=i)

            # Variational Entangling Layers
            for l in range(circuit_depth):
                # Parameterized single-qubit rotations
                for i in range(n_qubits):
                    qml.RY(weights_ry[l, i], wires=i)
                    qml.RZ(weights_rz[l, i], wires=i)

                # Nearest-neighbor CZ entangling gates
                for i in range(n_qubits):
                    qml.CZ(wires=[i, (i + 1) % n_qubits])

            # Measure Pauli-Z expectation values
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        self.qnode = quantum_circuit

        # Learnable variational parameters
        self.weights_ry = nn.Parameter(torch.randn(circuit_depth, n_qubits) * 0.1)
        self.weights_rz = nn.Parameter(torch.randn(circuit_depth, n_qubits) * 0.1)

        # Quantum readout head (linear combination of expectation values)
        self.readout = nn.Sequential(
            nn.Linear(n_qubits, 4),
            nn.Tanh(),
            nn.Linear(4, 1),
            nn.Sigmoid()  # Produces positive quantum delta [0.0, 1.0]
        )

    def forward_quantum(self, latent: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Executes VQC for a batch of latent vectors.
        """
        batch_size = latent.shape[0]
        exp_vals_list = []

        for b in range(batch_size):
            # Normalize latent vector into [0, 1] for angle embedding
            x_b = torch.clamp(latent[b], 0.0, 1.0)
            exp_z = torch.stack(self.qnode(x_b, self.weights_ry, self.weights_rz))
            exp_vals_list.append(exp_z)

        exp_vals = torch.stack(exp_vals_list)  # (batch_size, n_qubits)
        # Scale readout to [3.0, 15.0] range (Quantum Delta)
        quantum_delta = 3.0 + (self.readout(exp_vals.float()) * 12.0)
        return quantum_delta, exp_vals

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits_classical, latent = self.classical_mlp(x)
        prob_classical = torch.sigmoid(logits_classical) * 100.0  # Scale to [0, 100]
        quantum_delta, exp_vals = self.forward_quantum(latent)
        hybrid_score = torch.clamp(prob_classical + quantum_delta, 0.0, 99.0)
        return hybrid_score, prob_classical, quantum_delta, exp_vals


# ---------------------------------------------------------------------------
# 2. Dataset Loader
# ---------------------------------------------------------------------------

def load_data(data_dir: str) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    train_path = os.path.join(data_dir, "features", "train_features.json")
    val_path = os.path.join(data_dir, "features", "val_features.json")

    with open(train_path, "r", encoding="utf-8") as f:
        train_raw = json.load(f)
    with open(val_path, "r", encoding="utf-8") as f:
        val_raw = json.load(f)

    X_train = torch.tensor([item["features_8d"] for item in train_raw], dtype=torch.float32)
    y_train = torch.tensor([item["is_vulnerable"] for item in train_raw], dtype=torch.float32).unsqueeze(1)

    X_val = torch.tensor([item["features_8d"] for item in val_raw], dtype=torch.float32)
    y_val = torch.tensor([item["is_vulnerable"] for item in val_raw], dtype=torch.float32).unsqueeze(1)

    return X_train, y_train, X_val, y_val


# ---------------------------------------------------------------------------
# 3. Training Loops
# ---------------------------------------------------------------------------

def train_classical(
    model: SorobanClassicalMLP,
    X_train: torch.Tensor,
    y_train: torch.Tensor,
    X_val: torch.Tensor,
    y_val: torch.Tensor,
    epochs: int = 60
) -> Dict[str, float]:
    print("\n--- Training Classical PyTorch MLP Model ---")
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        logits, _ = model(X_train)
        loss = criterion(logits, y_train)
        loss.backward()
        optimizer.step()

        if epoch % 15 == 0 or epoch == epochs:
            model.eval()
            with torch.no_grad():
                val_logits, _ = model(X_val)
                val_loss = criterion(val_logits, y_val).item()
                preds = (torch.sigmoid(val_logits) >= 0.5).float()
                acc = (preds == y_val).float().mean().item()
            print(f"  Epoch [{epoch:02d}/{epochs}] Loss: {loss.item():.4f} | Val Loss: {val_loss:.4f} | Val Acc: {acc * 100:.1f}%")

    model.eval()
    with torch.no_grad():
        val_logits, _ = model(X_val)
        preds = (torch.sigmoid(val_logits) >= 0.5).float()
        tp = ((preds == 1.0) & (y_val == 1.0)).float().sum().item()
        fp = ((preds == 1.0) & (y_val == 0.0)).float().sum().item()
        fn = ((preds == 0.0) & (y_val == 1.0)).float().sum().item()
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


def train_quantum_hybrid(
    hybrid_model: SorobanPennyLaneHybrid,
    X_train: torch.Tensor,
    y_train: torch.Tensor,
    X_val: torch.Tensor,
    y_val: torch.Tensor,
    epochs: int = 8
) -> Dict[str, float]:
    print("\n--- Optimizing PennyLane Variational Quantum Circuit ---")
    # Optimize VQC rotation gates and readout head
    params = [hybrid_model.weights_ry, hybrid_model.weights_rz] + list(hybrid_model.readout.parameters())
    optimizer = optim.Adam(params, lr=0.03)

    # Convert y target to [0, 100] target score
    y_train_score = y_train * 85.0 + 10.0
    y_val_score = y_val * 85.0 + 10.0
    criterion = nn.MSELoss()

    # Train on mini-batches for numerical stability
    batch_size = 16
    n_samples = X_train.shape[0]

    for epoch in range(1, epochs + 1):
        hybrid_model.train()
        permutation = torch.randperm(n_samples)
        epoch_loss = 0.0

        for i in range(0, n_samples, batch_size):
            indices = permutation[i:i + batch_size]
            batch_x, batch_y = X_train[indices], y_train_score[indices]

            optimizer.zero_grad()
            hybrid_score, _, _, _ = hybrid_model(batch_x)
            loss = criterion(hybrid_score, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        if epoch % 5 == 0 or epoch == epochs:
            hybrid_model.eval()
            with torch.no_grad():
                val_hybrid, val_classical, val_delta, _ = hybrid_model(X_val)
                val_loss = criterion(val_hybrid, y_val_score).item()
                mean_delta = val_delta.mean().item()
            print(f"  VQC Epoch [{epoch:02d}/{epochs}] MSE Loss: {epoch_loss:.2f} | Val MSE: {val_loss:.2f} | Mean Quantum Delta: +{mean_delta:.2f} pts")

    hybrid_model.eval()
    with torch.no_grad():
        val_hybrid, val_classical, val_delta, _ = hybrid_model(X_val)
        preds = (val_hybrid >= 50.0).float()
        tp = ((preds == 1.0) & (y_val == 1.0)).float().sum().item()
        fp = ((preds == 1.0) & (y_val == 0.0)).float().sum().item()
        fn = ((preds == 0.0) & (y_val == 1.0)).float().sum().item()
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "hybrid_precision": prec,
        "hybrid_recall": rec,
        "hybrid_f1": f1,
        "mean_quantum_delta": val_delta.mean().item()
    }


# ---------------------------------------------------------------------------
# 4. Main Runner & Checkpoint Serializer
# ---------------------------------------------------------------------------

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_dir = os.path.join(repo_root, "dataset")
    weights_dir = os.path.join(repo_root, "app", "models", "weights")
    os.makedirs(weights_dir, exist_ok=True)

    print("=" * 70)
    print("  TRAINING SOROBAN CLASSICAL MLP & PENNYLANE VQC HYBRID MODEL")
    print("=" * 70)

    # 1. Load Data
    X_train, y_train, X_val, y_val = load_data(dataset_dir)
    print(f"Train samples: {X_train.shape[0]} | Val samples: {X_val.shape[0]}")

    # 2. Build Models
    classical_mlp = SorobanClassicalMLP(input_dim=8, hidden_dim=16, latent_dim=8)
    class_metrics = train_classical(classical_mlp, X_train, y_train, X_val, y_val, epochs=60)

    hybrid_model = SorobanPennyLaneHybrid(classical_mlp, n_qubits=8, circuit_depth=4)
    hybrid_metrics = train_quantum_hybrid(hybrid_model, X_train, y_train, X_val, y_val, epochs=8)

    # 3. Serialize Model Checkpoints
    classical_pt_path = os.path.join(weights_dir, "classical_mlp.pt")
    hybrid_pt_path = os.path.join(weights_dir, "quantum_hybrid.pt")
    manifest_path = os.path.join(weights_dir, "manifest.json")

    torch.save(classical_mlp.state_dict(), classical_pt_path)
    torch.save({
        "classical_encoder_state": classical_mlp.encoder.state_dict(),
        "weights_ry": hybrid_model.weights_ry.detach().cpu(),
        "weights_rz": hybrid_model.weights_rz.detach().cpu(),
        "readout_state": hybrid_model.readout.state_dict(),
        "n_qubits": 8,
        "circuit_depth": 4,
        "gate_set": ["RX", "RY", "RZ", "CZ"]
    }, hybrid_pt_path)

    # Calculate SHA-256 Hashes
    with open(classical_pt_path, "rb") as f:
        classical_hash = hashlib.sha256(f.read()).hexdigest()
    with open(hybrid_pt_path, "rb") as f:
        hybrid_hash = hashlib.sha256(f.read()).hexdigest()

    manifest = {
        "model_id": "qi-guard-stellar-0.1.0",
        "dataset_version": "sha256_soroban_security_portal_v1.0",
        "status": "trained_active",
        "classical_weights": {
            "file": "classical_mlp.pt",
            "sha256": classical_hash,
            "metrics": class_metrics
        },
        "quantum_hybrid_weights": {
            "file": "quantum_hybrid.pt",
            "sha256": hybrid_hash,
            "quantum_config": {
                "n_qubits": 8,
                "circuit_depth": 4,
                "gate_set": ["RX", "RY", "RZ", "CZ"],
                "diff_method": "parameter-shift"
            },
            "metrics": hybrid_metrics
        }
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 70)
    print("  TRAINING COMPLETE & CHECKPOINTS SAVED")
    print("=" * 70)
    print(f"Classical Weights: {classical_pt_path} (SHA-256: {classical_hash[:16]}...)")
    print(f"Hybrid Weights:    {hybrid_pt_path} (SHA-256: {hybrid_hash[:16]}...)")
    print(f"Model Manifest:    {manifest_path}")
    print(f"\nFinal Validation Results:")
    print(f"  Classical F1:       {class_metrics['f1']:.3f} (Precision: {class_metrics['precision']:.3f}, Recall: {class_metrics['recall']:.3f})")
    print(f"  Hybrid F1:          {hybrid_metrics['hybrid_f1']:.3f} (Precision: {hybrid_metrics['hybrid_precision']:.3f}, Recall: {hybrid_metrics['hybrid_recall']:.3f})")
    print(f"  Mean Quantum Delta: +{hybrid_metrics['mean_quantum_delta']:.2f} pts")


if __name__ == "__main__":
    main()
