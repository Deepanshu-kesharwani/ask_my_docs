from __future__ import annotations

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.schemas import Chunk


class DenseIndex:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks: list[Chunk] = []
        self.embeddings = None

    def build(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        texts = [c.text for c in chunks]
        emb = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        self.embeddings = np.array(emb).astype("float32")
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings)

    def search(self, query: str, top_k: int = 10) -> list[tuple[Chunk, float]]:
        if self.index is None:
            return []
        q = self.model.encode([query], normalize_embeddings=True)
        scores, idx = self.index.search(np.array(q).astype("float32"), top_k)
        out = []
        for i, s in zip(idx[0], scores[0]):
            if i == -1:
                continue
            out.append((self.chunks[i], float(s)))
        return out