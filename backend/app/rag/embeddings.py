from __future__ import annotations

import hashlib
import math
from functools import lru_cache

from app.config import get_settings


class EmbeddingService:
    def __init__(self, model_name: str, dimensions: int = 384) -> None:
        self.model_name = model_name
        self.dimensions = dimensions
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            model = self._load_model()
            vectors = model.encode(texts, normalize_embeddings=True)
            return [vector.tolist() for vector in vectors]
        except Exception:
            return [self._fallback_embedding(text) for text in texts]

    def _fallback_embedding(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


@lru_cache
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(settings.embedding_model)
