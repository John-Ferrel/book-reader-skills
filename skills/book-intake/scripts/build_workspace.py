#!/usr/bin/env python3
"""Write an ingest-ready reconstruction workspace from mechanical extraction."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from extractors import ExtractionResult
from language import detect_language, normalize_language
from source_map import normalize_and_map, source_sections_markdown, unit_candidates_markdown


REQUIRED_DIRECTORIES = (
    "source",
    "evidence",
    "units",
    "notes/unit-notes",
    "notes/deep-notes",
    "threads",
    "model",
    "indexes",
    "guide",
    "review",
    "reports",
)
SKILLS_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = SKILLS_ROOT / "book-reconstruct" / "templates"
REVIEW_TEMPLATE_ROOT = SKILLS_ROOT / "book-reviewer" / "templates"
MODEL_FILES = (
    "author-problem.md",
    "book-design.md",
    "argument-architecture.md",
    "concept-system.md",
    "reader-path.md",
    "assumptions-tradeoffs.md",
    "edition-layers.md",
)
INDEX_FILES = (
    "concept-index.md",
    "claim-evidence-index.md",
    "design-principle-index.md",
    "entity-index.md",
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, content: object) -> None:
    _write(path, json.dumps(content, ensure_ascii=False, indent=2))


def _render_template(path: Path, title: str) -> str:
    return path.read_text(encoding="utf-8").replace("{{BOOK_TITLE}}", title)


def _language_documents(
    title: str,
    source_format: str,
    language: str,
    confidence: str,
    warnings: list[str],
    output_language: str,
) -> dict[str, str]:
    chinese = output_language == "zh-CN"
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) or "- None recorded during extraction."
    if chinese:
        return {
            "README.md": f"""# {title} 阅读重建工作区

## 当前状态

- source format: {source_format}
- language: {language}
- extraction confidence: {confidence}
- workspace stage: source-ready
- review status: not-reviewed
- revision status: not-started
- review round: 0 / 3
- current required action: run-reconstruction
- reconstruction status: not-started

## 如何使用这个工作区

1. 先读 `guide/dashboard.md`。
2. 在 `source/normalized.md` 阅读可用原文。
3. 用 `units/unit-candidates.md` 作为结构线索。
4. 由 agent 确认 semantic reading units。
5. 在 `notes/` 中写 unit/deep notes。
6. 在 `model/` 中重建作者问题、概念系统、论证架构和书籍设计。
7. 在 `indexes/` 中连接概念、主张、设计原则与证据。

## 当前可依赖内容

- extracted source
- source map with section/page and block-level anchors
- unit candidates

## 当前不能依赖内容

- author model 尚未完成
- argument architecture 尚未完成
- concept system 尚未完成

## 下一步建议指令

- “继续使用 book-reader 进行第一轮重建阅读”
- “根据 unit candidates 确认 semantic reading units”
- “阅读 source/normalized.md 并填充 model/”
- “运行独立 book-reviewer audit”
""",
            "guide/dashboard.md": f"""# 工作区仪表板 — {title}

## 当前 loop 状态

- workspace stage: source-ready
- review status: not-reviewed
- revision status: not-started
- review round: 0 / 3
- current required action: run-reconstruction

## 现在有什么

- 已提取 `{source_format}` 来源，证据锚点见 `evidence/source-map.json`。
- `source/normalized.md` 可供阅读；`units/unit-candidates.md` 仅提供机械结构候选。
- `model/` 模板已准备，但没有任何作者/书籍设计推断。

## 还缺什么

- agent 确认最终 semantic reading units
- 带证据的 unit/deep notes 和跨单元 threads
- `model/` 的问题、概念、论证、设计、读者路径、取舍重建
- 从模型主张回到证据的索引条目

## 下一步

1. 阅读 normalized source 和 source map。
2. 确认、合并或拆分 unit candidates。
3. 从有代表性的 unit 开始写 evidence-linked notes。
4. 仅在有证据后填充 `model/`；每项推断必须包含置信度和替代解释。
5. 优先保持 `source block -> note item -> model inference` 追溯链；缺少 note item 时标记 weak traceability。

## 核心 artifacts

`model/` 是中心。`source/`、`evidence/`、`units/`、`notes/` 和 `threads/` 用来检验和修正它。
""",
            "guide/continue-reading.md": """# 继续重建阅读

先处理能改变模型的证据，而不是机械地填满候选单元。确认单元边界后，跟踪概念、论证或叙事线索，并把低置信度但影响大的模型主张列为深读重点。
""",
            "guide/limitations.md": f"""# 来源与提取限制

{_format_limitations(source_format, True)}

## 本次提取警告

{warning_lines}
""",
        }
    return {
        "README.md": f"""# {title} Reconstruction Workspace

## Current status

- source format: {source_format}
- language: {language}
- extraction confidence: {confidence}
- workspace stage: source-ready
- review status: not-reviewed
- revision status: not-started
- review round: 0 / 3
- current required action: run-reconstruction
- reconstruction status: not-started

## How to use this workspace

1. Read `guide/dashboard.md` first.
2. Read the available source in `source/normalized.md`.
3. Use `units/unit-candidates.md` only as structural clues.
4. Have an agent confirm semantic reading units.
5. Write unit/deep notes in `notes/`.
6. Reconstruct the author/book design model in `model/`.
7. Link concepts, claims, and design principles in `indexes/`.

## What is currently dependable

- extracted source
- source map with section/page and block-level anchors
- unit candidates

## What is not currently dependable

- author model is not yet reconstructed
- argument architecture is not yet reconstructed
- concept system is not yet reconstructed

## Suggested next prompts

- “Continue with book-reader for the first reconstruction reading.”
- “Confirm semantic reading units from unit candidates.”
- “Read source/normalized.md and populate model/.”
- “Run independent book-reviewer audit.”
""",
        "guide/dashboard.md": f"""# Dashboard — {title}

## Current loop state

- workspace stage: source-ready
- review status: not-reviewed
- revision status: not-started
- review round: 0 / 3
- current required action: run-reconstruction

## What exists now

- `{source_format}` source has been extracted; anchors are in `evidence/source-map.json`.
- `source/normalized.md` is ready to read; `units/unit-candidates.md` is only mechanical structure.
- `model/` templates are ready, but no author/book-design inference has been made.

## What is missing

- Agent-confirmed semantic reading units
- Evidence-linked unit/deep notes and cross-unit threads
- Reconstruction of problem, concepts, argument, design, reader path, and tradeoffs in `model/`
- Index entries linking model claims back to evidence

## Next action

1. Read normalized source and the source map.
2. Confirm, merge, or split unit candidates.
3. Write evidence-linked notes for representative units.
4. Populate `model/` only after evidence exists; state confidence and alternatives.
5. Prefer the chain `source block -> note item -> model inference`; mark weak traceability when a note item is missing.

## Core artifacts

`model/` is central. `source/`, `evidence/`, `units/`, `notes/`, and `threads/` exist to test and revise it.
""",
        "guide/continue-reading.md": """# Continue Reconstruction Reading

Prioritize evidence that can revise the model rather than mechanically filling every candidate. Confirm unit boundaries, trace concept/argument/narrative threads, and target high-impact low-confidence model claims for close reading.
""",
        "guide/limitations.md": f"""# Source and Extraction Limitations

{_format_limitations(source_format, False)}

## Extraction warnings

{warning_lines}
""",
    }


def _format_limitations(source_format: str, chinese: bool) -> str:
    if chinese:
        messages = {
            "epub": "- 图片、表格和样式可能丢失。\n- metadata 可能不完整。\n- 脚注/尾注可能被压平。",
            "pdf": "- 不支持扫描 PDF（未实现 OCR）。\n- 版面可能退化。\n- 表格和图片可能丢失。\n- 按页提取可能打断段落。",
            "txt": "- 结构只能从标题或空行推断。\n- metadata 可能缺失。",
            "md": "- 结构主要来自 Markdown 标题。\n- metadata 可能缺失。",
        }
    else:
        messages = {
            "epub": "- Images, tables, and styling may be lost.\n- Metadata may be incomplete.\n- Footnotes/endnotes may be flattened.",
            "pdf": "- Scanned PDFs are unsupported (no OCR).\n- Layout may be degraded.\n- Tables and figures may be lost.\n- Page extraction may fragment paragraphs.",
            "txt": "- Structure may only be inferred from headings or spacing.\n- Metadata may be absent.",
            "md": "- Structure primarily comes from Markdown headings.\n- Metadata may be absent.",
        }
    return messages[source_format]


def _supporting_documents(title: str, source_map_count: int, output_language: str) -> dict[str, str]:
    chinese = output_language == "zh-CN"
    if chinese:
        return {
            "notes/unit-notes/README.md": "# Unit Notes\n\n从 `units/` 确认后的单元开始。使用稳定 note item ID，例如 `obs-ru-006-001`、`inf-ru-006-001`。每个重要条目引用 block-level source anchor；推断必须包含 confidence 和 alternative。\n",
            "notes/deep-notes/README.md": "# Deep Notes\n\n仅为能改变高影响模型主张的细读问题创建 deep note。deep note 也必须保留 `source block -> note item -> model inference` 追溯链。\n",
            "threads/README.md": "# Threads\n\n这里记录跨单元的概念、主张、主题、角色、方法或母题；它们不是自动生成的结论。\n",
            "threads/thread-candidates.md": f"# Thread Candidates\n\n现有 {source_map_count} 个 source anchors。agent 应从已读单元发现跨单元线索，不能由此文件虚构主题。\n",
            "indexes/README.md": "# Indexes\n\n索引必须把 reconstruction claim、概念或设计选择连接到 source anchors 和 note item IDs。当前只有启动信息，没有推断条目。\n",
            "review/README.md": "# Review\n\n独立 reviewer 应审查模型主张是否有证据、置信度、替代解释和可修正条件。\n",
        }
    return {
        "notes/unit-notes/README.md": "# Unit Notes\n\nStart after confirming units in `units/`. Use stable note item IDs such as `obs-ru-006-001` and `inf-ru-006-001`. Each important item cites a block-level source anchor; inferences include confidence and an alternative.\n",
        "notes/deep-notes/README.md": "# Deep Notes\n\nCreate a deep note only for close-reading questions that can change a high-impact model claim. Deep notes also preserve the `source block -> note item -> model inference` chain.\n",
        "threads/README.md": "# Threads\n\nRecord cross-unit concepts, claims, themes, actors, methods, or motifs here; they are not automatically inferred conclusions.\n",
        "threads/thread-candidates.md": f"# Thread Candidates\n\nThere are {source_map_count} source anchors. The agent should discover cross-unit threads from read units; this file must not invent themes.\n",
        "indexes/README.md": "# Indexes\n\nIndexes must connect reconstruction claims, concepts, or design choices to source anchors and note item IDs. They currently contain bootstrap context, not inferred entries.\n",
        "review/README.md": "# Review\n\nAn independent reviewer should test whether model claims have evidence, confidence, alternatives, and revision conditions.\n",
    }


def _bootstrap_index(content: str, source_map_count: int, output_language: str) -> str:
    message = (
        f"\n## Workspace bootstrap\n\n{source_map_count} source anchors are available. No reconstruction claim has been entered yet; add entries only after evidence-linked reading.\n"
        if output_language != "zh-CN"
        else f"\n## 工作区启动信息\n\n现有 {source_map_count} 个 source anchors。尚未录入重建主张；只能在 evidence-linked reading 后新增条目。\n"
    )
    return content.rstrip() + message


def _prepare_directories(workspace: Path) -> None:
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError(f"workspace already exists and is not empty: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)
    for directory in REQUIRED_DIRECTORIES:
        (workspace / directory).mkdir(parents=True, exist_ok=True)


def create_ingested_workspace(
    source_path: Path,
    workspace: Path,
    extracted: ExtractionResult,
    book_language_override: str | None = None,
    output_language_override: str | None = None,
) -> dict[str, object]:
    """Build all runtime artifacts, leaving interpretation to the reading agent."""
    _prepare_directories(workspace)
    normalized, source_map = normalize_and_map(extracted.sections)
    if not normalized.strip():
        raise ValueError("extraction produced no normalized text")
    metadata_language = normalize_language(extracted.metadata_language)
    if book_language_override:
        book_language = normalize_language(book_language_override)
        language_source = "user-specified"
    elif metadata_language != "unknown":
        book_language = metadata_language
        language_source = "metadata"
    else:
        book_language = detect_language(normalized)
        language_source = "detected" if book_language != "unknown" else "unresolved"
    output_language = normalize_language(output_language_override) if output_language_override else book_language
    if output_language == "unknown":
        output_language = book_language
    section_count = len([item for item in source_map["items"] if not str(item.get("kind", "")).endswith("-block")])
    metadata = {
        "source_path": str(source_path.resolve()),
        "source_format": extracted.source_format,
        "title": extracted.title,
        "authors": extracted.authors,
        "language": book_language,
        "output_language": output_language,
        "language_source": language_source,
        "extraction_method": extracted.extraction_method,
        "extraction_confidence": extracted.extraction_confidence,
        "page_count": extracted.page_count,
        "section_count": section_count,
        "character_count": len(normalized),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "warnings": extracted.warnings,
    }
    original_name = f"original{source_path.suffix.lower()}"
    shutil.copy2(source_path, workspace / "source" / original_name)
    _write(workspace / "source/extracted.md", extracted.extracted_text)
    _write(workspace / "source/normalized.md", normalized)
    _write_json(workspace / "source/source-metadata.json", metadata)
    _write_json(workspace / "evidence/source-map.json", source_map)
    _write(workspace / "source/sections.md", source_sections_markdown(source_map))
    warnings = "\n".join(f"- {warning}" for warning in extracted.warnings) or "- No extraction warnings recorded."
    _write(workspace / "evidence/extraction-warnings.md", f"# Extraction Warnings\n\n{warnings}")
    _write(workspace / "units/README.md", "# Units\n\nFinal semantic reading units are agent judgments. Start with `unit-candidates.md`, then confirm, merge, split, or discard candidates.\n")
    _write(workspace / "units/unit-candidates.md", unit_candidates_markdown(source_map, output_language))
    documents = _language_documents(
        extracted.title,
        extracted.source_format,
        book_language,
        extracted.extraction_confidence,
        extracted.warnings,
        output_language,
    )
    documents.update(_supporting_documents(extracted.title, len(source_map["items"]), output_language))
    for relative_path, content in documents.items():
        _write(workspace / relative_path, content)
    for model_file in MODEL_FILES:
        _write(workspace / "model" / model_file, _render_template(TEMPLATE_ROOT / "model" / model_file, extracted.title))
    for index_file in INDEX_FILES:
        template = _render_template(TEMPLATE_ROOT / "indexes" / index_file, extracted.title)
        _write(workspace / "indexes" / index_file, _bootstrap_index(template, len(source_map["items"]), output_language))
    _write(workspace / "guide/review-targets.md", _render_template(TEMPLATE_ROOT / "guide" / "review-targets.md", extracted.title))
    _write(workspace / "review/review-report.md", _render_template(REVIEW_TEMPLATE_ROOT / "review-report.md", extracted.title))
    _write(workspace / "review/revision-plan.md", _render_template(REVIEW_TEMPLATE_ROOT / "revision-plan.md", extracted.title))
    manifest = {
        "title": extracted.title,
        "workspace_stage": "source-ready",
        "reconstruction_status": "not-started",
        "audit_status": "not-run",
        "coverage_depth": "surface",
        "review_status": "not-reviewed",
        "revision_status": "not-started",
        "review_round": 0,
        "max_review_rounds": 3,
        "stability_status": "unstable",
        "last_reader_session": None,
        "last_reviewer_session": None,
        "last_reviser_session": None,
        "current_required_action": "run-reconstruction",
        "primary_lens": None,
        "secondary_lenses": [],
        "lens_rationale": None,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "source_metadata": "source/source-metadata.json",
        "validation_report": "reports/validation-report.md",
        "purpose": "evidence-linked reconstruction workspace",
    }
    _write_json(workspace / "workspace.json", manifest)
    return {"metadata": metadata, "source_map": source_map}
