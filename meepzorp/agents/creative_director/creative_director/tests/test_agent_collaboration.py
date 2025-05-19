"""
Test file to demonstrate collaboration between Creative Director and Content Writer agents.
"""

import pytest
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from creative_director.agent import CreativeDirectorAgent, CreativeProject
from creative_director.capabilities.story_crafter import (
    Story, StoryElement, NarrativeStructure, StoryShape
)

class MockContentWriterAgent:
    """Mock Content Writer agent for testing collaboration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_story_element(self, story_id: str, element_type: str, content: str) -> StoryElement:
        """Create a story element with the given type and content."""
        return StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story_id,
            element_type=element_type,
            content={"text": content},
            emotional_value=0.5,
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
        CreativeProject(
            id=f"project_{datetime.now().timestamp()}",
            name="Test Story Project",
            description="A test project to demonstrate agent collaboration",
            status="active"
        )
    )
    
    # Create a story
    story = creative_director.create_story(
        Story(
            id=f"story_{datetime.now().timestamp()}",
            project_id=project.id,
            title="The Hero's Journey",
            genre="Fantasy",
            synopsis="A young hero embarks on an epic quest to save their world.",
            target_audience={
                "age_range": "12-18",
                "interests": ["fantasy", "adventure"],
                "reading_level": "young adult"
            },
            tone_and_style={
                "tone": "epic",
                "style": "adventurous",
                "mood": "inspiring"
            },
            narrative_structure=NarrativeStructure.HERO_JOURNEY,
            story_shape=StoryShape.MAN_IN_HOLE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    )
    
    # Content Writer creates story elements
    ordinary_world = content_writer.create_story_element(
        story_id=story.id,
        element_type="scene",
        content="The hero lives in their ordinary world, unaware of the adventure to come."
    )
    
    call_to_adventure = content_writer.create_story_element(
        story_id=story.id,
        element_type="scene", 
        content="A mysterious figure arrives with news of a great danger."
    )
    
    # Creative Director adds the elements to the story
    creative_director.add_story_element(story.id, ordinary_world)
    creative_director.add_story_element(story.id, call_to_adventure)
    
    # Analyze the narrative structure
    analysis = creative_director.analyze_narrative_structure(story.id)
    
    # Print the analysis results
    print("\nNarrative Analysis Results:")
    print(f"Structure Type: {analysis['structure_type']}")
    print(f"Story Shape: {analysis['story_shape']}")
    print(f"Emotional Arc:")
    for point in analysis['emotional_arc']:
        print(f"  - {point['element_type']} at {point['timestamp']}: {point['emotional_value']}")
    print("\nStructure Analysis:")
    for stage, details in analysis['structure_analysis'].items():
        print(f"  - {stage}: {details}")
    print("\nCharacter Development:")
    for character in analysis['character_development']:
        print(f"  - {character}")
    print("\nThematic Elements:")
    for theme in analysis['thematic_elements']:
        print(f"  - {theme}")
    print("\nPacing Analysis:")
    print(f"  Overall Pace: {analysis['pacing_analysis']['overall_pace']}")
    print("  Tension Points:")
    for point in analysis['pacing_analysis']['tension_points']:
        print(f"    - {point['description']} at {point['position']}%")

def test_analyze_no_talent_kid():
    """Test narrative analysis of The No-Talent Kid by Kurt Vonnegut."""
    # Initialize agent
    creative_director = CreativeDirectorAgent()
    
    # Create a project
    project = creative_director.create_project(
        CreativeProject(
            id=f"project_{datetime.now().timestamp()}",
            name="Short Story Analysis Project",
            description="Analysis of classic short stories",
            status="active"
        )
    )
    
    # Create the story
    story = creative_director.create_story(
        Story(
            id=f"story_{datetime.now().timestamp()}",
            project_id=project.id,
            title="The No-Talent Kid",
            genre="Short Story",
            synopsis="A determined but musically challenged student's quest to join the school band, and his unexpected triumph through persistence and cleverness.",
            target_audience={
                "age_range": "14+",
                "interests": ["coming of age", "school life", "music"],
                "reading_level": "high school"
            },
            tone_and_style={
                "tone": "wry",
                "style": "satirical",
                "mood": "humorous"
            },
            narrative_structure=NarrativeStructure.HERO_JOURNEY,
            story_shape=StoryShape.MAN_IN_HOLE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    )
    
    # Add story elements
    elements = [
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="scene",
            content={
                "text": "Walter Plummer's determination to join the marching band despite his lack of musical talent.",
                "emotional_value": 0.3
            },
            emotional_value=0.3,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="scene",
            content={
                "text": "Mr. Helmholtz's frustration with Plummer's persistent challenges to join the A Band.",
                "emotional_value": -0.2
            },
            emotional_value=-0.2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="scene",
            content={
                "text": "Plummer's discovery of the Knights of Kandahar's bass drum and his clever plan to acquire it.",
                "emotional_value": 0.5
            },
            emotional_value=0.5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="scene",
            content={
                "text": "The dramatic reveal of Plummer with the massive drum, and his negotiation with Mr. Helmholtz.",
                "emotional_value": 0.8
            },
            emotional_value=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="character",
            content={
                "text": "Walter Plummer - Determined, persistent, clever, and resourceful despite his lack of musical talent.",
                "emotional_value": 0.6
            },
            emotional_value=0.6,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="character",
            content={
                "text": "Mr. Helmholtz - Band director who values musical excellence but is ultimately outmaneuvered by Plummer's persistence.",
                "emotional_value": -0.1
            },
            emotional_value=-0.1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        StoryElement(
            id=f"element_{datetime.now().timestamp()}",
            story_id=story.id,
            element_type="theme",
            content={
                "text": "Persistence and cleverness can overcome traditional measures of talent and ability.",
                "emotional_value": 0.7
            },
            emotional_value=0.7,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    # Add elements to story
    for element in elements:
        creative_director.add_story_element(story.id, element)
    
    # Analyze the narrative structure
    analysis = creative_director.analyze_narrative_structure(story.id)
    
    # Print the analysis results
    print("\nNarrative Analysis of 'The No-Talent Kid':")
    print(f"Structure Type: {analysis['structure_type']}")
    print(f"Story Shape: {analysis['story_shape']}")
    print("\nEmotional Arc:")
    for point in analysis['emotional_arc']:
        print(f"  - {point['element_type']}: {point['emotional_value']}")
    print("\nStructure Analysis:")
    for stage, details in analysis['structure_analysis'].items():
        print(f"  - {stage}: {details}")
    print("\nCharacter Development:")
    for character in analysis['character_development']:
        print(f"  - {character}")
    print("\nThematic Elements:")
    for theme in analysis['thematic_elements']:
        print(f"  - {theme}")
    print("\nPacing Analysis:")
    print(f"  Overall Pace: {analysis['pacing_analysis']['overall_pace']}")
    print("  Tension Points:")
    for point in analysis['pacing_analysis']['tension_points']:
        print(f"    - {point['description']} at {point['position']}%")

if __name__ == "__main__":
    test_creative_director_content_writer_collaboration()
    test_analyze_no_talent_kid() 