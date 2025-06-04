import httpx
import pytest
import pytest_asyncio

from meepzorp.orchestration.router import RouteRequestTool


class MockResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class CaptureAsyncClient:
    def __init__(self):
        self.sent = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json=None):
        self.sent.append((url, json))
        return MockResponse({"status": "success", "result": {"ok": True}})

    async def get(self, url, params=None):
        if url.endswith("/agents"):
            return MockResponse(
                {
                    "status": "success",
                    "agents": [
                        {
                            "id": "test_agent_id",
                            "endpoint": "http://agent.test",
                            "capabilities": [{"name": "test_capability"}],
                        }
                    ],
                }
            )
        return MockResponse({})


@pytest_asyncio.fixture
def capture_client(monkeypatch):
    client = CaptureAsyncClient()
    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: client)
    return client


@pytest.mark.asyncio
async def test_router_forwards_request(capture_client):
    router = RouteRequestTool()
    result = await router.execute(
        {"capability": "test_capability", "parameters": {"x": 1}}
    )
    assert result["status"] == "success"
    assert capture_client.sent
    url, payload = capture_client.sent[0]
    assert url == "http://agent.test/mcp"
    assert payload["capability"] == "test_capability"
