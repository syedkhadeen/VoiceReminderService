"""Pydantic schemas for User API."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base schema for User with common fields."""
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Attributes:
        email: Valid email address (required)
    """
    pass


class UserResponse(UserBase):
    """
    Schema for user response.
    
    Attributes:
        id: User's unique identifier
        email: User's email address
        created_at: When the user was created
        updated_at: When the user was last updated
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Schema for paginated list of users."""
    items: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int
