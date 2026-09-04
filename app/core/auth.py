"""
FastAPI Authentication Dependencies & API Key Middleware
"""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from app.core.database import get_db
from app.core.security import hash_api_key
from app.models.api_key import APIKey, KeyType
from app.models.project import Project

security_scheme = HTTPBearer(auto_error=False)


class AuthenticatedContext:
    def __init__(self, api_key: APIKey, project: Project):
        self.api_key = api_key
        self.project = project


async def get_current_project(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> AuthenticatedContext:
    """
    Validates API Key from Authorization Bearer header.
    Valid key format: Bearer qig_live_xxx, Bearer qig_test_xxx, Bearer qig_ci_xxx
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Bearer header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    raw_key = credentials.credentials.strip()
    if not raw_key.startswith("qig_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Must start with 'qig_live_', 'qig_test_', or 'qig_ci_'",
            headers={"WWW-Authenticate": "Bearer"}
        )

    hashed_key = hash_api_key(raw_key)

    # Query DB for matching API Key
    result = await db.execute(
        select(APIKey).where(APIKey.hashed_key == hashed_key, APIKey.is_active == True)
    )
    api_key = result.scalars().first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Query DB for associated Project
    proj_result = await db.execute(
        select(Project).where(Project.id == api_key.project_id)
    )
    project = proj_result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Associated project not found"
        )

    return AuthenticatedContext(api_key=api_key, project=project)


def require_scopes(allowed_key_types: List[KeyType]):
    """Enforces key type scope constraints (e.g. CI key limited to contract analysis)."""
    async def scope_checker(auth: AuthenticatedContext = Depends(get_current_project)):
        if auth.api_key.key_type not in allowed_key_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API Key type '{auth.api_key.key_type}' is not authorized for this action."
            )
        return auth
    return scope_checker


async def get_optional_project(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[AuthenticatedContext]:
    """Returns AuthenticatedContext if valid bearer key is present, or None if absent/anonymous."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_project(credentials, db)
    except HTTPException:
        return None

