from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.user import User
from app.schemas.child import ChildCreate, ChildOut

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
):
    return db.query(Child).filter(Child.parent_id == current_user.id).all()
