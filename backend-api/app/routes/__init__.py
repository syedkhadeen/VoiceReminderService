"""API route modules."""
from app.routes.users import router as users_router
from app.routes.reminders import router as reminders_router
from app.routes.health import router as health_router

__all__ = ["users_router", "reminders_router", "health_router"]
