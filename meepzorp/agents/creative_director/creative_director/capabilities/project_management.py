"""
Project Management Capability

This capability handles the management of creative projects, including
project creation, tracking, and coordination with other agents.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectTask(BaseModel):
    """Model for project tasks"""
    id: str = Field(..., description="Unique identifier for the task")
    project_id: str = Field(..., description="ID of the project this task belongs to")
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Task description")
    status: str = Field(..., description="Current status of the task")
    assigned_to: Optional[str] = Field(None, description="Agent ID assigned to this task")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectManagementCapability:
    """Project Management Capability class"""
    
    def __init__(self):
        self.tasks: Dict[str, ProjectTask] = {}
        
    def create_task(self, task: ProjectTask) -> ProjectTask:
        """Create a new project task"""
        if task.id in self.tasks:
            raise ValueError(f"Task with ID {task.id} already exists")
            
        self.tasks[task.id] = task
        logger.info(f"Created new task: {task.title}")
        return task
        
    def get_task(self, task_id: str) -> Optional[ProjectTask]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
        
    def get_project_tasks(self, project_id: str) -> List[ProjectTask]:
        """Get all tasks for a project"""
        return [task for task in self.tasks.values() if task.project_id == project_id]
        
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[ProjectTask]:
        """Update an existing task"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
                
        task.updated_at = datetime.now()
        logger.info(f"Updated task: {task.title}")
        return task
        
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id not in self.tasks:
            return False
            
        del self.tasks[task_id]
        logger.info(f"Deleted task: {task_id}")
        return True
        
    def assign_task(self, task_id: str, agent_id: str) -> Optional[ProjectTask]:
        """Assign a task to an agent"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        task.assigned_to = agent_id
        task.updated_at = datetime.now()
        logger.info(f"Assigned task {task.title} to agent {agent_id}")
        return task
        
    def update_task_status(self, task_id: str, status: str) -> Optional[ProjectTask]:
        """Update the status of a task"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        task.status = status
        task.updated_at = datetime.now()
        logger.info(f"Updated task {task.title} status to {status}")
        return task 