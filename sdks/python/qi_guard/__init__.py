"""
QI-Guard Python SDK — Quantum Smart Contract Security for Stellar/Soroban.
"""

from qi_guard.client import QIGuardClient, AsyncQIGuardClient
from qi_guard.models import (
    RiskScore,
    Finding,
    QuantumResilienceScore,
    ContractRiskReport,
    BehavioralAnomalyScore,
    BehavioralAnalysisReport,
    QuantumResilienceReport,
    BenchmarkMetrics,
    QuantumDeltaMetrics,
    BenchmarkReport
)
from qi_guard.exceptions import (
    QIGuardError,
    QIGuardAPIError,
    QIGuardAuthenticationError,
    QIGuardRateLimitError
)

__version__ = "0.1.0"

__all__ = [
    "QIGuardClient",
    "AsyncQIGuardClient",
    "RiskScore",
    "Finding",
    "QuantumResilienceScore",
    "ContractRiskReport",
    "BehavioralAnomalyScore",
    "BehavioralAnalysisReport",
    "QuantumResilienceReport",
    "BenchmarkMetrics",
    "QuantumDeltaMetrics",
    "BenchmarkReport",
    "QIGuardError",
    "QIGuardAPIError",
    "QIGuardAuthenticationError",
    "QIGuardRateLimitError",
]
