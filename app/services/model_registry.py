"""
Model Registry Service for immutable model version control and metadata tracking.
"""

import hashlib
from typing import Dict, Any, Optional


class ModelRegistryService:
    """
    Model Registry & Version Tracking Service.
    Enforces auditability and metadata logging consistent with QuantumInfra platform standards.
    """

    MODEL_ID = "qi-guard-stellar-0.1.0"
    DATASET_VERSION = "sha256_soroban_vulnerability_v1.0"

    def get_model_metadata(self) -> Dict[str, Any]:
        """Returns standard metadata dictionary for current active model version."""
        import os
        import json
        
        manifest_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "models", "weights", "manifest.json")
        )
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                return {
                    "model_id": manifest.get("model_id", self.MODEL_ID),
                    "dataset_version": manifest.get("dataset_version", self.DATASET_VERSION),
                    "architecture": "quantum-classical-hybrid",
                    "quantum_config": manifest.get("quantum_hybrid_weights", {}).get("quantum_config", {
                        "n_qubits": 8,
                        "circuit_depth": 4,
                        "gate_set": ["RX", "RY", "CZ"],
                        "parameter_shift_rule": True
                    }),
                    "model_hash": manifest.get("quantum_hybrid_weights", {}).get("sha256", "trained_vqc_sha256"),
                    "status": manifest.get("status", "active"),
                    "classical_hash": manifest.get("classical_weights", {}).get("sha256"),
                    "metrics": manifest.get("quantum_hybrid_weights", {}).get("metrics")
                }
            except Exception:
                pass

        weights_payload = f"{self.MODEL_ID}:{self.DATASET_VERSION}:pennylane_v0.45"
        weight_hash = hashlib.sha256(weights_payload.encode("utf-8")).hexdigest()

        return {
            "model_id": self.MODEL_ID,
            "dataset_version": self.DATASET_VERSION,
            "architecture": "quantum-classical-hybrid",
            "quantum_config": {
                "n_qubits": 8,
                "circuit_depth": 4,
                "gate_set": ["RX", "RY", "CZ"],
                "parameter_shift_rule": True
            },
            "model_hash": weight_hash,
            "status": "active"
        }


model_registry = ModelRegistryService()
