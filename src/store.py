from __future__ import annotations
from typing import Any, Callable
from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """Isolated in-memory store. Dot products equal cosine for unit vectors."""

    def __init__(self, collection_name: str = "documents",
                 embedding_fn: Callable[[str], list[float]] | None = None) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._collection = None
        self._store: list[dict[str, Any]] = []
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata)
        metadata.setdefault("doc_id", doc.id)
        embedding = list(self._embedding_fn(doc.content))
        record = {"id": doc.id, "record_id": self._next_index,
                  "content": doc.content, "metadata": metadata, "embedding": embedding}
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []
        vector = self._embedding_fn(query)
        results = []
        for record in records:
            if len(vector) != len(record["embedding"]):
                raise ValueError("Query and document embedding dimensions differ")
            results.append({"id": record["id"], "content": record["content"],
                            "metadata": dict(record["metadata"]),
                            "score": _dot(vector, record["embedding"])})
        return sorted(results, key=lambda result: result["score"], reverse=True)[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        records = [self._make_record(doc) for doc in docs]
        self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3,
                           metadata_filter: dict | None = None) -> list[dict]:
        records = [record for record in self._store
                   if all(key in record["metadata"] and record["metadata"][key] == value
                          for key, value in (metadata_filter or {}).items())]
        return self._search_records(query, records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        old_size = len(self._store)
        self._store = [r for r in self._store if r["metadata"]["doc_id"] != doc_id]
        return len(self._store) < old_size
