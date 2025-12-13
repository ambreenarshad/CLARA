"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Note: Bcrypt has a 72-byte limit. We truncate to ensure we don't exceed it.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password (as string)
    """
    # Encode to bytes and truncate to 72 bytes for bcrypt
    password_bytes = password.encode('utf-8')[:72]
    # Generate salt and hash the password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Note: Must truncate the same way as hash_password for consistency.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password (as string)

    Returns:
        bool: True if password matches, False otherwise
    """
    # Encode to bytes and truncate to 72 bytes (same as hashing)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    config = get_config()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.security.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.security.secret_key,
        algorithm=config.security.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Optional[dict]: Decoded token payload, None if invalid
    """
    config = get_config()

    try:
        payload = jwt.decode(
            token,
            config.security.secret_key,
            algorithms=[config.security.algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None
