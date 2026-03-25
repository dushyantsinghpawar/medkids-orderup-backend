from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ChildCreate(BaseModel):
    name: str
    age: int
    allergies: Optional[str] = None
    diet_preferences: Optional[str] = None
    dislikes: Optional[str] = None
    
    @field_validator("diet_preferences")
    @classmethod
    def validate_diet_preferences(cls, v):
        """Validate diet preferences against allowed values."""
        if not v:
            return v
        from app.constants import parse_diet_preferences
        parse_diet_preferences(v)
        return v

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    allergies: Optional[str] = None
    diet_preferences: Optional[str] = None
    dislikes: Optional[str] = None
    
    @field_validator("diet_preferences")
    @classmethod
    def validate_diet_preferences(cls, v):
        """Validate diet preferences against allowed values."""
        if not v:
            return v
        from app.constants import parse_diet_preferences
        parse_diet_preferences(v)
        return v

class ChildOut(BaseModel):
    id: int
    name: str
    age: int
    allergies: Optional[str]
    diet_preferences: Optional[str]
    dislikes: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    
    class Config:
        from_attributes = True