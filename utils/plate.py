from __future__ import annotations

import re

_LAT_TO_CYR = str.maketrans({
    "A": "А", "B": "В", "E": "Е", "K": "К", "M": "М", "H": "Н", "O": "О",
    "P": "Р", "C": "С", "T": "Т", "X": "Х", "Y": "У", "V": "В",
})
_ALLOWED = re.compile(r"[^А-ЯA-Z0-9]")
_REGION_SUFFIX = re.compile(r"(\d{2,3})$")

def normalize_plate(value: str) -> str:
    cleaned = _ALLOWED.sub("", value.upper()).translate(_LAT_TO_CYR)
    return cleaned

def normalize_region(value: str) -> str:
    return re.sub(r"\D", "", value)[:3]

def split_plate_and_region(value: str) -> tuple[str, str]:
    """Parse a free-form value like 'ВТТ-360 RU797' into plate and region."""
    without_country = value.upper().replace("RU", "")
    normalized = normalize_plate(without_country)
    match = _REGION_SUFFIX.search(normalized)
    if not match:
        return normalized, ""
    region = match.group(1)
    plate = normalized[: -len(region)]
    return plate, region
