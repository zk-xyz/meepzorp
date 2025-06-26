import importlib
import pytest
from fastapi.testclient import TestClient


class MockResponse:
    def __init__(self, status_code: int, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json

def load_main(monkeypatch):
    """Set required environment variables and import the app module."""
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "key")
    module = importlib.import_module("registry_service.main")
    importlib.reload(module)
    return module

@pytest.fixture
def client(monkeypatch):
    main = load_main(monkeypatch)
    return TestClient(main.app)

def test_register_agent(mocker, client):
    async_mock = mocker.AsyncMock()
    async_mock.__aenter__.return_value = async_mock
    async_mock.post.return_value = MockResponse(201, [{"id": "123"}])
    mocker.patch("httpx.AsyncClient", return_value=async_mock)

    response = client.post("/agents", json={"name": "a"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["agent_id"] == "123"

def test_get_agents(mocker, client):
    async_mock = mocker.AsyncMock()
    async_mock.__aenter__.return_value = async_mock
    async_mock.get.return_value = MockResponse(200, [{"id": "1", "capabilities": []}])
    mocker.patch("httpx.AsyncClient", return_value=async_mock)

    response = client.get("/agents", params={"capabilities": "echo"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["agents"], list)
