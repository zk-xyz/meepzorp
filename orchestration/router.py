"""Request routing tool for the orchestration system."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List

import httpx

from .registry import AgentDiscoveryTool

logger = logging.getLogger(__name__)


class RouteRequestTool:
    """Tool for routing requests to appropriate agents."""

    def __init__(self, registry_url: str | None = None) -> None:
        self.registry_url = registry_url or os.getenv(
            "REGISTRY_URL", "http://localhost:8000"
        )
        self.discovery_tool = AgentDiscoveryTool(self.registry_url)

    async def _discover_agents(self, capability: str) -> List[Dict[str, Any]]:
        """Return agents that provide the requested capability."""
        discovery_result = await self.discovery_tool.execute(
            {"capabilities": [capability]}
        )
        agents = discovery_result.get("agents", [])
        return [
            a
            for a in agents
            if any(cap.get("name") == capability for cap in a.get("capabilities", []))
        ]

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to an agent."""
        capability = request.get("capability")
        params = request.get("parameters", {})
        preferred_agent_id = request.get("preferred_agent_id")
        timeout = request.get("timeout", 5.0)

        logger.info("Routing request for capability: %s", capability)

        try:
            agents = await self._discover_agents(capability)
            if not agents:
                return {
                    "status": "error",
                    "message": f"No agent found for capability '{capability}'",
                }

            agent: Dict[str, Any] | None = None
            if preferred_agent_id:
                agent = next(
                    (a for a in agents if str(a.get("id")) == str(preferred_agent_id)),
                    None,
                )
                if agent is None:
                    return {
                        "status": "error",
                        "message": "Preferred agent not available",
                    }
            else:
                agent = agents[0]

            endpoint = agent.get("endpoint")
            if not endpoint:
                return {"status": "error", "message": "Agent endpoint missing"}

            payload = {"capability": capability, "parameters": params}
            retries = 1
            for attempt in range(retries + 1):
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(f"{endpoint}/mcp", json=payload)
                        response.raise_for_status()
                        return response.json()
                except (
                    httpx.RequestError,
                    httpx.HTTPStatusError,
                ) as exc:  # pragma: no cover - network issues
                    logger.warning("Routing attempt %s failed: %s", attempt + 1, exc)
                    if attempt == retries:
                        return {"status": "error", "message": str(exc)}
                    await asyncio.sleep(0.1)
        except Exception as exc:  # pragma: no cover - unexpected issues
            logger.error("Routing error: %s", exc)
            return {"status": "error", "message": str(exc)}
