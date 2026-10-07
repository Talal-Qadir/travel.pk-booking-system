from __future__ import annotations

from typing import Any

from fastapi import HTTPException


def error_payload(code: str, message: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message}}


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=error_payload(code, message))
