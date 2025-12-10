"""Service layer for Reminder business logic."""
import logging
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.reminder_repository import ReminderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderListResponse
)
from app.models.reminder import ReminderStatus

logger = logging.getLogger(__name__)


class ReminderServiceError(Exception):
    """Base exception for ReminderService errors."""
    pass


class ReminderNotFoundError(ReminderServiceError):
    """Raised when reminder is not found."""
    pass


class UserNotFoundError(ReminderServiceError):
    """Raised when user is not found."""
    pass


class InvalidScheduleTimeError(ReminderServiceError):
    """Raised when scheduled time is invalid."""
    pass


class ReminderService:
    """
    Service class for Reminder business logic.
    Implements domain rules, validation, and state management.
    """
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.repository = ReminderRepository(db)
        self.user_repository = UserRepository(db)
    
    def create_reminder(self, data: ReminderCreate) -> ReminderResponse:
        """
        Create a new reminder.
        
        Args:
            data: ReminderCreate schema with reminder details
            
        Returns:
            ReminderResponse with created reminder data
            
        Raises:
            UserNotFoundError: If user does not exist
            InvalidScheduleTimeError: If scheduled_at is in the past
        """
        logger.info(f"Creating reminder for user {data.user_id}")
        
        # Validate user exists
        user = self.user_repository.get_by_id(data.user_id)
        if not user:
            logger.warning(f"User not found: {data.user_id}")
            raise UserNotFoundError(f"User with ID {data.user_id} not found")
        
        # Double-check scheduled_at is in the future (Pydantic also validates)
        scheduled_naive = data.scheduled_at.replace(tzinfo=None) if data.scheduled_at.tzinfo else data.scheduled_at
        if scheduled_naive <= datetime.utcnow():
            logger.warning(f"Invalid schedule time: {data.scheduled_at}")
            raise InvalidScheduleTimeError("Scheduled time must be in the future")
        
        reminder = self.repository.create(
            user_id=data.user_id,
            phone_number=data.phone_number,
            message=data.message,
            scheduled_at=data.scheduled_at
        )
        
        logger.info(f"Reminder created: {reminder.id} for user {data.user_id}")
        return ReminderResponse.model_validate(reminder)
    
    def get_reminder(self, reminder_id: UUID) -> ReminderResponse:
        """
        Get reminder by ID.
        
        Args:
            reminder_id: Reminder's UUID
            
        Returns:
            ReminderResponse with reminder data
            
        Raises:
            ReminderNotFoundError: If reminder not found
        """
        reminder = self.repository.get_by_id(reminder_id)
        if not reminder:
            logger.warning(f"Reminder not found: {reminder_id}")
            raise ReminderNotFoundError(f"Reminder with ID {reminder_id} not found")
        
        return ReminderResponse.model_validate(reminder)
    
    def list_user_reminders(
        self,
        user_id: UUID,
        status: str | None = None,
        page: int = 1,
        size: int = 10
    ) -> ReminderListResponse:
        """
        List reminders for a user with optional filtering.
        
        Args:
            user_id: User's UUID
            status: Optional status filter
            page: Page number (1-indexed)
            size: Items per page
            
        Returns:
            ReminderListResponse with paginated reminders
            
        Raises:
            UserNotFoundError: If user not found
        """
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        skip = (page - 1) * size
        reminders = self.repository.get_by_user_id(
            user_id=user_id,
            status=status,
            skip=skip,
            limit=size
        )
        total = self.repository.count_by_user_id(user_id, status)
        pages = (total + size - 1) // size if total > 0 else 1
        
        logger.info(f"Listed reminders for user {user_id}: page={page}, total={total}")
        
        return ReminderListResponse(
            items=[ReminderResponse.model_validate(r) for r in reminders],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def list_all_reminders(
        self,
        page: int = 1,
        size: int = 10
    ) -> ReminderListResponse:
        """
        List all reminders with pagination.
        
        Args:
            page: Page number (1-indexed)
            size: Items per page
            
        Returns:
            ReminderListResponse with paginated reminders
        """
        skip = (page - 1) * size
        reminders = self.repository.get_all(skip=skip, limit=size)
        total = self.repository.count()
        pages = (total + size - 1) // size if total > 0 else 1
        
        logger.info(f"Listed all reminders: page={page}, total={total}")
        
        return ReminderListResponse(
            items=[ReminderResponse.model_validate(r) for r in reminders],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def get_stats(self) -> dict:
        """
        Get reminder statistics.
        
        Returns:
            Dictionary with total and counts by status
        """
        total = self.repository.count()
        by_status = self.repository.count_by_status()
        
        # Ensure all statuses are present
        stats = {
            "total": total,
            "scheduled": by_status.get("scheduled", 0),
            "processing": by_status.get("processing", 0),
            "called": by_status.get("called", 0),
            "failed": by_status.get("failed", 0)
        }
        
        logger.info(f"Stats retrieved: {stats}")
        return stats
    
    def update_status(
        self,
        reminder_id: UUID,
        status: str,
        external_call_id: str | None = None
    ) -> ReminderResponse:
        """
        Update reminder status.
        
        Args:
            reminder_id: Reminder's UUID
            status: New status value
            external_call_id: Optional external call ID
            
        Returns:
            Updated ReminderResponse
            
        Raises:
            ReminderNotFoundError: If reminder not found
        """
        reminder = self.repository.update_status(
            reminder_id=reminder_id,
            status=ReminderStatus(status),
            external_call_id=external_call_id
        )
        
        if not reminder:
            raise ReminderNotFoundError(f"Reminder with ID {reminder_id} not found")
        
        logger.info(f"Reminder {reminder_id} status updated to {status}")
        return ReminderResponse.model_validate(reminder)
