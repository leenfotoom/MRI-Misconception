from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH, override=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://misconception:misconception@localhost:55432/misconception_mri",
)
