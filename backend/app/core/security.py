from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import jwt, JWTError
from app.core.config import settings
import bcrypt
import hashlib
import base64


def _prepare_password(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    return base64.b64encode(hashlib.sha256(password_bytes).digest())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        _prepare_password(plain_password),
        hashed_password.encode("utf-8")
    )

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        _prepare_password(password),
        bcrypt.gensalt()
    ).decode("utf-8")


# jwt tokens
def create_access_token(
        subject: str | dict,
        expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt

def create_refresh_token(subject: str | dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt

def decode_token(token: str) -> dict[str, Any]:
    try:
        payload =jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    
    except JWTError as e:
        raise JWTError(f"Could not validate token: {str(e)}")
    
def verify_token_type(payload: dict, expected_type: str) -> bool:
    return payload.get("type") == expected_type

# utils
def create_token_pair(user_id: str) -> dict[str, str]:
    return {
        "access_token": create_access_token(
            subject=user_id
        ),
        "refresh_token": create_refresh_token(
            subject=user_id
        )
    }