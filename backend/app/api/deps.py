"""Authentication & authorization dependencies for FastAPI (JWT + API Keys + RBAC)."""

from dataclasses import dataclass
from typing import Optional, Sequence, Union

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token, hash_api_key
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    ApiKey,
    User,
    UserRole,
    get_utc_now,
    organization_memberships,
)


@dataclass
class AuthContext:
    """Resolved authentication context for an API request."""

    user: Optional[User]
    org_id: str
    method: str  # "jwt" | "api_key"


async def _user_belongs_to_org(db: AsyncSession, user: User, org_id: str) -> bool:
    """Verifies a user belongs to an organization (home org or explicit membership)."""
    if user.organization_id == org_id:
        return True
    result = await db.execute(
        select(organization_memberships.c.user_id).where(
            organization_memberships.c.user_id == user.id,
            organization_memberships.c.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def resolve_auth(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_organization_id: Optional[str] = Header(default=None, alias="X-Organization-Id"),
) -> AuthContext:
    """Resolves the authenticated tenant context from a JWT bearer token or an API key."""
    # 1. JWT Bearer token path
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
        except pyjwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await db.get(User, payload.get("sub"))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo.",
            )

        org_id = x_organization_id or user.organization_id
        if not await _user_belongs_to_org(db, user, org_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta organización.",
            )
        return AuthContext(user=user, org_id=org_id, method="jwt")

    # 2. API Key path
    if x_api_key:
        key_hash = hash_api_key(x_api_key)
        result = await db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        api_key = result.scalar_one_or_none()
        if not api_key or not api_key.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key inválida o revocada.",
            )
        if api_key.expires_at and api_key.expires_at < api_key.created_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key expirada.",
            )
        if x_organization_id and x_organization_id != api_key.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La organización indicada no coincide con la API Key.",
            )

        api_key.last_used_at = get_utc_now()
        await db.commit()

        owner = await db.get(User, api_key.user_id) if api_key.user_id else None
        return AuthContext(user=owner, org_id=api_key.organization_id, method="api_key")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida: envía un Bearer token o X-API-Key.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _role_ok(user: Optional[User], roles: Sequence[Union[str, UserRole]]) -> bool:
    if not user:
        return False
    allowed = {r.value if isinstance(r, UserRole) else str(r) for r in roles}
    return user.role_value in allowed


def require_roles(*roles: Union[str, UserRole]):
    """Dependency factory enforcing that the authenticated user holds at least one role (JWT only)."""

    async def dependency(auth: AuthContext = Depends(resolve_auth)) -> AuthContext:
        if auth.method != "jwt":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta operación requiere un token de usuario (no API Key).",
            )
        if not _role_ok(auth.user, roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operación.",
            )
        return auth

    return dependency


def require_editor_or_api_key(
    auth: AuthContext = Depends(resolve_auth),
) -> AuthContext:
    """Allows ingesting/editing with a valid API key or a JWT user with editor role."""
    if auth.method == "api_key":
        return auth
    if _role_ok(auth.user, [UserRole.ADMIN, UserRole.MEMBER]):
        return auth
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Se requiere rol Admin o Member (o una API Key) para esta operación.",
    )


def get_current_user(
    auth: AuthContext = Depends(resolve_auth),
) -> Optional[User]:
    """Returns the authenticated user (None for org-scoped API keys)."""
    return auth.user