"""
Request routing tool for the orchestration system.
"""
from typing import Dict, Any
import logging
import httpx
from .registry import AGENT_DB

logger = logging.getLogger(__name__)

class RouteRequestTool:
    """Tool for routing requests to appropriate agents."""

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to an agent."""
        capability = request.get("capability")
        params = request.get("parameters", {})
        preferred_id = request.get("preferred_agent_id")
        timeout = request.get("timeout", 10.0)

        logger.info(f"Routing request for capability: {capability}")

        agent = None
        if preferred_id:
            agent = AGENT_DB.get(str(preferred_id))
            if agent and not any(cap.get("name") == capability for cap in agent.get("capabilities", [])):
                return {"status": "error", "message": "Preferred agent lacks capability"}
        if not agent:
            for a in AGENT_DB.values():
                if any(cap.get("name") == capability for cap in a.get("capabilities", [])):
                    agent = a
                    break

        if not agent:
            return {"status": "error", "message": "No agent found for capability"}

        url = f"{agent['endpoint'].rstrip('/')}/mcp"
        payload = {"capability": capability, "parameters": params}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return {"status": "error", "message": str(e)}
