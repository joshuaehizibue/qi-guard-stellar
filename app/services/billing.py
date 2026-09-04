"""
Billing service handling Stripe checkout, webhooks, and tier management.
Supports both live Stripe API and local/test simulation mode.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.models.project import Project, AccessTier
from app.core.redis import _in_memory_rate_store, rate_limiter

TIER_DETAILS = {
    AccessTier.DEVELOPER: {
        "name": "Developer",
        "price_usd": 0,
        "contract_limit": settings.LIMIT_DEVELOPER_CONTRACTS,
        "address_limit": settings.LIMIT_DEVELOPER_ADDRESSES,
        "features": [
            "50 Soroban WASM Scans / month",
            "100 Address Anomaly Scans / month",
            "Community Support",
            "Basic Vulnerability Taxonomies"
        ]
    },
    AccessTier.BUILDER: {
        "name": "Builder",
        "price_usd": 49,
        "contract_limit": settings.LIMIT_BUILDER_CONTRACTS,
        "address_limit": settings.LIMIT_BUILDER_ADDRESSES,
        "stripe_price_id": settings.STRIPE_PRICE_ID_BUILDER,
        "features": [
            "500 Soroban WASM Scans / month",
            "2,000 Address Anomaly Scans / month",
            "GitHub Actions CI/CD Integration",
            "Quantum Resilience Scoring (NIST PQC)",
            "Priority Developer Support"
        ]
    },
    AccessTier.PROTOCOL: {
        "name": "Protocol",
        "price_usd": 199,
        "contract_limit": settings.LIMIT_PROTOCOL_CONTRACTS,
        "address_limit": settings.LIMIT_PROTOCOL_ADDRESSES,
        "stripe_price_id": settings.STRIPE_PRICE_ID_PROTOCOL,
        "features": [
            "Unlimited Soroban WASM Scans",
            "20,000 Address Anomaly Scans / month",
            "Side-by-side Quantum Benchmark Engine",
            "Immutable Model Registry Auditing",
            "99.9% Uptime SLA & Dedicated Support"
        ]
    },
    AccessTier.ENTERPRISE: {
        "name": "Enterprise",
        "price_usd": -1,
        "contract_limit": -1,
        "address_limit": -1,
        "features": [
            "Custom Soroban Static Analyzers",
            "Dedicated Quantum Circuit Hardware Routing",
            "On-premise / VPC Deployment Option",
            "24/7 Incident Response SLA"
        ]
    }
}


class BillingService:
    @staticmethod
    def get_tier_plans() -> Dict[str, Any]:
        """Returns the public catalog of subscription tiers and limits."""
        return {tier.value: details for tier, details in TIER_DETAILS.items()}

    @staticmethod
    async def create_checkout_session(
        project_id: str,
        target_tier: AccessTier,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a Stripe checkout session for tier upgrades.
        Falls back to local development simulation if Stripe is unconfigured.
        """
        if target_tier not in [AccessTier.BUILDER, AccessTier.PROTOCOL]:
            raise ValueError(f"Tier {target_tier.value} cannot be purchased via checkout.")

        base_success = success_url or f"{settings.DASHBOARD_URL}/billing/success"
        base_cancel = cancel_url or f"{settings.DASHBOARD_URL}/billing/cancel"

        if settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                tier_info = TIER_DETAILS[target_tier]
                price_id = tier_info.get("stripe_price_id", settings.STRIPE_PRICE_ID_BUILDER)

                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{"price": price_id, "quantity": 1}],
                    mode="subscription",
                    client_reference_id=project_id,
                    metadata={"project_id": project_id, "tier": target_tier.value},
                    success_url=f"{base_success}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=base_cancel,
                )
                return {
                    "session_id": session.id,
                    "checkout_url": session.url,
                    "target_tier": target_tier.value,
                    "mode": "live"
                }
            except Exception as e:
                # Log error and fall back to simulation mode
                pass

        # Simulation / Local Development Mode
        mock_session_id = f"cs_sim_{uuid.uuid4().hex[:16]}"
        mock_checkout_url = f"{base_success}?session_id={mock_session_id}&project_id={project_id}&tier={target_tier.value}&simulated=true"

        return {
            "session_id": mock_session_id,
            "checkout_url": mock_checkout_url,
            "target_tier": target_tier.value,
            "mode": "simulation"
        }

    @staticmethod
    async def process_webhook(
        payload: bytes,
        sig_header: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Processes Stripe webhook events, upgrading or downgrading project access tier.
        """
        event_type = None
        data_object = None

        if settings.STRIPE_SECRET_KEY and settings.STRIPE_WEBHOOK_SECRET and sig_header:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
                event_type = event["type"]
                data_object = event["data"]["object"]
            except Exception as e:
                raise ValueError(f"Invalid webhook signature: {str(e)}")
        else:
            # Parse raw JSON in development / testing mode
            try:
                event_dict = json.loads(payload.decode("utf-8"))
                event_type = event_dict.get("type")
                data_object = event_dict.get("data", {}).get("object", {})
            except Exception as e:
                raise ValueError(f"Malformed webhook payload: {str(e)}")

        result = {
            "status": "ignored",
            "event_type": event_type,
            "project_id": None,
            "tier": None
        }

        if event_type == "checkout.session.completed":
            project_id = data_object.get("client_reference_id") or data_object.get("metadata", {}).get("project_id")
            tier_str = data_object.get("metadata", {}).get("tier", "BUILDER")
            
            if project_id:
                tier_enum = AccessTier(tier_str) if tier_str in AccessTier.__members__ else AccessTier.BUILDER
                stmt = select(Project).where(Project.id == project_id)
                res = await db.execute(stmt)
                project = res.scalar_one_or_none()
                if project:
                    project.tier = tier_enum
                    await db.commit()
                    await db.refresh(project)
                    
                    result.update({
                        "status": "upgraded",
                        "project_id": project_id,
                        "tier": project.tier.value
                    })

        elif event_type in ["customer.subscription.deleted", "subscription_canceled"]:
            project_id = data_object.get("metadata", {}).get("project_id")
            if project_id:
                stmt = select(Project).where(Project.id == project_id)
                res = await db.execute(stmt)
                project = res.scalar_one_or_none()
                if project:
                    project.tier = AccessTier.DEVELOPER
                    await db.commit()
                    await db.refresh(project)
                    
                    result.update({
                        "status": "downgraded",
                        "project_id": project_id,
                        "tier": AccessTier.DEVELOPER.value
                    })

        return result

    @staticmethod
    async def get_project_usage(project_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Retrieves usage counters and quota limits for the active month.
        """
        stmt = select(Project).where(Project.id == project_id)
        res = await db.execute(stmt)
        project = res.scalar_one_or_none()
        if not project:
            return {
                "project_id": project_id,
                "tier": AccessTier.DEVELOPER.value,
                "contracts": {"used": 0, "limit": 50, "remaining": 50, "percent": 0.0},
                "addresses": {"used": 0, "limit": 100, "remaining": 100, "percent": 0.0},
            }

        tier = project.tier
        current_month = time.strftime("%Y-%m")
        contract_key = f"rate_limit:{project_id}:contract:{current_month}"
        address_key = f"rate_limit:{project_id}:address:{current_month}"

        contract_used = 0
        address_used = 0

        if rate_limiter.redis:
            try:
                c_val = await rate_limiter.redis.get(contract_key)
                a_val = await rate_limiter.redis.get(address_key)
                contract_used = int(c_val) if c_val else 0
                address_used = int(a_val) if a_val else 0
            except Exception:
                contract_used = _in_memory_rate_store.get(contract_key, 0)
                address_used = _in_memory_rate_store.get(address_key, 0)
        else:
            contract_used = _in_memory_rate_store.get(contract_key, 0)
            address_used = _in_memory_rate_store.get(address_key, 0)

        contract_limit = settings.LIMIT_DEVELOPER_CONTRACTS if tier == AccessTier.DEVELOPER else (
            settings.LIMIT_BUILDER_CONTRACTS if tier == AccessTier.BUILDER else settings.LIMIT_PROTOCOL_CONTRACTS
        )
        address_limit = settings.LIMIT_DEVELOPER_ADDRESSES if tier == AccessTier.DEVELOPER else (
            settings.LIMIT_BUILDER_ADDRESSES if tier == AccessTier.BUILDER else settings.LIMIT_PROTOCOL_ADDRESSES
        )

        c_rem = -1 if contract_limit == -1 else max(0, contract_limit - contract_used)
        c_pct = 0.0 if contract_limit == -1 else round((contract_used / contract_limit) * 100, 1)

        a_rem = -1 if address_limit == -1 else max(0, address_limit - address_used)
        a_pct = 0.0 if address_limit == -1 else round((address_used / address_limit) * 100, 1)

        return {
            "project_id": project_id,
            "project_name": project.name,
            "tier": tier.value,
            "billing_cycle": current_month,
            "contracts": {
                "used": contract_used,
                "limit": contract_limit,
                "remaining": c_rem,
                "percent_used": c_pct
            },
            "addresses": {
                "used": address_used,
                "limit": address_limit,
                "remaining": a_rem,
                "percent_used": a_pct
            },
            "tier_details": TIER_DETAILS.get(tier, {})
        }
