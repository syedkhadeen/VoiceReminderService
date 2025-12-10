"""Repository for User data access operations."""
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User


class UserRepository:
    """
    Repository class for User CRUD operations.
    Encapsulates all database access for users.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, email: str) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address
            
        Returns:
            Created User instance
        """
        user = User(email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: UUID) -> User | None:
        """
        Get user by ID.
        
        Args:
            user_id: User's UUID
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.
        
        Args:
            email: User's email address
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 10) -> list[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of User instances
        """
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """
        Count total number of users.
        
        Returns:
            Total user count
        """
        return self.db.query(func.count(User.id)).scalar()
    
    def delete(self, user_id: UUID) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User's UUID
            
        Returns:
            True if deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
