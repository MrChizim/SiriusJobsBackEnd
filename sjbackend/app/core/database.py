# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Add SSL for Render
database_url = settings.DATABASE_URL
if "render.com" in database_url and "sslmode" not in database_url:
    database_url += "?sslmode=require"

engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()