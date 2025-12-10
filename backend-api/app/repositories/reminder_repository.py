"""Repository for Reminder data access operations."""
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.reminder import Reminder, ReminderStatus
from app.models.call_log import CallLog


class ReminderRepository:
    """
    Repository class for Reminder CRUD operations.
    Encapsulates all database access for reminders.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(
        self,
        user_id: UUID,
        phone_number: str,
        message: str,
        scheduled_at: datetime
    ) -> Reminder:
        """
        Create a new reminder.
        
        Args:
            user_id: User's UUID
            phone_number: Phone number to call
            message: Reminder message
            scheduled_at: When to trigger the reminder
            
        Returns:
            Created Reminder instance
        """
        reminder = Reminder(
            user_id=user_id,
            phone_number=phone_number,
            message=message,
            scheduled_at=scheduled_at,
            status=ReminderStatus.SCHEDULED
        )
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder
    
    def get_by_id(self, reminder_id: UUID) -> Reminder | None:
        """
        Get reminder by ID with call logs.
        
        Args:
            reminder_id: Reminder's UUID
            
        Returns:
            Reminder instance or None if not found
        """
        return (
            self.db.query(Reminder)
            .options(joinedload(Reminder.call_logs))
            .filter(Reminder.id == reminder_id)
            .first()
        )
    
    def get_by_user_id(
        self,
        user_id: UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 10
    ) -> list[Reminder]:
        """
        Get reminders for a user with optional status filter.
        
        Args:
            user_id: User's UUID
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Reminder instances
        """
        query = (
            self.db.query(Reminder)
            .options(joinedload(Reminder.call_logs))
            .filter(Reminder.user_id == user_id)
        )
        
        if status and status != "all":
            query = query.filter(Reminder.status == ReminderStatus(status))
        
        return (
            query
            .order_by(Reminder.scheduled_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_by_user_id(self, user_id: UUID, status: str | None = None) -> int:
        """
        Count reminders for a user.
        
        Args:
            user_id: User's UUID
            status: Optional status filter
            
        Returns:
            Count of reminders
        """
        query = self.db.query(func.count(Reminder.id)).filter(Reminder.user_id == user_id)
        
        if status and status != "all":
            query = query.filter(Reminder.status == ReminderStatus(status))
        
        return query.scalar()
    
    def get_due_reminders(self, limit: int = 100) -> list[Reminder]:
        """
        Get reminders that are due for processing.
        
        Args:
            limit: Maximum number of reminders to fetch
            
        Returns:
            List of due Reminder instances
        """
        return (
            self.db.query(Reminder)
            .filter(
                Reminder.status == ReminderStatus.SCHEDULED,
                Reminder.scheduled_at <= datetime.utcnow()
            )
            .order_by(Reminder.scheduled_at.asc())
            .limit(limit)
            .all()
        )
    
    def update_status(
        self,
        reminder_id: UUID,
        status: ReminderStatus,
        external_call_id: str | None = None
    ) -> Reminder | None:
        """
        Update reminder status.
        
        Args:
            reminder_id: Reminder's UUID
            status: New status
            external_call_id: Optional external call ID
            
        Returns:
            Updated Reminder instance or None if not found
        """
        reminder = self.get_by_id(reminder_id)
        if reminder:
            reminder.status = status
            if external_call_id:
                reminder.external_call_id = external_call_id
            self.db.commit()
            self.db.refresh(reminder)
        return reminder
    
    def get_by_external_call_id(self, external_call_id: str) -> Reminder | None:
        """
        Get reminder by external call ID.
        
        Args:
            external_call_id: External call ID from voice provider
            
        Returns:
            Reminder instance or None if not found
        """
        return (
            self.db.query(Reminder)
            .options(joinedload(Reminder.call_logs))
            .filter(Reminder.external_call_id == external_call_id)
            .first()
        )
    
    def add_call_log(
        self,
        reminder_id: UUID,
        external_call_id: str,
        status: str,
        transcript: str | None = None
    ) -> CallLog:
        """
        Add a call log entry for a reminder.
        
        Args:
            reminder_id: Reminder's UUID
            external_call_id: External call ID
            status: Call status
            transcript: Optional transcript
            
        Returns:
            Created CallLog instance
        """
        call_log = CallLog(
            reminder_id=reminder_id,
            external_call_id=external_call_id,
            status=status,
            transcript=transcript
        )
        self.db.add(call_log)
        self.db.commit()
        self.db.refresh(call_log)
        return call_log
    
    def call_log_exists(self, external_call_id: str, status: str) -> bool:
        """
        Check if a call log with given external_call_id and status exists.
        Used for idempotency checks.
        
        Args:
            external_call_id: External call ID
            status: Call status
            
        Returns:
            True if exists, False otherwise
        """
        return (
            self.db.query(CallLog)
            .filter(
                CallLog.external_call_id == external_call_id,
                CallLog.status == status
            )
            .first() is not None
        )
    
    def get_all(self, skip: int = 0, limit: int = 10) -> list[Reminder]:
        """
        Get all reminders with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Reminder instances
        """
        return (
            self.db.query(Reminder)
            .options(joinedload(Reminder.call_logs))
            .order_by(Reminder.scheduled_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count(self) -> int:
        """
        Count total number of reminders.
        
        Returns:
            Total reminder count
        """
        return self.db.query(func.count(Reminder.id)).scalar()
    
    def count_by_status(self) -> dict:
        """
        Count reminders grouped by status.
        
        Returns:
            Dictionary with status counts
        """
        results = (
            self.db.query(Reminder.status, func.count(Reminder.id))
            .group_by(Reminder.status)
            .all()
        )
        return {status.value: count for status, count in results}
