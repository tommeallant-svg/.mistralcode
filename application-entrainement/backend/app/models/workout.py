from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from datetime import datetime
from ..database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    workout_type = Column(String, index=True)  # Endurance, Tempo, Seuil, VO2 Max, Sprint
    name = Column(String, index=True)
    duration_minutes = Column(Integer)
    difficulty_level = Column(Integer)  # 1 to 10
    description_short = Column(String)
    description_long = Column(Text)
    
    # Training scheme stored as JSON
    # Structure example: [{"type": "interval", "pace": "4:00", "duration": 5, "distance": 1.25, "repetitions": 1}]
    scheme = Column(JSON, nullable=True)
    
    # Execution data
    date = Column(DateTime, index=True)
    is_validated = Column(Boolean, default=False)
    perceived_difficulty = Column(Integer, nullable=True)
    athlete_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
