"""
Workflow management tools for the orchestration system.
"""

from typing import Dict, Any, List
import logging
import uuid
import os
import httpx

logger = logging.getLogger(__name__)


class CreateWorkflowTool:
    """Tool for creating new workflows."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("WORKFLOW_URL", "http://localhost:8000")

    async def execute(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow."""
        logger.info(f"Creating workflow: {workflow['name']}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/workflows", json=workflow)
            response.raise_for_status()
            return response.json()


class ListWorkflowsTool:
    """Tool for listing available workflows."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("WORKFLOW_URL", "http://localhost:8000")

    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """List available workflows."""
        logger.info("Listing workflows")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/workflows", params=query)
            response.raise_for_status()
            return response.json()


class ExecuteWorkflowTool:
    """Tool for executing workflows."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("WORKFLOW_URL", "http://localhost:8000")

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        logger.info(f"Executing workflow: {request['workflow_id']}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/workflows/execute", json=request)
            response.raise_for_status()
            return response.json()

