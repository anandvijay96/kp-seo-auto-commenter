import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Load environment variables from .env file
load_dotenv()

from app.api.v1.api import api_router
from app.core.config import settings
from app.api.v1.endpoints import agent as agent_v1
print("ENVIRONMENT:", settings.ENVIRONMENT)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add a new endpoint to serve the new_ui.html file
@app.get("/new-ui")
async def read_new_ui():
    return FileResponse('frontend/new_ui.html')

# Add a root endpoint to serve the index.html file
@app.get("/", response_class=FileResponse)
async def read_index():
    return FileResponse("frontend/index.html")

# Add a health endpoint
@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}

# Add CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

app.include_router(api_router, prefix="/api/v1")

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8500,
        reload=True,
        log_level="info"
    )
