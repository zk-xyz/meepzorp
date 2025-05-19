from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskBase(BaseModel):
    """Base model for task data"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    project_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class TaskCreate(TaskBase):
    """Model for creating a new task"""
    pass

class TaskUpdate(BaseModel):
    """Model for updating an existing task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None

class Task(TaskBase):
    """Model for task response"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            return list(set(v))  # Remove duplicates
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid)
        }
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Implement task management API",
                "description": "Create REST endpoints for task CRUD operations",
                "status": "in_progress",
                "priority": "medium",
                "due_date": "2024-02-20T00:00:00Z",
                "assignee": "jason",
                "project_id": "project-123",
                "tags": ["api", "backend"],
                "created_at": "2024-02-15T12:00:00Z",
                "updated_at": "2024-02-15T12:00:00Z"
            }
        } 