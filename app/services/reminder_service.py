from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone
from typing import Optional
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate


class ReminderService:
    @staticmethod
    def create(db: Session, reminder: ReminderCreate) -> Reminder:
        """Create a new reminder"""
        # Convert timezone-aware datetime to UTC naive for storage
        scheduled_at = reminder.scheduled_at
        if scheduled_at.tzinfo is not None:
            scheduled_at = scheduled_at.astimezone(timezone.utc).replace(tzinfo=None)
        
        db_reminder = Reminder(
            title=reminder.title,
            message=reminder.message,
            phone_number=reminder.phone_number,
            scheduled_at=scheduled_at,
            timezone=reminder.timezone,
            status="scheduled",
        )
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    @staticmethod
    def get_all(
        db: Session,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Reminder]:
        """Get all reminders with optional filtering"""
        query = db.query(Reminder)

        # Filter by status
        if status and status != "all":
            query = query.filter(Reminder.status == status)

        # Search by title or message
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Reminder.title.ilike(search_term),
                    Reminder.message.ilike(search_term),
                )
            )

        # Sort
        if sort == "asc":
            query = query.order_by(Reminder.scheduled_at.asc())
        else:
            query = query.order_by(Reminder.scheduled_at.desc())

        # Pagination
        return query.offset(offset).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, reminder_id: int) -> Optional[Reminder]:
        """Get reminder by ID"""
        return db.query(Reminder).filter(Reminder.id == reminder_id).first()

    @staticmethod
    def update(db: Session, reminder_id: int, reminder_update: ReminderUpdate) -> Optional[Reminder]:
        """Update a reminder"""
        db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not db_reminder:
            return None

        update_data = reminder_update.model_dump(exclude_unset=True)
        
        # Handle timezone-aware datetime conversion for scheduled_at
        if 'scheduled_at' in update_data and update_data['scheduled_at'] is not None:
            scheduled_at = update_data['scheduled_at']
            if scheduled_at.tzinfo is not None:
                update_data['scheduled_at'] = scheduled_at.astimezone(timezone.utc).replace(tzinfo=None)
        
        for field, value in update_data.items():
            setattr(db_reminder, field, value)

        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    @staticmethod
    def delete(db: Session, reminder_id: int) -> bool:
        """Delete a reminder"""
        db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not db_reminder:
            return False

        db.delete(db_reminder)
        db.commit()
        return True

    @staticmethod
    def get_due_reminders(db: Session) -> list[Reminder]:
        """Get reminders that are due (scheduled_at <= now and status is scheduled)"""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (
            db.query(Reminder)
            .filter(Reminder.scheduled_at <= now)
            .filter(Reminder.status == "scheduled")
            .all()
        )

    @staticmethod
    def mark_completed(db: Session, reminder_id: int, vapi_call_id: Optional[str] = None) -> Optional[Reminder]:
        """Mark reminder as completed"""
        db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not db_reminder:
            return None

        db_reminder.status = "completed"
        db_reminder.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if vapi_call_id:
            db_reminder.vapi_call_id = vapi_call_id

        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    @staticmethod
    def mark_failed(db: Session, reminder_id: int, failure_reason: str) -> Optional[Reminder]:
        """Mark reminder as failed"""
        db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not db_reminder:
            return None

        db_reminder.status = "failed"
        db_reminder.failure_reason = failure_reason

        db.commit()
        db.refresh(db_reminder)
        return db_reminder

