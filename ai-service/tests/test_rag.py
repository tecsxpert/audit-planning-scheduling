import pytest
import shutil
from pathlib import Path
from services.rag_service import RagService
from services.config import settings

@pytest.fixture
def temp_chroma_path(tmp_path, monkeypatch):
    test_db = tmp_path / "chroma_test"
    monkeypatch.setattr(settings, "chroma_path", test_db)
    yield test_db
    if test_db.exists():
        shutil.rmtree(test_db)

def test_rag_embedding_and_query(temp_chroma_path):
    rag = RagService()
    
    # Manually seed a dummy document for testing
    dummy_text = "The financial audit found a major discrepancy in Q3 revenues."
    chunks = [{"id": "chunk1", "text": dummy_text, "source": "test_doc.txt"}]
    
    rag._collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=rag._embed_texts([c["text"] for c in chunks]),
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    
    # Query it back
    results = rag.retrieve("financial audit revenues", limit=1)
    
    assert len(results) == 1
    assert "financial audit" in results[0]["content"]
    assert results[0]["source"] == "test_doc.txt"
    assert results[0]["score"] > 0
