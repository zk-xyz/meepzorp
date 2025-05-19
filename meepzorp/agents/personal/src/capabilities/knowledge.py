"""
Knowledge capabilities for the Personal Knowledge Agent.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..db import KnowledgeDB
import logging

logger = logging.getLogger(__name__)

class KnowledgeCapability:
    """Knowledge management capabilities for the Personal Knowledge Agent."""
    
    def __init__(self, db: KnowledgeDB):
        self.db = db
    
    async def store_knowledge(self, content: str, tags: List[str] = None, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """Store a piece of knowledge with optional tags and embedding."""
        try:
            result = await self.db.store_knowledge(
                content=content,
                tags=tags,
                embedding=embedding
            )
            return {"status": "success", "knowledge": result}
        except Exception as e:
            logger.error(f"Error storing knowledge: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def query_knowledge(self, query: Optional[str] = None, tags: Optional[List[str]] = None, 
                            embedding: Optional[List[float]] = None, limit: int = 10) -> Dict[str, Any]:
        """Query knowledge items with semantic search capabilities."""
        try:
            results = await self.db.query_knowledge(
                query=query,
                tags=tags,
                embedding=embedding,
                limit=limit
            )
            return {"status": "success", "results": results}
        except Exception as e:
            logger.error(f"Error querying knowledge: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def update_knowledge(self, knowledge_id: str, content: Optional[str] = None, 
                             tags: Optional[List[str]] = None, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """Update a knowledge item."""
        try:
            result = await self.db.update_knowledge(
                knowledge_id=knowledge_id,
                content=content,
                tags=tags,
                embedding=embedding
            )
            return {"status": "success", "knowledge": result}
        except Exception as e:
            logger.error(f"Error updating knowledge: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def delete_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        """Delete a knowledge item."""
        try:
            await self.db.delete_knowledge(knowledge_id)
            return {"status": "success", "message": f"Knowledge item {knowledge_id} deleted"}
        except Exception as e:
            logger.error(f"Error deleting knowledge: {str(e)}")
            return {"status": "error", "message": str(e)} 