import pytest
import sys
import types
try:  # httpx may not be installed in the execution environment
    import httpx  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal test env
    httpx = types.ModuleType("httpx")
    class _DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
    httpx.AsyncClient = _DummyClient
    sys.modules["httpx"] = httpx

import os
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_KEY", "key")
import registry_service.main
from registry_service.main import app, RegistryDB, register_agent, get_agents
from unittest.mock import AsyncMock, patch
import asyncio

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "key")


def test_register_agent():
    async_mock = AsyncMock(return_value={"id": "123"})
    db_obj = RegistryDB()
    with patch("registry_service.main.db", db_obj):
        with patch.object(db_obj, "add_agent", async_mock):
            result = asyncio.run(register_agent({"name": "a"}))
    assert result["status"] == "success"
    assert result["agent_id"] == "123"

def test_get_agents():
    async_mock = AsyncMock(return_value=[{"id": "1", "capabilities": []}])
    db_obj = RegistryDB()
    with patch("registry_service.main.db", db_obj):
        with patch.object(db_obj, "list_agents", async_mock):
            data = asyncio.run(get_agents("echo"))
    assert data["status"] == "success"
    assert isinstance(data["agents"], list)


def test_get_agents_multi_capabilities():
    async_mock = AsyncMock(return_value=[{"id": "1", "capabilities": []}])
    db_obj = RegistryDB()
    with patch("registry_service.main.db", db_obj):
        with patch.object(db_obj, "list_agents", async_mock):
            data = asyncio.run(get_agents("echo,ping"))
    assert data["status"] == "success"
    assert isinstance(data["agents"], list)
    async_mock.assert_awaited_once_with(["echo", "ping"])
