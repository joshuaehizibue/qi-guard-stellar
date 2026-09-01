"""
Pydantic schemas for Quantum Resilience API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class FindingResilience(BaseModel):
    type: str
    severity: str
    detail: str
    mitigation: str


class ReadinessChecklist(BaseModel):
    key_rotation_policy: bool
    pqc_compatible_library: bool
    crypto_agility: str


class QuantumResilienceResponse(BaseModel):
    target: str
    quantum_exposure_score: int
    migration_status: str
    findings: List[FindingResilience]
    readiness_checklist: ReadinessChecklist
    timestamp: str
