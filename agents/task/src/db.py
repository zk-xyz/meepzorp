import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

import httpx
from src.models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)

class TaskDB:
    """Database client for task management"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
    
    async def create_task(self, task: TaskCreate, user_id: str) -> Task:
        """Create a new task in the database"""
        try:
            data = {
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "project_id": task.project_id,
                "assignee": task.assignee,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_by": user_id,
                "updated_by": user_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/tasks",
                    headers=self.headers,
                    json=data,
                )
                response.raise_for_status()
            
            task_data = response.json()
            return Task(**task_data)
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise
    
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Retrieve a task by ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/tasks?id=eq.{task_id}",
                    headers=self.headers,
                )
                response.raise_for_status()
            
            tasks = response.json()
            if not tasks:
                return None
                
            return Task(**tasks[0])
            
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            raise
    
    async def update_task(self, task_id: UUID, task: TaskUpdate, user_id: str) -> Optional[Task]:
        """Update an existing task.

        Args:
            task_id: ID of the task to update.
            task: :class:`TaskUpdate` instance with fields to change.
            user_id: ID of the user performing the update.
        """
        try:
            update_data = task.dict(exclude_unset=True)
            if update_data:
                update_data["updated_by"] = user_id
                update_data["updated_at"] = datetime.utcnow().isoformat()
                
                if "status" in update_data:
                    update_data["status"] = update_data["status"].value
                if "priority" in update_data:
                    update_data["priority"] = update_data["priority"].value
                if "due_date" in update_data and update_data["due_date"]:
                    update_data["due_date"] = update_data["due_date"].isoformat()
                
                async with httpx.AsyncClient() as client:
                    response = await client.patch(
                        f"{self.supabase_url}/rest/v1/tasks?id=eq.{task_id}",
                        headers=self.headers,
                        json=update_data,
                    )
                    response.raise_for_status()

                return await self.get_task(task_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise
    
    async def delete_task(self, task_id: UUID) -> bool:
        """Delete a task by ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.supabase_url}/rest/v1/tasks?id=eq.{task_id}",
                    headers=self.headers,
                )
                response.raise_for_status()

            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
    
    async def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        project_id: Optional[str] = None,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks with optional filters"""
        try:
            query_params = []
            
            if user_id:
                query_params.append(f"created_by=eq.{user_id}")
            if status:
                query_params.append(f"status=eq.{status.value}")
            if priority:
                query_params.append(f"priority=eq.{priority.value}")
            if project_id:
                query_params.append(f"project_id=eq.{project_id}")
            if assignee:
                query_params.append(f"assignee=eq.{assignee}")
            if tags:
                for tag in tags:
                    query_params.append(f"tags=cs.{{{tag}}}")
            
            query_params.append(f"limit={limit}")
            query_params.append(f"offset={offset}")
            
            url = f"{self.supabase_url}/rest/v1/tasks"
            if query_params:
                url += "?" + "&".join(query_params)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                tasks = response.json()
                return [Task(**task) for task in tasks]
            
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            raise 