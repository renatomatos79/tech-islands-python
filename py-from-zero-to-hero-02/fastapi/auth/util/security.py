from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import jwt
from passlib.context import CryptContext

# -----------------------
# Password hashing
# -----------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# -----------------------
# JWT Access Token
# -----------------------
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Resolve key files relative to this module so paths work in Docker and local runs.
KEYS_DIR = Path(__file__).resolve().parents[1] / "keys"
PRIVATE_KEY = (KEYS_DIR / "private.pem").read_text(encoding="utf-8")
PUBLIC_KEY = (KEYS_DIR / "public.pem").read_text(encoding="utf-8")


def create_access_token(
    *,
    sub: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Creates a JWT access token with standard claims:
      - sub (subject): user identifier (e.g. email)
      - iat (issued at)
      - exp (expiration)
    plus your custom claim:
      - role
    """
    now = datetime.now(timezone.utc)

    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload: Dict[str, Any] = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Verifies signature + exp and returns the payload.
    Raises jwt exceptions if invalid/expired.
    """
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
