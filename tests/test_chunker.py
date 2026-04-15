from app.ingestion.chunker import recursive_split

def test_recursive_split_makes_chunks():
    text = "A " * 2000
    chunks = recursive_split(text, chunk_size=200, overlap=20)
    assert len(chunks) > 1