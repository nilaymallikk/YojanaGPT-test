from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserProfile(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(40))
    state: Mapped[str] = mapped_column(String(80), index=True)
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    annual_income: Mapped[float] = mapped_column(Float, index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    student: Mapped[bool] = mapped_column(default=False)
    disability: Mapped[bool] = mapped_column(default=False)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Scheme(Base):
    __tablename__ = "schemes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(240), index=True)
    ministry: Mapped[str | None] = mapped_column(String(240), nullable=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    categories: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    income_limit: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    education_levels: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    deadline: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_url: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    documents: Mapped[list["Document"]] = relationship(back_populates="scheme", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    scheme_id: Mapped[int | None] = mapped_column(ForeignKey("schemes.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(260))
    source_url: Mapped[str] = mapped_column(Text, index=True)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    cleaned_text: Mapped[str] = mapped_column(Text, default="")
    doc_type: Mapped[str] = mapped_column(String(40), default="web")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scheme: Mapped[Scheme | None] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    scheme_id: Mapped[int | None] = mapped_column(ForeignKey("schemes.id"), nullable=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    section_type: Mapped[str] = mapped_column(String(60), default="general")
    state: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    income_limit: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    document: Mapped[Document] = relationship(back_populates="chunks")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    query: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    citations: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProfileIn(BaseModel):
    name: str | None = None
    age: int = Field(ge=0, le=120)
    gender: str
    state: str
    district: str | None = None
    annual_income: float = Field(ge=0)
    category: str
    student: bool = False
    disability: bool = False
    occupation: str | None = None
    education_level: str | None = None


class ProfileOut(ProfileIn):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AskRequest(BaseModel):
    query: str = Field(min_length=3)
    profile: ProfileIn | None = None
    profile_id: int | None = None


class IngestUrlRequest(BaseModel):
    url: HttpUrl
    state: str | None = None
    category: str | None = None
    scheme_name: str | None = None


class EligibilityRequest(BaseModel):
    profile: ProfileIn
    limit: int = Field(default=10, ge=1, le=50)
