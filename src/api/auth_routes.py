"""Authentication API routes."""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User
from src.models.user_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
    PasswordChangeRequest,
)
from src.services.auth import (
    register_user,
    authenticate_user,
    get_current_user,
    create_user_token,
)
from src.utils.security import hash_password, verify_password
from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Create auth router
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account",
)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If user already exists
    """
    logger.info(f"Registration request for username: {user_data.username}")

    user = await register_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        db=db
    )

    return UserResponse.from_orm(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticate user and get access token",
)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Login user and generate JWT token.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        TokenResponse: Access token and user info

    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login request for username: {credentials.username}")

    user = await authenticate_user(
        username=credentials.username,
        password=credentials.password,
        db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_user_token(user)

    config = get_config()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=config.security.access_token_expire_minutes,
        user_id=user.id,
        username=user.username
    )


@router.post(
    "/logout",
    summary="User Logout",
    description="Logout user (client should delete token)",
)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout user.

    Note: Since we're using stateless JWT tokens, logout is handled
    client-side by deleting the token. This endpoint is provided
    for consistency and can be extended for token blacklisting.

    Args:
        current_user: Current authenticated user

    Returns:
        Dict: Logout confirmation message
    """
    logger.info(f"Logout request for user: {current_user.username}")

    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user information",
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: User information
    """
    return UserResponse.from_orm(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update User Profile",
    description="Update current user's profile information",
)
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update user profile.

    Args:
        update_data: Profile update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse: Updated user information

    Raises:
        HTTPException: If email already exists
    """
    logger.info(f"Profile update request for user: {current_user.username}")

    # Update full name
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name

    # Update email
    if update_data.email is not None and update_data.email != current_user.email:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == update_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = update_data.email
        current_user.is_verified = False  # Require re-verification

    current_user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    logger.info(f"Profile updated for user: {current_user.username}")

    return UserResponse.from_orm(current_user)


@router.post(
    "/change-password",
    summary="Change Password",
    description="Change current user's password",
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dict: Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    logger.info(f"Password change request for user: {current_user.username}")

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()

    db.commit()

    logger.info(f"Password changed for user: {current_user.username}")

    return {
        "message": "Password changed successfully",
        "username": current_user.username
    }
