"""Tests for file upload, listing, and deletion (using /files routes)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_txt(client: AsyncClient):
    proj = await client.post("/api/projects", json={"name": "Doc Test"})
    pid = proj.json()["id"]

    content = b"This is a test document with some content for RAG testing."
    resp = await client.post(
        f"/api/projects/{pid}/files/upload",
        files=[("files", ("test.txt", content, "text/plain"))],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["uploaded"]) == 1
    item = data["uploaded"][0]
    assert item["filename"] == "test.txt"
    assert item["status"] == "indexed"


@pytest.mark.asyncio
async def test_upload_md(client: AsyncClient):
    proj = await client.post("/api/projects", json={"name": "MD Test"})
    pid = proj.json()["id"]

    content = b"# Hello\n\nThis is a markdown document.\n\n## Section 2\n\nMore content here."
    resp = await client.post(
        f"/api/projects/{pid}/files/upload",
        files=[("files", ("readme.md", content, "text/markdown"))],
    )
    assert resp.status_code == 201
    assert resp.json()["uploaded"][0]["status"] == "indexed"


@pytest.mark.asyncio
async def test_upload_unsupported(client: AsyncClient):
    proj = await client.post("/api/projects", json={"name": "Bad Upload"})
    pid = proj.json()["id"]

    resp = await client.post(
        f"/api/projects/{pid}/files/upload",
        files=[("files", ("image.jpg", b"\xff\xd8\xff", "image/jpeg"))],
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_files(client: AsyncClient):
    proj = await client.post("/api/projects", json={"name": "List Files"})
    pid = proj.json()["id"]

    await client.post(
        f"/api/projects/{pid}/files/upload",
        files=[("files", ("a.txt", b"file a content", "text/plain"))],
    )
    await client.post(
        f"/api/projects/{pid}/files/upload",
        files=[("files", ("b.txt", b"file b content", "text/plain"))],
    )

    resp = await client.get(f"/api/projects/{pid}/files")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # Verify FileRecordOut shape
    assert "mime_type" in data[0]
    assert "size_bytes" in data[0]


@pytest.mark.asyncio
async def test_delete_file(client: AsyncClient):
    proj = await client.post("/api/projects", json={"name": "Del File"})
    pid = proj.json()["id"]

    upload_resp = await client.post(
        f"/api/projects/{pid}/files/upload",
        files=[("files", ("del.txt", b"delete me", "text/plain"))],
    )
    file_id = upload_resp.json()["uploaded"][0]["id"]

    resp = await client.delete(f"/api/projects/{pid}/files/{file_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/projects/{pid}/files/{file_id}")
    assert resp.status_code == 404
