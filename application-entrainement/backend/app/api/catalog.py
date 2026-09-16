from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth import get_current_coach
from ..models.catalog import CatalogWorkout
from ..schemas.catalog import CatalogWorkoutCreate, CatalogWorkoutResponse, CatalogWorkoutUpdate

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("", response_model=List[CatalogWorkoutResponse])
def get_catalog(db: Session = Depends(get_db)):
    return db.query(CatalogWorkout).all()
