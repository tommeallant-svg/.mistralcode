from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class PlanBase(BaseModel):
    race_name: str
    race_date: datetime
    race_distance: float
    race_estimated_time: Optional[str] = None
    start_date: datetime
    sessions_per_week: int
    goal_type: str
    training_days: List[int]
    estimated_vma: float

class PlanCreate(PlanBase):
    pass

class PlanArchive(BaseModel):
    cancellation_comment: str

class PlanResponse(PlanBase):
    id: int
    athlete_id: int
    is_archived: bool
    cancellation_comment: Optional[str] = None

    class Config:
        from_attributes = True
