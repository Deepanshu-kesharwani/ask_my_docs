from __future__ import annotations

from sentence_transformers import CrossEncoder
from app.schemas import Chunk


class BGEReranker:
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[tuple[Chunk, float]], top_k: int = 8) -> list[tuple[Chunk, float]]:
        pairs = [(query, c.text) for c, _ in candidates]
        scores = self.model.predict(pairs)
        ranked = sorted(zip([c for c, _ in candidates], scores), key=lambda x: x[1], reverse=True)
        return [(chunk, float(score)) for chunk, score in ranked[:top_k]]