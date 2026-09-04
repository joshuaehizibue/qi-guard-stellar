"""
Typed data models for QI-Guard Python SDK.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskScore(BaseModel):
    classical: float
    hybrid: float
    delta: float


class Finding(BaseModel):
    id: str
    type: str
    component: Optional[str] = None
    severity: str
    evidence: List[str] = Field(default_factory=list)
    remediation: Optional[str] = None
    model_version: Optional[str] = None
    quantum_contribution: bool = False


class QuantumResilienceScore(BaseModel):
    score: float
    status: str



class ContractRiskReport(BaseModel):
    job_id: str
    contract_id: Optional[str] = None
    risk_score: RiskScore
    severity: str
    confidence: float
    findings: List[Finding] = Field(default_factory=list)
    quantum_resilience: QuantumResilienceScore
    timestamp: str


class BehavioralAnomalyScore(BaseModel):
    classical: float
    hybrid: float
    delta: float


class BehavioralAnalysisReport(BaseModel):
    job_id: str
    address: str
    analysis_window: str
    anomaly_score: BehavioralAnomalyScore
    risk_level: str
    flags: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str


class FindingResilience(BaseModel):
    type: str
    severity: str
    detail: str
    mitigation: str


class ReadinessChecklist(BaseModel):
    key_rotation_policy: bool
    pqc_compatible_library: bool
    crypto_agility: str


class QuantumResilienceReport(BaseModel):
    target: str
    quantum_exposure_score: int
    migration_status: str
    findings: List[FindingResilience] = Field(default_factory=list)
    readiness_checklist: Optional[ReadinessChecklist] = None
    timestamp: str

    @property
    def resilience_score(self) -> int:
        return 100 - self.quantum_exposure_score

    @property
    def status(self) -> str:
        return self.migration_status



class BenchmarkMetrics(BaseModel):
    precision: float
    recall: float
    f1: float
    latency_ms: float


class QuantumDeltaMetrics(BaseModel):
    f1_improvement: float
    latency_delta_ms: float
    quantum_advantage_observed: bool


class BenchmarkReport(BaseModel):
    job_id: str
    contract_id: Optional[str] = None
    classical: BenchmarkMetrics
    hybrid: BenchmarkMetrics
    quantum_delta: QuantumDeltaMetrics
