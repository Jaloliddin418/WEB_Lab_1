from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import DailySchedule, User
from app.schemas.schemas import DailyScheduleCreate, DailyScheduleOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("/", response_model=DailyScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    data: DailyScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyScheduleOut:
    schedule = DailySchedule(**data.model_dump(), user_id=current_user.id)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/", response_model=list[DailyScheduleOut])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DailyScheduleOut]:
    return db.query(DailySchedule).filter(DailySchedule.user_id == current_user.id).all()


@router.get("/{schedule_id}", response_model=DailyScheduleOut)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyScheduleOut:
    schedule = db.query(DailySchedule).filter(
        DailySchedule.id == schedule_id,
        DailySchedule.user_id == current_user.id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    schedule = db.query(DailySchedule).filter(
        DailySchedule.id == schedule_id,
        DailySchedule.user_id == current_user.id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(schedule)
    db.commit()
