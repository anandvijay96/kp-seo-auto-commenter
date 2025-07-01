from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # RabbitMQ
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    # Google Gemini
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
