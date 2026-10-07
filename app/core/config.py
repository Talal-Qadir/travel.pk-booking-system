from __future__ import annotations

import os

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _split_csv(value: str | None, default: str) -> list[str]:
    if value is None or value == "":
        return default.split(",") if default else []
    return [item.strip() for item in value.split(",") if item.strip()]


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travelpk.db")
CORS_ORIGINS = _split_csv(os.getenv("CORS_ORIGINS"), DEFAULT_CORS_ORIGINS)
PSP_SECRET = os.getenv("PSP_SECRET", "travelpk-psp-secret")
HOLD_MINUTES = int(os.getenv("HOLD_MINUTES", "20"))
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "24"))
DEBUG = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes", "on"}
