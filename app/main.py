from fastapi import FastAPI

from app.routers import (
    analytics_router,
    auth_router,
    categories_router,
    schedules_router,
    tags_router,
    tasks_router,
    time_entries_router,
)

app = FastAPI(
    title="Time Manager API",
    description="API для управления задачами, временем и расписанием",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(tasks_router)
app.include_router(time_entries_router)
app.include_router(schedules_router)
app.include_router(analytics_router)


@app.get("/", tags=["root"])
def root() -> dict:
    return {"message": "Time Manager API is running"}
