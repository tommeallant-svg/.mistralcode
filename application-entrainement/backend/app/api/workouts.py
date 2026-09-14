from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.workout import Workout
from ..schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate, WorkoutValidation

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    db_workout = Workout(**workout.model_dump())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.get("/", response_model=List[WorkoutResponse])
def read_workouts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Workout).order_by(Workout.date.asc()).offset(skip).limit(limit).all()

@router.get("/{workout_id}", response_model=WorkoutResponse)
def read_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@router.patch("/{workout_id}", response_model=WorkoutResponse)
def update_workout(workout_id: int, workout: WorkoutUpdate, db: Session = Depends(get_db)):
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    update_data = workout.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_workout, key, value)
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.post("/{workout_id}/validate", response_model=WorkoutResponse)
def validate_workout(workout_id: int, validation: WorkoutValidation, db: Session = Depends(get_db)):
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db_workout.is_validated = True
    db_workout.perceived_difficulty = validation.perceived_difficulty
    db_workout.athlete_comment = validation.athlete_comment
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(db_workout)
    db.commit()
    return None
