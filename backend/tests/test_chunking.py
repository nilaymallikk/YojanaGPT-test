from app.scraper import chunk_text


def test_chunk_text_keeps_short_text_together() -> None:
    assert chunk_text("one two three", chunk_size=10) == ["one two three"]


def test_chunk_text_overlaps_long_text() -> None:
    text = " ".join(str(i) for i in range(25))
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) >= 3
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]
