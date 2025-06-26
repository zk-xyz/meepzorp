"""
Agent registration module for MCP agents.
"""
import os
from typing import Any, Dict, List

import httpx
from loguru import logger

async def register_agent(
    name: str,
    description: str,
    capabilities: List[Dict[str, Any]],
    metadata: Dict[str, Any] | None = None,
    *,
    use_tool_wrapper: bool = False,
) -> Dict[str, Any]:
    """
    Register an agent with the orchestration service.
    
    Args:
        name: Agent name
        description: Agent description
        capabilities: List of agent capabilities
        metadata: Optional metadata about the agent
        use_tool_wrapper: Send payload wrapped as a tool request for
            backward compatibility
        
    Returns:
        Registration response from orchestration service
    """
    orchestration_url = os.getenv("ORCHESTRATION_URL")
    if not orchestration_url:
        raise ValueError("ORCHESTRATION_URL environment variable must be set")
        
    agent_host = os.getenv("AGENT_HOST", "0.0.0.0")
    agent_port = os.getenv("AGENT_PORT", os.getenv("MCP_PORT", "8002"))
    agent_external_host = os.getenv(
        "AGENT_EXTERNAL_HOST", f"{agent_host}:{agent_port}"
    )
    
    endpoint = f"http://{agent_external_host}"
    
    registration_data = {
        "name": name,
        "description": description,
        "endpoint": endpoint,
        "capabilities": capabilities,
        "metadata": metadata or {}
    }
    
    logger.info(f"Registering agent {name} with orchestration service at {orchestration_url}")
    logger.debug(f"Registration data: {registration_data}")
    
    payload = (
        {"tool": "register_agent", "parameters": registration_data}
        if use_tool_wrapper
        else registration_data
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{orchestration_url}/mcp/tools",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "success":
                logger.info(f"Successfully registered agent {name}")
                return result
            else:
                logger.error(f"Failed to register agent: {result.get('message')}")
                raise Exception(result.get("message"))
                
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        raise
