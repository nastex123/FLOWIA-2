"""Domain models and Pydantic schemas for authentication, API keys and RBAC."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

_EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class RegisterRequest(BaseModel):
    email: str = Field(..., pattern=_EMAIL_PATTERN, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = Field(None, max_length=100)
    organization_name: Optional[str] = Field(None, max_length=255)
    organization_id: Optional[str] = Field(None, max_length=36)


class LoginRequest(BaseModel):
    email: str = Field(..., pattern=_EMAIL_PATTERN, max_length=255)
    password: str


class OrganizationResponse(BaseModel):
    id: str
    name: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserResponse


class MeResponse(BaseModel):
    user: UserResponse
    default_organization: OrganizationResponse
    organizations: List[OrganizationResponse]


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    prefix: str
    is_active: bool
    last_used_at: Optional[str] = None
    expires_at: Optional[str] = None
    created_at: str


class ApiKeyCreatedResponse(ApiKeyResponse):
    key: str = Field(..., description="API Key en claro. Solo se muestra una vez.")