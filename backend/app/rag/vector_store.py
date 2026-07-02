from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.collection = settings.qdrant_collection
        self.client = QdrantClient(url=settings.qdrant_url, timeout=10)

    def ensure_collection(self, vector_size: int = 384) -> None:
        collections = self.client.get_collections().collections
        if any(collection.name == self.collection for collection in collections):
            return
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    def upsert_chunks(self, vectors: list[list[float]], payloads: list[dict]) -> None:
        if not vectors:
            return
        self.ensure_collection(len(vectors[0]))
        points = [
            models.PointStruct(id=int(payload["chunk_id"]), vector=vector, payload=payload)
            for vector, payload in zip(vectors, payloads, strict=True)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector: list[float], limit: int = 10, state: str | None = None) -> list[dict]:
        self.ensure_collection(len(vector))
        must = []
        if state:
            must.append(models.FieldCondition(key="state", match=models.MatchAny(any=[state, "All India"])))
        query_filter = models.Filter(must=must) if must else None
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
        return [{"score": result.score, "payload": result.payload or {}} for result in results]
