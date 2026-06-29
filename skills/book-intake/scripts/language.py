"""Small, transparent language detection for workspace presentation."""

from __future__ import annotations

import re


def normalize_language(value: str | None) -> str:
    """Normalize common language labels to the runtime's small vocabulary."""
    if not value:
        return "unknown"
    candidate = value.strip().lower().replace("_", "-")
    if candidate.startswith("zh") or candidate in {"cn", "chinese"}:
        return "zh-CN"
    if candidate.startswith("en") or candidate == "english":
        return "en"
    return "unknown"


def detect_language(text: str) -> str:
    """Return zh-CN, en, or unknown based on visible text, not a hidden model."""
    chinese_characters = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    latin_letters = len(re.findall(r"[A-Za-z]", text))
    if chinese_characters >= 6 and chinese_characters >= latin_letters * 0.08:
        return "zh-CN"
    if latin_letters >= 12 and latin_letters > chinese_characters * 2:
        return "en"
    return "unknown"
