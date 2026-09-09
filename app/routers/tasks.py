from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Tag, Task, TaskTag, User
from app.schemas.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_or_404(task_id: int, user_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    task = Task(**data.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=list[TaskOut])
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskOut]:
    q = db.query(Task).filter(Task.owner_id == current_user.id)
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    if category_id:
        q = q.filter(Task.category_id == category_id)
    if overdue_only:
        q = q.filter(Task.deadline < datetime.utcnow(), Task.status != "done")
    return q.all()


@router.get("/upcoming-deadlines", response_model=list[TaskOut])
def upcoming_deadlines(
    hours: int = Query(24, description="How many hours ahead to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskOut]:
    """Возвращает задачи с дедлайном в ближайшие N часов (уведомления о дедлайнах)."""
    now = datetime.utcnow()
    threshold = now + timedelta(hours=hours)
    return (
        db.query(Task)
        .filter(
            Task.owner_id == current_user.id,
            Task.deadline >= now,
            Task.deadline <= threshold,
            Task.status != "done",
        )
        .order_by(Task.deadline)
        .all()
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    return _get_task_or_404(task_id, current_user.id, db)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    task = _get_task_or_404(task_id, current_user.id, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    task = _get_task_or_404(task_id, current_user.id, db)
    db.delete(task)
    db.commit()


# ---------- Tag management on tasks ----------

@router.post("/{task_id}/tags/{tag_id}", response_model=TaskOut)
def add_tag_to_task(
    task_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    task = _get_task_or_404(task_id, current_user.id, db)
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    already = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
    if not already:
        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        db.add(task_tag)
        db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}/tags/{tag_id}", response_model=TaskOut)
def remove_tag_from_task(
    task_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    task = _get_task_or_404(task_id, current_user.id, db)
    task_tag = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
    if not task_tag:
        raise HTTPException(status_code=404, detail="Tag not attached to this task")
    db.delete(task_tag)
    db.commit()
    db.refresh(task)
    return task
