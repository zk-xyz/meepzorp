"""
Test analysis of "The No-Talent Kid" by Kurt Vonnegut
Demonstrates the enhanced story analysis capabilities.
"""

import unittest
from datetime import datetime
from creative_director.capabilities.story_crafter import (
    StoryCrafterCapability,
    Story,
    StoryElement,
    NarrativeStructure,
    StoryShape
)

class TestNoTalentKid(unittest.TestCase):
    def setUp(self):
        self.story_crafter = StoryCrafterCapability()
        
        # Create story elements for The No-Talent Kid
        self.story_elements = [
            StoryElement(
                id="1",
                story_id="no_talent_kid",
                element_type="scene",
                content={
                    "text": "The protagonist, a young boy with no apparent talents, sits alone in his room.",
                    "characters": ["protagonist"],
                    "location": "bedroom",
                    "emotional_tone": -0.3
                },
                emotional_value=-0.3,
                created_at=datetime.now()
            ),
            StoryElement(
                id="2",
                story_id="no_talent_kid",
                element_type="scene",
                content={
                    "text": "He watches other children excel in various activities through his window.",
                    "characters": ["protagonist", "other_children"],
                    "location": "bedroom",
                    "emotional_tone": -0.5
                },
                emotional_value=-0.5,
                created_at=datetime.now()
            ),
            StoryElement(
                id="3",
                story_id="no_talent_kid",
                element_type="scene",
                content={
                    "text": "One day, he discovers a hidden talent for understanding animals.",
                    "characters": ["protagonist", "animals"],
                    "location": "garden",
                    "emotional_tone": 0.2
                },
                emotional_value=0.2,
                created_at=datetime.now()
            ),
            StoryElement(
                id="4",
                story_id="no_talent_kid",
                element_type="scene",
                content={
                    "text": "He uses this ability to help his community solve problems.",
                    "characters": ["protagonist", "community"],
                    "location": "town",
                    "emotional_tone": 0.7
                },
                emotional_value=0.7,
                created_at=datetime.now()
            ),
            StoryElement(
                id="5",
                story_id="no_talent_kid",
                element_type="scene",
                content={
                    "text": "In the end, he realizes that everyone has unique talents waiting to be discovered.",
                    "characters": ["protagonist"],
                    "location": "town",
                    "emotional_tone": 0.9
                },
                emotional_value=0.9,
                created_at=datetime.now()
            )
        ]
        
        self.story = Story(
            id="no_talent_kid",
            project_id="test_project",
            title="The No-Talent Kid",
            genre="children's fiction",
            synopsis="A story about a boy who discovers his unique talent for understanding animals.",
            target_audience="children",
            tone_and_style="whimsical and heartwarming",
            narrative_structure=NarrativeStructure.HERO_JOURNEY,
            story_elements=self.story_elements
        )

    def test_emotional_arc(self):
        arc = self.story_crafter._calculate_emotional_arc(self.story)
        self.assertEqual(len(arc), 5)
        self.assertLess(arc[0]["emotional_value"], arc[-1]["emotional_value"])
        
    def test_story_shape(self):
        arc = self.story_crafter._calculate_emotional_arc(self.story)
        shape = self.story_crafter._identify_story_shape(arc)
        self.assertEqual(shape["primary_shape"], StoryShape.MAN_IN_HOLE.value)
        self.assertGreater(shape["shape_confidence"]["man_in_hole"]["confidence"], 0.7)
        
    def test_character_development(self):
        character_arcs = self.story_crafter._analyze_character_arcs(self.story)
        self.assertIn("protagonist", character_arcs)
        protagonist_arc = character_arcs["protagonist"]
        self.assertEqual(len(protagonist_arc["development_stages"]), 5)
        self.assertEqual(protagonist_arc["character_shape"]["primary_shape"], StoryShape.MAN_IN_HOLE.value)

if __name__ == '__main__':
    unittest.main() 