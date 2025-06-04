"""
Agent registry and discovery tools.
"""
from typing import Dict, Any, List
import logging
import os
import httpx

logger = logging.getLogger(__name__)

class AgentRegistryTool:
    """Tool for registering agents in the system."""
    
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("REGISTRY_URL", "http://localhost:8000")

    async def execute(self, agent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register an agent."""
        logger.info(f"Registering agent: {agent_info['name']}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/agents", json=agent_info)
            response.raise_for_status()
            return response.json()

class AgentDiscoveryTool:
    """Tool for discovering agents based on capabilities."""
    
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("REGISTRY_URL", "http://localhost:8000")

    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Discover agents based on capabilities."""
        logger.info(f"Discovering agents with capabilities: {query['capabilities']}")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/agents", params=query)
            response.raise_for_status()
            return response.json()
