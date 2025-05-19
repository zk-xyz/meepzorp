"""
Creative Director Agent

This agent is responsible for managing creative projects and coordinating
with other agents to execute creative tasks.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from .capabilities.project_management import ProjectManagementCapability, ProjectTask
from .capabilities.creative_strategy import CreativeStrategyCapability, CreativeStrategy
from .capabilities.story_crafter import StoryCrafterCapability, Story, StoryElement
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreativeProject(BaseModel):
    """Model for creative projects"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    client: str
    deadline: datetime
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CreativeDirectorAgent:
    """Creative Director Agent class"""
    
    def __init__(self):
        """Initialize the Creative Director agent."""
        self.projects: Dict[str, CreativeProject] = {}
        self.capabilities = {
            "project_management": ProjectManagementCapability(),
            "creative_strategy": CreativeStrategyCapability(),
            "story_crafter": StoryCrafterCapability()
        }
        logger.info("Creative Director agent initialized with capabilities")
        
    def register_capability(self, name: str, capability: Any) -> None:
        """Register a new capability"""
        self.capabilities[name] = capability
        logger.info(f"Registered capability: {name}")
        
    def list_capabilities(self) -> List[str]:
        """List all registered capabilities"""
        return list(self.capabilities.keys())
        
    def create_project(self, name: str, description: str, client: str, deadline: datetime) -> CreativeProject:
        """Create a new project."""
        project = CreativeProject(
            name=name,
            description=description,
            client=client,
            deadline=deadline
        )
        self.projects[project.id] = project
        logger.info(f"Created project: {name} (ID: {project.id})")
        return project
        
    def get_project(self, project_id: str) -> Optional[CreativeProject]:
        """Get a project by ID"""
        return self.projects.get(project_id)
        
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[CreativeProject]:
        """Update an existing project"""
        if project_id not in self.projects:
            return None
            
        project = self.projects[project_id]
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
                
        project.updated_at = datetime.now()
        logger.info(f"Updated project: {project.name}")
        return project
        
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        if project_id not in self.projects:
            return False
            
        del self.projects[project_id]
        logger.info(f"Deleted project: {project_id}")
        return True
        
    def create_project_task(self, task: ProjectTask) -> ProjectTask:
        """Create a new task for a project"""
        if task.project_id not in self.projects:
            raise ValueError(f"Project with ID {task.project_id} does not exist")
        return self.capabilities["project_management"].create_task(task)
        
    def get_project_tasks(self, project_id: str) -> List[ProjectTask]:
        """Get all tasks for a project"""
        if project_id not in self.projects:
            raise ValueError(f"Project with ID {project_id} does not exist")
        return self.capabilities["project_management"].get_project_tasks(project_id)
        
    def assign_project_task(self, task_id: str, agent_id: str) -> Optional[ProjectTask]:
        """Assign a project task to an agent"""
        return self.capabilities["project_management"].assign_task(task_id, agent_id)
        
    def update_project_task_status(self, task_id: str, status: str) -> Optional[ProjectTask]:
        """Update the status of a project task"""
        return self.capabilities["project_management"].update_task_status(task_id, status)
        
    def create_creative_strategy(self, strategy: CreativeStrategy) -> CreativeStrategy:
        """Create a new creative strategy"""
        if strategy.project_id not in self.projects:
            raise ValueError(f"Project with ID {strategy.project_id} does not exist")
        return self.capabilities["creative_strategy"].create_strategy(strategy)
        
    def get_project_strategies(self, project_id: str) -> List[CreativeStrategy]:
        """Get all strategies for a project"""
        if project_id not in self.projects:
            raise ValueError(f"Project with ID {project_id} does not exist")
        return self.capabilities["creative_strategy"].get_project_strategies(project_id)
        
    def generate_creative_brief(self, strategy_id: str) -> Dict[str, Any]:
        """Generate a creative brief from a strategy"""
        return self.capabilities["creative_strategy"].generate_creative_brief(strategy_id)
        
    def create_story(self, project_id: str, title: str, genre: str, synopsis: str, target_audience: str, tone_and_style: str) -> Story:
        """Create a new story."""
        if project_id not in self.projects:
            raise ValueError(f"Project with ID {project_id} does not exist")
        
        story = Story(
            project_id=project_id,
            title=title,
            genre=genre,
            synopsis=synopsis,
            target_audience=target_audience,
            tone_and_style=tone_and_style
        )
        return self.capabilities["story_crafter"].create_story(story)
        
    def get_project_stories(self, project_id: str) -> List[Story]:
        """Get all stories for a project"""
        if project_id not in self.projects:
            raise ValueError(f"Project with ID {project_id} does not exist")
        return self.capabilities["story_crafter"].get_project_stories(project_id)
        
    def add_story_element(self, story_id: str, element: StoryElement) -> Optional[Story]:
        """Add a story element to a story"""
        return self.capabilities["story_crafter"].add_story_element(story_id, element)
        
    def generate_story_outline(self, story_id: str) -> Dict[str, Any]:
        """Generate a story outline from a story"""
        return self.capabilities["story_crafter"].generate_story_outline(story_id)
        
    def get_story(self, story_id: str) -> Optional[Story]:
        """Get a story by ID"""
        return self.capabilities["story_crafter"].get_story(story_id)
        
    def get_story_elements(self, story_id: str, element_type: Optional[str] = None) -> List[StoryElement]:
        """Get story elements for a story, optionally filtered by type"""
        return self.capabilities["story_crafter"].get_story_elements(story_id, element_type)
        
    def analyze_narrative_structure(self, story_id: str) -> Dict[str, Any]:
        """Analyze the narrative structure of a story."""
        story = self.get_story(story_id)
        elements = self.get_story_elements(story_id)
        
        return self.capabilities["story_crafter"].analyze_narrative_structure(story_id) 