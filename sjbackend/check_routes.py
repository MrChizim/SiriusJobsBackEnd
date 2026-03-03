# check_routes.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

print("Registered routes under /api/v2/merchants:")
for route in app.routes:
    if hasattr(route, "path") and "/api/v2/merchants" in route.path:
        methods = ", ".join(route.methods) if hasattr(route, "methods") else "ANY"
        print(f"  {methods}: {route.path}")      