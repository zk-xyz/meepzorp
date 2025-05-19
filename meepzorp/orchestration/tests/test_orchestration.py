"""
Tests for the orchestration system components.

This module provides integration tests for the registry, router, and workflow components.
"""
import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any
import httpx

from meepzorp.orchestration.registry import AgentRegistryTool, AgentDiscoveryTool, AGENT_DB
from meepzorp.orchestration.router import RouteRequestTool
from meepzorp.orchestration.workflows import (
    ExecuteWorkflowTool,
    CreateWorkflowTool,
    ListWorkflowsTool,
    WORKFLOW_DB,
)
from meepzorp.orchestration.tests import mock_agent

@pytest_asyncio.fixture
async def mock_agent_info():
    """Fixture providing mock agent information."""
    return {
        "name": "test_agent",
        "description": "Test agent for integration testing",
        "endpoint": "http://localhost:8811",
        "capabilities": [{"name": "test_capability", "description": "Test capability"}],
        "metadata": {
            "version": "1.0.0",
            "environment": "test"
        }
    }


@pytest_asyncio.fixture(autouse=True)
async def reset_stores():
    AGENT_DB.clear()
    WORKFLOW_DB.clear()
    yield
    AGENT_DB.clear()
    WORKFLOW_DB.clear()


@pytest_asyncio.fixture(autouse=True)
async def mock_agent_server(monkeypatch):
    """Patch httpx.AsyncClient to route to the mock agent app."""
    transport = httpx.ASGITransport(app=mock_agent.app)

    original_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs.setdefault("transport", transport)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)
    yield
    monkeypatch.setattr(httpx, "AsyncClient", original_client)

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
                "parameters": {
                    "test_param": "test_value"
                }
            }
        ],
        "variables": {
            "test_var": "test_value"
        }
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
        "metadata": {"version": "1.0.0"}
    }
    
    result = await registry.execute(agent_info)
    assert result["status"] == "success"
    assert "agent_id" in result
    
    # Give the registry a moment to process
    await asyncio.sleep(0.1)
    
    # Discover agents
    discovery_result = await discovery.execute({
        "capabilities": ["test_capability"]
    })
    assert discovery_result["status"] == "success"
    assert len(discovery_result["agents"]) > 0
    
    # Verify agent info
    found_agent = False
    for agent in discovery_result["agents"]:
        if agent["name"] == "test_agent":
            found_agent = True
            assert any(cap["name"] == "test_capability" for cap in agent["capabilities"])
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
    result = await router.execute({
        "capability": "test_capability",
        "parameters": {
            "test_param": "test_value"
        },
        "preferred_agent_id": str(registered_agent),  # Ensure it's a string
        "timeout": 5.0
    })
    
    assert result["status"] == "success", f"Request routing failed: {result.get('message', 'No error message')}"
    assert "result" in result, "Response missing result field"

@pytest.mark.asyncio
async def test_workflow_creation_and_execution(mock_workflow):
    """Test workflow creation and execution."""
    # Create workflow
    creator = CreateWorkflowTool()
    create_result = await creator.execute(mock_workflow)
    assert create_result["status"] == "success", f"Workflow creation failed: {create_result.get('message', 'No error message')}"
    assert "workflow_id" in create_result
    
    # List workflows
    lister = ListWorkflowsTool()
    list_result = await lister.execute({})
    assert list_result["status"] == "success"
    assert len(list_result["workflows"]) > 0
    
    # Execute workflow
    executor = ExecuteWorkflowTool()
    execute_result = await executor.execute({
        "workflow_id": create_result["workflow_id"],
        "input_variables": {
            "test_input": "test_value"
        }
    })
    assert execute_result["status"] == "success", f"Workflow execution failed: {execute_result.get('message', 'No error message')}"
    assert "results" in execute_result

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in orchestration components."""
    router = RouteRequestTool()
    
    # Test invalid capability
    result = await router.execute({
        "capability": "nonexistent_capability",
        "parameters": {},
        "timeout": 1.0
    })
    assert result["status"] == "error"
    assert "message" in result
    
    # Test invalid agent ID
    result = await router.execute({
        "capability": "test_capability",
        "parameters": {},
        "preferred_agent_id": "invalid_id",
        "timeout": 1.0
    })
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
    execute_result = await executor.execute({
        "workflow_id": create_result["workflow_id"],
        "input_variables": {
            "invalid_input": "this_should_fail"
        }
    })
    assert "partial_results" in execute_result
    
    # Test execution with invalid workflow ID
    execute_result = await executor.execute({
        "workflow_id": "invalid_workflow_id",
        "input_variables": {}
    })
    assert execute_result["status"] == "error"
    assert "message" in execute_result 