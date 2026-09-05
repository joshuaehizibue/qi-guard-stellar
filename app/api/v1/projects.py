"""
FastAPI router for Project Management and API Key Lifecycle.
Enables self-serve project registration, tier assignment, and API key provisioning.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import datetime

from app.core.database import get_db
from app.core.auth import get_current_project, AuthenticatedContext
from app.core.security import generate_api_key, hash_api_key
from app.models.project import Project, AccessTier
from app.models.api_key import APIKey, KeyType

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CreateProjectRequest(BaseModel):
    name: str = Field(..., example="Soroswap Protocol")
    tier: Optional[str] = Field("DEVELOPER", example="DEVELOPER", description="Tier: DEVELOPER, BUILDER, or PROTOCOL")
    contact_email: Optional[str] = Field(None, example="security@soroswap.org")


class APIKeyResponse(BaseModel):
    id: str
    key_prefix: str
    key_type: str
    name: Optional[str]
    is_active: bool
    created_at: str
    raw_key: Optional[str] = None  # Only returned upon generation


class ProjectResponse(BaseModel):
    id: str
    name: str
    tier: str
    created_at: str
    api_keys: List[APIKeyResponse] = []


class CreateKeyRequest(BaseModel):
    key_type: str = Field("live", example="live", description="Type: live, test, or ci")
    name: Optional[str] = Field("Default Key", example="CI/CD Pipeline Key")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a New Project",
    description="Creates a new project and automatically generates its initial live and test API keys."
)
async def create_project(
    req: CreateProjectRequest,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    try:
        tier_enum = AccessTier(req.tier.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier '{req.tier}'. Allowed options: DEVELOPER, BUILDER, PROTOCOL"
        )

    # 1. Create Project
    project = Project(
        id=str(uuid.uuid4()),
        name=req.name,
        tier=tier_enum
    )
    db.add(project)
    await db.flush()

    # 2. Generate Initial Live Key
    raw_live, prefix_live, hash_live = generate_api_key("live")
    live_key = APIKey(
        id=str(uuid.uuid4()),
        project_id=project.id,
        key_prefix=prefix_live,
        hashed_key=hash_live,
        key_type=KeyType.LIVE,
        name="Default Live Key",
        is_active=True
    )
    db.add(live_key)

    # 3. Generate Initial Test Key
    raw_test, prefix_test, hash_test = generate_api_key("test")
    test_key = APIKey(
        id=str(uuid.uuid4()),
        project_id=project.id,
        key_prefix=prefix_test,
        hashed_key=hash_test,
        key_type=KeyType.TEST,
        name="Default Test Key",
        is_active=True
    )
    db.add(test_key)

    await db.commit()

    return ProjectResponse(
        id=project.id,
        name=project.name,
        tier=project.tier.value,
        created_at=project.created_at.isoformat() if hasattr(project.created_at, "isoformat") else str(project.created_at),
        api_keys=[
            APIKeyResponse(
                id=live_key.id,
                key_prefix=live_key.key_prefix,
                key_type=live_key.key_type.value,
                name=live_key.name,
                is_active=live_key.is_active,
                created_at=live_key.created_at.isoformat() if hasattr(live_key.created_at, "isoformat") else str(live_key.created_at),
                raw_key=raw_live
            ),
            APIKeyResponse(
                id=test_key.id,
                key_prefix=test_key.key_prefix,
                key_type=test_key.key_type.value,
                name=test_key.name,
                is_active=test_key.is_active,
                created_at=test_key.created_at.isoformat() if hasattr(test_key.created_at, "isoformat") else str(test_key.created_at),
                raw_key=raw_test
            ),
        ]
    )


@router.get(
    "/me",
    response_model=ProjectResponse,
    summary="Get Authenticated Project Profile",
    description="Returns the currently authenticated project details and active API key metadata."
)
async def get_my_project(
    auth: AuthenticatedContext = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    result = await db.execute(
        select(APIKey).where(APIKey.project_id == auth.project.id)
    )
    keys = result.scalars().all()

    return ProjectResponse(
        id=auth.project.id,
        name=auth.project.name,
        tier=auth.project.tier.value,
        created_at=auth.project.created_at.isoformat() if hasattr(auth.project.created_at, "isoformat") else str(auth.project.created_at),
        api_keys=[
            APIKeyResponse(
                id=k.id,
                key_prefix=k.key_prefix,
                key_type=k.key_type.value,
                name=k.name,
                is_active=k.is_active,
                created_at=k.created_at.isoformat() if hasattr(k.created_at, "isoformat") else str(k.created_at),
                raw_key=None  # Masked for security
            )
            for k in keys
        ]
    )


@router.post(
    "/keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Additional API Key",
    description="Generates a new API key for the authenticated project."
)
async def create_api_key(
    req: CreateKeyRequest,
    auth: AuthenticatedContext = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
) -> APIKeyResponse:
    raw_key, prefix, key_hash = generate_api_key(req.key_type)

    new_key = APIKey(
        id=str(uuid.uuid4()),
        project_id=auth.project.id,
        key_prefix=prefix,
        hashed_key=key_hash,
        key_type=KeyType(req.key_type.lower()),
        name=req.name,
        is_active=True
    )
    db.add(new_key)
    await db.commit()

    return APIKeyResponse(
        id=new_key.id,
        key_prefix=new_key.key_prefix,
        key_type=new_key.key_type.value,
        name=new_key.name,
        is_active=new_key.is_active,
        created_at=new_key.created_at.isoformat() if hasattr(new_key.created_at, "isoformat") else str(new_key.created_at),
        raw_key=raw_key
    )
