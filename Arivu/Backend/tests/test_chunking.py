"""Tests for the text chunking module."""

from __future__ import annotations

from app.rag.chunking import chunk_text


def test_chunk_basic():
    text = "a" * 500
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
    assert len(chunks) >= 3
    assert chunks[0].char_offset == 0
    assert chunks[0].char_length == 200


def test_chunk_overlap():
    text = "a" * 400
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
    # Second chunk should start at 150 (200 - 50 overlap)
    assert chunks[1].char_offset == 150


def test_chunk_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_short_text():
    text = "short"
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0].text == "short"


def test_chunk_indices():
    text = "x" * 1000
    chunks = chunk_text(text, chunk_size=300, chunk_overlap=50)
    for i, c in enumerate(chunks):
        assert c.index == i
