from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..auth import get_current_user
from ..models.user import User
from ..models.plan import Plan
from ..schemas.plan import PlanCreate, PlanResponse, PlanArchive

from ..models.catalog import CatalogWorkout
from ..services.plan_generator import PlanGenerator
from ..models.workout import Workout

router = APIRouter(prefix="/plans", tags=["plans"])

@router.get("/current", response_model=Optional[PlanResponse])
def get_current_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Plan).filter(Plan.athlete_id == current_user.id, Plan.is_archived == False).first()

@router.post("", response_model=PlanResponse)
def create_plan(plan_in: PlanCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Vérifier s'il y a déjà un plan actif
    active_plan = db.query(Plan).filter(Plan.athlete_id == current_user.id, Plan.is_archived == False).first()
    if active_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un plan actif existe déjà.")
    
    db_plan = Plan(**plan_in.model_dump(), athlete_id=current_user.id)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Récupérer le catalogue
    catalog = db.query(CatalogWorkout).all()
    
    # Générer les entraînements
    generator = PlanGenerator(db, db_plan, catalog)
    workouts = generator.generate()
    
    for workout in workouts:
        workout.plan_id = db_plan.id
        db.add(workout)
    
    db.commit()
    return db_plan

@router.post("/{plan_id}/archive", response_model=PlanResponse)
def archive_plan(plan_id: int, archive_data: PlanArchive, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id, Plan.athlete_id == current_user.id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan non trouvé")
    
    db_plan.is_archived = True
    db_plan.cancellation_comment = archive_data.cancellation_comment
    
    # Optionnel: Supprimer les séances futures non validées du calendrier ? 
    # L'énoncé dit : "son plan ne s'affiche plus dans le calendrier"
    # On peut filtrer dans la route /workouts pour ne pas renvoyer les séances des plans archivés.
    
    db.commit()
    db.refresh(db_plan)
    return db_plan
