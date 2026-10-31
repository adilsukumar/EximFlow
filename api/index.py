import sys
from pathlib import Path

# Ensure project root is in sys.path so app modules import cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app


class VercelPathMiddleware:
    """
    Middleware to unwrap Vercel's rewrite path so FastAPI routes
    match the user's actual browser URL instead of '/api/index.py'.
    """
    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            # Vercel sends the client requested path in x-matched-path or x-forwarded-uri
            matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
            if matched_path and matched_path not in ("/api/index.py", "/api/index"):
                scope["path"] = matched_path
                scope["raw_path"] = matched_path.encode("utf-8")
            elif scope["path"] in ("/api/index.py", "/api/index", "/api/index.py/", "/api/index/"):
                scope["path"] = "/"
                scope["raw_path"] = b"/"

        await self.app(scope, receive, send)


# Vercel entrypoint handler
handler = VercelPathMiddleware(app)
