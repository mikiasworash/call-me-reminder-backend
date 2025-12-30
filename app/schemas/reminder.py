from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import datetime, timezone
from typing import Optional
from phonenumbers import parse, is_valid_number, NumberParseException


class ReminderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=1000)
    phone_number: str = Field(..., min_length=1, max_length=20)
    scheduled_at: datetime
    timezone: str = Field(..., min_length=1, max_length=50)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        try:
            parsed = parse(v, None)
            if not is_valid_number(parsed):
                raise ValueError("Invalid phone number format")
            return v
        except NumberParseException:
            raise ValueError("Invalid phone number format. Use E.164 format (e.g., +14155552671)")

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v: datetime) -> datetime:
        from datetime import timezone
        # Handle both timezone-aware and timezone-naive datetimes
        now = datetime.now(timezone.utc)
        
        # If v is timezone-naive, assume it's UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        # Compare both as timezone-aware
        if v <= now:
            raise ValueError("Scheduled time must be in the future")
        
        # Return as timezone-aware UTC
        if v.tzinfo is not None:
            v = v.astimezone(timezone.utc)
        
        return v


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=20)
    scheduled_at: Optional[datetime] = None
    timezone: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            parsed = parse(v, None)
            if not is_valid_number(parsed):
                raise ValueError("Invalid phone number format")
            return v
        except NumberParseException:
            raise ValueError("Invalid phone number format. Use E.164 format (e.g., +14155552671)")

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        from datetime import timezone
        if v is None:
            return v
        
        # Handle both timezone-aware and timezone-naive datetimes
        now = datetime.now(timezone.utc)
        
        # If v is timezone-naive, assume it's UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        # Compare both as timezone-aware
        if v <= now:
            raise ValueError("Scheduled time must be in the future")
        
        # Return as timezone-aware UTC
        if v.tzinfo is not None:
            v = v.astimezone(timezone.utc)
        
        return v


class ReminderResponse(BaseModel):
    id: int
    title: str
    message: str
    phone_number: str
    scheduled_at: datetime
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    vapi_call_id: Optional[str] = None

    @field_serializer("scheduled_at", "created_at", "updated_at", "completed_at")
    def serialize_datetime(self, value: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime fields with Z suffix for UTC"""
        if value is None:
            return None
        if value.tzinfo is None:
            # Naive datetime - assume UTC and add Z
            return value.isoformat() + 'Z'
        # Aware datetime - convert to UTC and add Z
        utc_value = value.astimezone(timezone.utc)
        return utc_value.isoformat().replace('+00:00', 'Z')

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    success: bool = True
    data: list[ReminderResponse]
    message: Optional[str] = None


class ReminderSingleResponse(BaseModel):
    success: bool = True
    data: ReminderResponse
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
    message: Optional[str] = None

