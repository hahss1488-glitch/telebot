from __future__ import annotations

import re

_LAT_TO_CYR = str.maketrans({
    "A": "А", "B": "В", "E": "Е", "K": "К", "M": "М", "H": "Н", "O": "О",
    "P": "Р", "C": "С", "T": "Т", "X": "Х", "Y": "У", "V": "В", "R": "Р", "U": "У",
})
_ALLOWED = re.compile(r"[^А-ЯA-Z0-9]")


def normalize_plate(value: str) -> str:
    cleaned = _ALLOWED.sub("", value.upper().replace("RU", "")).translate(_LAT_TO_CYR)
    return cleaned


def normalize_region(value: str) -> str:
    return re.sub(r"\D", "", value)[:3]


def split_plate_and_region(value: str) -> tuple[str, str]:
    """Parse free-form input into canonical plate and optional region.

    Supported forms: Х360РУ797, ХРУ360797, 360ХРУ, including Latin look-alikes.
    The stored canonical form is always letters[0] + number + letters[1:].
    """
    normalized = normalize_plate(value)
    letters = "".join(ch for ch in normalized if ch.isalpha())
    digits = "".join(ch for ch in normalized if ch.isdigit())
    if len(letters) < 3 or len(digits) < 3:
        return normalized, ""
    plate = f"{letters[0]}{digits[:3]}{letters[1:3]}"
    region = digits[3:6]
    return plate, region


def format_vehicle_number(plate: str, region: str | None = None) -> str:
    return f"{plate}{region or ''}"
