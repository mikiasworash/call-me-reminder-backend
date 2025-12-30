import asyncio
import logging
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import SessionLocal
from app.services.reminder_service import ReminderService
from app.services.vapi_service import VapiService

# Configure logging to show scheduler logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

scheduler = BackgroundScheduler()
vapi_service = VapiService()


async def process_due_reminders():
    """Process reminders that are due"""
    db = SessionLocal()
    try:
        logger.info("=" * 60)
        logger.info("SCHEDULER: Checking for due reminders...")
        due_reminders = ReminderService.get_due_reminders(db)
        logger.info(f"SCHEDULER: Found {len(due_reminders)} due reminders")

        if len(due_reminders) == 0:
            logger.info("SCHEDULER: No due reminders to process")
            return

        for reminder in due_reminders:
            try:
                logger.info("-" * 60)
                logger.info(f"SCHEDULER: Processing reminder {reminder.id}: '{reminder.title}'")
                logger.info(f"SCHEDULER: Phone: {reminder.phone_number}")
                logger.info(f"SCHEDULER: Message: {reminder.message}")
                logger.info(f"SCHEDULER: Scheduled at: {reminder.scheduled_at}")
                
                # Create Vapi call
                logger.info("SCHEDULER: Creating Vapi call...")
                call_id = await vapi_service.create_call(
                    phone_number=reminder.phone_number,
                    message=reminder.message,
                    reminder_id=reminder.id,
                )

                # Mark as completed
                ReminderService.mark_completed(db, reminder.id, call_id)
                logger.info(f"SCHEDULER: ✓ Reminder {reminder.id} marked as completed")
                logger.info(f"SCHEDULER: ✓ Vapi call ID: {call_id}")
                logger.info("-" * 60)

            except Exception as e:
                error_msg = f"Failed to process reminder {reminder.id}: {str(e)}"
                logger.error("=" * 60)
                logger.error(f"SCHEDULER ERROR: {error_msg}")
                logger.error(f"SCHEDULER ERROR: Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"SCHEDULER ERROR: Traceback:\n{traceback.format_exc()}")
                logger.error("=" * 60)
                ReminderService.mark_failed(db, reminder.id, error_msg)

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"SCHEDULER FATAL ERROR: {str(e)}")
        import traceback
        logger.error(f"SCHEDULER FATAL ERROR: Traceback:\n{traceback.format_exc()}")
        logger.error("=" * 60)
    finally:
        db.close()
        logger.info("SCHEDULER: Finished processing cycle")
        logger.info("=" * 60)


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
    logger.info("=" * 60)
    logger.info("SCHEDULER STARTED - Checking for due reminders every minute")
    logger.info("=" * 60)
    
    # Log scheduler status
    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"Scheduled job: {job.name} (next run: {job.next_run_time})")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

