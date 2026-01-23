import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this file (override=True to override any empty env vars)
load_dotenv(Path(__file__).parent / ".env", override=True)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "users"
PROMPTS_DIR = BASE_DIR / "prompts"

# API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"

# Memory settings
MAX_CONVERSATION_HISTORY = 20  # turns to keep in context
