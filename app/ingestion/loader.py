from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.schemas import Chunk
from app.utils import sha1_text


def load_pdf(path: str) -> list[Chunk]:
    reader = PdfReader(path)
    chunks: list[Chunk] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(
                Chunk(
                    chunk_id=sha1_text(f"{path}-{i}-{text[:200]}"),
                    source=Path(path).name,
                    page=i + 1,
                    section=None,
                    text=text,
                    metadata={"source_type": "pdf"},
                )
            )
    return chunks


def load_docx(path: str) -> list[Chunk]:
    doc = DocxDocument(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [
        Chunk(
            chunk_id=sha1_text(f"{path}-docx-{text[:200]}"),
            source=Path(path).name,
            page=None,
            section=None,
            text=text,
            metadata={"source_type": "docx"},
        )
    ]


def load_txt(path: str) -> list[Chunk]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return [
        Chunk(
            chunk_id=sha1_text(f"{path}-txt-{text[:200]}"),
            source=Path(path).name,
            page=None,
            section=None,
            text=text,
            metadata={"source_type": "txt"},
        )
    ]


def load_html(path: str) -> list[Chunk]:
    html = Path(path).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    return [
        Chunk(
            chunk_id=sha1_text(f"{path}-html-{text[:200]}"),
            source=Path(path).name,
            page=None,
            section=None,
            text=text,
            metadata={"source_type": "html"},
        )
    ]


def load_document(path: str) -> list[Chunk]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    if ext == ".docx":
        return load_docx(path)
    if ext in {".txt", ".md"}:
        return load_txt(path)
    if ext in {".html", ".htm"}:
        return load_html(path)
    raise ValueError(f"Unsupported file type: {ext}")