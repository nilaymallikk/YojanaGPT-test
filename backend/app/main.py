from __future__ import annotations

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db, init_db
from app.models import (
    AskRequest,
    ChatHistory,
    Chunk,
    Document,
    EligibilityRequest,
    IngestUrlRequest,
    ProfileIn,
    ProfileOut,
    Scheme,
    UserProfile,
)
from app.official_sources import list_official_sources
from app.rag.embeddings import get_embedding_service
from app.rag.pipeline import answer_question, eligible_scheme_query
from app.rag.vector_store import VectorStore
from app.scraper import chunk_text, parse_pdf_bytes, scrape_url

settings = get_settings()
app = FastAPI(title="YojanaGPT API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True, "app": settings.app_name}


@app.post("/profile", response_model=ProfileOut)
def create_profile(profile: ProfileIn, db: Session = Depends(get_db)) -> UserProfile:
    user = UserProfile(**profile.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/ask")
async def ask(request: AskRequest, db: Session = Depends(get_db)) -> dict:
    profile = request.profile
    if request.profile_id:
        user = db.get(UserProfile, request.profile_id)
        if not user:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile = ProfileIn.model_validate(user, from_attributes=True)

    result = await answer_question(db, request.query, profile)
    db.add(
        ChatHistory(
            profile_id=request.profile_id,
            query=request.query,
            answer=result["answer"],
            citations={"contexts": result["contexts"]},
            latency_ms=result["latency_ms"],
        )
    )
    db.commit()
    return result


@app.post("/eligibility/check")
def check_eligibility(request: EligibilityRequest, db: Session = Depends(get_db)) -> dict:
    schemes = eligible_scheme_query(db, request.profile, request.limit)
    return {
        "matches": [
            {
                "id": scheme.id,
                "name": scheme.name,
                "ministry": scheme.ministry,
                "state": scheme.state or "All India",
                "deadline": scheme.deadline,
                "source_url": scheme.source_url,
                "reason": "Matched state and income metadata filters.",
            }
            for scheme in schemes
        ]
    }


@app.post("/ingest/url")
def ingest_url(request: IngestUrlRequest, db: Session = Depends(get_db)) -> dict:
    scraped = scrape_url(str(request.url))
    scheme = Scheme(
        name=request.scheme_name or scraped.title[:230],
        state=request.state or "All India",
        categories={"values": [request.category] if request.category else []},
        source_url=scraped.source_url,
        summary=scraped.cleaned_text[:1200],
    )
    db.add(scheme)
    db.flush()
    document = Document(
        scheme_id=scheme.id,
        title=scraped.title,
        source_url=scraped.source_url,
        raw_text=scraped.raw_text,
        cleaned_text=scraped.cleaned_text,
        doc_type=scraped.doc_type,
    )
    db.add(document)
    db.flush()
    chunks = _persist_chunks(db, document, scheme.id, request.state, request.category)
    db.commit()
    _index_chunks(chunks)
    return {"scheme_id": scheme.id, "document_id": document.id, "chunks": len(chunks)}


@app.post("/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    data = await file.read()
    scraped = parse_pdf_bytes(data, file.filename or "uploaded.pdf")
    document = Document(
        title=scraped.title,
        source_url=scraped.source_url,
        raw_text=scraped.raw_text,
        cleaned_text=scraped.cleaned_text,
        doc_type="pdf",
    )
    db.add(document)
    db.flush()
    chunks = _persist_chunks(db, document, None, None, None)
    db.commit()
    _index_chunks(chunks)
    return {"document_id": document.id, "chunks": len(chunks)}


@app.get("/schemes")
def list_schemes(db: Session = Depends(get_db)) -> dict:
    schemes = db.query(Scheme).order_by(Scheme.created_at.desc()).limit(100).all()
    return {
        "schemes": [
            {
                "id": scheme.id,
                "name": scheme.name,
                "state": scheme.state or "All India",
                "ministry": scheme.ministry,
                "deadline": scheme.deadline,
                "source_url": scheme.source_url,
                "summary": scheme.summary,
            }
            for scheme in schemes
        ]
    }


@app.get("/schemes/{scheme_id}")
def get_scheme(scheme_id: int, db: Session = Depends(get_db)) -> dict:
    scheme = db.get(Scheme, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {
        "id": scheme.id,
        "name": scheme.name,
        "state": scheme.state or "All India",
        "ministry": scheme.ministry,
        "deadline": scheme.deadline,
        "source_url": scheme.source_url,
        "summary": scheme.summary,
        "documents": [{"id": doc.id, "title": doc.title, "source_url": doc.source_url} for doc in scheme.documents],
    }


@app.get("/sources")
def list_sources(db: Session = Depends(get_db)) -> dict:
    documents = db.query(Document).order_by(Document.created_at.desc()).limit(100).all()
    return {
        "sources": [
            {
                "id": doc.id,
                "title": doc.title,
                "source_url": doc.source_url,
                "doc_type": doc.doc_type,
                "chunks": len(doc.chunks),
            }
            for doc in documents
        ]
    }


@app.get("/official-sources")
def official_sources() -> dict:
    return {"sources": list_official_sources()}


def _persist_chunks(
    db: Session,
    document: Document,
    scheme_id: int | None,
    state: str | None,
    category: str | None,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for text in chunk_text(document.cleaned_text):
        chunk = Chunk(
            document_id=document.id,
            scheme_id=scheme_id,
            text=text,
            section_type=_guess_section(text),
            state=state or "All India",
            category=category,
            payload={"source_url": document.source_url, "title": document.title},
        )
        db.add(chunk)
        chunks.append(chunk)
    db.flush()
    return chunks


def _index_chunks(chunks: list[Chunk]) -> None:
    if not chunks:
        return
    vectors = get_embedding_service().embed([chunk.text for chunk in chunks])
    payloads = [
        {
            "chunk_id": chunk.id,
            "scheme_id": chunk.scheme_id,
            "source_url": chunk.payload.get("source_url"),
            "title": chunk.payload.get("title"),
            "section_type": chunk.section_type,
            "state": chunk.state,
            "category": chunk.category,
        }
        for chunk in chunks
    ]
    try:
        VectorStore().upsert_chunks(vectors, payloads)
    except Exception:
        pass


def _guess_section(text: str) -> str:
    lowered = text.lower()
    if "eligibility" in lowered or "eligible" in lowered:
        return "eligibility"
    if "document" in lowered:
        return "documents"
    if "benefit" in lowered or "assistance" in lowered:
        return "benefits"
    if "deadline" in lowered or "last date" in lowered:
        return "deadline"
    return "general"
