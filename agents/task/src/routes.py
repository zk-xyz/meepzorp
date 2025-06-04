from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from datetime import datetime

from models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from db import TaskDB
from agents.common.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Dependency to get the database client
async def get_db() -> TaskDB:
    return TaskDB()

@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    db: TaskDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new task"""
    return await db.create_task(task, current_user)

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: UUID,
    db: TaskDB = Depends(get_db)
):
    """Get a task by ID"""
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task: TaskUpdate,
    db: TaskDB = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Update a task"""
    updated_task = await db.update_task(task_id, task, current_user)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    db: TaskDB = Depends(get_db)
):
    """Delete a task"""
    if not await db.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

@router.get("/", response_model=List[Task])
async def list_tasks(
    user_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    project_id: Optional[str] = None,
    assignee: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: TaskDB = Depends(get_db)
):
    """List tasks with optional filters"""
    return await db.list_tasks(
        user_id=user_id,
        status=status,
        priority=priority,
        project_id=project_id,
        assignee=assignee,
        tags=tags,
        limit=limit,
        offset=offset
    )
