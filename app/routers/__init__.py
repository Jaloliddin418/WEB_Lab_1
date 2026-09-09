from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.schedules import router as schedules_router
from app.routers.tags import router as tags_router
from app.routers.tasks import router as tasks_router
from app.routers.time_entries import router as time_entries_router

__all__ = [
    "auth_router",
    "categories_router",
    "tags_router",
    "tasks_router",
    "time_entries_router",
    "schedules_router",
    "analytics_router",
]
