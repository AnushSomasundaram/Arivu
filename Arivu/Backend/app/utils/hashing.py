"""Content hashing for deduplication."""

from __future__ import annotations

import hashlib


def sha256_bytes(data: bytes) -> str:
    """Return hex-encoded SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()
