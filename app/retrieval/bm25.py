from __future__ import annotations

import pickle
import re
from rank_bm25 import BM25Okapi
from app.schemas import Chunk


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class BM25Index:
    def __init__(self):
        self.bm25: BM25Okapi | None = None
        self.chunks: list[Chunk] = []

    def build(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        corpus = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 10) -> list[tuple[Chunk, float]]:
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self.chunks[i], float(score)) for i, score in ranked]

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump({"chunks": self.chunks, "bm25": self.bm25}, f)

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.chunks = data["chunks"]
        self.bm25 = data["bm25"]