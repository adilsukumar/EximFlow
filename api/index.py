import sys
import traceback
from pathlib import Path

# Add project root to sys.path so 'app' can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    err_tb = traceback.format_exc()
    app = FastAPI()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def startup_error(path: str):
        return HTMLResponse(f"<h1>EximFlow / Harvey Startup Error</h1><pre>{err_tb}</pre>", status_code=500)
