"""Password hashing, JWT tokens and API key utilities (100% local, stdlib + PyJWT)."""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from app.core.config import settings

_PBKDF2_ITERATIONS = 210_000
_ALGORITHM = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    """Hashes a plaintext password using PBKDF2-SHA256 with a random per-user salt."""
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return (
        f"{_ALGORITHM}${_PBKDF2_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"
    )


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plaintext password against a PBKDF2 hash produced by hash_password."""
    try:
        algo, iterations_str, salt_b64, derived_b64 = hashed.split("$")
        if algo != _ALGORITHM:
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(derived_b64)
        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations_str)
        )
        return hmac.compare_digest(derived, expected)
    except Exception:
        return False


def create_access_token(
    user_id: str,
    organization_id: str,
    role: str,
    expires_minutes: Optional[int] = None,
) -> str:
    """Creates a signed JWT access token embedding user identity and tenant."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRES_MINUTES
    )
    payload: Dict[str, Any] = {
        "sub": user_id,
        "org": organization_id,
        "role": role,
        "iat": now,
        "exp": expires,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token. Raises jwt.PyJWTError on failure."""
    return jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def generate_api_key() -> str:
    """Generates a cryptographically random API key with a recognizable prefix."""
    return f"{settings.API_KEY_PREFIX}{secrets.token_urlsafe(24)}"


def hash_api_key(api_key: str) -> str:
    """Hashes an API key for secure storage (plaintext is only shown once)."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()