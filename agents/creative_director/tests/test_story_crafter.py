"""
Test suite for the Story Crafter capability.
"""
import pytest
from datetime import datetime
from creative_director.capabilities.story_crafter import (
    StoryCrafterCapability,
    Story,
    StoryElement,
    NarrativeStructure,
    StoryShape,
    CharacterDevelopmentStage
)

@pytest.fixture
def story_crafter():
    """Create a StoryCrafterCapability instance for testing."""
    return StoryCrafterCapability()

@pytest.fixture
def sample_story():
    """Create a sample story for testing."""
    return Story(
        id="test-story-1",
        project_id="test-project-1",
        title="The No-Talent Kid",
        genre="Coming of Age",
        synopsis="A young boy discovers his true talent through unexpected circumstances.",
        target_audience="Young Adult",
        tone_and_style="Heartwarming and Inspirational",
        story_elements=[
            StoryElement(
                id="elem-1",
                story_id="test-story-1",
                element_type="scene",
                content={
                    "description": "The protagonist, a young boy, struggles with feeling inadequate in school.",
                    "location": "School classroom",
                    "characters": ["Protagonist", "Teacher", "Classmates"]
                },
                emotional_value=-0.7,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            StoryElement(
                id="elem-2",
                story_id="test-story-1",
                element_type="scene",
                content={
                    "description": "The boy discovers an old piano in the school basement.",
                    "location": "School basement",
                    "characters": ["Protagonist"]
                },
                emotional_value=0.2,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            StoryElement(
                id="elem-3",
                story_id="test-story-1",
                element_type="scene",
                content={
                    "description": "The boy plays the piano for the first time and feels a connection.",
                    "location": "School basement",
                    "characters": ["Protagonist"]
                },
                emotional_value=0.5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            StoryElement(
                id="elem-4",
                story_id="test-story-1",
                element_type="scene",
                content={
                    "description": "The boy performs at the school talent show, receiving standing ovation.",
                    "location": "School auditorium",
                    "characters": ["Protagonist", "Teacher", "Classmates", "Parents"]
                },
                emotional_value=0.9,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
    )

@pytest.mark.asyncio
async def test_create_story(story_crafter, sample_story):
    """Test story creation functionality."""
    result = await story_crafter.create_story(sample_story)
    assert result["status"] == "success"
    assert result["story_id"] == sample_story.id
    assert story_crafter.stories[sample_story.id] == sample_story

@pytest.mark.asyncio
async def test_analyze_story(story_crafter, sample_story):
    """Test story analysis functionality."""
    await story_crafter.create_story(sample_story)
    analysis = await story_crafter.analyze_story(sample_story.id)
    
    assert analysis["status"] == "success"
    assert analysis["story_id"] == sample_story.id
    
    # Verify narrative structure analysis
    assert "structure" in analysis["analysis"]
    assert analysis["analysis"]["structure"]["type"] == NarrativeStructure.HERO_JOURNEY
    
    # Verify emotional arc analysis
    assert "emotional_arc" in analysis["analysis"]
    emotional_arc = analysis["analysis"]["emotional_arc"]
    assert len(emotional_arc["points"]) == len(sample_story.story_elements)
    assert emotional_arc["points"][0]["value"] < emotional_arc["points"][-1]["value"]  # Emotional growth
    
    # Verify character development analysis
    assert "character_development" in analysis["analysis"]
    character_analysis = analysis["analysis"]["character_development"]
    assert character_analysis["protagonist"]["arc"] == CharacterDevelopmentStage.TRANSFORMATION

@pytest.mark.asyncio
async def test_suggest_improvements(story_crafter, sample_story):
    """Test story improvement suggestions."""
    await story_crafter.create_story(sample_story)
    improvements = await story_crafter.suggest_improvements(sample_story.id, "character_development")
    
    assert improvements["status"] == "success"
    assert improvements["story_id"] == sample_story.id
    assert "suggestions" in improvements
    assert len(improvements["suggestions"]) > 0

@pytest.mark.asyncio
async def test_story_shape_analysis(story_crafter, sample_story):
    """Test Vonnegut story shape analysis."""
    await story_crafter.create_story(sample_story)
    analysis = await story_crafter.analyze_story(sample_story.id)
    
    assert "story_shape" in analysis["analysis"]
    story_shape = analysis["analysis"]["story_shape"]
    assert story_shape["shape"] == StoryShape.MAN_IN_HOLE
    assert story_shape["confidence"] > 0.7

@pytest.mark.asyncio
async def test_emotional_arc_calculation(story_crafter, sample_story):
    """Test emotional arc calculation with local context."""
    await story_crafter.create_story(sample_story)
    analysis = await story_crafter.analyze_story(sample_story.id)
    
    emotional_arc = analysis["analysis"]["emotional_arc"]
    assert "local_context" in emotional_arc
    assert "narrative_context" in emotional_arc
    assert emotional_arc["overall_trend"] == "positive"
    assert emotional_arc["key_moments"][0]["type"] == "low_point"
    assert emotional_arc["key_moments"][-1]["type"] == "climax" 