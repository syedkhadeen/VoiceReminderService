"""Reminder API endpoints."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderListResponse,
    ReminderStatusFilter
)
from app.services.reminder_service import (
    ReminderService,
    ReminderNotFoundError,
    UserNotFoundError,
    InvalidScheduleTimeError
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Reminders"])


@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new reminder.
    
    - **user_id**: UUID of the user creating the reminder
    - **phone_number**: Phone number to call (international format)
    - **message**: Message to be spoken in the call
    - **scheduled_at**: When to trigger the reminder (must be in future)
    
    Returns 201 Created on success, 400/404 on validation errors.
    """
    logger.info(f"POST /api/reminders - User: {data.user_id}, Phone: {data.phone_number}")
    
    try:
        service = ReminderService(db)
        reminder = service.create_reminder(data)
        logger.info(f"Reminder created: {reminder.id}")
        return reminder
    except UserNotFoundError as e:
        logger.warning(f"Reminder creation failed - user not found: {data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidScheduleTimeError as e:
        logger.warning(f"Reminder creation failed - invalid time: {data.scheduled_at}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/reminders", response_model=ReminderListResponse)
async def list_all_reminders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all reminders with pagination.
    
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    """
    logger.info(f"GET /api/reminders - page={page}, size={size}")
    
    service = ReminderService(db)
    return service.list_all_reminders(page=page, size=size)


@router.get("/reminders/stats")
async def get_reminder_stats(db: Session = Depends(get_db)):
    """
    Get reminder statistics.
    
    Returns total count and counts by status (scheduled, processing, called, failed).
    """
    logger.info("GET /api/reminders/stats")
    
    service = ReminderService(db)
    return service.get_stats()


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get reminder by ID.
    
    - **reminder_id**: Reminder's unique identifier (UUID)
    
    Returns full reminder details including status and call logs.
    """
    logger.info(f"GET /api/reminders/{reminder_id}")
    
    try:
        service = ReminderService(db)
        return service.get_reminder(reminder_id)
    except ReminderNotFoundError as e:
        logger.warning(f"Reminder not found: {reminder_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/users/{user_id}/reminders", response_model=ReminderListResponse)
async def list_user_reminders(
    user_id: UUID,
    status: ReminderStatusFilter = Query(ReminderStatusFilter.ALL, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List reminders for a specific user.
    
    - **user_id**: User's unique identifier (UUID)
    - **status**: Filter by reminder status (optional)
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    """
    logger.info(f"GET /api/users/{user_id}/reminders - status={status}, page={page}")
    
    try:
        service = ReminderService(db)
        return service.list_user_reminders(
            user_id=user_id,
            status=status.value if status != ReminderStatusFilter.ALL else None,
            page=page,
            size=size
        )
    except UserNotFoundError as e:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/reminders/notifications/recent")
async def get_recent_notifications(
    since_seconds: int = Query(30, ge=1, le=300, description="Get updates from last N seconds"),
    db: Session = Depends(get_db)
):
    """
    Get recent reminder updates for real-time notifications.
    
    Returns reminders that have been updated in the last N seconds.
    Useful for polling-based real-time updates in the frontend.
    
    - **since_seconds**: Look back this many seconds (default: 30, max: 300)
    """
    from datetime import datetime, timedelta
    from app.models.reminder import Reminder
    
    logger.debug(f"GET /api/reminders/notifications/recent - since={since_seconds}s")
    
    cutoff_time = datetime.utcnow() - timedelta(seconds=since_seconds)
    
    # Get reminders updated since cutoff time
    recent_reminders = (
        db.query(Reminder)
        .filter(Reminder.updated_at >= cutoff_time)
        .order_by(Reminder.updated_at.desc())
        .limit(50)
        .all()
    )
    
    notifications = []
    for reminder in recent_reminders:
        # Get the latest call log if available
        latest_log = None
        if reminder.call_logs:
            latest_log = max(reminder.call_logs, key=lambda x: x.received_at)
        
        notifications.append({
            "reminder_id": str(reminder.id),
            "user_id": str(reminder.user_id),
            "phone_number": reminder.phone_number,
            "message": reminder.message,
            "status": reminder.status.value,
            "updated_at": reminder.updated_at.isoformat(),
            "external_call_id": reminder.external_call_id,
            "latest_log": {
                "status": latest_log.status,
                "transcript": latest_log.transcript,
                "received_at": latest_log.received_at.isoformat()
            } if latest_log else None
        })
    
    return {
        "count": len(notifications),
        "since_seconds": since_seconds,
        "notifications": notifications
    }
