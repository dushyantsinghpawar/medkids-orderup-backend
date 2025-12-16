from pydantic import BaseModel
from typing import Optional


class ChildCreate(BaseModel):
    name: str
    age: int
    allergies: Optional[str] = None


class ChildOut(BaseModel):
    id: int
    name: str
    age: int
    allergies: Optional[str]

    class Config:
        from_attributes = True
