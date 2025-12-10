"""Service layer for User business logic."""
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserListResponse
from app.models.user import User

logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """Base exception for UserService errors."""
    pass


class UserNotFoundError(UserServiceError):
    """Raised when user is not found."""
    pass


class UserAlreadyExistsError(UserServiceError):
    """Raised when user with email already exists."""
    pass


class UserService:
    """
    Service class for User business logic.
    Implements domain rules and validation.
    """
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.repository = UserRepository(db)
    
    def create_user(self, data: UserCreate) -> UserResponse:
        """
        Create a new user.
        
        Args:
            data: UserCreate schema with email
            
        Returns:
            UserResponse with created user data
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
        """
        logger.info(f"Creating user with email: {data.email}")
        
        # Check if user already exists
        existing = self.repository.get_by_email(data.email)
        if existing:
            logger.warning(f"User with email {data.email} already exists")
            raise UserAlreadyExistsError(f"User with email {data.email} already exists")
        
        try:
            user = self.repository.create(email=data.email)
            logger.info(f"User created successfully: {user.id}")
            return UserResponse.model_validate(user)
        except IntegrityError:
            logger.error(f"IntegrityError creating user: {data.email}")
            raise UserAlreadyExistsError(f"User with email {data.email} already exists")
    
    def get_user(self, user_id: UUID) -> UserResponse:
        """
        Get user by ID.
        
        Args:
            user_id: User's UUID
            
        Returns:
            UserResponse with user data
            
        Raises:
            UserNotFoundError: If user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return UserResponse.model_validate(user)
    
    def list_users(self, page: int = 1, size: int = 10) -> UserListResponse:
        """
        List all users with pagination.
        
        Args:
            page: Page number (1-indexed)
            size: Items per page
            
        Returns:
            UserListResponse with paginated users
        """
        skip = (page - 1) * size
        users = self.repository.get_all(skip=skip, limit=size)
        total = self.repository.count()
        pages = (total + size - 1) // size if total > 0 else 1
        
        logger.info(f"Listed users: page={page}, size={size}, total={total}")
        
        return UserListResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def user_exists(self, user_id: UUID) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id: User's UUID
            
        Returns:
            True if user exists, False otherwise
        """
        return self.repository.get_by_id(user_id) is not None
    
    def delete_user(self, user_id: UUID) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User's UUID
            
        Returns:
            True if deleted
            
        Raises:
            UserNotFoundError: If user not found
        """
        if not self.repository.delete(user_id):
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        logger.info(f"User deleted: {user_id}")
        return True
