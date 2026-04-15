from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")

    primary_model: str = Field("anthropic/claude-3.5-sonnet", alias="PRIMARY_MODEL")
    fallback_models: List[str] = Field(
        default_factory=lambda: ["openai/gpt-4o-mini", "mistralai/mistral-large"],
        alias="FALLBACK_MODELS",
    )

    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    reranker_model: str = Field("BAAI/bge-reranker-base", alias="RERANKER_MODEL")

    data_dir: str = Field("data", alias="DATA_DIR")
    raw_dir: str = Field("data/raw", alias="RAW_DIR")
    chunk_dir: str = Field("data/chunks", alias="CHUNK_DIR")
    faiss_index_path: str = Field("data/index/faiss.index", alias="FAISS_INDEX_PATH")
    bm25_path: str = Field("data/index/bm25.pkl", alias="BM25_PATH")

    redis_url: str = Field("redis://redis:6379/0", alias="REDIS_URL")
    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field("ask-my-docs", alias="LANGSMITH_PROJECT")

    top_k_bm25: int = 20
    top_k_dense: int = 20
    top_k_rrf: int = 20
    top_k_rerank: int = 8
    chunk_size: int = 900
    chunk_overlap: int = 150

    faithfulness_threshold: float = 0.85
    answer_relevance_threshold: float = 0.80
    context_precision_threshold: float = 0.75
    context_recall_threshold: float = 0.75


@lru_cache
def get_settings() -> Settings:
    return Settings()