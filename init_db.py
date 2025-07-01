import logging

from app.core.database import engine, SessionLocal
from app.models.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_db()
