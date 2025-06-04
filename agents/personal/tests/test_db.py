import os
import pytest
from agents.personal.src.db import KnowledgeDB
import httpx

class MockResponse:
    def __init__(self, status_code: int, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json

@pytest.fixture
def db(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    return KnowledgeDB()

@pytest.mark.asyncio
async def test_store_knowledge(mocker, db):
    post_resp = MockResponse(201, {"id": "1", "content": "hello", "tags": {"tags": ["tag1"]}})
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.post.return_value = post_resp
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    result = await db.store_knowledge("hello", ["tag1"], [0.1])
    assert result["id"] == "1"
    assert result["tags"] == ["tag1"]

@pytest.mark.asyncio
async def test_query_knowledge(mocker, db):
    get_resp = MockResponse(200, [{"id": "1", "content": "hello", "tags": "[\"tag1\"]"}])
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = get_resp
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    items = await db.query_knowledge(query="hello")
    assert len(items) == 1
    assert items[0]["tags"] == ["tag1"]

@pytest.mark.asyncio
async def test_update_knowledge(mocker, db):
    patch_resp = MockResponse(200, [{"id": "1", "content": "updated", "tags": {"tags": ["tag2"]}}])
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.patch.return_value = patch_resp
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    result = await db.update_knowledge("1", content="updated", tags=["tag2"])
    assert result["content"] == "updated"
    assert result["tags"] == ["tag2"]

@pytest.mark.asyncio
async def test_delete_knowledge(mocker, db):
    delete_resp = MockResponse(204)
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.delete.return_value = delete_resp
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    await db.delete_knowledge("1")

