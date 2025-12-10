"""
Voice Reminder Service - Worker Service

FastAPI application with APScheduler for processing reminders.
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pythonjsonlogger import jsonlogger
import time

from app.config import settings
from app.routes.webhooks import router as webhooks_router
from app.scheduler.reminder_scheduler import run_scheduler_sync


# Configure logging
def setup_logging():
    """Configure structured JSON logging."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler("worker.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


setup_logging()
logger = logging.getLogger(__name__)

# APScheduler instance
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Voice Reminder Worker Service")
    logger.info(f"Scheduler interval: {settings.SCHEDULER_INTERVAL_SECONDS} seconds")
    
    # Start the scheduler
    scheduler.add_job(
        run_scheduler_sync,
        trigger=IntervalTrigger(seconds=settings.SCHEDULER_INTERVAL_SECONDS),
        id="process_due_reminders",
        name="Process Due Reminders",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown scheduler
    logger.info("Shutting down scheduler...")
    scheduler.shutdown(wait=False)
    logger.info("Worker service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Voice Reminder Worker Service - Processes reminders and handles webhooks",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()
    
    logger.info(
        f"Request started",
        extra={
            "method": request.method,
            "path": request.url.path
        }
    )
    
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2)
        }
    )
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    scheduler_running = scheduler.running
    return {
        "status": "healthy" if scheduler_running else "degraded",
        "service": "worker",
        "scheduler": "running" if scheduler_running else "stopped",
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


# Include routers
app.include_router(webhooks_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
