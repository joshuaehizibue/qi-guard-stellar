"""
FastAPI router for Soroban design partner onboarding and telemetry.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.telemetry import TelemetryService

router = APIRouter()


class PartnerOnboardRequest(BaseModel):
    organization_name: str = Field(..., example="Soroswap Labs")
    contact_email: str = Field(..., example="security@soroswap.org")
    protocol_category: str = Field("DEFI", example="DEFI")


class PartnerFeedbackRequest(BaseModel):
    finding_id: str = Field(..., example="QIG-SCF-0041")
    project_id: str = Field(..., example="prj_123")
    is_true_positive: bool = Field(..., example=True)
    notes: Optional[str] = Field(None, example="Confirmed missing require_auth() on transfer_admin")


@router.post("/onboard", summary="Onboard Design Partner")
async def onboard_partner(
    req: PartnerOnboardRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Provisions a Soroban design partner team with complimentary Protocol tier access.
    """
    try:
        partner_info = await TelemetryService.onboard_partner(
            organization_name=req.organization_name,
            contact_email=req.contact_email,
            protocol_category=req.protocol_category,
            db=db
        )
        return partner_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", summary="Submit Finding Verification Feedback")
async def submit_feedback(req: PartnerFeedbackRequest) -> Dict[str, Any]:
    """Records real-world developer validation of detected vulnerability findings."""
    return TelemetryService.record_feedback(
        finding_id=req.finding_id,
        project_id=req.project_id,
        is_true_positive=req.is_true_positive,
        notes=req.notes
    )


@router.get("/telemetry", summary="Get Ecosystem Partner Telemetry")
async def get_telemetry() -> Dict[str, Any]:
    """Returns aggregated audit throughput and precision metrics across beta partner protocols."""
    return TelemetryService.get_aggregated_telemetry()
