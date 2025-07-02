from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Environment
    ENVIRONMENT: str = "production"  # Default to production if not set

    # Database
    DATABASE_URL: str

    # RabbitMQ
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASS: Optional[str] = None

    # Google Gemini
    GEMINI_API_KEY: str

settings = Settings()