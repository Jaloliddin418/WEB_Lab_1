from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Task, TimeEntry, User
from app.schemas.schemas import TimeEntryCreate, TimeEntryOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/tasks/{task_id}/time-entries", tags=["time-entries"])


def _get_task_or_404(task_id: int, user_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TimeEntryOut, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    task_id: int,
    data: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimeEntryOut:
    _get_task_or_404(task_id, current_user.id, db)

    duration = None
    if data.ended_at:
        delta = data.ended_at - data.started_at
        duration = delta.total_seconds() / 60

    entry = TimeEntry(
        task_id=task_id,
        started_at=data.started_at,
        ended_at=data.ended_at,
        duration_minutes=duration,
        note=data.note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/", response_model=list[TimeEntryOut])
def list_time_entries(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TimeEntryOut]:
    _get_task_or_404(task_id, current_user.id, db)
    return db.query(TimeEntry).filter(TimeEntry.task_id == task_id).all()


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry(
    task_id: int,
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_task_or_404(task_id, current_user.id, db)
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id, TimeEntry.task_id == task_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    db.delete(entry)
    db.commit()
