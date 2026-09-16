import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.models.workout import Workout
from app.models.user import User
from app.models.plan import Plan
from app.models.catalog import CatalogWorkout
from app.auth import get_password_hash

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    # Clean existing data
    db.query(Workout).delete()
    db.query(Plan).delete()
    db.query(User).delete()
    db.query(CatalogWorkout).delete()

    # Create users
    coach = User(
        email="tom.meallant@gmail.com",
        hashed_password=get_password_hash("ToML2Bégé"),
        role="coach"
    )
    athlete = User(
        email="paloma.mouyade@gmail.com",
        hashed_password=get_password_hash("Pal0LaPl0uBéL"),
        role="athlete"
    )
    db.add(coach)
    db.add(athlete)
    db.commit()
    db.refresh(coach)
    db.refresh(athlete)
    
    # Create default catalog workouts
    catalog_workouts = [
        {
            "name": "VMA Courte 30/30",
            "workout_type": "VO2 Max",
            "category": "Fractionné",
            "perceived_difficulty": 8,
            "scheme": [
                {"type": "Echauffement", "duration": 15, "pace_vma": 65, "repetitions": 1},
                {"type": "Vite", "duration": 0.5, "pace_vma": 105, "repetitions": 10},
                {"type": "Lent", "duration": 0.5, "pace_vma": 60, "repetitions": 10},
                {"type": "Retour calme", "duration": 10, "pace_vma": 65, "repetitions": 1}
            ]
        },
        {
            "name": "VMA Longue 1000m",
            "workout_type": "Seuil",
            "category": "Fractionné",
            "perceived_difficulty": 7,
            "scheme": [
                {"type": "Echauffement", "duration": 20, "pace_vma": 65, "repetitions": 1},
                {"type": "Fraction", "duration": 4, "pace_vma": 90, "repetitions": 5},
                {"type": "Récup", "duration": 2, "pace_vma": 60, "repetitions": 5},
                {"type": "Retour calme", "duration": 10, "pace_vma": 65, "repetitions": 1}
            ]
        }
    ]
    for cw_data in catalog_workouts:
        cw = CatalogWorkout(**cw_data)
        db.add(cw)
    db.commit()
    
    today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    
    workouts = [
        {
            "workout_type": "Endurance",
            "name": "Footing de récupération",
            "duration_minutes": 45,
            "difficulty_level": 3,
            "description_short": "Footing lent en zone 2 pour récupérer.",
            "description_long": "L'objectif est de rester sous les 75% de FCM. Relâchement total des épaules et respiration fluide.",
            "date": today - timedelta(days=today.weekday()), # Monday
            "scheme": [
                {"type": "Echauffement", "pace": "6:00", "duration": 10, "repetitions": 1},
                {"type": "Corps de séance", "pace": "5:45", "duration": 30, "repetitions": 1},
                {"type": "Retour au calme", "pace": "6:15", "duration": 5, "repetitions": 1}
            ]
        },
        {
            "workout_type": "Seuil",
            "name": "Blocs au seuil anaérobie",
            "duration_minutes": 60,
            "difficulty_level": 7,
            "description_short": "3 x 10 minutes au seuil, récup 2 min.",
            "description_long": "Travailler l'endurance à haute intensité. Le cardio doit monter progressivement vers le seuil.",
            "date": today - timedelta(days=today.weekday() - 2), # Wednesday
            "scheme": [
                {"type": "Echauffement", "pace": "5:30", "duration": 15, "repetitions": 1},
                {"type": "Fractionné", "pace": "4:05", "duration": 10, "repetitions": 3},
                {"type": "Récupération", "pace": "6:30", "duration": 2, "repetitions": 3},
                {"type": "Retour au calme", "pace": "6:00", "duration": 5, "repetitions": 1}
            ]
        },
        {
            "workout_type": "VO2 Max",
            "name": "VMA Courte 30/30",
            "duration_minutes": 50,
            "difficulty_level": 9,
            "description_short": "2 séries de 10 x (30s vite / 30s lent).",
            "description_long": "Séance intense pour développer la consommation maximale d'oxygène. Vitesse cible 105% VMA.",
            "date": today - timedelta(days=today.weekday() - 4), # Friday
            "scheme": [
                {"type": "Echauffement", "pace": "5:45", "duration": 20, "repetitions": 1},
                {"type": "Sprint", "pace": "3:20", "duration": 0.5, "repetitions": 20},
                {"type": "Récup", "pace": "7:00", "duration": 0.5, "repetitions": 20},
                {"type": "Retour au calme", "pace": "6:00", "duration": 10, "repetitions": 1}
            ]
        },
        {
            "workout_type": "Endurance",
            "name": "Sortie Longue",
            "duration_minutes": 90,
            "difficulty_level": 5,
            "description_short": "Sortie plaisir en forêt.",
            "description_long": "Maintenir une allure stable, tester le ravitaillement pour la prochaine course.",
            "date": today - timedelta(days=today.weekday() - 6), # Sunday
            "scheme": [
                {"type": "Endurance", "pace": "5:30", "duration": 90, "repetitions": 1}
            ]
        }
    ]
    
    for w_data in workouts:
        workout = Workout(**w_data)
        workout.athlete_id = athlete.id
        db.add(workout)
    
    db.commit()
    print("Database seeded!")

if __name__ == "__main__":
    seed()
