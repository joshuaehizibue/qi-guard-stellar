"""
Unit tests for Sprint 2 Intelligence Engine modules.
"""

import pytest
from app.services.classical_engine import classical_engine
from app.services.quantum_engine import quantum_engine
from app.services.benchmark_engine import benchmark_engine
from app.services.behavioral_engine import behavioral_engine
from app.services.resilience_engine import resilience_engine
from app.services.model_registry import model_registry
from app.services.wasm_parser import wasm_disassembler


def test_classical_engine_encoding():
    parsed_wasm = {
        "byte_size": 1200,
        "function_count": 5,
        "exported_functions": ["transfer_admin", "deposit"],
        "imported_functions": ["env::require_auth"],
        "opcode_frequencies": {"loop": 2, "call": 4},
        "call_site_count": 4,
        "vulnerability_findings": [{"id": "QIG-SCF-0041", "severity": "HIGH"}]
    }
    feat_vec, latent_emb, score = classical_engine.encode_wasm_features(parsed_wasm)
    
    assert len(feat_vec) == 8
    assert len(latent_emb) == 8
    assert 10.0 <= score <= 98.0


def test_quantum_engine_hybrid_circuit():
    latent_emb = [0.2, 0.4, 0.6, 0.8, 0.1, 0.3, 0.5, 0.7]
    classical_score = 70.0
    
    hybrid_score, delta, exp_vals, q_config = quantum_engine.execute_hybrid_circuit(
        latent_emb, classical_score
    )
    
    assert hybrid_score > classical_score
    assert delta > 0
    assert len(exp_vals) == 8
    assert q_config["n_qubits"] == 8
    assert "RX" in q_config["gate_set"]


def test_benchmark_engine_computation():
    bench = benchmark_engine.compute_benchmark(71.0, 78.0, 42.0)
    
    assert bench["classical"]["f1_score"] > 0
    assert bench["hybrid"]["f1_score"] >= bench["classical"]["f1_score"]
    assert bench["delta"]["quantum_contribution_positive"] is True


def test_behavioral_engine_anomaly_scoring():
    tx_records = [{"memo": "swap", "operation_count": 8, "fee_charged": 12000}]
    c_score, h_score, delta, patterns, related = behavioral_engine.analyze_account_activity(
        "GABC123456789WXYZ", tx_records, "7d"
    )
    
    assert c_score > 0
    assert h_score >= c_score
    assert len(patterns) > 0


def test_resilience_engine_evaluation():
    account_info = {"signers": [{"type": "ed25519_public_key"}]}
    score, status, findings, checklist = resilience_engine.evaluate_target("GABC123", account_info)
    
    assert score == 61
    assert status == "PARTIALLY_READY"
    assert len(findings) > 0


def test_model_registry_metadata():
    meta = model_registry.get_model_metadata()
    
    assert meta["model_id"] == "qi-guard-stellar-0.1.0"
    assert len(meta["model_hash"]) == 64
