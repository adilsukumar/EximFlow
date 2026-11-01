import sys
import traceback
from pathlib import Path

# Add project root to sys.path so 'app' can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app.main import app

    # Add ASGI middleware to normalize paths rewritten by Vercel
    @app.middleware("http")
    async def vercel_path_normalizer(request, call_next):
        path = request.scope.get("path", "")
        if path in ("/api/index.py", "/api/index"):
            request.scope["path"] = "/"
        elif path.startswith("/api/index.py/"):
            request.scope["path"] = path[len("/api/index.py"):]
        elif path.startswith("/api/index/"):
            request.scope["path"] = path[len("/api/index"):]
        return await call_next(request)

    # Expose both app and handler for Vercel Python runtime compatibility
    handler = app

except Exception:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    err_tb = traceback.format_exc()
    app = FastAPI()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def startup_error(path: str):
        return HTMLResponse(
            f"<html><body style='font-family:sans-serif;background:#0b0f19;color:#e2e8f0;padding:24px'>"
            f"<h2 style='color:#f87171'>EximFlow Startup Initialization Traceback</h2>"
            f"<pre style='background:#1e293b;padding:16px;border-radius:8px;overflow:auto'>{err_tb}</pre>"
            f"</body></html>",
            status_code=500
        )
    handler = app
