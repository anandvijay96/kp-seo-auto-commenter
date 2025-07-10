import os
import logging
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from google.oauth2 import service_account

# Configure logging
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

class Settings(BaseSettings):
    # Base settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "KP SEO Auto Commenter"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Allow all origins in development
    
    # Database settings
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # RabbitMQ settings (optional for MVP)
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASS: Optional[str] = None

    # Google Cloud settings
    GCP_PROJECT_ID: str = "kp-seo-blog-automator"
    GCP_LOCATION: str = "us-central1"  # or your preferred region
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None  # Will be set in __init__
    GOOGLE_API_KEY: Optional[str] = None # For authenticating with Generative AI services
    
    # Gemini API settings
    GEMINI_API_KEY: Optional[str] = None  # Legacy API key for fallback
    GEMINI_MODEL: str = "gemini-1.0-pro"  # Using stable Vertex AI model
    USE_VERTEX_AI: bool = True  # Set to True to use Vertex AI instead of direct Gemini API
    
    @property
    def GCP_CREDENTIALS(self):
        """Load GCP credentials from the service account key file."""
        if not hasattr(self, '_credentials'):
            try:
                # Try alternative paths
                paths_to_try = [
                    self.GOOGLE_APPLICATION_CREDENTIALS,  # Original path
                    str(PROJECT_ROOT / "credentials" / "kp-seo-agent-key.json"),  # Local development
                    "/app/credentials/kp-seo-agent-key.json",  # Docker
                ]
                
                # If in WSL, add Windows-style path
                if os.name != 'nt' and str(PROJECT_ROOT).startswith('/mnt/'):
                    parts = str(PROJECT_ROOT).split('/')
                    if len(parts) > 3:
                        drive = parts[2].upper()
                        win_path = f"{drive}:/{'/'.join(parts[3:])}/credentials/kp-seo-agent-key.json"
                        paths_to_try.append(win_path)
                
                # Try all paths
                for path in paths_to_try:
                    if path and os.path.exists(path):
                        logger.info(f"Loading GCP credentials from: {path}")
                        self._credentials = service_account.Credentials.from_service_account_file(path)
                        return self._credentials
                
                # If no paths work, raise error with all attempted paths
                raise ValueError(f"Credentials file not found. Tried: {', '.join(str(p) for p in paths_to_try if p)}")
                
            except Exception as e:
                logger.error(f"Failed to load GCP credentials: {str(e)}")
                raise
        
        return self._credentials

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set credentials path based on environment
        if self.ENVIRONMENT == "development":
            # Local development path - use project root
            self.GOOGLE_APPLICATION_CREDENTIALS = str(PROJECT_ROOT / "credentials" / "kp-seo-agent-key.json")
        else:
            # Docker/production path
            self.GOOGLE_APPLICATION_CREDENTIALS = "/app/credentials/kp-seo-agent-key.json"
        
        logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to: {self.GOOGLE_APPLICATION_CREDENTIALS}")
        
        # Construct database URI if not provided
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

    class Config:
        env_file = ".env"

settings = Settings()