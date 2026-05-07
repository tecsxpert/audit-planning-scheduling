import logging
import os
from typing import Any

from dotenv import load_dotenv
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

load_dotenv()

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class ChromaClient:
    def __init__(self, collection_name: str = "audit_planning"):
        self.persist_directory = os.getenv("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_data"))
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self._client = Client(Settings(persist_directory=self.persist_directory, is_persistent=True))
        self._embedder = SentenceTransformer(self.embedding_model_name)
        self.collection = self._client.get_or_create_collection(name=collection_name)

    def embed(self, text: str) -> list[float]:
        return self._embedder.encode(text, normalize_embeddings=True).tolist()

    def add_documents(self, documents: list[str], ids: list[str] | None = None, metadatas: list[dict[str, Any]] | None = None):
        embeddings = [self.embed(text) for text in documents]
        self.collection.add(
            ids=ids or [str(i) for i in range(len(documents))],
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def query(self, query_text: str, n_results: int = 3) -> dict:
        query_embedding = self.embed(query_text)
        result = self.collection.query(query_embeddings=[query_embedding], n_results=n_results, include=["documents", "metadatas", "distances"])
        documents = result.get("documents", [[]])[0] if result.get("documents") else []
        return {"documents": documents, "metadata": result.get("metadatas", [[]])[0] if result.get("metadatas") else [], "distances": result.get("distances", [[]])[0] if result.get("distances") else []}

    def count(self) -> int:
        return self.collection.count()
