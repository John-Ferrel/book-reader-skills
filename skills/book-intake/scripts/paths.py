"""Shared path constants for Book Intake scripts."""

from __future__ import annotations

from pathlib import Path


SCRIPTS_ROOT = Path(__file__).resolve().parent
SKILLS_ROOT = SCRIPTS_ROOT.parents[1]
RECONSTRUCT_TEMPLATE_ROOT = SKILLS_ROOT / "book-reconstruct" / "templates"
REVIEW_TEMPLATE_ROOT = SKILLS_ROOT / "book-reviewer" / "templates"
