"""
FastAPI router for billing, subscriptions, and quota management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_optional_project, AuthenticatedContext
from app.models.project import Project, AccessTier
from app.services.billing import BillingService

router = APIRouter()


class CheckoutRequest(BaseModel):
    project_id: Optional[str] = Field(None, description="Project ID to upgrade (defaults to authenticated project)")
    tier: str = Field(..., description="Target tier: BUILDER or PROTOCOL")
    success_url: Optional[str] = Field(None, description="Redirect URL upon successful payment")
    cancel_url: Optional[str] = Field(None, description="Redirect URL if payment is cancelled")


@router.get("/plans", summary="List Subscription Tiers")
async def list_plans() -> Dict[str, Any]:
    """Returns available subscription tiers, monthly prices, and quota limits."""
    return BillingService.get_tier_plans()


@router.post("/checkout", summary="Create Stripe Checkout Session")
async def create_checkout(
    req: CheckoutRequest,
    auth_ctx: Optional[AuthenticatedContext] = Depends(get_optional_project),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generates a Stripe checkout session URL for upgrading the project's subscription."""
    project_id = req.project_id or (auth_ctx.project.id if auth_ctx else None)
    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="Project ID must be provided either via bearer API key or in the request body."
        )

    try:
        tier_enum = AccessTier(req.tier.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{req.tier}'. Allowed options: BUILDER, PROTOCOL"
        )

    try:
        session_info = await BillingService.create_checkout_session(
            project_id=project_id,
            target_tier=tier_enum,
            success_url=req.success_url,
            cancel_url=req.cancel_url
        )
        return session_info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook", summary="Stripe Webhook Receiver")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Receives and verifies Stripe webhook events to automatically update project tier quotas.
    """
    payload = await request.body()
    try:
        result = await BillingService.process_webhook(payload, stripe_signature, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usage", summary="Check Quota and Usage")
async def get_usage(
    project_id: Optional[str] = Query(None),
    auth_ctx: Optional[AuthenticatedContext] = Depends(get_optional_project),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Returns the current month's usage stats, limits, and percentage used for the project."""
    target_project_id = project_id or (auth_ctx.project.id if auth_ctx else None)
    if not target_project_id:
        raise HTTPException(
            status_code=400,
            detail="Project ID must be specified via API key or 'project_id' query parameter."
        )

    return await BillingService.get_project_usage(target_project_id, db)
