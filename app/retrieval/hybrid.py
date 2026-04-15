from __future__ import annotations

from collections import defaultdict
from app.retrieval.bm25 import BM25Index
from app.retrieval.dense import DenseIndex
from app.schemas import Chunk


def rrf_fusion(results_a: list[tuple[Chunk, float]], results_b: list[tuple[Chunk, float]], k: int = 60) -> list[tuple[Chunk, float]]:
    scores = defaultdict(float)
    seen = {}
    for rank, (chunk, _) in enumerate(results_a, start=1):
        scores[chunk.chunk_id] += 1.0 / (k + rank)
        seen[chunk.chunk_id] = chunk
    for rank, (chunk, _) in enumerate(results_b, start=1):
        scores[chunk.chunk_id] += 1.0 / (k + rank)
        seen[chunk.chunk_id] = chunk
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(seen[cid], score) for cid, score in ranked]


class HybridRetriever:
    def __init__(self, bm25: BM25Index, dense: DenseIndex):
        self.bm25 = bm25
        self.dense = dense

    def search(self, query: str, top_k_bm25: int, top_k_dense: int, top_k: int) -> list[tuple[Chunk, float]]:
        sparse = self.bm25.search(query, top_k=top_k_bm25)
        dense = self.dense.search(query, top_k=top_k_dense)
        fused = rrf_fusion(sparse, dense)
        return fused[:top_k]