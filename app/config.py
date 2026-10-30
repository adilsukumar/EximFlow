import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect Apollo Zip file in workspace
APOLLO_ZIP_FILENAME = "Entire Apollo Database 99,311,285.zip"
APOLLO_ZIP_PATH = BASE_DIR / APOLLO_ZIP_FILENAME
HAS_APOLLO_ZIP = APOLLO_ZIP_PATH.exists()

# App settings
APP_NAME = "EximFlow AI"
APP_DESCRIPTION = "Autonomous Lead Gen & Cold Outreach Engine for B2B Exporters & Startups"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", "8000"))

# Optional AI API Keys (if provided in environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Email sending configuration limits
MAX_COLD_EMAILS_PER_INBOX_PER_DAY = 35
WARMUP_DAYS_REQUIRED = 21
TARGET_BOUNCE_RATE_LIMIT = 0.02  # 2%
