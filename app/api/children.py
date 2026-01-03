from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.user import User
from app.schemas.child import ChildCreate, ChildUpdate, ChildOut

router = APIRouter(
    prefix="/children",
    tags=["children"]
)


@router.post("/", response_model=ChildOut)
def create_child(
    data: ChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = Child(
        name=data.name,
        age=data.age,
        allergies=data.allergies,
        parent_id=current_user.id,
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@router.get("/", response_model=list[ChildOut])
def list_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    return (
        db.query(Child)
        .filter(
            Child.parent_id == current_user.id,
            Child.deleted_at.is_(None),
        )
        .order_by(Child.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


@router.put("/{child_id}", response_model=ChildOut)
def update_child(
    child_id: int,
    data: ChildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = (
        db.query(Child)
        .filter(
            Child.id == child_id,
            Child.parent_id == current_user.id,
            Child.deleted_at.is_(None),
        )
        .first()
    )

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    if data.name is not None:
        child.name = data.name
    if data.age is not None:
        child.age = data.age
    if data.allergies is not None:
        child.allergies = data.allergies

    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = (
        db.query(Child)
        .filter(
            Child.id == child_id,
            Child.parent_id == current_user.id,
            Child.deleted_at.is_(None),
        )
        .first()
    )

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    child.deleted_at = datetime.utcnow()
    db.commit()
    return None


@router.post("/{child_id}/restore", response_model=ChildOut)
def restore_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    child = (
        db.query(Child)
        .filter(
            Child.id == child_id,
            Child.parent_id == current_user.id,
            Child.deleted_at.isnot(None),
        )
        .first()
    )

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted child not found",
        )

    child.deleted_at = None
    db.commit()
    db.refresh(child)
    return child