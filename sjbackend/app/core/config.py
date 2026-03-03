# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from typing import Optional, List
import secrets
import os

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "SiriusJobs API"
    VERSION: str = "2.0.0"
    API_V2_PREFIX: str = "/api/v2"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    PORT: int = 4000
    HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    # Change from MySQL to PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/siriusjobs_v2")
    @property
    def database_url_with_ssl(self) -> str:
        """Add SSL requirement for Render"""
        if "render.com" in self.DATABASE_URL:
            return self.DATABASE_URL + "?sslmode=require"
        return self.DATABASE_URL
    
    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5500"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v, values):
        # Check if we're in development mode and using default key
        env_file = os.getenv("ENVIRONMENT", "development")
        if v == "your-super-secret-key-change-in-production" and env_file == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from env file

# Create global settings object
try:
    settings = Settings()
    print(f"✅ Configuration loaded successfully")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔌 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    print("Please check your .env file and ensure all required variables are set.")

    raisepython
