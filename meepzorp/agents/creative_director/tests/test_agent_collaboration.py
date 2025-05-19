"""
Test file demonstrating collaboration between Creative Director and Content Writer agents.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import pytest

from creative_director.agent import CreativeDirectorAgent
from creative_director.capabilities.story_crafter import StoryElement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockContentWriterAgent:
    """Mock Content Writer agent for testing collaboration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_story_element(self, element_type: str, content: str) -> StoryElement:
        """Create a story element with the given type and content."""
        self.logger.info(f"Creating story element of type {element_type}")
        return StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id="test_story",
            element_type=element_type,
            content=content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

def test_creative_director_content_writer_collaboration():
    """Test collaboration between Creative Director and Content Writer agents."""
    # Initialize agents
    creative_director = CreativeDirectorAgent()
    content_writer = MockContentWriterAgent()
    
    # Create a project
    project = creative_director.create_project(
        name="Test Project",
        description="A test project for collaboration",
        client="Test Client",
        deadline=datetime.now()
    )
    
    # Create a story
    story = creative_director.create_story(
        project_id=project.id,
        title="Test Story",
        genre="Fantasy",
        synopsis="A test story about collaboration",
        target_audience="Young adults",
        tone_and_style="Epic and adventurous"
    )
    
    # Content writer creates story elements
    elements = [
        content_writer.create_story_element(
            element_type="character",
            content="Protagonist: A young hero with a mysterious past"
        ),
        content_writer.create_story_element(
            element_type="setting",
            content="A magical kingdom in peril"
        ),
        content_writer.create_story_element(
            element_type="plot_point",
            content="The hero receives a call to adventure"
        )
    ]
    
    # Creative director adds elements to the story
    for element in elements:
        creative_director.add_story_element(story.id, element)
    
    # Analyze the narrative structure
    analysis = creative_director.analyze_narrative_structure(story.id)
    
    # Verify the analysis
    assert analysis is not None
    assert "structure_type" in analysis
    assert "story_shape" in analysis
    assert "emotional_arc" in analysis
    assert "overall_pace" in analysis
    assert "tension_points" in analysis
    
    # Print the analysis results
    print("\nNarrative Analysis Results:")
    print(f"Structure Type: {analysis['structure_type']}")
    print(f"Story Shape: {analysis['story_shape']}")
    print(f"Emotional Arc: {analysis['emotional_arc']}")
    print(f"Overall Pace: {analysis['overall_pace']}")
    print("\nTension Points:")
    for point in analysis['tension_points']:
        print(f"- {point}")

if __name__ == "__main__":
    test_creative_director_content_writer_collaboration() 