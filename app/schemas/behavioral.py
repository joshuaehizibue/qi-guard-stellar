"""
Pydantic schemas for Behavioral Anomaly API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnomalyScore(BaseModel):
    classical: float
    hybrid: float
    delta: float


class PatternDetail(BaseModel):
    type: str
    confidence: float
    evidence: List[str]


class BehavioralAnalysisRequest(BaseModel):
    address: str = Field(..., description="Stellar G... or C... address")
    analysis_window: str = Field(default="7d", description="Lookback window: 24h | 7d | 30d")
    transactions: Optional[List[Dict[str, Any]]] = Field(default=None)


class BehavioralAnalysisResponse(BaseModel):
    job_id: str
    address: str
    analysis_window: str
    anomaly_score: AnomalyScore
    risk_level: str
    patterns: List[PatternDetail]
    related_addresses: List[str]
    model_version: str
    timestamp: str
