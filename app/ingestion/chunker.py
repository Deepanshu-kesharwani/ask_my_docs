from __future__ import annotations

from app.schemas import Chunk
from app.utils import sha1_text


def recursive_split(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    separators = ["\n\n", "\n", ". ", " ", ""]
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    def split_with_sep(t: str, sep: str) -> list[str]:
        if sep == "":
            return [t[i : i + chunk_size] for i in range(0, len(t), chunk_size - overlap)]
        parts = t.split(sep)
        out, cur = [], ""
        for part in parts:
            candidate = (cur + sep + part).strip() if cur else part.strip()
            if len(candidate) <= chunk_size:
                cur = candidate
            else:
                if cur:
                    out.append(cur)
                cur = part.strip()
        if cur:
            out.append(cur)
        return out

    segments = [text]
    for sep in separators:
        next_segments = []
        for seg in segments:
            if len(seg) <= chunk_size:
                next_segments.append(seg)
            else:
                next_segments.extend(split_with_sep(seg, sep))
        segments = next_segments

    merged = []
    for seg in segments:
        if not merged:
            merged.append(seg)
            continue
        if len(merged[-1]) + len(seg) <= chunk_size:
            merged[-1] = merged[-1] + " " + seg
        else:
            merged.append(seg)

    return merged


def chunk_document(doc: Chunk, chunk_size: int, overlap: int) -> list[Chunk]:
    texts = recursive_split(doc.text, chunk_size=chunk_size, overlap=overlap)
    chunks: list[Chunk] = []
    for idx, txt in enumerate(texts):
        chunks.append(
            Chunk(
                chunk_id=sha1_text(f"{doc.source}-{doc.page}-{idx}-{txt[:120]}"),
                source=doc.source,
                page=doc.page,
                section=doc.section,
                text=txt,
                metadata={**doc.metadata, "parent_chunk": doc.chunk_id, "chunk_index": idx},
            )
        )
    return chunks