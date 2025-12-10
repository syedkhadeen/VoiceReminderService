"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Application health status with version and timestamp
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        Welcome message with API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
