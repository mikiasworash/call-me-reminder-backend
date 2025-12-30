from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="API is running")

