from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.routes import reminders, health
from app.api.routes import debug
from app.scheduler.reminder_scheduler import start_scheduler, stop_scheduler

# Initialize database
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title="Call Me Reminder API",
    description="API for managing reminders with automated voice calls",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
# Default origins for development
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# Use configured origins or defaults
cors_origins = settings.cors_origins_list if hasattr(settings, 'cors_origins_list') else default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reminders.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(debug.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Call Me Reminder API", "version": "1.0.0"}

