"""Reminder model - copied from backend-api for consistency."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class ReminderStatus(str, PyEnum):
    """Reminder status enum."""
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    CALLED = "called"
    FAILED = "failed"

    def __str__(self):
        return self.value


class Reminder(Base):
    """Reminder model representing a voice reminder."""
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(
        Enum(ReminderStatus, name="reminder_status", create_type=False, values_callable=lambda x: [e.value for e in x]),
        default=ReminderStatus.SCHEDULED,
        nullable=False
    )
    external_call_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="reminders")
    call_logs = relationship("CallLog", back_populates="reminder", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_reminders_user_id", "user_id"),
        Index("ix_reminders_status_scheduled_at", "status", "scheduled_at"),
    )
