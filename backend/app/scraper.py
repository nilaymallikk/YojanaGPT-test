from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScrapedDocument:
    title: str
    source_url: str
    raw_text: str
    cleaned_text: str
    doc_type: str = "web"


def scrape_url(url: str) -> ScrapedDocument:
    import requests
    import trafilatura
    from bs4 import BeautifulSoup

    response = requests.get(url, timeout=30, headers={"User-Agent": "YojanaGPT/0.1"})
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")

    if "pdf" in content_type or url.lower().endswith(".pdf"):
        return parse_pdf_bytes(response.content, url)

    html = response.text
    extracted = trafilatura.extract(html, include_comments=False, include_tables=True) or ""
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else url).strip()
    fallback_text = soup.get_text("\n", strip=True)
    cleaned = extracted.strip() or fallback_text
    return ScrapedDocument(title=title, source_url=url, raw_text=fallback_text, cleaned_text=cleaned)


def parse_pdf_bytes(data: bytes, source_url: str) -> ScrapedDocument:
    from io import BytesIO

    raw_parts: list[str] = []
    try:
        import pdfplumber

        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                raw_parts.append(page.extract_text() or "")
    except Exception:
        import fitz

        with fitz.open(stream=data, filetype="pdf") as doc:
            for page in doc:
                raw_parts.append(page.get_text())

    text = "\n".join(part for part in raw_parts if part).strip()
    title = Path(source_url).name or "PDF notice"
    return ScrapedDocument(title=title, source_url=source_url, raw_text=text, cleaned_text=text, doc_type="pdf")


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        piece = " ".join(words[start : start + chunk_size]).strip()
        if piece:
            chunks.append(piece)
    return chunks
