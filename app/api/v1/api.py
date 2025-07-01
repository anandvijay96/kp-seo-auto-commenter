from fastapi import APIRouter
from .endpoints import missions

api_router = APIRouter()
api_router.include_router(missions.router, prefix="/missions", tags=["Missions"])
