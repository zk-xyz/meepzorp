import os
import logging
import json
import requests
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from uuid import UUID
from models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from agents.common.auth import get_current_user
from agents.common.registration import register_agent
from db import TaskDB
from routes import router as task_router
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Task Agent API",
    description="API for managing tasks in the MCP system",
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

# Initialize database client
db = TaskDB()

# Include task routes
app.include_router(task_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Register with orchestration service
@app.on_event("startup")
async def startup_event():
    """Initialize the agent and register with orchestration service"""
    capabilities = [
        {
            "name": "create_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                    "assignee": {"type": "string"},
                    "project_id": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title"]
            }
        },
        {
            "name": "get_task",
            "description": "Get a task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                    "assignee": {"type": "string"},
                    "project_id": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "list_tasks",
            "description": "List all tasks with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "assignee": {"type": "string"},
                    "project_id": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    ]

    try:
        await register_agent(
            name="Task Management Agent",
            description="Agent for managing tasks and project management",
            capabilities=capabilities
        )
    except Exception as e:
        print(f"Error during startup: {str(e)}")

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate, user_id: str = Query(..., description="ID of the user creating the task")):
    """Create a new task"""
    try:
        result = db.create_task(task, user_id)
        return Task(**result)
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID):
    """Get a task by ID"""
    try:
        task = db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return Task(**task)
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    user_id: str = Query(..., description="ID of the user updating the task")
):
    """Update an existing task"""
    try:
        result = db.update_task(task_id, task_update, user_id)
        return Task(**result)
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: UUID):
    """Delete a task"""
    try:
        db.delete_task(task_id)
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks", response_model=List[Task])
async def list_tasks(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List tasks with optional filters"""
    try:
        tasks = db.list_tasks(
            user_id=user_id,
            project_id=project_id,
            status=status,
            priority=priority,
            assignee=assignee,
            tags=tags,
            limit=limit,
            offset=offset
        )
        return [Task(**task) for task in tasks]
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("AGENT_HOST", "0.0.0.0"),
        port=int(os.getenv("AGENT_PORT", "8003"))
    ) 
