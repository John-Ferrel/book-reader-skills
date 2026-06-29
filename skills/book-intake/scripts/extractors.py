"""Format-specific extraction that stops before semantic interpretation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from language import normalize_language


class ExtractionError(RuntimeError):
    """The supplied source cannot be mechanically extracted."""


class MissingDependencyError(ExtractionError):
    """A supported source requires an optional runtime dependency."""


@dataclass
class ExtractedSection:
    kind: str
    title: str
    content: str
    href: str | None = None
    page: int | None = None
    reason: str = "source section"


@dataclass
class ExtractionResult:
    source_format: str
    title: str
    authors: list[str]
    metadata_language: str | None
    sections: list[ExtractedSection]
    extraction_method: str
    extraction_confidence: str
    warnings: list[str] = field(default_factory=list)
    page_count: int | None = None

    @property
    def extracted_text(self) -> str:
        parts = [section.content.rstrip() for section in self.sections if section.content.strip()]
        return "\n\n".join(parts).rstrip() + "\n" if parts else ""


SUPPORTED_FORMATS = {".txt", ".md", ".epub", ".pdf"}
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def _fallback_title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip() or "Untitled book"


def _decode_text(path: Path) -> tuple[str, str]:
    payload = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk", "latin-1"):
        try:
            return payload.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ExtractionError(f"could not decode text source: {path}")


def _chunk_plain_text(text: str, kind: str) -> list[ExtractedSection]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        return []
    chunks: list[ExtractedSection] = []
    buffer: list[str] = []
    size = 0
    for paragraph in paragraphs:
        if buffer and size + len(paragraph) > 5000:
            content = "\n\n".join(buffer)
            chunks.append(
                ExtractedSection(kind, f"Text range {len(chunks) + 1}", content, reason="paragraph chunk")
            )
            buffer, size = [], 0
        buffer.append(paragraph)
        size += len(paragraph) + 2
    if buffer:
        chunks.append(
            ExtractedSection(kind, f"Text range {len(chunks) + 1}", "\n\n".join(buffer), reason="paragraph chunk")
        )
    return chunks


def _sections_from_text(text: str, source_format: str) -> list[ExtractedSection]:
    headings = list(HEADING_PATTERN.finditer(text))
    if not headings:
        return _chunk_plain_text(text, f"{source_format}-chunk")
    sections: list[ExtractedSection] = []
    if text[: headings[0].start()].strip():
        sections.extend(_chunk_plain_text(text[: headings[0].start()], f"{source_format}-chunk"))
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        title = heading.group(2).strip()
        sections.append(
            ExtractedSection(
                f"{source_format}-section",
                title,
                text[heading.start() : end].strip(),
                reason="markdown heading",
            )
        )
    return sections


def _extract_text(path: Path, source_format: str) -> ExtractionResult:
    text, encoding = _decode_text(path)
    sections = _sections_from_text(text, source_format)
    if not sections:
        raise ExtractionError(f"source contains no readable text: {path}")
    title_match = HEADING_PATTERN.search(text)
    title = title_match.group(2).strip() if title_match else _fallback_title(path)
    warning = [] if encoding in {"utf-8", "utf-8-sig"} else [f"Decoded source using {encoding}."]
    return ExtractionResult(
        source_format=source_format,
        title=title,
        authors=[],
        metadata_language=None,
        sections=sections,
        extraction_method=f"plain text decode ({encoding})",
        extraction_confidence="high",
        warnings=warning,
    )


def _html_to_markdownish(payload: bytes) -> tuple[str, str | None, list[str]]:
    try:
        from bs4 import BeautifulSoup
    except ImportError as error:
        raise MissingDependencyError(
            "EPUB ingestion requires ebooklib and beautifulsoup4. Run: pip install -e ."
        ) from error
    warnings: list[str] = []
    try:
        soup = BeautifulSoup(payload, "lxml")
    except Exception:
        soup = BeautifulSoup(payload, "html.parser")
        warnings.append("lxml parser was unavailable; used Python HTML parser instead.")
    for noise in soup(["script", "style", "nav", "noscript"]):
        noise.decompose()
    body = soup.body or soup
    blocks: list[str] = []
    heading: str | None = None
    block_names = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre"}
    for node in body.find_all(list(block_names)):
        if node.find_parent(block_names):
            continue
        text = node.get_text(" ", strip=True)
        if not text:
            continue
        if node.name and node.name.startswith("h") and node.name[1:].isdigit():
            level = min(int(node.name[1:]), 6)
            heading = heading or text
            blocks.append(f"{'#' * level} {text}")
        elif node.name == "li":
            blocks.append(f"- {text}")
        elif node.name == "blockquote":
            blocks.append(f"> {text}")
        elif node.name == "pre":
            blocks.append(f"```\n{text}\n```")
        else:
            blocks.append(text)
    if not blocks:
        fallback = body.get_text("\n", strip=True)
        if fallback:
            blocks.append(fallback)
            warnings.append("HTML had no recognized blocks; used flattened text.")
    return "\n\n".join(blocks), heading, warnings


def _epub_metadata(book: Any, namespace: str, name: str) -> list[str]:
    values = book.get_metadata(namespace, name) or []
    return [str(value[0]).strip() for value in values if value and str(value[0]).strip()]


def _extract_epub(path: Path) -> ExtractionResult:
    try:
        from ebooklib import ITEM_DOCUMENT, epub
    except ImportError as error:
        raise MissingDependencyError(
            "EPUB ingestion requires ebooklib, beautifulsoup4, and lxml. Run: pip install -e ."
        ) from error
    try:
        book = epub.read_epub(str(path))
    except Exception as error:
        raise ExtractionError(f"could not read EPUB {path}: {error}") from error
    titles = _epub_metadata(book, "DC", "title")
    authors = _epub_metadata(book, "DC", "creator")
    languages = _epub_metadata(book, "DC", "language")
    warnings: list[str] = [
        "EPUB images, tables, visual styling, and some footnotes/endnotes may not survive text extraction."
    ]
    document_items = list(book.get_items_of_type(ITEM_DOCUMENT))
    by_id = {str(item.get_id()): item for item in document_items}
    ordered_items = []
    seen: set[str] = set()
    for spine_entry in book.spine:
        item_id = str(spine_entry[0])
        item = by_id.get(item_id)
        if item is not None:
            ordered_items.append(item)
            seen.add(item_id)
    ordered_items.extend(item for item in document_items if str(item.get_id()) not in seen)
    sections: list[ExtractedSection] = []
    for item in ordered_items:
        href = str(item.get_name())
        if "nav" in href.lower() or "toc" in href.lower():
            continue
        content, heading, item_warnings = _html_to_markdownish(item.get_content())
        warnings.extend(item_warnings)
        if not content.strip():
            continue
        sections.append(
            ExtractedSection(
                "epub-section",
                heading or Path(href).stem.replace("_", " ") or f"EPUB section {len(sections) + 1}",
                content,
                href=href,
                reason="EPUB spine item",
            )
        )
    if not sections:
        raise ExtractionError("EPUB contains no readable spine text; it may be image-only or malformed.")
    return ExtractionResult(
        source_format="epub",
        title=titles[0] if titles else _fallback_title(path),
        authors=authors,
        metadata_language=normalize_language(languages[0]) if languages else None,
        sections=sections,
        extraction_method="ebooklib spine extraction with BeautifulSoup HTML-to-Markdown-ish conversion",
        extraction_confidence="medium",
        warnings=list(dict.fromkeys(warnings)),
    )


def _extract_pdf(path: Path) -> ExtractionResult:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise MissingDependencyError("PDF ingestion requires pypdf. Run: pip install -e .") from error
    try:
        reader = PdfReader(str(path))
    except Exception as error:
        raise ExtractionError(f"could not read PDF {path}: {error}") from error
    metadata = reader.metadata or {}
    title = str(getattr(metadata, "title", "") or "").strip() or _fallback_title(path)
    author = str(getattr(metadata, "author", "") or "").strip()
    warnings = [
        "Scanned PDFs are unsupported without OCR.",
        "PDF layout may be degraded; figures and tables may be lost.",
        "Page extraction can fragment paragraphs and reading order.",
    ]
    sections: list[ExtractedSection] = []
    empty_pages = 0
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as error:
            page_text = ""
            warnings.append(f"Page {page_number} could not be extracted: {error}")
        if not page_text.strip():
            empty_pages += 1
            warnings.append(f"Page {page_number} has no extractable text and may be scanned.")
        sections.append(
            ExtractedSection(
                "pdf-page",
                f"Page {page_number}",
                f"<!-- page: {page_number} -->\n\n{page_text.strip()}",
                page=page_number,
                reason="PDF page",
            )
        )
    confidence = "low" if empty_pages == len(sections) else "medium"
    return ExtractionResult(
        source_format="pdf",
        title=title,
        authors=[author] if author else [],
        metadata_language=None,
        sections=sections,
        extraction_method="pypdf page-by-page text extraction",
        extraction_confidence=confidence,
        warnings=list(dict.fromkeys(warnings)),
        page_count=len(sections),
    )


def extract_book(path: Path) -> ExtractionResult:
    """Extract a supported book source without deriving reading conclusions."""
    if not path.is_file():
        raise ExtractionError(f"input file does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ExtractionError(f"unsupported input format {suffix or '(none)'}; supported formats: {supported}")
    if suffix == ".txt":
        return _extract_text(path, "txt")
    if suffix == ".md":
        return _extract_text(path, "md")
    if suffix == ".epub":
        return _extract_epub(path)
    return _extract_pdf(path)
