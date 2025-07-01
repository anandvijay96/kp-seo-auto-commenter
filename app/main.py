from fastapi import FastAPI

app = FastAPI(
    title="KloudPortal SEO Blog Commenting Automation API",
    description="API for managing blog discovery, comment generation, and submission.",
    version="0.1.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the KloudPortal SEO API"}

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
