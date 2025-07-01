from pydantic import BaseModel
from .models.models import MissionStatus
import datetime

class MissionBase(BaseModel):
    goal: str

class MissionCreate(MissionBase):
    pass

class Mission(MissionBase):
    id: int
    status: MissionStatus
    result: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

    class Config:
        from_attributes = True # For Pydantic v2
