from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.dependencies import get_database
from app.services.reminder_service import ReminderService
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse,
    ReminderSingleResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("", response_model=ReminderSingleResponse, status_code=201)
async def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_database),
):
    """Create a new reminder"""
    try:
        db_reminder = ReminderService.create(db, reminder)
        return ReminderSingleResponse(
            success=True,
            data=ReminderResponse.model_validate(db_reminder),
            message="Reminder created successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reminder: {str(e)}")


@router.get("", response_model=ReminderListResponse)
async def get_reminders(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by title or message"),
    sort: str = Query("asc", description="Sort order: asc or desc"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_database),
):
    """Get all reminders with optional filtering"""
    try:
        reminders = ReminderService.get_all(db, status, search, sort, limit, offset)
        return ReminderListResponse(
            success=True,
            data=[ReminderResponse.model_validate(r) for r in reminders],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reminders: {str(e)}")


@router.get("/{reminder_id}", response_model=ReminderSingleResponse)
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_database),
):
    """Get a single reminder by ID"""
    reminder = ReminderService.get_by_id(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderSingleResponse(
        success=True,
        data=ReminderResponse.model_validate(reminder),
    )


@router.patch("/{reminder_id}", response_model=ReminderSingleResponse)
async def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    db: Session = Depends(get_database),
):
    """Update a reminder"""
    try:
        updated_reminder = ReminderService.update(db, reminder_id, reminder_update)
        if not updated_reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return ReminderSingleResponse(
            success=True,
            data=ReminderResponse.model_validate(updated_reminder),
            message="Reminder updated successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update reminder: {str(e)}")


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_database),
):
    """Delete a reminder"""
    success = ReminderService.delete(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")

