# run.py
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📡 http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Docs: http://localhost:{settings.PORT}/docs")
    print(f"🔧 Workers API: http://localhost:{settings.PORT}{settings.API_V2_PREFIX}/workers")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )