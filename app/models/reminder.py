from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="scheduled", index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    vapi_call_id = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_scheduled_at", "scheduled_at"),
        Index("idx_status", "status"),
    )

