"""
Main orchestration service for the MCP system.
Handles agent registration and tool routing.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from registry import AgentRegistryTool, AgentDiscoveryTool
from router import RouteRequestTool
from workflows import ExecuteWorkflowTool

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Orchestration Service",
    description="Orchestration service for managing agent interactions and workflows",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate tools
registry_tool = AgentRegistryTool()
discovery_tool = AgentDiscoveryTool()
router_tool = RouteRequestTool()
workflow_tool = ExecuteWorkflowTool()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/mcp/tools")
async def handle_tool_request(request: Dict[str, Any]):
    """
    Handle tool requests from agents.
    This endpoint either:
    1. Registers new agent capabilities when ``request.get("tool") == "register_agent"``
    2. Routes tool requests to the appropriate agent for any other tool name
    """
    try:
        # Check if this is a registration request
        if request.get("tool") == "register_agent":
            result = await registry_tool.execute(request)
            return {"status": "success", "message": "Agent registered successfully", "data": result}
        
        # Otherwise, treat it as a tool request
        if "tool" not in request:
            raise HTTPException(status_code=400, detail="Tool name not specified")
            
        # Use the instantiated router tool
        result = await router_tool.execute(request) 
        return result
        
    except Exception as e:
        logger.error(f"Error handling tool request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/tools")
async def list_tools():
    """List all available tools/capabilities from registered agents"""
    try:
        # Use the instantiated tool - Assuming discovery tool lists capabilities
        # Note: The current DiscoveryTool needs a query. We might need to adjust its logic
        # For now, let's just call it with an empty query as a placeholder.
        capabilities = await discovery_tool.execute({"capabilities": []}) 
        return {"tools": capabilities.get("agents", [])} # Adjust based on actual discovery tool output
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/workflows")
async def handle_workflow(workflow: Dict[str, Any]):
    """Execute a multi-step workflow"""
    try:
        # Use the instantiated workflow tool
        result = await workflow_tool.execute(workflow)
        return result
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "9810"))
    ) 