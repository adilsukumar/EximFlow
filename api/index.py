import sys
from pathlib import Path

# Add project root to sys.path so 'app' can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Top-level application import for Vercel AST & runtime inspection
from app.main import app

# Top-level ASGI exports
handler = app
application = app

# ASGI middleware to normalize paths rewritten by Vercel
@app.middleware("http")
async def vercel_path_normalizer(request, call_next):
    path = request.scope.get("path", "")
    if path in ("/api/index", "/api/index.py"):
        request.scope["path"] = "/"
    elif path.startswith("/api/index/"):
        request.scope["path"] = path[len("/api/index"):]
    elif path.startswith("/api/index.py/"):
        request.scope["path"] = path[len("/api/index.py"):]
    return await call_next(request)
