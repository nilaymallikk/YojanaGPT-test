from __future__ import annotations

from functools import lru_cache

from app.config import get_settings


class Reranker:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, passages: list[str], limit: int = 5) -> list[int]:
        if not passages:
            return []
        try:
            model = self._load_model()
            scores = model.predict([(query, passage) for passage in passages])
            ranked = sorted(enumerate(scores), key=lambda item: float(item[1]), reverse=True)
            return [index for index, _ in ranked[:limit]]
        except Exception:
            return list(range(min(limit, len(passages))))


@lru_cache
def get_reranker() -> Reranker:
    settings = get_settings()
    return Reranker(settings.reranker_model)
