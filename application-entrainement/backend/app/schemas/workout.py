from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime

class WorkoutBase(BaseModel):
    workout_type: str
    name: str
    duration_minutes: int
    difficulty_level: int = Field(..., ge=1, le=10)
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    scheme: Optional[List[Any]] = None
    date: datetime

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    workout_type: Optional[str] = None
    name: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[int] = None
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    scheme: Optional[List[Any]] = None
    date: Optional[datetime] = None
    is_validated: Optional[bool] = None
    perceived_difficulty: Optional[int] = Field(None, ge=1, le=10)
    athlete_comment: Optional[str] = None

class WorkoutValidation(BaseModel):
    perceived_difficulty: int = Field(..., ge=1, le=10)
    athlete_comment: Optional[str] = None

class WorkoutResponse(WorkoutBase):
    id: int
    is_validated: bool
    perceived_difficulty: Optional[int] = None
    athlete_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
