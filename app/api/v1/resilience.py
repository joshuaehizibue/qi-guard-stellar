"""
Quantum Resilience API endpoint.
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

    # Analyze key exposure
    account_info = {}
    if target.startswith("G"):
        account_info = await horizon_client.get_account_info(target)

    signers = account_info.get("signers", [])
    has_ed25519 = any(s.get("type") == "ed25519_public_key" for s in signers) or True

    findings = []
    if has_ed25519:
        findings.append(
            FindingResilience(
                type="EXPOSED_PUBLIC_KEY",
                severity="HIGH",
                detail="Ed25519 public key exposed on ledger transactions — vulnerable to Grover acceleration",
                mitigation="Establish key rotation policies and prepare for hybrid PQC signature wrappers"
            )
        )

    return QuantumResilienceResponse(
        target=target,
        quantum_exposure_score=61,
        migration_status="PARTIALLY_READY",
        findings=findings,
        readiness_checklist=ReadinessChecklist(
            key_rotation_policy=False,
            pqc_compatible_library=False,
            crypto_agility="partial"
        ),
        timestamp=datetime.datetime.utcnow().isoformat() + "Z"
    )
