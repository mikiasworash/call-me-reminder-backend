from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.routes import reminders, health
from app.scheduler.reminder_scheduler import start_scheduler

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Call Me Reminder API",
    description="API for managing reminders with automated voice calls",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reminders.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Start scheduler on application startup"""
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    pass


@app.get("/")
async def root():
    return {"message": "Call Me Reminder API", "version": "1.0.0"}

