from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChildCreate(BaseModel):
    name: str
    age: int
    allergies: Optional[str] = None

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    allergies: Optional[str] = None

class ChildOut(BaseModel):
    id: int
    name: str
    age: int
    allergies: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


    class Config:
        from_attributes = True
