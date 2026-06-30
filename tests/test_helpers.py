"""Dependency-free runtime tests for book-reader v2 ingestion."""

from __future__ import annotations

import json
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "book-intake" / "scripts"
INSTALL_SCRIPT = ROOT / "scripts" / "install_skills.py"
sys.path.insert(0, str(SCRIPTS))
from language import detect_language  # noqa: E402


class HelperRuntimeTests(unittest.TestCase):
    @staticmethod
    def write_text_pdf(path: Path) -> None:
        """Create a dependency-free one-page PDF with an extractable text stream."""
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 300] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length 55 >>\nstream\nBT /F1 18 Tf 40 180 Td (Readable PDF body text.) Tj ET\nendstream",
        ]
        payload = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for number, object_body in enumerate(objects, start=1):
            offsets.append(len(payload))
            payload.extend(f"{number} 0 obj\n".encode("ascii"))
            payload.extend(object_body)
            payload.extend(b"\nendobj\n")
        xref_offset = len(payload)
        payload.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        payload.extend(b"0000000000 65535 f \n")
        payload.extend(b"".join(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets[1:]))
        payload.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
        )
        path.write_bytes(payload)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "book_reader.py"), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def ingest(self, source: Path, workspace: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli("ingest", "--input", str(source), "--output", str(workspace), *extra)

    def test_txt_ingest_creates_source_ready_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# 标题\n\n这是第一段内容。\n\n这是第二段内容。\n", encoding="utf-8")

            result = self.ingest(source, workspace)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((workspace / "source" / "original.txt").is_file())
            self.assertTrue((workspace / "source" / "extracted.md").is_file())
            self.assertTrue((workspace / "source" / "normalized.md").is_file())
            self.assertTrue((workspace / "reports" / "validation-report.md").is_file())
            metadata = json.loads((workspace / "source" / "source-metadata.json").read_text("utf-8"))
            self.assertEqual(metadata["source_format"], "txt")
            self.assertEqual(metadata["language"], "zh-CN")
            self.assertEqual(metadata["output_language"], "zh-CN")
            source_map = json.loads((workspace / "evidence" / "source-map.json").read_text("utf-8"))
            self.assertGreaterEqual(len(source_map["items"]), 1)
            self.assert_source_map_has_block_items(source_map, "txt-block")
            self.assertIn("source-ready", (workspace / "README.md").read_text("utf-8"))
            self.assertIn("候选", (workspace / "units" / "unit-candidates.md").read_text("utf-8"))
            workspace_state = json.loads((workspace / "workspace.json").read_text("utf-8"))
            self.assertEqual(workspace_state["workspace_stage"], "source-ready")
            self.assertEqual(workspace_state["review_status"], "not-reviewed")
            self.assertEqual(workspace_state["revision_status"], "not-started")
            self.assertEqual(workspace_state["review_round"], 0)
            self.assertEqual(workspace_state["max_review_rounds"], 3)
            self.assertEqual(workspace_state["stability_status"], "unstable")
            self.assertEqual(workspace_state["current_required_action"], "run-reconstruction")
            self.assertIsNone(workspace_state["last_reader_session"])
            self.assertIsNone(workspace_state["last_reviewer_session"])
            self.assertIsNone(workspace_state["last_reviser_session"])
            self.assertEqual(workspace_state["coverage_depth"], "surface")
            self.assertIn("last_updated", workspace_state)
            self.assertEqual(workspace_state["source_metadata"], "source/source-metadata.json")
            self.assertEqual(workspace_state["validation_report"], "reports/validation-report.md")

    def test_markdown_ingest_keeps_headings_and_builds_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.md"
            workspace = directory / "workspace"
            source.write_text("# Main Title\n\nIntro.\n\n## First Move\n\nEvidence.\n", encoding="utf-8")

            result = self.ingest(source, workspace)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            normalized = (workspace / "source" / "normalized.md").read_text("utf-8")
            self.assertIn("## First Move", normalized)
            source_map = json.loads((workspace / "evidence" / "source-map.json").read_text("utf-8"))
            self.assertGreaterEqual(len(source_map["items"]), 2)
            self.assert_source_map_has_block_items(source_map, "md-block")
            self.assert_unique_source_map_ids(source_map)
            candidates = (workspace / "units" / "unit-candidates.md").read_text("utf-8")
            self.assertIn("Main Title", candidates)
            self.assertIn("First Move", candidates)

    def test_language_detection_handles_chinese_english_and_unknown(self) -> None:
        self.assertEqual(detect_language("这是一本中文书，包含足够的汉字。"), "zh-CN")
        self.assertEqual(detect_language("This is an English book with enough words."), "en")
        self.assertEqual(detect_language("12345 ---"), "unknown")

    def test_validate_and_info_report_workspace_facts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("A small English book.\n\nA second paragraph.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)

            valid = self.run_cli("validate", "--workspace", str(workspace))
            info = self.run_cli("info", "--workspace", str(workspace))

            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertIn("Validation: PASS", valid.stdout)
            self.assertEqual(info.returncode, 0, info.stdout + info.stderr)
            self.assertIn("format: txt", info.stdout)
            self.assertIn("source map items:", info.stdout)
            self.assertIn("revision status:", info.stdout)
            self.assertIn("current required action:", info.stdout)
            state = json.loads((workspace / "workspace.json").read_text("utf-8"))
            self.assertEqual(state["workspace_stage"], "source-ready")
            self.assertNotEqual(state["workspace_stage"], "reconstructed")

    def test_validator_rejects_forbidden_legacy_directory_and_updates_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("A readable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            (workspace / "chapters").mkdir()

            result = self.run_cli("validate", "--workspace", str(workspace))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden legacy directory", result.stdout + result.stderr)
            report = (workspace / "reports" / "validation-report.md").read_text("utf-8")
            self.assertIn("chapters", report)

    def test_validator_rejects_empty_index_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            (workspace / "indexes" / "design-principle-index.md").write_text("# Design Principle Index\n", encoding="utf-8")

            result = self.run_cli("validate", "--workspace", str(workspace))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty or unresolved artifact", result.stdout + result.stderr)

    def test_validator_allows_explicitly_deferred_artifact_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            (workspace / "indexes" / "design-principle-index.md").write_text(
                "# Design Principle Index\n\nStatus: deferred\nReason: no reconstruction reading has been completed yet.\n",
                encoding="utf-8",
            )

            result = self.run_cli("validate", "--workspace", str(workspace))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_accepts_non_table_index_with_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            (workspace / "indexes" / "concept-index.md").write_text(
                """# Concept Index

## Entry: Decision variable

- Type: concept
- Evidence: src-001-b002
- Note: obs-ru-001-001
- Status: active
- Notes: Identifies what changes the selected action.
""",
                encoding="utf-8",
            )

            result = self.run_cli("validate", "--workspace", str(workspace))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_strict_validate_catches_readme_workspace_stage_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            manifest_path = workspace / "workspace.json"
            manifest = json.loads(manifest_path.read_text("utf-8"))
            manifest["workspace_stage"] = "reconstructed"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

            normal = self.run_cli("validate", "--workspace", str(workspace))
            strict = self.run_cli("validate", "--workspace", str(workspace), "--strict")

            self.assertEqual(normal.returncode, 0, normal.stdout + normal.stderr)
            self.assertNotEqual(strict.returncode, 0)
            self.assertIn("README stage does not match workspace.json", strict.stdout + strict.stderr)

    def test_strict_validator_catches_essay_only_active_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            self.mark_reconstructed(workspace)
            (workspace / "model" / "author-problem.md").write_text(
                "# Author Problem\n\nStatus: active\n\nThe author is clearly trying to solve a reader confusion problem with a careful sequence.\n",
                encoding="utf-8",
            )

            result = self.run_cli("validate", "--workspace", str(workspace), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("active model file missing claim card", result.stdout + result.stderr)

    def test_strict_validator_catches_active_model_missing_required_claim_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            self.mark_reconstructed(workspace)
            (workspace / "model" / "author-problem.md").write_text(
                """# Author Problem

Status: active

## Claim: The book frames better judgment as evidence selection.

Claim ID: model-author-problem-001
Type: inference
Status: active

Reasoning:
The prose says decision-relevant evidence matters.
""",
                encoding="utf-8",
            )

            result = self.run_cli("validate", "--workspace", str(workspace), "--strict")

            self.assertNotEqual(result.returncode, 0)
            output = result.stdout + result.stderr
            self.assertIn("missing required claim-card field Evidence", output)
            self.assertIn("missing required claim-card field Confidence", output)
            self.assertIn("missing required claim-card field Alternative Interpretation", output)

    def test_strict_validator_does_not_treat_self_audit_as_independent_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            manifest_path = workspace / "workspace.json"
            manifest = json.loads(manifest_path.read_text("utf-8"))
            manifest["workspace_stage"] = "stable"
            manifest["review_status"] = "self-checked"
            manifest["stability_status"] = "stable"
            manifest["current_required_action"] = "none"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            readme = (workspace / "README.md").read_text("utf-8").replace("workspace stage: source-ready", "workspace stage: stable")
            (workspace / "README.md").write_text(readme, encoding="utf-8")
            dashboard = (workspace / "guide" / "dashboard.md").read_text("utf-8").replace("workspace stage: source-ready", "workspace stage: stable")
            (workspace / "guide" / "dashboard.md").write_text(dashboard, encoding="utf-8")

            result = self.run_cli("validate", "--workspace", str(workspace), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("self-audit is not independent review", result.stdout + result.stderr)

    def test_strict_validator_reports_readme_only_optional_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            optional = workspace / "optional-map"
            optional.mkdir()
            (optional / "README.md").write_text("# Optional Map\n\nPurpose: possible future map.\n", encoding="utf-8")

            result = self.run_cli("validate", "--workspace", str(workspace), "--strict")
            report = (workspace / "reports" / "validation-report.md").read_text("utf-8")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("README-only optional directory", report)

    def test_strict_validator_catches_note_summary_without_note_items(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.txt"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nReadable source text.", encoding="utf-8")
            self.assertEqual(self.ingest(source, workspace).returncode, 0)
            note = workspace / "notes" / "unit-notes" / "unit-001.md"
            note.write_text("# Unit 1\n\nThis chapter says useful things about evidence and judgment.\n", encoding="utf-8")

            result = self.run_cli("validate", "--workspace", str(workspace), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("note file has no note item IDs", result.stdout + result.stderr)

    @unittest.skipUnless(importlib.util.find_spec("ebooklib"), "ebooklib is not installed")
    def test_epub_ingest_extracts_spine_metadata_and_source_map(self) -> None:
        from ebooklib import epub

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.epub"
            workspace = directory / "workspace"
            book = epub.EpubBook()
            book.set_identifier("runtime-test")
            book.set_title("EPUB Runtime Test")
            book.set_language("en")
            book.add_author("Test Author")
            chapter = epub.EpubHtml(title="Opening", file_name="opening.xhtml", lang="en")
            chapter.content = "<h1>Opening</h1><p>Readable EPUB body text.</p>"
            book.add_item(chapter)
            book.toc = (epub.Link("opening.xhtml", "Opening", "opening"),)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = ["nav", chapter]
            epub.write_epub(str(source), book)

            result = self.ingest(source, workspace)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metadata = json.loads((workspace / "source" / "source-metadata.json").read_text("utf-8"))
            self.assertEqual(metadata["source_format"], "epub")
            self.assertEqual(metadata["title"], "EPUB Runtime Test")
            source_map = json.loads((workspace / "evidence" / "source-map.json").read_text("utf-8"))
            self.assertEqual(source_map["items"][0]["kind"], "epub-section")
            self.assertEqual(source_map["items"][0]["href"], "opening.xhtml")
            self.assert_source_map_has_block_items(source_map, "epub-block")

    @unittest.skipUnless(importlib.util.find_spec("pypdf"), "pypdf is not installed")
    def test_pdf_ingest_creates_page_anchors_and_page_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.pdf"
            workspace = directory / "workspace"
            self.write_text_pdf(source)

            result = self.ingest(source, workspace)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            normalized = (workspace / "source" / "normalized.md").read_text("utf-8")
            self.assertIn("<!-- page: 1 -->", normalized)
            self.assertIn("Readable PDF body text.", normalized)
            source_map = json.loads((workspace / "evidence" / "source-map.json").read_text("utf-8"))
            self.assertEqual(source_map["items"][0]["page"], 1)
            self.assert_source_map_has_block_items(source_map, "pdf-block")

    def test_ingest_creates_edition_layer_template(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "book.md"
            workspace = directory / "workspace"
            source.write_text("# Book\n\nPreface to the revised edition.\n", encoding="utf-8")

            result = self.ingest(source, workspace)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            edition_layer = workspace / "model" / "edition-layers.md"
            self.assertTrue(edition_layer.is_file())
            content = edition_layer.read_text("utf-8")
            self.assertIn("Edition / Revision Layers", content)
            self.assertIn("Status: deferred", content)

    def test_reviewer_and_revision_templates_are_round_based(self) -> None:
        review_template = (ROOT / "skills" / "book-reviewer" / "templates" / "review-report.md").read_text("utf-8")
        revision_plan = (ROOT / "skills" / "book-reviewer" / "templates" / "revision-plan.md").read_text("utf-8")
        revision_log = (ROOT / "skills" / "book-revise" / "templates" / "revision-log.md").read_text("utf-8")

        self.assertIn("Review Round", review_template)
        self.assertIn("Artifact Redundancy Audit", review_template)
        self.assertIn("Anti-Laziness Audit", review_template)
        self.assertIn("Next Required Action", review_template)
        self.assertIn("revision-plan-round", revision_plan)
        self.assertIn("revision-log-round", revision_log)
        self.assertIn("re-read", revision_log.lower())
        self.assertIn("Source blocks re-read", revision_log)

    def test_model_templates_use_claim_card_structure(self) -> None:
        model_directory = ROOT / "skills" / "book-reconstruct" / "templates" / "model"
        required_markers = (
            "## Claim:",
            "Claim ID:",
            "Type:",
            "Status:",
            "Confidence:",
            "Evidence:",
            "Reasoning:",
            "Alternative Interpretation:",
            "What Would Change This Model:",
            "Revision History:",
        )
        for model_template in model_directory.glob("*.md"):
            content = model_template.read_text("utf-8")
            for marker in required_markers:
                self.assertIn(marker, content, f"{model_template} missing {marker}")

    def test_note_templates_define_minimum_note_item_fields(self) -> None:
        unit_note = (ROOT / "skills" / "book-reconstruct" / "templates" / "notes" / "unit-note.md").read_text("utf-8")
        deep_note = (ROOT / "skills" / "book-reconstruct" / "templates" / "notes" / "deep-note.md").read_text("utf-8")
        for content in (unit_note, deep_note):
            self.assertIn("Type:", content)
            self.assertIn("Source:", content)
            self.assertIn("Confidence:", content)
            self.assertIn("Content:", content)
        self.assertIn("What Would Change This:", unit_note)
        self.assertIn("What Would Resolve This:", unit_note)
        self.assertIn("coverage-level", unit_note)

    def test_install_script_discovers_expected_skills_flattened(self) -> None:
        installer = self.load_install_module()

        skills = installer.discover_skills(ROOT)
        names = [skill.name for skill in skills]

        self.assertIn("book-reader", names)
        self.assertIn("book-intake", names)
        self.assertIn("book-reconstruct", names)
        self.assertIn("book-reviewer", names)
        self.assertIn("book-revise", names)
        self.assertIn("technical-book", names)
        self.assertIn("fiction-narrative", names)
        self.assertNotIn("lenses", names)
        for skill in skills:
            self.assertEqual(skill.path.name, skill.name)
            self.assertTrue((skill.path / "SKILL.md").is_file())
            self.assertNotIn("books", skill.path.parts)
            self.assertNotIn("workspaces", skill.path.parts)

    def test_install_script_validates_all_skill_frontmatter(self) -> None:
        installer = self.load_install_module()

        skills = installer.discover_skills(ROOT)

        self.assertEqual(len(skills), 13)
        for skill in skills:
            metadata = installer.parse_skill_frontmatter(skill.path / "SKILL.md")
            self.assertEqual(metadata["name"], skill.name)
            self.assertTrue(metadata["description"].strip())
            self.assertLessEqual(len(metadata["description"]), 1024)

    def test_install_script_rejects_invalid_skill_frontmatter(self) -> None:
        installer = self.load_install_module()

        cases = [
            ("missing-frontmatter", "# Missing Frontmatter\n", "frontmatter"),
            ("missing-name", "---\ndescription: Use when testing.\n---\n", "missing required frontmatter field 'name'"),
            ("missing-description", "---\nname: missing-description\n---\n", "missing required frontmatter field 'description'"),
            ("empty-description", "---\nname: empty-description\ndescription: \n---\n", "description must be non-empty"),
            ("name-mismatch", "---\nname: other-name\ndescription: Use when testing.\n---\n", "does not match install name"),
            ("illegal_name", "---\nname: illegal_name\ndescription: Use when testing.\n---\n", "invalid skill name"),
        ]
        for directory_name, content, expected_message in cases:
            with self.subTest(directory_name=directory_name):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repo = Path(temporary_directory)
                    self.write_skill(repo, directory_name, content)

                    with self.assertRaises(ValueError) as error:
                        installer.discover_skills(repo)

                    self.assertIn(expected_message, str(error.exception))
                    self.assertIn("SKILL.md", str(error.exception))

    def test_install_script_rejects_missing_uppercase_skill_file(self) -> None:
        installer = self.load_install_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_directory = Path(temporary_directory) / "skills" / "lowercase-file"
            skill_directory.mkdir(parents=True)
            (skill_directory / "skill.md").write_text(
                "---\nname: lowercase-file\ndescription: Use when testing.\n---\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as error:
                installer.validate_skill_package(installer.SkillPackage(name="lowercase-file", path=skill_directory))

            self.assertIn("SKILL.md not found", str(error.exception))

    def test_install_script_dry_run_validates_skills_before_planning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            scripts = repo / "scripts"
            scripts.mkdir(parents=True)
            shutil.copy2(INSTALL_SCRIPT, scripts / "install_skills.py")
            self.write_skill(
                repo,
                "broken-skill",
                "---\nname: other-name\ndescription: Use when testing dry-run validation.\n---\n",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(scripts / "install_skills.py"),
                    "--target",
                    "opencode-project",
                    "--project",
                    str(repo),
                    "--dry-run",
                ],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not match install name", result.stderr)
            self.assertIn("SKILL.md", result.stderr)

    def test_install_script_resolves_project_targets(self) -> None:
        installer = self.load_install_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory) / "project"

            self.assertEqual(
                installer.resolve_target_directory("opencode-project", project),
                project / ".opencode" / "skills",
            )
            self.assertEqual(
                installer.resolve_target_directory("agents-project", project),
                project / ".agents" / "skills",
            )

    def test_install_script_dry_run_does_not_write(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(INSTALL_SCRIPT),
                "--target",
                "opencode-project",
                "--project",
                tempfile.gettempdir(),
                "--dry-run",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("book-reader", result.stdout)
        self.assertIn("technical-book", result.stdout)

    def test_install_script_installs_copy_and_refuses_overwrite_without_force(self) -> None:
        installer = self.load_install_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory) / "project"
            target = installer.resolve_target_directory("agents-project", project)
            skills = [skill for skill in installer.discover_skills(ROOT) if skill.name in {"book-reader", "technical-book"}]

            first = installer.install_skills(skills, target, mode="copy", force=False, dry_run=False)
            second = installer.install_skills(skills, target, mode="copy", force=False, dry_run=False)
            forced = installer.install_skills(skills, target, mode="copy", force=True, dry_run=False)

            self.assertEqual(first.installed, 2)
            self.assertEqual(first.skipped, 0)
            self.assertEqual(second.installed, 0)
            self.assertEqual(second.skipped, 2)
            self.assertEqual(forced.installed, 2)
            self.assertTrue((target / "book-reader" / "SKILL.md").is_file())
            self.assertTrue((target / "technical-book" / "SKILL.md").is_file())
            self.assertFalse((target / "lenses" / "technical-book").exists())

    def test_install_script_symlink_mode_creates_skill_symlink(self) -> None:
        installer = self.load_install_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory) / "project"
            target = installer.resolve_target_directory("opencode-project", project)
            skills = [skill for skill in installer.discover_skills(ROOT) if skill.name == "book-reader"]

            result = installer.install_skills(skills, target, mode="symlink", force=False, dry_run=False)

            self.assertEqual(result.installed, 1)
            self.assertTrue((target / "book-reader").is_symlink())
            self.assertTrue((target / "book-reader" / "SKILL.md").is_file())

    def assert_source_map_has_block_items(self, source_map: dict, kind: str) -> None:
        block_items = [item for item in source_map["items"] if item.get("kind") == kind]
        self.assertGreaterEqual(len(block_items), 1)
        for item in block_items:
            self.assertIn("text_preview", item)
            self.assertTrue(item["text_preview"].strip())
            self.assertIn("block_type", item)
            self.assertIsInstance(item["start_char"], int)
            self.assertIsInstance(item["end_char"], int)
            self.assertGreater(item["end_char"], item["start_char"])

    def assert_unique_source_map_ids(self, source_map: dict) -> None:
        ids = [item["id"] for item in source_map["items"]]
        self.assertEqual(len(ids), len(set(ids)))

    def mark_reconstructed(self, workspace: Path) -> None:
        manifest_path = workspace / "workspace.json"
        manifest = json.loads(manifest_path.read_text("utf-8"))
        manifest["workspace_stage"] = "reconstructed"
        manifest["review_status"] = "self-checked"
        manifest["current_required_action"] = "run-review"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        readme = (workspace / "README.md").read_text("utf-8").replace("workspace stage: source-ready", "workspace stage: reconstructed")
        (workspace / "README.md").write_text(readme, encoding="utf-8")
        dashboard = (workspace / "guide" / "dashboard.md").read_text("utf-8").replace("workspace stage: source-ready", "workspace stage: reconstructed")
        (workspace / "guide" / "dashboard.md").write_text(dashboard, encoding="utf-8")

    def write_skill(self, repo: Path, name: str, content: str) -> Path:
        skill_directory = repo / "skills" / name
        skill_directory.mkdir(parents=True)
        skill_file = skill_directory / "SKILL.md"
        skill_file.write_text(content, encoding="utf-8")
        return skill_file

    def load_install_module(self):
        spec = importlib.util.spec_from_file_location("install_skills", INSTALL_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules["install_skills"] = module
        spec.loader.exec_module(module)
        return module


if __name__ == "__main__":
    unittest.main()
