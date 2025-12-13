"""Pydantic schemas for user authentication and management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    full_name: Optional[str] = Field(None, max_length=200, description="Full name")


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Response schema for token generation."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in minutes")
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is email verified")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Request schema for updating user profile."""

    full_name: Optional[str] = Field(None, max_length=200, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")


class PasswordChangeRequest(BaseModel):
    """Request schema for changing password."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)")
