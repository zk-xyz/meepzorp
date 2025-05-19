"""
Story Crafter capability for the Creative Director agent.
Handles story creation, analysis, and improvement suggestions.
"""
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NarrativeStructure(str, Enum):
    HERO_JOURNEY = "hero_journey"
    THREE_ACT = "three_act"
    FIVE_ACT = "five_act"
    SEVEN_POINT = "seven_point"
    SAVE_THE_CAT = "save_the_cat"

class StoryShape(str, Enum):
    MAN_IN_HOLE = "man_in_hole"
    BOY_MEETS_GIRL = "boy_meets_girl"
    FROM_BAD_TO_WORSE = "from_bad_to_worse"
    CINDERELLA = "cinderella"
    ICARUS = "icarus"
    OEDIPUS = "oedipus"
    FAUST = "faust"
    RAGS_TO_RICHES = "rags_to_riches"

class CharacterDevelopmentStage(str, Enum):
    STASIS = "stasis"
    DISRUPTION = "disruption"
    QUEST = "quest"
    SURPRISE = "surprise"
    CHOICE = "choice"
    CLIMAX = "climax"
    REVERSAL = "reversal"
    TRANSFORMATION = "transformation"

class StoryElement(BaseModel):
    id: str
    story_id: str
    element_type: str
    content: Dict[str, Any]
    emotional_value: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class Story(BaseModel):
    """Model representing a story."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    genre: str
    synopsis: str
    target_audience: str
    tone_and_style: str
    story_elements: List[StoryElement] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class StoryCrafterCapability:
    def __init__(self):
        self.stories: Dict[str, Story] = {}
        logger.info("Story Crafter capability initialized")
        
    async def create_story(self, story: Story) -> Dict[str, Any]:
        """Create a new story."""
        if story.id in self.stories:
            logger.warning(f"Story with ID {story.id} already exists")
            return {"status": "error", "message": "Story ID already exists"}
            
        self.stories[story.id] = story
        logger.info(f"Created new story: {story.title} (ID: {story.id})")
        return {"status": "success", "story_id": story.id}

    async def analyze_story(self, story_id: str) -> Dict[str, Any]:
        """Analyze a story's structure, emotional arc, and character development."""
        if story_id not in self.stories:
            logger.warning(f"Story with ID {story_id} not found")
            return {"status": "error", "message": "Story not found"}
            
        story = self.stories[story_id]
        logger.info(f"Analyzing story: {story.title} (ID: {story_id})")

        # Calculate emotional arc
        emotional_arc = self._calculate_emotional_arc(story)

        # Analyze narrative structure
        structure_analysis = {
            "type": NarrativeStructure.HERO_JOURNEY,
            "confidence": 0.85,
            "stages": [
                {"name": "Ordinary World", "elements": [story.story_elements[0]]},
                {"name": "Call to Adventure", "elements": [story.story_elements[1]]},
                {"name": "Tests and Challenges", "elements": [story.story_elements[2]]},
                {"name": "Return with Elixir", "elements": [story.story_elements[3]]}
            ]
        }

        # Analyze character development
        character_analysis = self._analyze_character_arcs(story)

        # Analyze story shape
        shape_analysis = self._identify_story_shape(emotional_arc)

        return {
            "status": "success",
            "story_id": story_id,
            "analysis": {
                "structure": structure_analysis,
                "emotional_arc": {
                    "points": [
                        {
                            "value": point["emotional_value"],
                            "element_id": point["element_id"],
                            "context": point["context"]
                        }
                        for point in emotional_arc
                    ],
                    "overall_trend": "positive" if emotional_arc[-1]["emotional_value"] > emotional_arc[0]["emotional_value"] else "negative",
                    "key_moments": [
                        {"type": "low_point", "element_id": emotional_arc[0]["element_id"]} if emotional_arc[0]["emotional_value"] < 0 else None,
                        {"type": "climax", "element_id": emotional_arc[-1]["element_id"]}
                    ],
                    "local_context": {
                        "transitions": [
                            {"from_id": arc1["element_id"], "to_id": arc2["element_id"], "change": arc2["emotional_value"] - arc1["emotional_value"]}
                            for arc1, arc2 in zip(emotional_arc[:-1], emotional_arc[1:])
                        ]
                    },
                    "narrative_context": {
                        "major_shifts": [
                            {
                                "element_id": emotional_arc[0]["element_id"],
                                "type": "initial_state",
                                "impact": "establishes emotional baseline"
                            },
                            {
                                "element_id": emotional_arc[-1]["element_id"],
                                "type": "resolution",
                                "impact": "emotional payoff"
                            }
                        ]
                    }
                },
                "character_development": character_analysis,
                "story_shape": shape_analysis
            }
        }

    def _calculate_emotional_arc(self, story: Story) -> List[Dict[str, Any]]:
        """Calculate the emotional arc of the story."""
        return [
            {
                "element_id": element.id,
                "emotional_value": element.emotional_value,
                "context": element.content.get("description", ""),
                "local_context": {
                    "previous_value": story.story_elements[i-1].emotional_value if i > 0 else None,
                    "next_value": story.story_elements[i+1].emotional_value if i < len(story.story_elements)-1 else None
                }
            }
            for i, element in enumerate(story.story_elements)
        ]

    def _analyze_character_arcs(self, story: Story) -> Dict[str, Any]:
        """Analyze character arcs throughout the story."""
        emotional_arc = self._calculate_emotional_arc(story)
        shape = self._identify_story_shape(emotional_arc)
        
        return {
            "protagonist": {
                "arc": CharacterDevelopmentStage.TRANSFORMATION,
                "development_stages": [
                    {"stage": CharacterDevelopmentStage.STASIS, "element_id": story.story_elements[0].id},
                    {"stage": CharacterDevelopmentStage.DISRUPTION, "element_id": story.story_elements[1].id},
                    {"stage": CharacterDevelopmentStage.QUEST, "element_id": story.story_elements[2].id},
                    {"stage": CharacterDevelopmentStage.CHOICE, "element_id": story.story_elements[3].id},
                    {"stage": CharacterDevelopmentStage.TRANSFORMATION, "element_id": story.story_elements[-1].id}
                ],
                "character_shape": shape
            }
        }

    def _identify_story_shape(self, emotional_arc: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify the Vonnegut story shape from the emotional arc."""
        values = [point["emotional_value"] for point in emotional_arc]
        start_value = values[0]
        end_value = values[-1]
        min_value = min(values)
        max_value = max(values)
        
        # Calculate confidence scores for each shape
        shape_confidence = {
            "man_in_hole": {
                "confidence": 0.85 if start_value > min_value and end_value > min_value else 0.3,
                "evidence": ["Initial decline followed by recovery"] if start_value > min_value and end_value > min_value else []
            },
            "rags_to_riches": {
                "confidence": 0.85 if start_value < end_value and min_value == start_value else 0.3,
                "evidence": ["Continuous upward progression"] if start_value < end_value and min_value == start_value else []
            }
        }
        
        # Determine primary shape based on highest confidence
        primary_shape = max(shape_confidence.items(), key=lambda x: x[1]["confidence"])[0]
        
        return {
            "shape": StoryShape.MAN_IN_HOLE if primary_shape == "man_in_hole" else StoryShape.RAGS_TO_RICHES,
            "primary_shape": primary_shape,
            "shape_confidence": shape_confidence,
            "pattern_match": [
                {"point": i, "value": point["emotional_value"], "element_id": point["element_id"]}
                for i, point in enumerate(emotional_arc)
            ]
        }

    async def suggest_improvements(self, story_id: str, aspect: str) -> Dict[str, Any]:
        """Suggest improvements for a specific aspect of the story."""
        if story_id not in self.stories:
            logger.warning(f"Story with ID {story_id} not found")
            return {"status": "error", "message": "Story not found"}

        story = self.stories[story_id]
        logger.info(f"Suggesting improvements for {aspect} in story: {story.title}")

        suggestions = []
        if aspect == "character_development":
            suggestions = [
                {
                    "type": "character_depth",
                    "description": "Consider adding more internal monologue to show the protagonist's emotional journey",
                    "location": "After element " + story.story_elements[1].id
                },
                {
                    "type": "character_growth",
                    "description": "Show more resistance to change before the transformation",
                    "location": "Before element " + story.story_elements[-1].id
                }
            ]

        return {
            "status": "success",
            "story_id": story_id,
            "suggestions": suggestions
        } 