from __future__ import annotations

import asyncio
import random
import uuid
from typing import Any

AIRLINE_RESULTS: dict[str, dict[str, Any]] = {}
AIRLINE_TASKS: dict[str, asyncio.Task[Any]] = {}


def create_pnr() -> str:
    return uuid.uuid4().hex[:6].upper()


async def _do_issue_airline_request(key: str, mode: str = "normal") -> dict[str, Any]:
    if mode == "flaky" and random.random() < 0.5:
        raise RuntimeError("Airline flaky failure")

    if mode == "slow":
        await asyncio.sleep(6)

    pnr = create_pnr()
    AIRLINE_RESULTS[key] = {"pnr": pnr, "status": "completed"}
    return {"pnr": pnr, "status": "completed"}


async def issue_airline_ticket(booking_reference: str, idempotency_key: str, mode: str = "normal") -> dict[str, Any]:
    if idempotency_key in AIRLINE_RESULTS and AIRLINE_RESULTS[idempotency_key].get("status") == "completed":
        return AIRLINE_RESULTS[idempotency_key]

    if idempotency_key in AIRLINE_TASKS and not AIRLINE_TASKS[idempotency_key].done():
        return await AIRLINE_TASKS[idempotency_key]

    task = asyncio.create_task(_do_issue_airline_request(idempotency_key, mode=mode))
    AIRLINE_TASKS[idempotency_key] = task
    try:
        result = await task
        return result
    except Exception:
        if idempotency_key in AIRLINE_RESULTS:
            return AIRLINE_RESULTS[idempotency_key]
        raise
    finally:
        AIRLINE_TASKS.pop(idempotency_key, None)
