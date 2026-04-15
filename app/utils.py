import hashlib
import os
from pathlib import Path
from typing import Iterable


def ensure_dirs(*paths: str) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def read_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def chunk_iter(items: list, size: int) -> Iterable[list]:
    for i in range(0, len(items), size):
        yield items[i : i + size]