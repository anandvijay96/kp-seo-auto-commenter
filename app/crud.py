from sqlalchemy.orm import Session
from .models import models
from . import schemas


def create_mission(db: Session, mission: schemas.MissionCreate):
    db_mission = models.Mission(**mission.model_dump())
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission
