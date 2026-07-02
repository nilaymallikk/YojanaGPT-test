from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Chunk, ProfileIn, Scheme
from app.rag.bm25_search import BM25Search
from app.rag.llm import OpenRouterClient
from app.rag.reranker import get_reranker


def eligible_scheme_query(db: Session, profile: ProfileIn, limit: int = 10) -> list[Scheme]:
    query = db.query(Scheme)
    query = query.filter((Scheme.state.is_(None)) | (Scheme.state == "All India") | (Scheme.state == profile.state))
    query = query.filter((Scheme.income_limit.is_(None)) | (Scheme.income_limit >= profile.annual_income))
    return query.limit(limit).all()


async def answer_question(db: Session, query: str, profile: ProfileIn | None) -> dict:
    chunks = db.query(Chunk).limit(250).all()
    texts = [chunk.text for chunk in chunks]
    profile_text = f"{profile.model_dump() if profile else {}} {query}"

    bm25 = BM25Search(texts)
    sparse = bm25.search(profile_text, limit=20)
    candidate_indexes = [result.index for result in sparse]

    if not candidate_indexes:
        candidate_indexes = list(range(min(20, len(chunks))))

    candidates = [chunks[index] for index in candidate_indexes]
    reranked_indexes = get_reranker().rerank(profile_text, [chunk.text for chunk in candidates], limit=5)
    selected = [candidates[index] for index in reranked_indexes]

    contexts = [
        {
            "chunk_id": chunk.id,
            "scheme_id": chunk.scheme_id,
            "text": chunk.text[:1400],
            "source_url": chunk.payload.get("source_url"),
            "section_type": chunk.section_type,
        }
        for chunk in selected
    ]
    llm = OpenRouterClient()
    response = await llm.generate(query=query, profile=profile.model_dump() if profile else {}, contexts=contexts)
    return {"answer": response.answer, "contexts": contexts, "cached": response.cached, "latency_ms": response.latency_ms}
