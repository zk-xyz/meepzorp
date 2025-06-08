"""
Tests for the orchestration system components.

This module provides integration tests for the registry, router, and workflow components.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict

import httpx
import pytest
import pytest_asyncio

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
    """Stateful mock of ``httpx.AsyncClient`` used in integration tests."""

    agents: Dict[str, Dict[str, Any]] = {}
    workflows: Dict[str, Dict[str, Any]] = {}
    sent_requests: list[Dict[str, Any]] = []

    def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - mimic httpx API
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json=None):
        if url.endswith("/agents"):
            agent_id = str(uuid.uuid4())
            data = dict(json)
            data["id"] = agent_id
            self.__class__.agents[agent_id] = data
            return MockResponse({"status": "success", "agent_id": agent_id})

        if url.endswith("/workflows") and not url.endswith("/workflows/execute"):
            workflow_id = str(uuid.uuid4())
            data = dict(json)
            data["id"] = workflow_id
            self.__class__.workflows[workflow_id] = data
            return MockResponse({"status": "success", "workflow_id": workflow_id})

        if url.endswith("/workflows/execute"):
            workflow_id = json.get("workflow_id") if json else None
            if workflow_id not in self.__class__.workflows:
                return MockResponse({"status": "error", "message": "Workflow not found"})
            return MockResponse(
                {
                    "status": "success",
                    "results": {
                        "step1": {"status": "success", "output": "Test output"}
                    },
                }
            )

        if url.endswith("/mcp"):
            self.__class__.sent_requests.append({"url": url, "json": json})
            return MockResponse({"status": "success", "result": {"ok": True}})

        return MockResponse({})

    async def get(self, url, params=None):
        if url.endswith("/agents"):
            capability_filter = params.get("capabilities", []) if params else []
            agents: list[Dict[str, Any]] = []
            for agent in self.__class__.agents.values():
                caps = agent.get("capabilities", [])
                if not capability_filter or any(
                    cap.get("name") in capability_filter for cap in caps
                ):
                    agents.append(agent)
            return MockResponse({"status": "success", "agents": agents})

        if url.endswith("/workflows"):
            workflows = list(self.__class__.workflows.values())
            return MockResponse({"status": "success", "workflows": workflows})

        return MockResponse({})


@pytest_asyncio.fixture(autouse=True)
async def patch_httpx(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)
    MockAsyncClient.agents.clear()
    MockAsyncClient.workflows.clear()
    MockAsyncClient.sent_requests.clear()
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
    agent_id = result["agent_id"]
    assert agent_id

    # Give the registry a moment to process
    await asyncio.sleep(0.1)

    # Discover agents
    discovery_result = await discovery.execute({"capabilities": ["test_capability"]})
    assert discovery_result["status"] == "success"
    assert len(discovery_result["agents"]) > 0

    # Verify agent info
    found_agent = False
    for agent in discovery_result["agents"]:
        if agent["id"] == agent_id:
            found_agent = True
            assert agent["name"] == "test_agent"
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
    result = await router.execute(
        {
            "capability": "test_capability",
            "parameters": {"test_param": "test_value"},
            "preferred_agent_id": str(registered_agent),  # Ensure it's a string
            "timeout": 5.0,
        }
    )

    assert (
        result["status"] == "success"
    ), f"Request routing failed: {result.get('message', 'No error message')}"
    assert "result" in result, "Response missing result field"


@pytest.mark.asyncio
async def test_workflow_creation_and_execution(mock_workflow):
    """Test workflow creation and execution."""
    # Create workflow
    creator = CreateWorkflowTool()
    create_result = await creator.execute(mock_workflow)
    assert (
        create_result["status"] == "success"
    ), f"Workflow creation failed: {create_result.get('message', 'No error message')}"
    workflow_id = create_result["workflow_id"]
    assert workflow_id

    # List workflows
    lister = ListWorkflowsTool()
    list_result = await lister.execute({})
    assert list_result["status"] == "success"
    assert any(wf["id"] == workflow_id for wf in list_result["workflows"])

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
    assert execute_result["status"] == "success"
    assert "results" in execute_result

    # Test execution with invalid workflow ID
    execute_result = await executor.execute(
        {"workflow_id": "invalid_workflow_id", "input_variables": {}}
    )
    assert execute_result["status"] == "error"
    assert "message" in execute_result
