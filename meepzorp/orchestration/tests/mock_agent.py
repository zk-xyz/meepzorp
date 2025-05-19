"""
Mock agent for testing the orchestration system.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

app = FastAPI(title="Mock Agent")

class MCPRequest(BaseModel):
    """Model for MCP requests."""
    capability: str
    parameters: Dict[str, Any]

@app.post("/mcp")
async def handle_mcp_request(request: MCPRequest):
    """Handle MCP requests."""
    if request.capability == "test_capability":
        return {
            "status": "success",
            "result": {
                "received_params": request.parameters,
                "mock_response": "Test response from mock agent"
            }
        }
    elif request.capability == "search_knowledge":
        return {
            "status": "success",
            "result": {
                "matches": [
                    {"content": "Test content 1", "score": 0.9},
                    {"content": "Test content 2", "score": 0.8}
                ]
            }
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported capability: {request.capability}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8811) 