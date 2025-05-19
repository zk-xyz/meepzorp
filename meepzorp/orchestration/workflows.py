"""
Workflow management tools for the orchestration system.
"""
from typing import Dict, Any, List
import logging
import uuid
import os
import requests
from .router import RouteRequestTool

logger = logging.getLogger(__name__)

# In-memory workflow storage used when no database is configured
WORKFLOW_DB: Dict[str, Dict[str, Any]] = {}

class CreateWorkflowTool:
    """Tool for creating new workflows."""
    
    async def execute(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow."""
        logger.info(f"Creating workflow: {workflow['name']}")

        workflow_id = str(uuid.uuid4())
        record = {"id": workflow_id, **workflow}
        WORKFLOW_DB[workflow_id] = record

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                }
                requests.post(
                    f"{supabase_url}/rest/v1/workflows",
                    headers=headers,
                    json=record,
                    timeout=5,
                ).raise_for_status()
            except Exception as e:
                logger.error(f"Failed to persist workflow to Supabase: {e}")

        return {"status": "success", "workflow_id": workflow_id}

class ListWorkflowsTool:
    """Tool for listing available workflows."""
    
    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """List available workflows."""
        logger.info("Listing workflows")
        workflows = list(WORKFLOW_DB.values())

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                }
                resp = requests.get(
                    f"{supabase_url}/rest/v1/workflows",
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    workflows = resp.json()
            except Exception as e:
                logger.error(f"Failed to query workflows from Supabase: {e}")

        return {"status": "success", "workflows": workflows}

class ExecuteWorkflowTool:
    """Tool for executing workflows."""
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        workflow_id = request.get("workflow_id")
        logger.info(f"Executing workflow: {workflow_id}")

        workflow = WORKFLOW_DB.get(str(workflow_id))
        if not workflow:
            return {"status": "error", "message": "Workflow not found"}

        input_vars = request.get("input_variables", {})
        expected_vars = set(workflow.get("variables", {}).keys())
        if not expected_vars.issuperset(input_vars.keys()):
            return {"status": "error", "message": "Invalid input", "partial_results": {}}

        router = RouteRequestTool()
        results = {}
        for step in workflow.get("steps", []):
            step_request = {
                "capability": step.get("capability"),
                "parameters": step.get("parameters", {}),
                "preferred_agent_id": step.get("agent_id"),
            }
            res = await router.execute(step_request)
            results[step.get("id", "step")] = res
            if res.get("status") != "success":
                return {"status": "error", "message": "Workflow step failed", "partial_results": results}

        return {"status": "success", "results": results}
