import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
KB_DIR = BASE_DIR / "knowledge-base"

TICKETS_FILE = DATA_DIR / "tickets.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ANALYSIS_DATE = "2026-05-31"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Create a .env file with your API key."
    )

