from __future__ import annotations

from dataclasses import dataclass

from rank_bm25 import BM25Okapi


@dataclass(frozen=True)
class BM25Result:
    index: int
    score: float


class BM25Search:
    def __init__(self, documents: list[str]) -> None:
        self.documents = documents
        self.tokens = [self._tokenize(doc) for doc in documents]
        self.index = BM25Okapi(self.tokens) if self.tokens else None

    def search(self, query: str, limit: int = 10) -> list[BM25Result]:
        if not self.index:
            return []
        scores = self.index.get_scores(self._tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        return [BM25Result(index=i, score=float(score)) for i, score in ranked[:limit]]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token.strip(".,;:()[]{}").lower() for token in text.split() if token.strip()]
