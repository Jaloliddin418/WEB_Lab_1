from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.models import Priority, TaskStatus


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class CategoryOut(BaseModel):
    id: int
    name: str
    color: str
    user_id: int

    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    name: str


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}



class TaskTagOut(BaseModel):
    tag_id: int
    tag: TagOut
    added_at: datetime

    model_config = {"from_attributes": True}


class TimeEntryCreate(BaseModel):
    started_at: datetime
    ended_at: Optional[datetime] = None
    note: Optional[str] = None


class TimeEntryOut(BaseModel):
    id: int
    task_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    duration_minutes: Optional[float]
    note: Optional[str]

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    schedule_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    schedule_id: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    status: TaskStatus
    deadline: Optional[datetime]
    estimated_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    owner_id: int
    category_id: Optional[int]
    schedule_id: Optional[int]
    category: Optional[CategoryOut]
    task_tags: list[TaskTagOut]
    time_entries: list[TimeEntryOut]

    model_config = {"from_attributes": True}


class DailyScheduleCreate(BaseModel):
    date: datetime
    note: Optional[str] = None


class DailyScheduleOut(BaseModel):
    id: int
    user_id: int
    date: datetime
    note: Optional[str]
    tasks: list[TaskOut]

    model_config = {"from_attributes": True}


class TaskTimeStats(BaseModel):
    task_id: int
    title: str
    total_minutes: float
    entry_count: int


class AnalyticsOut(BaseModel):
    total_tasks: int
    done_tasks: int
    overdue_tasks: int
    total_tracked_minutes: float
    per_task: list[TaskTimeStats]
