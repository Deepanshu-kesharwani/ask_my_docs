from __future__ import annotations
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import IngestResponse, QueryRequest, QueryResponse
from app.ingestion.store import save_raw_file, save_chunks
from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_document
from app.settings import get_settings
from app.retrieval.bm25 import BM25Index
from app.retrieval.dense import DenseIndex
from app.retrieval.hybrid import HybridRetriever
from app.reranker.bge_reranker import BGEReranker
from app.generation.answerer import Answerer
from app.orchestration.graph import build_graph
from app.utils import ensure_dirs


router = APIRouter()
settings = get_settings()

BM25 = BM25Index()
DENSE = DenseIndex(settings.embedding_model)
RERANKER = BGEReranker(settings.reranker_model)
ANSWERER = Answerer()
GRAPH = None
DOC_CHUNKS = []


def rebuild_indexes(chunks):
    global BM25, DENSE, GRAPH, DOC_CHUNKS
    DOC_CHUNKS = chunks
    BM25.build(chunks)
    DENSE.build(chunks)
    retriever = HybridRetriever(BM25, DENSE)
    GRAPH = build_graph(
        retriever,
        RERANKER,
        ANSWERER,
        settings.top_k_bm25,
        settings.top_k_dense,
        settings.top_k_rrf,
        settings.top_k_rerank,
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest(files: List[UploadFile] = File(...)):
    print("🔥 INGEST CALLED")
    ensure_dirs(settings.raw_dir, settings.chunk_dir, "data/index")
    all_chunks = []

    for f in files:
        raw = await f.read()
        raw_path = save_raw_file(f.filename, raw)

        docs = load_document(raw_path)

        print("Loaded docs:", len(docs))   # ✅ ADD HERE

        for d in docs:
            chunks = chunk_document(d, settings.chunk_size, settings.chunk_overlap)
            print("Chunks from one doc:", len(chunks))   # ✅ ADD HERE
            all_chunks.extend(chunks)

        save_chunks(all_chunks, "latest_chunks")

    print("Total chunks:", len(all_chunks))   # ✅ ADD HERE

    rebuild_indexes(all_chunks)
    return IngestResponse(status="ok", documents=len(files), chunks=len(all_chunks))


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):

    print("GRAPH status:", GRAPH)   # ✅ ADD HERE

    if GRAPH is None:
        raise HTTPException(status_code=400, detail="No index found. Ingest documents first.")

    result = GRAPH.invoke({"query": req.query})
    chunks = [c for c, _ in result["reranked"]]

    return ANSWERER.answer(req.query, chunks, model=req.model)


@router.post("/evaluate")
async def evaluate():
    from app.evaluation.ragas_eval import run_ragas_eval
    return run_ragas_eval()