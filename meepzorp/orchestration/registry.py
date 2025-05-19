"""
Agent registry and discovery tools.
"""
from typing import Dict, Any, List
import logging
import os
import uuid
import requests

# In-memory fallback store for tests or when Supabase is not configured
AGENT_DB: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)

class AgentRegistryTool:
    """Tool for registering agents in the system."""

    async def execute(self, agent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register an agent and persist it."""
        logger.info(f"Registering agent: {agent_info['name']}")

        agent_id = str(uuid.uuid4())
        record = {
            "id": agent_id,
            "name": agent_info.get("name"),
            "description": agent_info.get("description"),
            "endpoint": agent_info.get("endpoint"),
            "capabilities": agent_info.get("capabilities", []),
            "metadata": agent_info.get("metadata", {}),
            "status": "active",
        }

        # Store in memory
        AGENT_DB[agent_id] = record

        # Persist to Supabase if configured
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                }
                requests.post(
                    f"{supabase_url}/rest/v1/agents",
                    headers=headers,
                    json=record,
                    timeout=5,
                ).raise_for_status()
            except Exception as e:
                logger.error(f"Failed to persist agent to Supabase: {e}")

        return {"status": "success", "agent_id": agent_id}

class AgentDiscoveryTool:
    """Tool for discovering agents based on capabilities."""

    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Discover agents based on capabilities."""
        capabilities: List[str] = query.get("capabilities", [])
        logger.info(f"Discovering agents with capabilities: {capabilities}")

        # Start with in-memory records
        agents = list(AGENT_DB.values())

        if capabilities:
            agents = [
                a for a in agents
                if any(cap.get("name") in capabilities for cap in a.get("capabilities", []))
            ]

        # Query Supabase if configured
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                }
                params = {}
                if capabilities:
                    params["or"] = ",".join([
                        f"capabilities->>name.ilike.*{cap}*" for cap in capabilities
                    ])
                resp = requests.get(
                    f"{supabase_url}/rest/v1/agents",
                    headers=headers,
                    params=params,
                    timeout=5,
                )
                if resp.status_code == 200:
                    agents = resp.json()
            except Exception as e:
                logger.error(f"Failed to query Supabase for agents: {e}")

        return {"status": "success", "agents": agents}
