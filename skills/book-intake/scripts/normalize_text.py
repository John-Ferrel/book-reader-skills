#!/usr/bin/env python3
"""Normalize plain UTF-8 source text without interpreting its meaning."""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from pathlib import Path


def normalize_text(text: str) -> str:
    """Use LF, remove trailing whitespace, and cap blank-line runs at one."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def normalize_sections(sections: Iterable[str]) -> tuple[str, list[str]]:
    """Normalize sections independently so source-map boundaries stay meaningful."""
    normalized_sections = [normalize_text(section).rstrip() for section in sections]
    normalized_sections = [section for section in normalized_sections if section]
    if not normalized_sections:
        return "", []
    return "\n\n".join(normalized_sections).rstrip() + "\n", normalized_sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a UTF-8 .txt or .md source file.")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    try:
        source_text = arguments.source.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        parser.error(f"cannot read UTF-8 source {arguments.source}: {error}")
    arguments.destination.parent.mkdir(parents=True, exist_ok=True)
    arguments.destination.write_text(normalize_text(source_text), encoding="utf-8")
    print(f"normalized: {arguments.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
