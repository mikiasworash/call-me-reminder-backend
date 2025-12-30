from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.api.dependencies import get_database
from app.models.reminder import Reminder
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/reminders")
async def debug_reminders(db: Session = Depends(get_database)):
    """Debug endpoint to check all reminders and their status"""
    all_reminders = db.query(Reminder).all()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    result = {
        "current_utc_time": now.isoformat(),
        "total_reminders": len(all_reminders),
        "reminders": []
    }
    
    for reminder in all_reminders:
        is_due = reminder.scheduled_at <= now
        time_diff_seconds = (reminder.scheduled_at - now).total_seconds()
        time_diff_minutes = time_diff_seconds / 60
        
        result["reminders"].append({
            "id": reminder.id,
            "title": reminder.title,
            "status": reminder.status,
            "scheduled_at": reminder.scheduled_at.isoformat(),
            "timezone": reminder.timezone,
            "is_due": is_due,
            "time_diff_minutes": round(time_diff_minutes, 1),
            "phone_number": reminder.phone_number,
        })
    
    return result


@router.get("/due-check")
async def debug_due_check(db: Session = Depends(get_database)):
    """Check what the scheduler would find"""
    due_reminders = ReminderService.get_due_reminders(db)
    
    return {
        "due_reminders_count": len(due_reminders),
        "due_reminders": [
            {
                "id": r.id,
                "title": r.title,
                "scheduled_at": r.scheduled_at.isoformat(),
                "status": r.status,
            }
            for r in due_reminders
        ]
    }

