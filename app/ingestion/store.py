from __future__ import annotations

import json
from pathlib import Path
from app.settings import get_settings
from app.schemas import Chunk
from app.utils import ensure_dirs


def save_raw_file(upload_name: str, content: bytes) -> str:
    s = get_settings()
    ensure_dirs(s.raw_dir, s.chunk_dir, "data/index")
    path = Path(s.raw_dir) / upload_name
    path.write_bytes(content)
    return str(path)


def save_chunks(chunks: list[Chunk], filename: str) -> str:
    s = get_settings()
    ensure_dirs(s.chunk_dir)
    path = Path(s.chunk_dir) / f"{filename}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")
    return str(path)


def load_chunks_from_jsonl(path: str) -> list[Chunk]:
    out: list[Chunk] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            out.append(Chunk.model_validate_json(line))
    return out