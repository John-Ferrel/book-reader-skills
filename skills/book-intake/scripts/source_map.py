"""Build structural source anchors without declaring semantic reading units."""

from __future__ import annotations

import re
from typing import Any

from extractors import ExtractedSection
from normalize_text import normalize_sections


def _preview(text: str, limit: int = 120) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"


def _block_type(block: str) -> str:
    stripped = block.strip()
    first_line = stripped.splitlines()[0] if stripped else ""
    if first_line.startswith("```"):
        return "preformatted"
    if re.match(r"^#{1,6}\s+", first_line):
        return "heading"
    if re.match(r"^[-*+]\s+", first_line) or re.match(r"^\d+[.)]\s+", first_line):
        return "list-item"
    if first_line.startswith(">"):
        return "blockquote"
    if first_line.startswith("[^") or "footnote" in first_line.lower():
        return "footnote"
    if "|" in first_line and re.search(r"\s\|\s|\|", first_line):
        return "table-text"
    return "paragraph" if stripped else "unknown"


def _iter_blocks(section_text: str) -> list[tuple[int, int, str]]:
    """Return paragraph-like blocks with offsets relative to a normalized section."""
    blocks: list[tuple[int, int, str]] = []
    for match in re.finditer(r"(?:^|\n\n)([^\n].*?)(?=\n\n|$)", section_text, flags=re.DOTALL):
        block = match.group(1).strip()
        if not block or block.startswith("<!-- page:"):
            continue
        start = match.start(1)
        end = match.end(1)
        blocks.append((start, end, section_text[start:end]))
    return blocks


def _block_kind(section_kind: str) -> str:
    if section_kind.startswith("epub-"):
        return "epub-block"
    if section_kind.startswith("pdf-"):
        return "pdf-block"
    if section_kind.startswith("md-"):
        return "md-block"
    if section_kind.startswith("txt-"):
        return "txt-block"
    return "source-block"


def _block_id(parent_id: str, section: ExtractedSection, block_index: int) -> str:
    if section.page is not None:
        return f"src-p{section.page:03d}-b{block_index:03d}"
    return f"{parent_id}-b{block_index:03d}"


def normalize_and_map(sections: list[ExtractedSection]) -> tuple[str, dict[str, Any]]:
    """Return normalized text and its per-section offsets in that exact text."""
    normalized_text, normalized_sections = normalize_sections(section.content for section in sections)
    if len(normalized_sections) != len(sections):
        raise ValueError("source contains an empty section that cannot be anchored")
    cursor = 0
    items: list[dict[str, Any]] = []
    for index, (section, text) in enumerate(zip(sections, normalized_sections), start=1):
        start_char = cursor
        end_char = start_char + len(text)
        parent_id = f"src-{index:03d}"
        item: dict[str, Any] = {
            "id": parent_id,
            "kind": section.kind,
            "title": section.title,
            "start_char": start_char,
            "end_char": end_char,
        }
        if section.href:
            item["href"] = section.href
        if section.page is not None:
            item["page"] = section.page
        items.append(item)
        for block_index, (relative_start, relative_end, block_text) in enumerate(_iter_blocks(text), start=1):
            block_item: dict[str, Any] = {
                "id": _block_id(parent_id, section, block_index),
                "kind": _block_kind(section.kind),
                "parent": parent_id,
                "title": section.title,
                "block_type": _block_type(block_text),
                "text_preview": _preview(block_text),
                "start_char": start_char + relative_start,
                "end_char": start_char + relative_end,
            }
            if section.href:
                block_item["href"] = section.href
            if section.page is not None:
                block_item["page"] = section.page
            items.append(block_item)
        cursor = end_char + 2
    return normalized_text, {"version": 2, "block_level_evidence": "available", "items": items}


def source_sections_markdown(source_map: dict[str, Any]) -> str:
    """Render a transparent, non-semantic list of mechanically found sections."""
    lines = ["# Initial Source Sections", "", "Mechanical source anchors; not semantic reading units.", ""]
    for item in source_map["items"]:
        if str(item.get("kind", "")).endswith("-block"):
            continue
        location = item.get("href") or (f"page {item['page']}" if "page" in item else "text range")
        lines.extend(
            [
                f"## {item['id']}: {item['title']}",
                "",
                f"- Kind: {item['kind']}",
                f"- Location: {location}",
                f"- Character range: {item['start_char']}-{item['end_char']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def unit_candidates_markdown(source_map: dict[str, Any], output_language: str) -> str:
    """Make reviewable candidates from source structure, never final units."""
    chinese = output_language == "zh-CN"
    if chinese:
        lines = [
            "# 语义阅读单元候选",
            "",
            "这些只是候选，未经过验证。agent 必须自行确认、合并、拆分或丢弃，不能把它们当作最终语义阅读单元。",
            "",
        ]
        task = "确认 / 合并 / 拆分 / 丢弃"
        anchors = "Source anchors"
        approximate = "Approx range"
        why = "Why candidate"
        agent_task = "Agent task"
    else:
        lines = [
            "# Semantic Reading Unit Candidates",
            "",
            "These are candidates, not validated reading units. The agent must infer final semantic reading units.",
            "",
        ]
        task = "confirm / merge / split / discard"
        anchors = "Source anchors"
        approximate = "Approx range"
        why = "Why candidate"
        agent_task = "Agent task"
    section_items = [item for item in source_map["items"] if not str(item.get("kind", "")).endswith("-block")]
    for index, item in enumerate(section_items, start=1):
        reason = "heading / EPUB spine item / PDF page / paragraph chunk"
        lines.extend(
            [
                f"## unit-candidate-{index:03d}: {item['title']}",
                "",
                f"{anchors}:",
                f"- {item['id']}",
                "",
                f"{approximate}:",
                f"- chars {item['start_char']}-{item['end_char']}",
                "",
                f"{why}:",
                f"- {reason}",
                "",
                f"{agent_task}:",
                f"- {task}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
