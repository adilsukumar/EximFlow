import sys
from pathlib import Path
import urllib.parse

# Add project root to sys.path so 'app' can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the core FastAPI instance
from app.main import app as _fastapi_app

class VercelASGIProxy:
    """
    Pure ASGI middleware wrapper for Vercel Serverless Functions.
    Accurately maps rewritten paths (via query parameter, Vercel headers, or scope)
    to internal FastAPI API routes while routing root traffic to the UI dashboard.
    """
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            raw_path = scope.get("path", "")
            raw_qs = scope.get("query_string", b"").decode("latin1", errors="ignore")

            # Extract headers in lowercase
            headers = {}
            for k, v in scope.get("headers", []):
                try:
                    headers[k.decode("latin1").lower()] = v.decode("latin1")
                except Exception:
                    pass

            target_path = None

            # 1. Check for query param __api_path if injected by Vercel rewrite
            if "__api_path=" in raw_qs:
                qs_parts = urllib.parse.parse_qs(raw_qs, keep_blank_values=True)
                if "__api_path" in qs_parts and qs_parts["__api_path"]:
                    target_path = qs_parts["__api_path"][0]
                    # Strip __api_path so application endpoints receive clean params
                    cleaned_qs = {k: v for k, v in qs_parts.items() if k != "__api_path"}
                    scope["query_string"] = urllib.parse.urlencode(cleaned_qs, doseq=True).encode("latin1")

            # 2. Check if raw_path is already a valid API or static route
            if not target_path and raw_path.startswith(("/api/", "/static/")):
                if raw_path not in ("/api/index", "/api/index.py", "/api/index/"):
                    target_path = raw_path

            # 3. Check Vercel proxy headers
            if not target_path:
                for h_name in ("x-matched-path", "x-invoke-path", "x-forwarded-uri", "x-original-url"):
                    h_val = headers.get(h_name, "")
                    if h_val:
                        clean_h = h_val.split("?")[0]
                        if clean_h.startswith(("/api/", "/static/")) and clean_h not in ("/api/index", "/api/index.py", "/api/index/"):
                            target_path = clean_h
                            break

            # 4. Set resolved path or fallback to root UI
            if target_path:
                scope["path"] = target_path
                scope["raw_path"] = target_path.encode("latin1")
            elif raw_path in ("", "/", "/index", "/index.html", "/api/index", "/api/index.py", "/api/index/"):
                scope["path"] = "/"
                scope["raw_path"] = b"/"

        await self.asgi_app(scope, receive, send)

# Top-level exports for Vercel Python runtime inspection
app = VercelASGIProxy(_fastapi_app)
handler = app
application = app
