from __future__ import annotations

import re

_LAT_TO_CYR = str.maketrans({
    "A": "А", "B": "В", "E": "Е", "K": "К", "M": "М", "H": "Н", "O": "О",
    "P": "Р", "C": "С", "T": "Т", "X": "Х", "Y": "У",
})
_ALLOWED = re.compile(r"[^А-ЯA-Z0-9]")

def normalize_plate(value: str) -> str:
    cleaned = _ALLOWED.sub("", value.upper()).translate(_LAT_TO_CYR)
    return cleaned

def normalize_region(value: str) -> str:
    return re.sub(r"\D", "", value)[:3]
