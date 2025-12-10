"""
Reminder Scheduler - processes due reminders.

Uses APScheduler to periodically check for and process due reminders.
"""
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.models.reminder import Reminder, ReminderStatus
from app.models.call_log import CallLog
from app.integrations.voice_provider import voice_provider

logger = logging.getLogger(__name__)

# Pakistan Standard Time (PKT) is UTC+5
PKT = timezone(timedelta(hours=5))

# Maximum reminders to process per batch
MAX_BATCH_SIZE = 50

# Maximum retry attempts for failed calls
MAX_RETRIES = 3


async def process_due_reminders():
    """
    Main scheduler job - finds and processes all due reminders.
    
    This function:
    1. Queries for reminders where scheduled_at <= now and status = 'scheduled'
    2. For each reminder, updates status to 'processing'
    3. Calls voice provider API
    4. Stores call_id and creates call log
    5. Handles errors with logging
    """
    # Get current time in PKT (Pakistan Standard Time)
    current_time_pkt = datetime.now(PKT)
    current_time_naive = current_time_pkt.replace(tzinfo=None)
    
    logger.info(f"Scheduler: Checking for due reminders... (Current PKT: {current_time_pkt.strftime('%Y-%m-%d %H:%M:%S')})")
    
    db = get_db_session()
    try:
        # Find due reminders (compare timezone-naive datetimes)
        due_reminders = (
            db.query(Reminder)
            .filter(
                Reminder.status == ReminderStatus.SCHEDULED,
                Reminder.scheduled_at <= current_time_naive
            )
            .order_by(Reminder.scheduled_at.asc())
            .limit(MAX_BATCH_SIZE)
            .all()
        )
        
        # Log all scheduled reminders for debugging
        all_scheduled = db.query(Reminder).filter(Reminder.status == ReminderStatus.SCHEDULED).all()
        if all_scheduled:
            logger.info(f"Found {len(all_scheduled)} scheduled reminders in DB:")
            for r in all_scheduled[:5]:  # Show first 5
                is_due = r.scheduled_at <= current_time_naive
                logger.info(f"  - Scheduled: {r.scheduled_at}, Due: {is_due}, Message: {r.message[:30]}...")
        
        if not due_reminders:
            logger.debug("No due reminders found")
            return
        
        logger.info(f"Found {len(due_reminders)} due reminder(s) to process")
        
        # Process each reminder
        for reminder in due_reminders:
            await process_single_reminder(db, reminder)
            
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}", exc_info=True)
    finally:
        db.close()


async def process_single_reminder(db: Session, reminder: Reminder):
    """
    Process a single reminder - trigger voice call.
    
    Args:
        db: Database session
        reminder: Reminder to process
    """
    reminder_id = str(reminder.id)
    
    try:
        logger.info(f"Processing reminder {reminder_id}")
        
        # Lock the reminder by setting status to processing
        reminder.status = ReminderStatus.PROCESSING
        db.commit()
        
        logger.info(f"Reminder {reminder_id} status updated to PROCESSING")
        
        # Call voice provider (real or mock)
        response = await voice_provider.create_call(
            phone_number=reminder.phone_number,
            message=reminder.message,
            reminder_id=reminder_id
        )
        
        if response.success:
            # Store external call ID
            reminder.external_call_id = response.call_id
            db.commit()
            
            # Create initial call log entry
            call_log = CallLog(
                reminder_id=reminder.id,
                external_call_id=response.call_id,
                status="created"
            )
            db.add(call_log)
            db.commit()
            
            logger.info(
                f"Call created for reminder {reminder_id}: call_id={response.call_id}",
                extra={
                    "reminder_id": reminder_id,
                    "call_id": response.call_id,
                    "phone_number": reminder.phone_number
                }
            )
            
            # If in mock mode, simulate immediate completion
            if voice_provider.mock_mode:
                await _simulate_mock_completion(db, reminder)
        else:
            # Call failed
            logger.error(
                f"Failed to create call for reminder {reminder_id}: {response.error_message}"
            )
            
            # Mark as failed
            reminder.status = ReminderStatus.FAILED
            db.commit()
            
            # Create failure call log
            call_log = CallLog(
                reminder_id=reminder.id,
                external_call_id=response.call_id or "failed-to-create",
                status="failed",
                transcript=f"Error: {response.error_message}"
            )
            db.add(call_log)
            db.commit()
            
    except Exception as e:
        logger.error(f"Error processing reminder {reminder_id}: {str(e)}", exc_info=True)
        
        try:
            # Mark as failed on exception
            reminder.status = ReminderStatus.FAILED
            db.commit()
        except:
            db.rollback()


async def _simulate_mock_completion(db: Session, reminder: Reminder):
    """
    Simulate call completion for mock mode.
    
    Waits a few seconds then marks the call as completed with a mock transcript.
    """
    import asyncio
    import random
    
    # Simulate call duration (2-5 seconds)
    await asyncio.sleep(random.uniform(2, 5))
    
    try:
        # Refresh reminder from DB
        db.refresh(reminder)
        
        # Simulate success (90% of the time)
        is_success = random.random() < 0.95
        
        if is_success:
            # Mark as called
            reminder.status = ReminderStatus.CALLED
            
            # Create completion call log with mock transcript
            call_log = CallLog(
                reminder_id=reminder.id,
                external_call_id=reminder.external_call_id,
                status="completed",
                transcript=f"[MOCK TRANSCRIPT] Your reminder: {reminder.message}. Call duration: {random.randint(10, 30)} seconds."
            )
            db.add(call_log)
            db.commit()
            
            logger.info(
                f"🎭 [MOCK] Call completed for reminder {reminder.id}",
                extra={
                    "reminder_id": str(reminder.id),
                    "status": "completed"
                }
            )
        else:
            # Simulate failure
            reminder.status = ReminderStatus.FAILED
            
            call_log = CallLog(
                reminder_id=reminder.id,
                external_call_id=reminder.external_call_id,
                status="failed",
                transcript="[MOCK] Call failed - no answer"
            )
            db.add(call_log)
            db.commit()
            
            logger.warning(
                f"🎭 [MOCK] Call failed for reminder {reminder.id}",
                extra={
                    "reminder_id": str(reminder.id),
                    "status": "failed"
                }
            )
            
    except Exception as e:
        logger.error(f"Error simulating mock completion: {str(e)}", exc_info=True)
        db.rollback()


def run_scheduler_sync():
    """
    Synchronous wrapper for the async scheduler job.
    Called by APScheduler.
    """
    asyncio.run(process_due_reminders())
