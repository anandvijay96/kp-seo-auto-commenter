from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
print("ENVIRONMENT:", settings.ENVIRONMENT)

app = FastAPI(
    title="KloudPortal SEO Blog Automator",
    description="API for managing blog discovery, comment generation, and submission.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the KloudPortal SEO API"}

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8500,
        reload=True,
        log_level="info"
    )
