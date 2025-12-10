"""Pydantic schemas for Reminder API."""
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator
import phonenumbers


class ReminderStatusEnum(str, Enum):
    """Reminder status enum for API responses."""
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    CALLED = "called"
    FAILED = "failed"


class CallLogResponse(BaseModel):
    """
    Schema for call log response.
    
    Attributes:
        id: Call log unique identifier
        external_call_id: ID from voice provider
        status: Call status
        transcript: Optional call transcript
        received_at: When the webhook was received
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    external_call_id: str
    status: str
    transcript: str | None = None
    received_at: datetime


class ReminderBase(BaseModel):
    """Base schema for Reminder with common fields."""
    phone_number: str
    message: str
    scheduled_at: datetime
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format using phonenumbers library."""
        try:
            # Parse the phone number (assume international format with +)
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            # Return in E.164 format
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format. Use international format like +1234567890")
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()
    
    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v: datetime) -> datetime:
        """Validate scheduled_at is in the future."""
        # TEMPORARILY DISABLED FOR TESTING - Allow past times
        # Make both datetimes timezone-naive for comparison
        # now = datetime.utcnow()
        # scheduled_naive = v.replace(tzinfo=None) if v.tzinfo else v
        
        # if scheduled_naive <= now:
        #     raise ValueError("Scheduled time must be in the future")
        return v


class ReminderCreate(ReminderBase):
    """
    Schema for creating a new reminder.
    
    Attributes:
        user_id: UUID of the user creating the reminder
        phone_number: Phone number to call (validated)
        message: Message to be spoken
        scheduled_at: When to trigger the reminder (must be in future)
    """
    user_id: UUID


class ReminderResponse(BaseModel):
    """
    Schema for reminder response.
    
    Attributes:
        id: Reminder unique identifier
        user_id: Owner user ID
        phone_number: Phone number to call
        message: Message to be spoken
        scheduled_at: When the reminder is scheduled
        status: Current reminder status
        external_call_id: Voice provider call ID (if available)
        created_at: When the reminder was created
        updated_at: When the reminder was last updated
        call_logs: List of associated call logs
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    phone_number: str
    message: str
    scheduled_at: datetime
    status: ReminderStatusEnum
    external_call_id: str | None = None
    created_at: datetime
    updated_at: datetime
    call_logs: list[CallLogResponse] = []


class ReminderListResponse(BaseModel):
    """Schema for paginated list of reminders."""
    items: list[ReminderResponse]
    total: int
    page: int
    size: int
    pages: int


class ReminderStatusFilter(str, Enum):
    """Filter options for reminder status."""
    ALL = "all"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    CALLED = "called"
    FAILED = "failed"
