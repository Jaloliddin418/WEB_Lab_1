from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Task, TaskStatus, TimeEntry, User
from app.schemas.schemas import AnalyticsOut, TaskTimeStats
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalyticsOut:
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()

    total_tasks = len(tasks)
    done_tasks = sum(1 for t in tasks if t.status == TaskStatus.done)
    now = datetime.utcnow()
    overdue_tasks = sum(
        1 for t in tasks
        if t.deadline and t.deadline < now and t.status != TaskStatus.done
    )

    per_task: list[TaskTimeStats] = []
    total_tracked = 0.0

    for task in tasks:
        entries = db.query(TimeEntry).filter(TimeEntry.task_id == task.id).all()
        minutes = sum(e.duration_minutes or 0.0 for e in entries)
        total_tracked += minutes
        if entries:
            per_task.append(
                TaskTimeStats(
                    task_id=task.id,
                    title=task.title,
                    total_minutes=round(minutes, 2),
                    entry_count=len(entries),
                )
            )

    per_task.sort(key=lambda x: x.total_minutes, reverse=True)

    return AnalyticsOut(
        total_tasks=total_tasks,
        done_tasks=done_tasks,
        overdue_tasks=overdue_tasks,
        total_tracked_minutes=round(total_tracked, 2),
        per_task=per_task,
    )
