"""User API endpoints."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserListResponse
from app.services.user_service import (
    UserService,
    UserNotFoundError,
    UserAlreadyExistsError
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    - **email**: Valid email address (required)
    
    Returns 201 Created on success, 400 Bad Request if user exists.
    """
    logger.info(f"POST /api/users - Creating user: {data.email}")
    
    try:
        service = UserService(db)
        user = service.create_user(data)
        logger.info(f"User created: {user.id}")
        return user
    except UserAlreadyExistsError as e:
        logger.warning(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all users with pagination.
    
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    """
    logger.info(f"GET /api/users - page={page}, size={size}")
    
    service = UserService(db)
    return service.list_users(page=page, size=size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get user by ID.
    
    - **user_id**: User's unique identifier (UUID)
    """
    logger.info(f"GET /api/users/{user_id}")
    
    try:
        service = UserService(db)
        return service.get_user(user_id)
    except UserNotFoundError as e:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete user by ID.
    
    - **user_id**: User's unique identifier (UUID)
    
    Note: This will also delete all reminders for this user.
    """
    logger.info(f"DELETE /api/users/{user_id}")
    
    try:
        service = UserService(db)
        service.delete_user(user_id)
    except UserNotFoundError as e:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
