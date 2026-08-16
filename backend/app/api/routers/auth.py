"""Authentication, user management and API keys endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthContext, require_roles, resolve_auth
from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)
from app.domain.auth_models import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    LoginRequest,
    MeResponse,
    OrganizationResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    ApiKey,
    Organization,
    User,
    UserRole,
    organization_memberships,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & API Keys"])


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role_value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


async def _get_organization(session: AsyncSession, org_id: str) -> Organization:
    org = await session.get(Organization, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organización '{org_id}' no encontrada.",
        )
    return org


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Registers a new user (and optionally a new organization) and returns a JWT token."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo electrónico.",
        )

    # Resolve or create the organization
    if payload.organization_id:
        org = await db.get(Organization, payload.organization_id)
        if not org:
            org = Organization(
                id=payload.organization_id,
                name=payload.organization_name or payload.organization_id,
            )
            db.add(org)
            await db.flush()
    else:
        org_name = payload.organization_name or f"Organización de {payload.email}"
        org = Organization(
            id=str(uuid.uuid4()),
            name=org_name,
        )
        db.add(org)
        await db.flush()

    # First user of the organization becomes Admin; subsequent users are Members
    member_count = await db.execute(
        select(organization_memberships.c.user_id).where(
            organization_memberships.c.organization_id == org.id
        )
    )
    is_first = member_count.scalar_one_or_none() is None

    user = User(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.ADMIN if is_first else UserRole.MEMBER,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.execute(
        organization_memberships.insert().values(
            user_id=user.id, organization_id=org.id
        )
    )
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, org.id, user.role_value)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRES_MINUTES,
        user=_user_response(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login_user(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticates a user with email/password and returns a JWT access token."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está desactivado.",
        )

    token = create_access_token(user.id, user.organization_id, user.role_value)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRES_MINUTES,
        user=_user_response(user),
    )


@router.get(
    "/me",
    response_model=MeResponse,
)
async def get_me(
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
):
    """Returns the current user, their default organization and org memberships."""
    user = auth.user
    default_org = await _get_organization(db, user.organization_id)
    org_ids = await db.execute(
        select(organization_memberships.c.organization_id).where(
            organization_memberships.c.user_id == user.id
        )
    )
    org_id_list = [oid for (oid,) in org_ids.all()]
    if user.organization_id not in org_id_list:
        org_id_list.insert(0, user.organization_id)

    organizations: list[OrganizationResponse] = []
    for org_id in org_id_list:
        org = await _get_organization(db, org_id)
        organizations.append(
            OrganizationResponse(id=org.id, name=org.name)
        )

    return MeResponse(
        user=_user_response(user),
        default_organization=OrganizationResponse(id=default_org.id, name=default_org.name),
        organizations=organizations,
    )


# ==========================================
# API Keys (unattended ingestion)
# ==========================================


@router.post(
    "/api-keys",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    payload: ApiKeyCreate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Generates a new API key for unattended ingestion. The plaintext key is shown once."""
    plaintext = generate_api_key()
    api_key = ApiKey(
        id=str(uuid.uuid4()),
        organization_id=auth.org_id,
        user_id=auth.user.id if auth.user else None,
        name=payload.name,
        prefix=plaintext[:10],
        key_hash=hash_api_key(plaintext),
        expires_at=payload.expires_at.replace(tzinfo=None) if payload.expires_at else None,
        is_active=True,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreatedResponse(
        id=api_key.id,
        organization_id=api_key.organization_id,
        name=api_key.name,
        prefix=api_key.prefix,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        created_at=api_key.created_at.isoformat(),
        key=plaintext,
    )


@router.get(
    "/api-keys",
    response_model=list[ApiKeyResponse],
)
async def list_api_keys(
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Lists API keys for the current organization (hashed values are never returned)."""
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.organization_id == auth.org_id)
        .order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()
    return [
        ApiKeyResponse(
            id=k.id,
            organization_id=k.organization_id,
            name=k.name,
            prefix=k.prefix,
            is_active=k.is_active,
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None,
            expires_at=k.expires_at.isoformat() if k.expires_at else None,
            created_at=k.created_at.isoformat(),
        )
        for k in keys
    ]


@router.delete(
    "/api-keys/{key_id}",
    status_code=status.HTTP_200_OK,
)
async def revoke_api_key(
    key_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Revokes an API key (deactivates it)."""
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.id == key_id,
            ApiKey.organization_id == auth.org_id,
        )
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key no encontrada.",
        )
    api_key.is_active = False
    await db.commit()
    return {"status": "revoked", "api_key_id": key_id}