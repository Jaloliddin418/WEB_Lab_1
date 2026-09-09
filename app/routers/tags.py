from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Tag, User
from app.schemas.schemas import TagCreate, TagOut
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TagOut:
    existing = db.query(Tag).filter(Tag.name == data.name).first()
    if existing:
        return existing
    tag = Tag(name=data.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("/", response_model=list[TagOut])
def list_tags(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[TagOut]:
    return db.query(Tag).all()


@router.get("/{tag_id}", response_model=TagOut)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TagOut:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
