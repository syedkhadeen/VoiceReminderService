"""CallLog model for storing voice call history and transcripts."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CallLog(Base):
    """
    CallLog model representing a voice call log entry.
    
    Stores the result of voice provider webhook callbacks including
    status updates and transcripts.
    
    Attributes:
        id: Unique identifier (UUID)
        reminder_id: Foreign key to the associated reminder
        external_call_id: ID from the voice provider
        status: Status of the call (created, completed, failed)
        transcript: Optional transcript of the call
        received_at: Timestamp when the webhook was received
    """
    __tablename__ = "call_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False)
    external_call_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    transcript = Column(Text, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    reminder = relationship("Reminder", back_populates="call_logs")
    
    # Indexes
    __table_args__ = (
        Index("ix_call_logs_reminder_id", "reminder_id"),
        Index("ix_call_logs_external_call_id_status", "external_call_id", "status"),
    )
    
    def __repr__(self):
        return f"<CallLog(id={self.id}, external_call_id={self.external_call_id}, status={self.status})>"
