"""CallLog model - copied from backend-api for consistency."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CallLog(Base):
    """CallLog model representing a voice call log entry."""
    __tablename__ = "call_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False)
    external_call_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    transcript = Column(Text, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    reminder = relationship("Reminder", back_populates="call_logs")
    
    __table_args__ = (
        Index("ix_call_logs_reminder_id", "reminder_id"),
        Index("ix_call_logs_external_call_id_status", "external_call_id", "status"),
    )
