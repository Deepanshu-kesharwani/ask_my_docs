from __future__ import annotations

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from app.retrieval.hybrid import HybridRetriever
from app.reranker.bge_reranker import BGEReranker
from app.generation.answerer import Answerer
from app.schemas import Chunk


class RAGState(TypedDict, total=False):
    query: str
    rewritten_query: str
    candidates: List[tuple[Chunk, float]]
    reranked: List[tuple[Chunk, float]]
    answer: str
    model: str


def build_graph(retriever: HybridRetriever, reranker: BGEReranker, answerer: Answerer, top_k_bm25: int, top_k_dense: int, top_k_rrf: int, top_k_rerank: int):
    def rewrite(state: RAGState) -> RAGState:
        return {"rewritten_query": state["query"]}

    def retrieve(state: RAGState) -> RAGState:
        cands = retriever.search(state["rewritten_query"], top_k_bm25, top_k_dense, top_k_rrf)
        return {"candidates": cands}

    def rerank(state: RAGState) -> RAGState:
        ranked = reranker.rerank(state["rewritten_query"], state["candidates"], top_k=top_k_rerank)
        return {"reranked": ranked}

    def generate(state: RAGState) -> RAGState:
        chunks = [c for c, _ in state["reranked"]]
        resp = answerer.answer(state["rewritten_query"], chunks)
        return {"answer": resp.answer, "model": resp.model_used}

    graph = StateGraph(RAGState)
    graph.add_node("rewrite", rewrite)
    graph.add_node("retrieve", retrieve)
    graph.add_node("rerank", rerank)
    graph.add_node("generate", generate)

    graph.set_entry_point("rewrite")
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", END)
    return graph.compile()