"""
Pydantic schemas for Contract Risk API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RiskScore(BaseModel):
    classical: float = Field(..., description="Base score from classical model (0-100)")
    hybrid: float = Field(..., description="Enhanced score from quantum-classical hybrid model (0-100)")
    delta: float = Field(..., description="Quantum delta score (hybrid - classical)")


class FindingDetail(BaseModel):
    id: str = Field(..., example="QIG-SCF-0041")
    type: str = Field(..., example="ACCESS_CONTROL")
    component: Optional[str] = Field(None, example="transfer_admin()")
    severity: str = Field(..., example="HIGH")
    evidence: List[str] = Field(default_factory=list)
    remediation: Optional[str] = Field(None)
    model_version: str = Field(default="qi-guard-stellar-0.1.0")
    quantum_contribution: bool = Field(default=True)


class QuantumResilienceSummary(BaseModel):
    score: int = Field(..., example=38)
    status: str = Field(..., example="NOT_READY")


class ContractAnalysisRequest(BaseModel):
    wasm_byte_code: Optional[str] = Field(None, description="Hex or base64 WASM binary string")
    contract_address: Optional[str] = Field(None, description="Stellar contract address C...")
    source_code_url: Optional[str] = Field(None, description="Optional repository URL")
    network: str = Field(default="mainnet", description="mainnet | testnet")


class ContractAnalysisResponse(BaseModel):
    job_id: str
    contract_id: Optional[str] = None
    risk_score: RiskScore
    severity: str
    confidence: float
    findings: List[FindingDetail]
    quantum_resilience: QuantumResilienceSummary
    timestamp: str
