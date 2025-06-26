"""
Tests for the orchestration system components.

This module provides integration tests for the registry, router, and workflow components.
"""

import asyncio
import uuid
import pytest

httpx = pytest.importorskip(
    "httpx", reason="httpx is required for orchestration tests"
)
pytest_asyncio = pytest.importorskip(
    "pytest_asyncio", reason="pytest_asyncio is required for orchestration tests"
)

from meepzorp.orchestration.registry import AgentDiscoveryTool, AgentRegistryTool
from meepzorp.orchestration.router import RouteRequestTool
from meepzorp.orchestration.workflows import (
    CreateWorkflowTool,
    ExecuteWorkflowTool,
    ListWorkflowsTool,
)

class MockResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class MockAsyncClient:
    """Stateful mock for ``httpx.AsyncClient`` covering registry, router and workflow endpoints."""

    agents: dict[str, dict] = {}
    workflows: dict[str, dict] = {}
    sent_requests: list[tuple[str, dict]] = []

    def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - compatibility
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json=None):
        if url.endswith("/agents"):
            agent_id = str(uuid.uuid4())
            self.agents[agent_id] = {"id": agent_id, **(json or {})}
            return MockResponse({"status": "success", "agent_id": agent_id})

        if url.endswith("/workflows") and not url.endswith("/workflows/execute"):
            workflow_id = str(uuid.uuid4())
            self.workflows[workflow_id] = {"id": workflow_id, **(json or {})}
            return MockResponse({"status": "success", "workflow_id": workflow_id})

        if url.endswith("/workflows/execute"):
            workflow_id = (json or {}).get("workflow_id")
            if workflow_id not in self.workflows:
                return MockResponse({"status": "error", "message": "Workflow not found"})
            if "invalid_input" in (json or {}).get("input_variables", {}):
                return MockResponse({"status": "error", "partial_results": {}})
            return MockResponse({
                "status": "success",
                "results": {"step1": {"status": "success", "output": "Test output"}}
            })

        if url.endswith("/mcp"):
            self.sent_requests.append((url, json))
            return MockResponse({"status": "success", "result": {"ok": True}})

        return MockResponse({})

    async def get(self, url, params=None):
        if url.endswith("/agents"):
            capability = None
            if params:
                caps = params.get("capabilities")
                capability = caps[0] if isinstance(caps, list) and caps else caps
            agents = list(self.agents.values())
            if capability:
                agents = [
                    a for a in agents
                    if any(c.get("name") == capability for c in a.get("capabilities", []))
                ]
            return MockResponse({"status": "success", "agents": agents})

        if url.endswith("/workflows"):
            return MockResponse({"status": "success", "workflows": list(self.workflows.values())})

        return MockResponse({})


@pytest_asyncio.fixture(autouse=True)
async def patch_httpx(monkeypatch):
    MockAsyncClient.agents.clear()
    MockAsyncClient.workflows.clear()
    MockAsyncClient.sent_requests.clear()
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)
    yield


@pytest_asyncio.fixture
async def mock_agent_info():
    """Fixture providing mock agent information."""
    return {
        "name": "test_agent",
        "description": "Test agent for integration testing",
        "endpoint": "http://localhost:8811",
        "capabilities": [{"name": "test_capability", "description": "Test capability"}],
        "metadata": {"version": "1.0.0", "environment": "test"},
    }


@pytest_asyncio.fixture
async def registered_agent(mock_agent_info):
    """Fixture that registers a mock agent and yields its ID."""
    registry = AgentRegistryTool()
    result = await registry.execute(mock_agent_info)
    assert result["status"] == "success"
    return result["agent_id"]


@pytest_asyncio.fixture
def mock_workflow():
    """Fixture providing a mock workflow definition."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for integration testing",
        "steps": [
            {
                "id": "step1",
                "name": "Test Step",
                "description": "A test step",
                "capability": "test_capability",
                "parameters": {"test_param": "test_value"},
            }
        ],
        "variables": {"test_var": "test_value"},
    }


@pytest.mark.asyncio
async def test_agent_registry_and_discovery():
    """Test agent registration and discovery."""
    # Initialize tools
    registry = AgentRegistryTool()
    discovery = AgentDiscoveryTool()

    # Register a test agent
    agent_info = {
        "name": "test_agent",
        "description": "Test agent for integration testing",
        "endpoint": "http://localhost:8811",
        "capabilities": [{"name": "test_capability", "description": "Test capability"}],
        "metadata": {"version": "1.0.0"},
    }

    result = await registry.execute(agent_info)
    assert result["status"] == "success"
    assert "agent_id" in result

    # Give the registry a moment to process
    await asyncio.sleep(0.1)

    # Discover agents
    discovery_result = await discovery.execute({"capabilities": ["test_capability"]})
    assert discovery_result["status"] == "success"
    assert len(discovery_result["agents"]) > 0

    # Verify agent info
    found_agent = False
    for agent in discovery_result["agents"]:
        if agent["name"] == "test_agent":
            found_agent = True
            assert any(
                cap["name"] == "test_capability" for cap in agent["capabilities"]
            )
            assert agent["endpoint"] == "http://localhost:8811"
            break
    assert found_agent, "Expected agent not found in discovery results"


@pytest.mark.asyncio
async def test_request_routing(registered_agent):
    """Test request routing to registered agent."""
    router = RouteRequestTool()

    # Give the registry a moment to process
    await asyncio.sleep(0.1)

    # Route a test request
    payload = {
        "capability": "test_capability",
        "parameters": {"test_param": "test_value"},
        "preferred_agent_id": str(registered_agent),
        "timeout": 5.0,
    }
    result = await router.execute(payload)

    assert result["status"] == "success"
    assert MockAsyncClient.sent_requests
    url, body = MockAsyncClient.sent_requests[0]
    assert url == "http://localhost:8811/mcp"
    assert body["capability"] == payload["capability"]


@pytest.mark.asyncio
async def test_workflow_creation_and_execution(mock_workflow):
    """Test workflow creation and execution."""
    # Create workflow
    creator = CreateWorkflowTool()
    create_result = await creator.execute(mock_workflow)
    assert (
        create_result["status"] == "success"
    ), f"Workflow creation failed: {create_result.get('message', 'No error message')}"
    assert "workflow_id" in create_result

    # List workflows
    lister = ListWorkflowsTool()
    list_result = await lister.execute({})
    assert list_result["status"] == "success"
    assert len(list_result["workflows"]) > 0

    # Execute workflow
    executor = ExecuteWorkflowTool()
    execute_result = await executor.execute(
        {
            "workflow_id": create_result["workflow_id"],
            "input_variables": {"test_input": "test_value"},
        }
    )
    assert (
        execute_result["status"] == "success"
    ), f"Workflow execution failed: {execute_result.get('message', 'No error message')}"
    assert "results" in execute_result


@pytest.mark.asyncio
async def test_execute_workflow_invalid_id(mock_workflow):
    """Ensure executing a non-existent workflow returns an error."""
    creator = CreateWorkflowTool()
    create_result = await creator.execute(mock_workflow)
    assert create_result["status"] == "success"

    executor = ExecuteWorkflowTool()
    execute_result = await executor.execute(
        {"workflow_id": "bogus_id", "input_variables": {}}
    )
    assert execute_result["status"] == "error"


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in orchestration components."""
    router = RouteRequestTool()

    # Test invalid capability
    result = await router.execute(
        {"capability": "nonexistent_capability", "parameters": {}, "timeout": 1.0}
    )
    assert result["status"] == "error"
    assert "message" in result

    # Test invalid agent ID
    result = await router.execute(
        {
            "capability": "test_capability",
            "parameters": {},
            "preferred_agent_id": "invalid_id",
            "timeout": 1.0,
        }
    )
    assert result["status"] == "error"
    assert "message" in result


@pytest.mark.asyncio
async def test_workflow_error_handling(mock_workflow):
    """Test workflow error handling."""
    creator = CreateWorkflowTool()
    executor = ExecuteWorkflowTool()

    # Create workflow
    create_result = await creator.execute(mock_workflow)
    assert create_result["status"] == "success"

    # Test execution with invalid input
    execute_result = await executor.execute(
        {
            "workflow_id": create_result["workflow_id"],
            "input_variables": {"invalid_input": "this_should_fail"},
        }
    )
    assert "partial_results" in execute_result

    # Test execution with invalid workflow ID
    execute_result = await executor.execute(
        {"workflow_id": "invalid_workflow_id", "input_variables": {}}
    )
    assert execute_result["status"] == "error"
    assert "message" in execute_result
