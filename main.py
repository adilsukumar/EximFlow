from app.main import app

# Top-level ASGI exports for Vercel Serverless Function runtime
handler = app
application = app
