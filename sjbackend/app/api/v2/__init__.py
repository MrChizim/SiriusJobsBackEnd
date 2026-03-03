# app/api/v2/__init__.py
from .auth import router as auth_router
from .workers import router as workers_router
from .employers import router as employers_router
from .jobs import router as jobs_router
from .applications import router as applications_router
from .stats import router as stats_router
from .ratings import router as ratings_router
from .merchants import router as merchants_router  

__all__ = [
    'auth_router',
    'workers_router', 
    'employers_router',
    'jobs_router',
    'applications_router',
    'stats_router',
    'ratings_router',
    'merchants_router'  
]