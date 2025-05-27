from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from agents.common.registration import register_agent

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MCP Base Agent")

class MCPRequest(BaseModel):
    capability: str
    parameters: dict

@app.on_event("startup")
async def startup_event():
    """Register agent with orchestration service on startup"""
    capabilities = [
        {
            "name": "echo",
            "description": "Echo back a message",
            "parameters": {
                "message": "string"
            }
        }
    ]
    
    try:
        await register_agent(
            name="Base Agent",
            description="Basic MCP agent with echo capability",
            capabilities=capabilities
        )
    except Exception as e:
        logger.error(f"Failed to register agent: {str(e)}")
        # Don't raise the exception - allow the agent to start even if registration fails
        # It can retry registration later

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/execute")
async def execute_request(request: MCPRequest):
    """Execute an MCP request"""
    logger.info(f"Received request for capability: {request.capability}")
    
    # Example capability handling
    if request.capability == "echo":
        return {"result": request.parameters.get("message", "Hello from base agent!")}
    
    raise HTTPException(status_code=400, detail=f"Unsupported capability: {request.capability}")

@app.get("/capabilities")
async def list_capabilities():
    """List available capabilities"""
    return {
        "capabilities": [
            {
                "name": "echo",
                "description": "Echo back a message",
                "parameters": {
                    "message": "string"
                }
            }
        ]
    } 
