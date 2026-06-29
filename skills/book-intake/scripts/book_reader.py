#!/usr/bin/env python3
"""CLI for mechanically preparing book-reader v2 reconstruction workspaces."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from build_workspace import create_ingested_workspace
from extractors import ExtractionError, extract_book
from validate_workspace import validate_workspace, write_validation_report


def _ingest(arguments: argparse.Namespace) -> int:
    try:
        extracted = extract_book(arguments.input)
        create_ingested_workspace(
            arguments.input,
            arguments.output,
            extracted,
            arguments.book_language,
            arguments.output_language,
        )
    except (ExtractionError, ValueError, OSError) as error:
        print(f"ingest failed: {error}", file=sys.stderr)
        return 2
    result = validate_workspace(arguments.output)
    write_validation_report(result)
    if not result.ok:
        print("ingest created an invalid workspace; see reports/validation-report.md", file=sys.stderr)
        for failure in result.failed:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Ingested: {arguments.input}")
    print(f"Workspace: {arguments.output}")
    print(f"Title: {extracted.title}")
    print(f"Format: {extracted.source_format}")
    print(f"Source map items: {result.source_map_count if result.source_map_count is not None else 'unavailable'}")
    print("Workspace stage: source-ready")
    return 0


def _validate(arguments: argparse.Namespace) -> int:
    result = validate_workspace(arguments.workspace, strict=arguments.strict)
    write_validation_report(result)
    print(f"Validation: {'PASS' if result.ok else 'FAIL'}")
    for failure in result.failed:
        print(f"- {failure}", file=sys.stderr)
    return 0 if result.ok else 1


def _info(arguments: argparse.Namespace) -> int:
    metadata_path = arguments.workspace / "source" / "source-metadata.json"
    map_path = arguments.workspace / "evidence" / "source-map.json"
    manifest_path = arguments.workspace / "workspace.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source_map = json.loads(map_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"info failed: {error}", file=sys.stderr)
        return 2
    warnings = metadata.get("warnings") or []
    print(f"title: {metadata.get('title', 'unknown')}")
    print(f"format: {metadata.get('source_format', 'unknown')}")
    print(f"language: {metadata.get('language', 'unknown')}")
    print(f"output language: {metadata.get('output_language', 'unknown')}")
    print(f"extraction confidence: {metadata.get('extraction_confidence', 'unknown')}")
    print(f"character count: {metadata.get('character_count', 'unavailable')}")
    print(f"source map items: {len(source_map.get('items', []))}")
    print(f"workspace stage: {manifest.get('workspace_stage', 'unknown')}")
    print(f"review status: {manifest.get('review_status', 'unknown')}")
    print(f"revision status: {manifest.get('revision_status', 'unknown')}")
    print(f"review round: {manifest.get('review_round', 'unknown')} / {manifest.get('max_review_rounds', 'unknown')}")
    print(f"stability status: {manifest.get('stability_status', 'unknown')}")
    print(f"current required action: {manifest.get('current_required_action', 'unknown')}")
    print("main next action: read guide/dashboard.md, then confirm semantic reading units")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("warnings: none")
    return 0


def _set_state(arguments: argparse.Namespace) -> int:
    manifest_path = arguments.workspace / "workspace.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"set-state failed: {error}", file=sys.stderr)
        return 2
    if arguments.stage:
        manifest["workspace_stage"] = arguments.stage
    if arguments.audit_status:
        manifest["audit_status"] = arguments.audit_status
    if arguments.coverage_depth:
        manifest["coverage_depth"] = arguments.coverage_depth
    if arguments.review_status:
        manifest["review_status"] = arguments.review_status
    if arguments.revision_status:
        manifest["revision_status"] = arguments.revision_status
    if arguments.stability_status:
        manifest["stability_status"] = arguments.stability_status
    if arguments.current_required_action:
        manifest["current_required_action"] = arguments.current_required_action
    if arguments.review_round is not None:
        manifest["review_round"] = arguments.review_round
    if arguments.max_review_rounds is not None:
        manifest["max_review_rounds"] = arguments.max_review_rounds
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    manifest.setdefault("source_metadata", "source/source-metadata.json")
    manifest.setdefault("validation_report", "reports/validation-report.md")
    manifest.setdefault("revision_status", "not-started")
    manifest.setdefault("review_round", 0)
    manifest.setdefault("max_review_rounds", 3)
    manifest.setdefault("stability_status", "unstable")
    manifest.setdefault("last_reader_session", None)
    manifest.setdefault("last_reviewer_session", None)
    manifest.setdefault("last_reviser_session", None)
    manifest.setdefault("current_required_action", "run-review" if manifest.get("workspace_stage") == "reconstructed" else "run-reconstruction")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2).rstrip() + "\n", encoding="utf-8")
    print(f"updated workspace state: {manifest_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest books into v2 reconstruction workspaces.")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="extract a supported book into a source-ready workspace")
    ingest.add_argument("--input", required=True, type=Path, help=".txt, .md, .epub, or .pdf book source")
    ingest.add_argument("--output", required=True, type=Path, help="new, empty workspace directory")
    ingest.add_argument("--book-language", help="override detected/metadata book language (zh-CN or en)")
    ingest.add_argument("--output-language", help="workspace prose language (zh-CN or en)")
    validate = commands.add_parser("validate", help="validate an ingested workspace and update its report")
    validate.add_argument("--workspace", required=True, type=Path)
    validate.add_argument("--strict", action="store_true", help="fail on state consistency warnings")
    info = commands.add_parser("info", help="print an ingested workspace summary")
    info.add_argument("--workspace", required=True, type=Path)
    set_state = commands.add_parser("set-state", help="update machine-readable workspace state")
    set_state.add_argument("--workspace", required=True, type=Path)
    set_state.add_argument("--stage", choices=("source-ready", "reconstructed", "revised", "verified", "stable"))
    set_state.add_argument("--audit-status", choices=("not-run", "pass", "warning", "fail", "source-limited"))
    set_state.add_argument("--coverage-depth", choices=("surface", "usable", "deep"))
    set_state.add_argument("--review-status", choices=("not-reviewed", "self-checked", "reviewed-fail", "reviewed-warning", "reviewed-pass"))
    set_state.add_argument("--revision-status", choices=("not-started", "required", "in-progress", "applied", "not-needed"))
    set_state.add_argument("--stability-status", choices=("unstable", "stable", "max-rounds-reached"))
    set_state.add_argument("--current-required-action", choices=("run-reconstruction", "run-review", "run-revise", "run-verify", "none"))
    set_state.add_argument("--review-round", type=int)
    set_state.add_argument("--max-review-rounds", type=int)
    arguments = parser.parse_args()
    if arguments.command == "ingest":
        return _ingest(arguments)
    if arguments.command == "validate":
        return _validate(arguments)
    if arguments.command == "info":
        return _info(arguments)
    return _set_state(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
