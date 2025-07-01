from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Mission)
def create_mission_endpoint(mission: schemas.MissionCreate, db: Session = Depends(get_db)):
    # In the future, this endpoint will trigger the agent's execution loop.
    return crud.create_mission(db=db, mission=mission)
