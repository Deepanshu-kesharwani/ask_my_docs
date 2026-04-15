from pydantic import BaseModel, Field
from typing import Any, List, Optional


class Chunk(BaseModel):
    chunk_id: str
    source: str
    page: Optional[int] = None
    section: Optional[str] = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    status: str
    documents: int
    chunks: int


class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None
    top_k: int = 5


class Citation(BaseModel):
    chunk_id: str
    source: str
    page: Optional[int] = None
    score: float
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieved_chunks: List[Chunk] = Field(default_factory=list)
    model_used: str


class EvalRequest(BaseModel):
    dataset_path: str