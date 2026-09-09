"""User File Adapter (PART III §9). The highest-priority source for
personal author-corpus material (Tier 1 in references/source-hierarchy.md).

Deliberately local-only: this module never makes a network call, and a
user manuscript is never sent to an external scholarly API "merely for
stylistic analysis." No OCR is implemented — PDF text extraction requires
either host-native extraction or an injected extractor callable; if
neither is available, extraction fails loudly rather than guessing.
"""

from __future__ import annotations

import os
import re
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable, Optional
from xml.etree import ElementTree as ET

from scb.adapters.base import AdapterCapabilities

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".html", ".htm", ".xml", ".docx", ".pdf"}


class UnsupportedFileType(ValueError):
    pass


class ExtractionUnavailable(RuntimeError):
    """Raised when a format (currently: PDF) needs an extractor that was
    not provided — never silently guessed at."""


@dataclass
class ExtractedDocument:
    text: str
    source_format: str
    source_path: str


class _HtmlTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip and data.strip():
            self._parts.append(data.strip())

    def get_text(self) -> str:
        return "\n".join(self._parts)


def _extract_txt(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def _extract_html(raw: bytes) -> str:
    parser = _HtmlTextExtractor()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return parser.get_text()


def _extract_xml(raw: bytes) -> str:
    root = ET.fromstring(raw)
    return "\n".join(t.strip() for t in root.itertext() if t and t.strip())


_DOCX_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _extract_docx(raw: bytes) -> str:
    import io

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        with zf.open("word/document.xml") as f:
            root = ET.fromstring(f.read())
    paragraphs = []
    for para in root.iter("{%s}p" % _DOCX_NS["w"]):
        runs = [t.text or "" for t in para.iter("{%s}t" % _DOCX_NS["w"])]
        text = "".join(runs).strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


class UserFileAdapter:
    """Not a BaseAdapter subclass — local file extraction has no HTTP
    client, cache, or rate-limit state; it still exposes the same
    capability-declaration contract every adapter is expected to."""

    name = "user_files"
    capabilities = AdapterCapabilities(lookup=True)

    def __init__(self, pdf_extractor: Optional[Callable[[bytes], str]] = None):
        self.pdf_extractor = pdf_extractor

    def extract_text(self, file_path: str) -> ExtractedDocument:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFileType("unsupported file extension: %s" % ext)

        with open(file_path, "rb") as f:
            raw = f.read()

        if ext in (".txt", ".md", ".markdown"):
            text = _extract_txt(raw)
            fmt = "markdown" if ext in (".md", ".markdown") else "text"
        elif ext in (".html", ".htm"):
            text = _extract_html(raw)
            fmt = "html"
        elif ext == ".xml":
            text = _extract_xml(raw)
            fmt = "xml"
        elif ext == ".docx":
            text = _extract_docx(raw)
            fmt = "docx"
        elif ext == ".pdf":
            if self.pdf_extractor is None:
                raise ExtractionUnavailable(
                    "PDF text extraction requires a host-native or injected extractor; "
                    "none was provided (see UserFileAdapter(pdf_extractor=...))"
                )
            text = self.pdf_extractor(raw)
            fmt = "pdf"
        else:  # pragma: no cover — guarded by SUPPORTED_EXTENSIONS check above
            raise UnsupportedFileType(ext)

        text = re.sub(r"[ \t]+\n", "\n", text).strip()
        return ExtractedDocument(text=text, source_format=fmt, source_path=file_path)
