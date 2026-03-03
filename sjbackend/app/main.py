# app/main.py - Add Depends to the import
from fastapi import FastAPI, Depends  # Add Depends here
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from sqlalchemy.orm import Session  # Add this if not already present

from app.core.config import settings
from app.core.database import engine, get_db  # Make sure get_db is imported
from app.models import base
from app.models.user import User
from app.api.v2 import (
    auth_router, 
    workers_router, 
    employers_router, 
    jobs_router, 
    applications_router,
    stats_router, 
    ratings_router,
    merchants_router
)
from app.core.response import success_response


# Setup logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting SiriusJobs API v2...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Create database tables
    base.Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down SiriusJobs API...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SiriusJobs API v2 - Connecting verified professionals, artisans, and businesses across Nigeria.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix=settings.API_V2_PREFIX)
app.include_router(workers_router, prefix=settings.API_V2_PREFIX)
app.include_router(employers_router, prefix=settings.API_V2_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V2_PREFIX)
app.include_router(applications_router, prefix=settings.API_V2_PREFIX)  # Add this
app.include_router(stats_router, prefix=settings.API_V2_PREFIX)
app.include_router(ratings_router, prefix=settings.API_V2_PREFIX)
app.include_router(merchants_router, prefix=settings.API_V2_PREFIX)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return success_response(
        data={
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            },
            "endpoints": {
                "auth": f"{settings.API_V2_PREFIX}/auth",
                "workers": f"{settings.API_V2_PREFIX}/workers",
            }
        },
        message="Welcome to SiriusJobs API v2"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": str(datetime.utcnow())
    }

@app.get("/public/stats")
async def get_public_statistics(db: Session = Depends(get_db)):
    """Public endpoint for homepage statistics"""
    from app.models.user import User, AccountType
    from app.models.job import Job
    
    total_users = db.query(User).filter(User.is_active == True).count()
    
    active_workers = db.query(User).filter(
        User.account_type == AccountType.WORKER,
        User.is_active == True,
        User.is_verified == True
    ).count()
    
    open_jobs = db.query(Job).filter(Job.status == "open").count()
    
    return success_response(data={
        "total_users": total_users,
        "active_workers": active_workers,
        "open_jobs": open_jobs,
        "platform": "SiriusJobs API v2"
    })    
