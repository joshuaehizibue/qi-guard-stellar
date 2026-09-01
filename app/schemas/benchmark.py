"""
Pydantic schemas for Quantum Benchmark API.
"""

from typing import Dict, Any
from pydantic import BaseModel


class QuantumConfig(BaseModel):
    n_qubits: int
    circuit_depth: int
    gate_set: list[str]


class ModelMetric(BaseModel):
    precision: float
    recall: float
    f1_score: float
    latency_ms: float


class DeltaMetric(BaseModel):
    f1_improvement: float
    latency_cost_ms: float
    quantum_contribution_positive: bool


class MetricsGroup(BaseModel):
    classical: ModelMetric
    hybrid: ModelMetric
    delta: DeltaMetric


class QuantumBenchmarkResponse(BaseModel):
    job_id: str
    model_version: str
    quantum_config: QuantumConfig
    metrics: MetricsGroup
