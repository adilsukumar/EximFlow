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
    raw_path = request.scope.get("path", "")

    # Check query param path override if passed by Vercel rewrite
    query_path = request.query_params.get("path")
    if query_path and query_path.startswith("/api/"):
        request.scope["path"] = query_path
        return await call_next(request)

    # 1. If it's already an API route (other than index), never touch it
    if raw_path.startswith("/api/") and raw_path not in ("/api/index", "/api/index.py", "/api/index/"):
        return await call_next(request)

    # 2. If it's a static file request, never touch it
    if raw_path.startswith("/static/"):
        return await call_next(request)

    # 3. Check if x-matched-path contains a specific API route
    matched_path = request.headers.get("x-matched-path", "")
    if matched_path:
        clean_matched = matched_path.split("?")[0]
        if clean_matched.startswith("/api/") and clean_matched not in ("/api/index", "/api/index.py", "/api/index/"):
            request.scope["path"] = clean_matched
            return await call_next(request)

    # 4. If it's root or the entrypoint file, route to homepage
    if raw_path in ("", "/", "/index", "/index.html", "/api/index", "/api/index.py", "/api/index/"):
        request.scope["path"] = "/"

    return await call_next(request)
