"""
Webhook endpoints for receiving voice provider callbacks.

Handles call status updates with idempotency checks.
"""
import logging
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.reminder import Reminder, ReminderStatus
from app.models.call_log import CallLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class WebhookMetadata(BaseModel):
    """Metadata from webhook payload."""
    reminder_id: str


class CallStatusWebhook(BaseModel):
    """
    Webhook payload for call status updates.
    
    Expected from voice provider when call completes or fails.
    """
    call_id: str
    status: str  # 'completed', 'failed', etc.
    metadata: WebhookMetadata
    transcript: str | None = None


class InfobipResult(BaseModel):
    """Infobip result structure."""
    messageId: str
    to: str
    sentAt: str | None = None
    doneAt: str | None = None
    duration: int | None = None
    mccMnc: str | None = None
    price: dict | None = None
    status: dict
    error: dict | None = None


class InfobipWebhook(BaseModel):
    """
    Infobip webhook payload structure.
    
    Infobip sends delivery reports with this format.
    """
    results: list[InfobipResult]
    customData: dict | None = None


@router.post("/call-status", status_code=status.HTTP_200_OK)
async def handle_call_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle call status webhook from Infobip.
    
    This endpoint:
    1. Validates the webhook payload (supports both Infobip and generic formats)
    2. Checks for idempotency (duplicate webhooks)
    3. Updates reminder status to 'called' or 'failed'
    4. Stores call info in call_logs
    
    Returns 200 OK on success, even for duplicates (idempotent).
    """
    # Get raw body for logging
    body = await request.json()
    logger.info(f"Webhook received: {body}")
    
    # Try to parse as Infobip format first
    try:
        if "results" in body:
            # Infobip format
            webhook = InfobipWebhook(**body)
            return await _process_infobip_webhook(webhook, db)
        else:
            # Generic format (backward compatibility)
            webhook = CallStatusWebhook(**body)
            return await _process_generic_webhook(webhook, db)
    except Exception as e:
        logger.error(f"Error parsing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook format: {str(e)}"
        )


async def _process_infobip_webhook(
    payload: InfobipWebhook,
    db: Session
):
    """Process Infobip-specific webhook format."""
    if not payload.results:
        logger.warning("No results in Infobip webhook")
        return {"message": "No results to process"}
    
    result = payload.results[0]  # Process first result
    call_id = result.messageId
    status_info = result.status
    status_name = status_info.get("name", "UNKNOWN")
    status_group = status_info.get("groupName", "UNKNOWN")
    
    logger.info(
        f"Infobip webhook: messageId={call_id}, status={status_name}, group={status_group}"
    )
    
    # Extract reminder_id from customData
    if not payload.customData or "reminder_id" not in payload.customData:
        logger.warning("No reminder_id in customData")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing reminder_id in customData"
        )
    
    try:
        reminder_id = UUID(payload.customData["reminder_id"])
    except ValueError:
        logger.warning(f"Invalid reminder_id format: {payload.customData['reminder_id']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reminder_id format"
        )
    
    # Find the reminder
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        logger.warning(f"Reminder not found: {reminder_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found"
        )
    
    # Idempotency check
    existing_log = (
        db.query(CallLog)
        .filter(
            CallLog.external_call_id == call_id,
            CallLog.status == status_name
        )
        .first()
    )
    
    if existing_log:
        logger.info(f"Duplicate webhook - already processed: {call_id}")
        return {"message": "Webhook already processed", "idempotent": True}
    
    # Map Infobip status to reminder status
    # Infobip groups: PENDING, UNDELIVERABLE, DELIVERED, EXPIRED, REJECTED
    if status_group in ["DELIVERED"]:
        new_status = ReminderStatus.CALLED
    elif status_group in ["PENDING"]:
        new_status = ReminderStatus.PROCESSING
    else:
        new_status = ReminderStatus.FAILED
    
    # Update reminder status
    reminder.status = new_status
    
    # Create call log entry
    call_log = CallLog(
        reminder_id=reminder_id,
        external_call_id=call_id,
        status=status_name,
        transcript=f"Status: {status_name}, Group: {status_group}, Duration: {result.duration}s" if result.duration else f"Status: {status_name}",
        received_at=datetime.utcnow()
    )
    db.add(call_log)
    
    try:
        db.commit()
        logger.info(
            f"Infobip webhook processed: reminder {reminder_id} -> {new_status.value}"
        )
        return {
            "message": "Webhook processed successfully",
            "reminder_id": str(reminder_id),
            "new_status": new_status.value
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


async def _process_generic_webhook(
    payload: CallStatusWebhook,
    db: Session
):
    """Process generic webhook format (backward compatibility)."""
    logger.info(
        f"Generic webhook: call_id={payload.call_id}, status={payload.status}"
    )
    
    try:
        reminder_id = UUID(payload.metadata.reminder_id)
    except ValueError:
        logger.warning(f"Invalid reminder_id format: {payload.metadata.reminder_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reminder_id format"
        )
    
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        logger.warning(f"Reminder not found: {reminder_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found"
        )
    
    existing_log = (
        db.query(CallLog)
        .filter(
            CallLog.external_call_id == payload.call_id,
            CallLog.status == payload.status
        )
        .first()
    )
    
    if existing_log:
        logger.info(f"Duplicate webhook - already processed: {payload.call_id}")
        return {"message": "Webhook already processed", "idempotent": True}
    
    if payload.status in ["completed", "ended"]:
        new_status = ReminderStatus.CALLED
    else:
        new_status = ReminderStatus.FAILED
    
    reminder.status = new_status
    
    call_log = CallLog(
        reminder_id=reminder_id,
        external_call_id=payload.call_id,
        status=payload.status,
        transcript=payload.transcript,
        received_at=datetime.utcnow()
    )
    db.add(call_log)
    
    try:
        db.commit()
        logger.info(f"Generic webhook processed: reminder {reminder_id} -> {new_status.value}")
        return {
            "message": "Webhook processed successfully",
            "reminder_id": str(reminder_id),
            "new_status": new_status.value
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


@router.get("/health")
async def webhook_health():
    """Health check for webhook endpoint."""
    return {"status": "healthy", "service": "webhook"}
