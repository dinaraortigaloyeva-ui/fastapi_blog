from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Engine - PostgreSQL ga ulanish
engine = create_engine(settings.database_url)

# Session - har bir so'rov uchun
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base - barcha modellar shu classdan meros oladi
Base = declarative_base()

# Dependency - har endpoint uchun DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()