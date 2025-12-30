import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import SessionLocal
from app.services.reminder_service import ReminderService
from app.services.vapi_service import VapiService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
vapi_service = VapiService()


async def process_due_reminders():
    """Process reminders that are due"""
    db = SessionLocal()
    try:
        due_reminders = ReminderService.get_due_reminders(db)
        logger.info(f"Found {len(due_reminders)} due reminders")

        for reminder in due_reminders:
            try:
                logger.info(f"Processing reminder {reminder.id}: {reminder.title}")
                
                # Create Vapi call
                call_id = await vapi_service.create_call(
                    phone_number=reminder.phone_number,
                    message=reminder.message,
                    reminder_id=reminder.id,
                )

                # Mark as completed
                ReminderService.mark_completed(db, reminder.id, call_id)
                logger.info(f"Reminder {reminder.id} marked as completed. Call ID: {call_id}")

            except Exception as e:
                error_msg = f"Failed to process reminder {reminder.id}: {str(e)}"
                logger.error(error_msg)
                ReminderService.mark_failed(db, reminder.id, error_msg)

    except Exception as e:
        logger.error(f"Error processing due reminders: {str(e)}")
    finally:
        db.close()


def run_scheduler():
    """Run the scheduler task"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(process_due_reminders())


def start_scheduler():
    """Start the background scheduler"""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    # Schedule job to run every minute
    scheduler.add_job(
        run_scheduler,
        trigger=IntervalTrigger(minutes=1),
        id="process_reminders",
        name="Process due reminders",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started - checking for due reminders every minute")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

