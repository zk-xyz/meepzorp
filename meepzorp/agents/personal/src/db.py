"""
Database client module for knowledge storage using Supabase.
"""

import json
import os
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger


class KnowledgeDB:
    """Database operations for knowledge storage."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable must be set")
        if not self.supabase_key:
            raise ValueError("SUPABASE_KEY environment variable must be set")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def store_knowledge(
        self,
        content: str,
        tags: List[str] = None,
        embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Store a piece of knowledge.

        Args:
            content: The text content to store
            tags: Optional list of tags for categorization
            embedding: Optional vector embedding for semantic search
        """
        try:
            data = {
                "content": content,
                "tags": {"tags": tags or []},  # Store tags in the correct format
            }

            if embedding:
                data["embedding"] = embedding

            logger.debug(f"Storing knowledge with data: {data}")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/knowledge",
                    headers=self.headers,
                    json=data,
                )

            if response.status_code != 201:
                raise Exception(f"Failed to store knowledge: {response.text}")

            result = response.json()
            logger.info(f"Stored knowledge with ID {result['id']}")

            # Parse tags back to list for consistent return format
            result["tags"] = (
                result["tags"].get("tags", []) if result.get("tags") else []
            )
            return result

        except Exception as e:
            logger.error(f"Error storing knowledge: {str(e)}")
            raise

    async def query_knowledge(
        self,
        query: str = None,
        tags: List[str] = None,
        embedding: List[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Query knowledge items.

        Args:
            query: Optional text query to search in content
            tags: Optional list of tags to filter by
            embedding: Optional vector embedding for semantic search
            limit: Maximum number of results to return
        """
        try:
            # Build query parameters
            params = {}
            if limit:
                params["limit"] = str(limit)

            # Build filter conditions
            filters = []

            if tags:
                # Convert tags to JSON string for comparison
                tags_json = json.dumps(sorted(tags))
                filters.append(f"tags->>'tags'=eq.{tags_json}")

            if query:
                filters.append(f"content.ilike.*{query}*")

            if embedding:
                # If we have an embedding, use vector similarity search
                filters.append(f"embedding <-> '{embedding}'::vector < 0.3")
                # Order by vector distance using the provided embedding
                params["order"] = f"embedding <-> '{embedding}'::vector"

            if filters:
                # Combine filters using the PostgREST "and" operator
                # Example result: "(filter1,filter2)"
                params["and"] = "(" + ",".join(filters) + ")"

            # Make the request
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/knowledge",
                    headers=self.headers,
                    params=params,
                )

            if response.status_code != 200:
                raise Exception(f"Failed to query knowledge: {response.text}")

            # Parse results
            items = response.json()
            for item in items:
                item["tags"] = json.loads(item["tags"])

            logger.info(f"Found {len(items)} knowledge items")
            return items

        except Exception as e:
            logger.error(f"Error querying knowledge: {str(e)}")
            raise

    async def delete_knowledge(self, knowledge_id: str) -> None:
        """Delete a knowledge item by ID."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.supabase_url}/rest/v1/knowledge",
                    headers=self.headers,
                    params={"id": f"eq.{knowledge_id}"},
                )

            if response.status_code != 204:
                raise Exception(f"Failed to delete knowledge: {response.text}")

            logger.info(f"Deleted knowledge with ID {knowledge_id}")

        except Exception as e:
            logger.error(f"Error deleting knowledge: {str(e)}")
            raise

    async def update_knowledge(
        self,
        knowledge_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Update a knowledge item.

        Args:
            knowledge_id: ID of the knowledge item to update
            content: Optional new content
            tags: Optional new tags
            embedding: Optional new embedding
        """
        try:
            # Build update data
            data = {}
            if content is not None:
                data["content"] = content
            if tags is not None:
                data["tags"] = json.dumps(tags)
            if embedding is not None:
                data["embedding"] = embedding

            if not data:
                raise ValueError("No update data provided")

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.supabase_url}/rest/v1/knowledge",
                    headers=self.headers,
                    params={"id": f"eq.{knowledge_id}"},
                    json=data,
                )

            if response.status_code != 200:
                raise Exception(f"Failed to update knowledge: {response.text}")

            result = response.json()[0]
            logger.info(f"Updated knowledge with ID {knowledge_id}")

            # Parse tags back to list
            result["tags"] = json.loads(result["tags"])
            return result

        except Exception as e:
            logger.error(f"Error updating knowledge: {str(e)}")
            raise
