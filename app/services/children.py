from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.child import Child

def get_child_for_parent(
    db: Session,
    child_id: int,
    parent_id: int
) -> Child:
    child = (
        db.query(Child)
        .filter(
            Child.id == child_id,
            Child.parent_id == parent_id
        )
        .first()
    )

    if not child:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this child"
        )

    return child