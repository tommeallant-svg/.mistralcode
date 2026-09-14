import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.models.workout import Workout

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    # Clean existing workouts
    db.query(Workout).delete()
    
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
        db.add(workout)
    
    db.commit()
    print("Database seeded!")

if __name__ == "__main__":
    seed()
