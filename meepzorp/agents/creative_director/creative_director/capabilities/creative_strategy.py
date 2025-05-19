"""
Creative Strategy Capability

This capability enables the Creative Director to develop and manage creative strategies,
including brand positioning, messaging frameworks, and creative briefs.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreativeStrategy(BaseModel):
    """Model for creative strategies"""
    id: str = Field(..., description="Unique identifier for the strategy")
    project_id: str = Field(..., description="ID of the project this strategy belongs to")
    name: str = Field(..., description="Name of the strategy")
    objective: str = Field(..., description="Primary objective of the strategy")
    target_audience: Dict[str, Any] = Field(..., description="Target audience profile")
    key_messages: List[str] = Field(..., description="Key messages to communicate")
    tone_and_style: Dict[str, Any] = Field(..., description="Tone and style guidelines")
    creative_approach: str = Field(..., description="Overall creative approach")
    success_metrics: List[str] = Field(..., description="Success metrics and KPIs")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CreativeStrategyCapability:
    """Creative Strategy Capability class"""
    
    def __init__(self):
        self.strategies: Dict[str, CreativeStrategy] = {}
        
    def create_strategy(self, strategy: CreativeStrategy) -> CreativeStrategy:
        """Create a new creative strategy"""
        if strategy.id in self.strategies:
            raise ValueError(f"Strategy with ID {strategy.id} already exists")
            
        self.strategies[strategy.id] = strategy
        logger.info(f"Created new creative strategy: {strategy.name}")
        return strategy
        
    def get_strategy(self, strategy_id: str) -> Optional[CreativeStrategy]:
        """Get a strategy by ID"""
        return self.strategies.get(strategy_id)
        
    def get_project_strategies(self, project_id: str) -> List[CreativeStrategy]:
        """Get all strategies for a project"""
        return [strategy for strategy in self.strategies.values() 
                if strategy.project_id == project_id]
        
    def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> Optional[CreativeStrategy]:
        """Update an existing strategy"""
        if strategy_id not in self.strategies:
            return None
            
        strategy = self.strategies[strategy_id]
        for key, value in updates.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)
                
        strategy.updated_at = datetime.now()
        logger.info(f"Updated creative strategy: {strategy.name}")
        return strategy
        
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy"""
        if strategy_id not in self.strategies:
            return False
            
        del self.strategies[strategy_id]
        logger.info(f"Deleted strategy: {strategy_id}")
        return True
        
    def generate_creative_brief(self, strategy_id: str) -> Dict[str, Any]:
        """Generate a creative brief from a strategy"""
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy with ID {strategy_id} not found")
            
        brief = {
            "project_id": strategy.project_id,
            "strategy_name": strategy.name,
            "objective": strategy.objective,
            "target_audience": strategy.target_audience,
            "key_messages": strategy.key_messages,
            "tone_and_style": strategy.tone_and_style,
            "creative_approach": strategy.creative_approach,
            "success_metrics": strategy.success_metrics,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Generated creative brief for strategy: {strategy.name}")
        return brief 