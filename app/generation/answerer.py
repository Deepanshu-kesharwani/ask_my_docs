from __future__ import annotations

from app.generation.prompts import SYSTEM_PROMPT
from app.llm.openrouter_client import OpenRouterClient
from app.schemas import Chunk, Citation, QueryResponse


def build_context(chunks: list[Chunk]) -> str:
    lines = []
    for c in chunks:
        loc = f"{c.source}"
        if c.page is not None:
            loc += f":page {c.page}"
        lines.append(f"[{loc}|{c.chunk_id}]\n{c.text}")
    return "\n\n".join(lines)


class Answerer:
    def __init__(self):
        self.llm = OpenRouterClient()

    def answer(self, query: str, chunks: list[Chunk], model: str | None = None) -> QueryResponse:
        context = build_context(chunks)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {query}\n\nContext:\n{context}\n\nReturn a direct answer with citations.",
            },
        ]
        result = self.llm.chat(messages=messages, model=model, temperature=0.2)
        citations = [
            Citation(
                chunk_id=c.chunk_id,
                source=c.source,
                page=c.page,
                score=1.0,
                excerpt=c.text[:240],
            )
            for c in chunks
        ]
        return QueryResponse(answer=result.content, citations=citations, retrieved_chunks=chunks, model_used=result.model)