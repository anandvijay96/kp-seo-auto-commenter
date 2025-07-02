from fastapi import APIRouter
from .endpoints import missions, agent

api_router = APIRouter()
api_router.include_router(missions.router, prefix="/missions", tags=["Missions"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])