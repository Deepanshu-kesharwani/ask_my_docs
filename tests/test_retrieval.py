from app.schemas import Chunk
from app.retrieval.bm25 import BM25Index

def test_bm25_search():
    chunks = [
        Chunk(chunk_id="1", source="a.txt", text="apple banana policy", metadata={}),
        Chunk(chunk_id="2", source="b.txt", text="server deployment guide", metadata={}),
    ]
    idx = BM25Index()
    idx.build(chunks)
    res = idx.search("banana", top_k=1)
    assert res[0][0].chunk_id == "1"