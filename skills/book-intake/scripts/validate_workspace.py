#!/usr/bin/env python3
"""Validate runtime workspace mechanics, never the quality of interpretation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_workspace import INDEX_FILES, MODEL_FILES, REQUIRED_DIRECTORIES


REQUIRED_FILES = (
    "README.md",
    "workspace.json",
    "source/extracted.md",
    "source/normalized.md",
    "source/source-metadata.json",
    "evidence/source-map.json",
    "evidence/extraction-warnings.md",
    "units/README.md",
    "units/unit-candidates.md",
    "notes/unit-notes/README.md",
    "notes/deep-notes/README.md",
    "threads/README.md",
    "threads/thread-candidates.md",
    "indexes/README.md",
    "guide/dashboard.md",
    "guide/continue-reading.md",
    "guide/limitations.md",
    "guide/review-targets.md",
    "review/README.md",
)
FORBIDDEN_LEGACY_DIRECTORIES = ("chapters", "reading-passes", "projections")
ARTIFACT_DIRECTORIES = ("units", "notes", "threads", "model", "indexes", "guide", "review")
MODEL_TRACEABILITY_MARKERS = ("Evidence", "Confidence", "Alternative")
TERMINAL_STATUS_VALUES = ("deferred", "blocked", "not-applicable")


@dataclass
class ValidationResult:
    workspace: Path
    strict: bool = False
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] | None = None
    source_map_count: int | None = None
    missing_files: list[str] = field(default_factory=list)
    forbidden_directories: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failed


def _read_json(path: Path, label: str, result: ValidationResult) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result.failed.append(f"invalid {label}: {error}")
        return None
    if not isinstance(data, dict):
        result.failed.append(f"invalid {label}: expected a JSON object")
        return None
    return data


def _substantive_file(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return len(content) >= 80 and "{{" not in content


def _explicitly_terminal_artifact(content: str) -> bool:
    lowered = content.lower()
    has_status = any(f"status: {value}" in lowered for value in TERMINAL_STATUS_VALUES)
    if not has_status:
        return False
    return bool(re.search(r"(?im)^reason:\s+\S", content))


def _heading_only(content: str) -> bool:
    meaningful_lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$", line.strip())
    ]
    return bool(meaningful_lines) and all(line.startswith("#") for line in meaningful_lines)


def _artifact_is_resolved(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    if not content or "{{" in content:
        return False
    if _explicitly_terminal_artifact(content):
        return True
    if _heading_only(content):
        return False
    return len(content) >= 20


def _index_artifact_is_resolved(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    if not content or "{{" in content:
        return False
    if _explicitly_terminal_artifact(content):
        return True
    if _heading_only(content):
        return False
    meaningful_rows = [
        line.strip()
        for line in content.splitlines()
        if line.strip().startswith("|") and not re.match(r"^\|\s*:?-{3,}", line.strip())
    ]
    if len(meaningful_rows) >= 2:
        return True
    required_markers = ("entry", "type", "category", "evidence", "source", "note", "status", "confidence", "notes", "role")
    lowered = content.lower()
    has_entry = re.search(r"(?im)^(##+\s+entry:|\-\s+entry:|entry:\s*)", content) is not None
    has_evidence = any(marker in lowered for marker in ("evidence:", "source:", "note:"))
    has_status = any(marker in lowered for marker in ("status:", "confidence:"))
    has_role = any(marker in lowered for marker in ("notes:", "role:"))
    has_type = any(marker in lowered for marker in ("type:", "category:"))
    has_marker = any(marker + ":" in lowered for marker in required_markers)
    return has_entry and has_evidence and has_status and has_role and has_type and has_marker


def _stage_marker_matches(content: str, stage: str) -> bool:
    pattern = re.compile(r"(?im)^\s*-?\s*workspace stage:\s*([a-z-]+)\s*$")
    matches = [match.group(1).strip() for match in pattern.finditer(content)]
    return not matches or stage in matches


def _review_status_from_latest_report(workspace: Path) -> str | None:
    review_dir = workspace / "review"
    reports = sorted(review_dir.glob("review-report-round-*.md"))
    if not reports:
        return None
    content = reports[-1].read_text(encoding="utf-8")
    match = re.search(r"(?im)^Audit Result:\s*(pass|warning|fail)\s*$", content)
    if not match:
        return None
    return f"reviewed-{match.group(1)}"


def _has_latest_revision_log(workspace: Path) -> bool:
    return any((workspace / "revisions").glob("revision-log-round-*.md")) if (workspace / "revisions").is_dir() else False


def _record_consistency(result: ValidationResult, message: str) -> None:
    if result.strict:
        result.failed.append(message)
    else:
        result.warnings.append(message)


def _check_markdown_artifacts(workspace: Path, result: ValidationResult) -> None:
    for directory in ARTIFACT_DIRECTORIES:
        root = workspace / directory
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            if not _artifact_is_resolved(path):
                result.failed.append(
                    f"empty or unresolved artifact: {path.relative_to(workspace)} "
                    "(populate it, or mark Status: deferred/blocked/not-applicable with Reason)"
                )


def validate_workspace(workspace: Path, strict: bool = False) -> ValidationResult:
    result = ValidationResult(workspace=workspace, strict=strict)
    if not workspace.is_dir():
        result.failed.append(f"workspace directory does not exist: {workspace}")
        return result
    for directory in REQUIRED_DIRECTORIES:
        path = workspace / directory
        if not path.is_dir():
            result.failed.append(f"missing required directory: {directory}")
        else:
            result.passed.append(f"directory exists: {directory}")
    for relative_path in REQUIRED_FILES:
        path = workspace / relative_path
        if not path.is_file():
            result.failed.append(f"missing required file: {relative_path}")
            result.missing_files.append(relative_path)
        else:
            result.passed.append(f"file exists: {relative_path}")
    if not list((workspace / "source").glob("original.*")):
        result.failed.append("missing source/original.*")
        result.missing_files.append("source/original.*")
    normalized_path = workspace / "source/normalized.md"
    if normalized_path.is_file() and not normalized_path.read_text(encoding="utf-8").strip():
        result.failed.append("source/normalized.md is empty")
    metadata_path = workspace / "source/source-metadata.json"
    if metadata_path.is_file():
        result.metadata = _read_json(metadata_path, "source/source-metadata.json", result)
        if result.metadata is not None:
            required_metadata = {
                "source_path", "source_format", "title", "authors", "language", "output_language",
                "language_source", "extraction_method", "extraction_confidence", "page_count",
                "section_count", "character_count", "created_at", "warnings",
            }
            absent = sorted(required_metadata.difference(result.metadata))
            if absent:
                result.failed.append("source metadata missing fields: " + ", ".join(absent))
            warnings = result.metadata.get("warnings")
            if isinstance(warnings, list):
                result.warnings.extend(str(warning) for warning in warnings)
    manifest_path = workspace / "workspace.json"
    if manifest_path.is_file():
        manifest = _read_json(manifest_path, "workspace.json", result)
        if manifest is not None:
            required_manifest = {
                "workspace_stage",
                "audit_status",
                "coverage_depth",
                "review_status",
                "revision_status",
                "review_round",
                "max_review_rounds",
                "stability_status",
                "last_reader_session",
                "last_reviewer_session",
                "last_reviser_session",
                "current_required_action",
                "last_updated",
                "source_metadata",
                "validation_report",
            }
            absent = sorted(required_manifest.difference(manifest))
            if absent:
                result.failed.append("workspace.json missing fields: " + ", ".join(absent))
            if manifest.get("workspace_stage") not in {"source-ready", "reconstructed", "revised", "verified", "stable"}:
                result.failed.append("workspace.json has invalid workspace_stage")
            if manifest.get("audit_status") not in {"not-run", "pass", "warning", "fail", "source-limited"}:
                result.failed.append("workspace.json has invalid audit_status")
            if manifest.get("coverage_depth") not in {"surface", "usable", "deep"}:
                result.failed.append("workspace.json has invalid coverage_depth")
            if manifest.get("review_status") not in {"not-reviewed", "self-checked", "reviewed-fail", "reviewed-warning", "reviewed-pass"}:
                result.failed.append("workspace.json has invalid review_status")
            if manifest.get("revision_status") not in {"not-started", "required", "in-progress", "applied", "not-needed"}:
                result.failed.append("workspace.json has invalid revision_status")
            if manifest.get("stability_status") not in {"unstable", "stable", "max-rounds-reached"}:
                result.failed.append("workspace.json has invalid stability_status")
            if manifest.get("current_required_action") not in {"run-reconstruction", "run-review", "run-revise", "run-verify", "none"}:
                result.failed.append("workspace.json has invalid current_required_action")
            if not isinstance(manifest.get("review_round"), int) or manifest.get("review_round", -1) < 0:
                result.failed.append("workspace.json has invalid review_round")
            if not isinstance(manifest.get("max_review_rounds"), int) or manifest.get("max_review_rounds", 0) < 1:
                result.failed.append("workspace.json has invalid max_review_rounds")
            stage = str(manifest.get("workspace_stage", ""))
            readme = workspace / "README.md"
            if readme.is_file() and not _stage_marker_matches(readme.read_text(encoding="utf-8"), stage):
                _record_consistency(result, "README stage does not match workspace.json")
            dashboard = workspace / "guide/dashboard.md"
            if dashboard.is_file() and not _stage_marker_matches(dashboard.read_text(encoding="utf-8"), stage):
                _record_consistency(result, "guide/dashboard stage does not match workspace.json")
            latest_review_status = _review_status_from_latest_report(workspace)
            if latest_review_status and manifest.get("review_status") != latest_review_status:
                _record_consistency(result, "review status does not match latest review report")
            if _has_latest_revision_log(workspace) and manifest.get("revision_status") not in {"applied", "not-needed"}:
                _record_consistency(result, "revision status does not match latest revision log")
            if manifest.get("revision_status") == "required" and manifest.get("current_required_action") != "run-revise":
                _record_consistency(result, "current_required_action is inconsistent with revision_status")
            if manifest.get("workspace_stage") == "source-ready" and manifest.get("current_required_action") != "run-reconstruction":
                _record_consistency(result, "current_required_action is inconsistent with source-ready stage")
    source_map_path = workspace / "evidence/source-map.json"
    if source_map_path.is_file():
        source_map = _read_json(source_map_path, "evidence/source-map.json", result)
        if source_map is not None:
            items = source_map.get("items")
            if not isinstance(items, list) or not items:
                result.failed.append("source-map.json has no items")
            else:
                result.source_map_count = len(items)
                ids: set[str] = set()
                has_block_items = False
                metadata_format = (result.metadata or {}).get("source_format", "unknown")
                for item in items:
                    if not isinstance(item, dict) or not {"id", "kind", "title", "start_char", "end_char"}.issubset(item):
                        result.failed.append("source-map.json contains an incomplete item")
                        break
                    item_id = str(item.get("id"))
                    if item_id in ids:
                        result.failed.append(f"source-map.json contains duplicate id: {item_id}")
                        break
                    ids.add(item_id)
                    start = item.get("start_char")
                    end = item.get("end_char")
                    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
                        result.failed.append(f"source-map.json has invalid character range: {item_id}")
                        break
                    if str(item.get("kind", "")).endswith("-block"):
                        has_block_items = True
                        required_block = {"id", "kind", "start_char", "end_char", "text_preview", "block_type"}
                        if not required_block.issubset(item) or not str(item.get("text_preview", "")).strip():
                            result.failed.append(f"source-map.json has incomplete block item: {item_id}")
                            break
                if metadata_format in {"txt", "md", "epub", "pdf"} and not has_block_items:
                    result.failed.append("source-map.json has no block-level items")
    for model_file in MODEL_FILES:
        model_path = workspace / "model" / model_file
        if not model_path.is_file():
            result.failed.append(f"missing model file: model/{model_file}")
            result.missing_files.append(f"model/{model_file}")
        else:
            content = model_path.read_text(encoding="utf-8")
            for marker in MODEL_TRACEABILITY_MARKERS:
                if marker not in content:
                    result.failed.append(f"model file missing traceability marker {marker}: model/{model_file}")
                    break
    for index_file in INDEX_FILES:
        path = workspace / "indexes" / index_file
        if not path.is_file():
            result.failed.append(f"missing index file: indexes/{index_file}")
            result.missing_files.append(f"indexes/{index_file}")
        elif not _index_artifact_is_resolved(path):
            result.failed.append(
                f"empty or unresolved artifact: indexes/{index_file} "
                "(populate it, or mark Status: deferred/blocked/not-applicable with Reason)"
            )
    _check_markdown_artifacts(workspace, result)
    for forbidden in FORBIDDEN_LEGACY_DIRECTORIES:
        if (workspace / forbidden).exists():
            result.failed.append(f"forbidden legacy directory exists: {forbidden}")
            result.forbidden_directories.append(forbidden)
    return result


def render_validation_report(result: ValidationResult) -> str:
    metadata = result.metadata or {}
    count = str(result.source_map_count) if result.source_map_count is not None else "unavailable"
    def listed(values: list[str]) -> list[str]:
        return [f"- {value}" for value in values] or ["- None"]

    lines = [
        "# Validation Report",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Workspace path: {result.workspace.resolve()}",
        f"- Strict mode: {'yes' if result.strict else 'no'}",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Checks passed",
        "",
        *listed(result.passed),
        "",
        "## Checks failed",
        "",
        *listed(result.failed),
        "",
        "## Warnings",
        "",
        *listed(result.warnings),
        "",
        "## Source metadata summary",
        "",
        f"- Title: {metadata.get('title', 'unavailable')}",
        f"- Format: {metadata.get('source_format', 'unavailable')}",
        f"- Language: {metadata.get('language', 'unavailable')}",
        f"- Extraction confidence: {metadata.get('extraction_confidence', 'unavailable')}",
        f"- Character count: {metadata.get('character_count', 'unavailable')}",
        "",
        "## Source map",
        "",
        f"- Item count: {count}",
        "",
        "## Missing files",
        "",
        *listed(result.missing_files),
        "",
        "## Forbidden legacy directories",
        "",
        *listed(result.forbidden_directories),
    ]
    return "\n".join(lines) + "\n"


def write_validation_report(result: ValidationResult) -> None:
    reports_directory = result.workspace / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)
    (reports_directory / "validation-report.md").write_text(render_validation_report(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a book-reader v2 runtime workspace.")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--strict", action="store_true", help="fail on metadata/dashboard/review consistency warnings")
    arguments = parser.parse_args()
    result = validate_workspace(arguments.workspace, strict=arguments.strict)
    write_validation_report(result)
    print(f"Validation: {'PASS' if result.ok else 'FAIL'}")
    for failure in result.failed:
        print(f"- {failure}", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
