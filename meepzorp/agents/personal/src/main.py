from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from agents.common.registration import register_agent
from .db import KnowledgeDB
from .capabilities.knowledge import KnowledgeCapability
from .capabilities.graph_suggestions import SuggestConnectionsCapability

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize FastAPI app and services
app = FastAPI(title="MCP Personal Agent")
db = KnowledgeDB()
knowledge_capability = KnowledgeCapability(db)
graph_suggestions = SuggestConnectionsCapability(db)

class StoreKnowledgeParams(BaseModel):
    content: str
    tags: Optional[List[str]] = None
    embedding: Optional[List[float]] = None

class MCPRequest(BaseModel):
    capability: str
    parameters: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Register agent with orchestration service on startup"""
    capabilities = [
        {
            "name": "store_knowledge",
            "description": "Store knowledge in the personal knowledge base",
            "parameters": {
                "content": "string",
                "tags": "list[string]",
                "embedding": "list[float]"
            }
        },
        {
            "name": "query_knowledge",
            "description": "Query the personal knowledge base with semantic search",
            "parameters": {
                "query": "string",
                "tags": "list[string]",
                "embedding": "list[float]",
                "limit": "integer"
            }
        },
        {
            "name": "update_knowledge",
            "description": "Update a knowledge item",
            "parameters": {
                "knowledge_id": "string",
                "content": "string",
                "tags": "list[string]",
                "embedding": "list[float]"
            }
        },
        {
            "name": "delete_knowledge",
            "description": "Delete a knowledge item",
            "parameters": {
                "knowledge_id": "string"
            }
        },
        {
            "name": "suggest_connections",
            "description": "Suggest potential connections between entities",
            "parameters": {
                "entity_id": "string",
                "max_suggestions": "integer",
                "min_confidence": "float",
                "relationship_types": "list[string]"
            }
        }
    ]
    
    try:
        await register_agent(
            name="Personal Knowledge Agent",
            description="Agent for managing personal knowledge with vector search capabilities",
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
    
    try:
        if request.capability == "store_knowledge":
            params = StoreKnowledgeParams(**request.parameters)
            result = await knowledge_capability.store_knowledge(
                content=params.content,
                tags=params.tags,
                embedding=params.embedding
            )
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            return result
            
        elif request.capability == "query_knowledge":
            result = await knowledge_capability.query_knowledge(
                query=request.parameters.get("query"),
                tags=request.parameters.get("tags"),
                embedding=request.parameters.get("embedding"),
                limit=request.parameters.get("limit", 10)
            )
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            return result
            
        elif request.capability == "update_knowledge":
            result = await knowledge_capability.update_knowledge(
                knowledge_id=request.parameters.get("knowledge_id"),
                content=request.parameters.get("content"),
                tags=request.parameters.get("tags"),
                embedding=request.parameters.get("embedding")
            )
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            return result
            
        elif request.capability == "delete_knowledge":
            result = await knowledge_capability.delete_knowledge(
                knowledge_id=request.parameters.get("knowledge_id")
            )
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            return result
            
        elif request.capability == "suggest_connections":
            result = await graph_suggestions.suggest_connections(
                entity_id=request.parameters.get("entity_id"),
                max_suggestions=request.parameters.get("max_suggestions", 5),
                min_confidence=request.parameters.get("min_confidence", 0.5),
                relationship_types=request.parameters.get("relationship_types")
            )
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            return result
        
        raise HTTPException(status_code=400, detail=f"Unsupported capability: {request.capability}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/capabilities")
async def list_capabilities():
    """List available capabilities"""
    return {
        "capabilities": [
            {
                "name": "store_knowledge",
                "description": "Store knowledge in the personal knowledge base",
                "parameters": {
                    "content": "string",
                    "tags": "list[string]",
                    "embedding": "list[float]"
                }
            },
            {
                "name": "query_knowledge",
                "description": "Query the personal knowledge base with semantic search",
                "parameters": {
                    "query": "string",
                    "tags": "list[string]",
                    "embedding": "list[float]",
                    "limit": "integer"
                }
            },
            {
                "name": "update_knowledge",
                "description": "Update a knowledge item",
                "parameters": {
                    "knowledge_id": "string",
                    "content": "string",
                    "tags": "list[string]",
                    "embedding": "list[float]"
                }
            },
            {
                "name": "delete_knowledge",
                "description": "Delete a knowledge item",
                "parameters": {
                    "knowledge_id": "string"
                }
            },
            {
                "name": "suggest_connections",
                "description": "Suggest potential connections between entities",
                "parameters": {
                    "entity_id": "string",
                    "max_suggestions": "integer",
                    "min_confidence": "float",
                    "relationship_types": "list[string]"
                }
            }
        ]
    } 