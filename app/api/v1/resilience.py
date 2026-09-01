"""
Quantum Resilience API endpoint connected to live PQC Surface Scanner.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from app.core.database import get_db
from app.core.auth import get_current_project, AuthenticatedContext
from app.schemas import (
    QuantumResilienceResponse,
    FindingResilience,
    ReadinessChecklist,
)
from app.services.horizon import horizon_client
from app.services.resilience_engine import resilience_engine

router = APIRouter()


@router.get(
    "/{target}",
    response_model=QuantumResilienceResponse,
    summary="Get Quantum Resilience Score",
    description="Scores a Stellar account or Soroban contract against post-quantum cryptographic migration standards."
)
async def get_quantum_resilience(
    target: str,
    auth: AuthenticatedContext = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
):
    if not (target.startswith("G") or target.startswith("C")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target address must be a valid Stellar account (G...) or contract (C...)"
        )

    # Fetch account information from Horizon
    account_info = {}
    if target.startswith("G"):
        account_info = await horizon_client.get_account_info(target)

    # Run Quantum Resilience Engine evaluation
    score, status_str, findings_raw, checklist_raw = resilience_engine.evaluate_target(target, account_info)

    findings = [
        FindingResilience(
            type=f["type"],
            severity=f["severity"],
            detail=f["detail"],
            mitigation=f["mitigation"]
        )
        for f in findings_raw
    ]

    return QuantumResilienceResponse(
        target=target,
        quantum_exposure_score=score,
        migration_status=status_str,
        findings=findings,
        readiness_checklist=ReadinessChecklist(**checklist_raw),
        timestamp=datetime.datetime.utcnow().isoformat() + "Z"
    )
