from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

_NUMERIC_RE = re.compile(r"^(?:\d+\.\d+|\d+|\.\d+)$")


def parse_money_to_paisa(value: str | Decimal | int) -> int:
    if isinstance(value, bool):
        raise ValueError("Money value cannot be boolean.")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("Money cannot be negative.")
        return value * 100

    text = str(value).strip()
    if text == "":
        raise ValueError("Money value is required.")
    if text.lower() in {"nan", "inf", "infinity"} or "e" in text.lower():
        raise ValueError("Invalid money amount")
    if not _NUMERIC_RE.fullmatch(text):
        raise ValueError("Invalid money amount")

    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid money amount") from exc

    if not amount.is_finite() or amount < 0:
        raise ValueError("Invalid money amount")

    paise = (amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(paise)


def money_to_text(paisa: int) -> str:
    return f"{paisa / 100:.2f}"
