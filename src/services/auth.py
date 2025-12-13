"""Authentication service for user management."""

from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User
from src.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# HTTP Bearer token scheme
security_scheme = HTTPBearer()


async def register_user(
    email: str,
    username: str,
    password: str,
    full_name: Optional[str],
    db: Session
) -> User:
    """
    Register a new user.

    Args:
        email: User email address
        username: Username
        password: Plain text password
        full_name: Optional full name
        db: Database session

    Returns:
        User: Created user object

    Raises:
        HTTPException: If user already exists
    """
    logger.info(f"Registering new user: {username}")

    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        if existing_user.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create new user
    hashed_pwd = hash_password(password)
    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_pwd,
        full_name=full_name,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User registered successfully: {username} (id={new_user.id})")

    return new_user


async def authenticate_user(
    username: str,
    password: str,
    db: Session
) -> Optional[User]:
    """
    Authenticate a user by username and password.

    Args:
        username: Username or email
        password: Plain text password
        db: Database session

    Returns:
        Optional[User]: User object if authenticated, None otherwise
    """
    logger.info(f"Authenticating user: {username}")

    # Find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user:
        logger.warning(f"User not found: {username}")
        return None

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {username}")
        return None

    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {username}")
        return None

    logger.info(f"User authenticated successfully: {username}")
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


def create_user_token(user: User) -> str:
    """
    Create JWT access token for a user.

    Args:
        user: User object

    Returns:
        str: JWT access token
    """
    config = get_config()

    access_token_expires = timedelta(
        minutes=config.security.access_token_expire_minutes
    )

    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )

    return access_token
