from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Environment
    ENVIRONMENT: str = "production"  # Default to production if not set

    # Database
    DATABASE_URL: str

    # RabbitMQ
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    # Google Gemini
    GEMINI_API_KEY: str

settings = Settings()