#!/bin/bash
# Script to create the Python source files for the Second Me multi-agent project

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_green() {
    echo -e "${GREEN}$1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}$1${NC}"
}

print_red() {
    echo -e "${RED}$1${NC}"
}

print_blue() {
    echo -e "${BLUE}$1${NC}"
}

# Create a file from a here document
create_file_heredoc() {
    local file_path=$1
    
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$file_path")"
    
    # The caller should redirect a here document to this function
    cat > "$file_path"
    print_yellow "Created file: $file_path"
}

# Check if we're in the project directory
if [ ! -d "orchestration" ] || [ ! -d "agents" ]; then
    print_red "Please run this script from the project root directory (second-me-project)."
    exit 1
fi

print_green "Creating Python source files..."

# Create orchestration registry.py
print_blue "Creating orchestration/src/registry.py..."
create_file_heredoc "orchestration/src/registry.py" << 'EOF'
"""
Agent registry module for the orchestration system.

This module provides tools for registering agents and discovering
their capabilities within the system.
"""
import uuid
import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from fastmcp.tools import MCPTool
from loguru import logger
import asyncio
import backoff

# Models for agent registry
class AgentCapability(BaseModel):
    """Model representing an agent capability."""
    name: str = Field(..., description="The name of the capability")
    description: str = Field(..., description="Description of what the capability does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters required by the capability")
    return_type: Dict[str, Any] = Field(default_factory=dict, description="Return type of the capability")

class AgentInfo(BaseModel):
    """Model representing agent information for registration."""
    name: str = Field(..., description="The name of the agent")
    description: str = Field(..., description="Description of the agent's purpose")
    endpoint: str = Field(..., description="The URL endpoint for the agent's MCP server")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="List of agent capabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class RegisteredAgent(AgentInfo):
    """Model representing a registered agent with system-added fields."""
    id: str = Field(..., description="Unique identifier for the agent")
    status: str = Field(default="active", description="Status of the agent (active, inactive)")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the agent was registered")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the agent was last updated")
    last_seen: Optional[datetime] = Field(default=None, description="Timestamp when the agent was last seen active")
    
class AgentRegistryTool(MCPTool):
    """Tool for registering agents in the system."""
    
    name = "register_agent"
    description = "Register a new specialized agent in the system"
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, agent_info: AgentInfo) -> Dict[str, Any]:
        """
        Register a new agent in the system.
        
        Args:
            agent_info: Information about the agent to register
            
        Returns:
            Dictionary with registration status and agent ID
        """
        try:
            # Generate a unique ID for the agent
            agent_id = str(uuid.uuid4())
            
            # Create a registered agent object
            registered_agent = RegisteredAgent(
                **agent_info.dict(),
                id=agent_id,
                status="active",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_seen=datetime.now()
            )
            
            # Store in database (placeholder for Supabase implementation)
            # Here we would store the registered_agent in Supabase
            # For now, we'll just log it
            logger.info(f"Registered new agent: {registered_agent.name} ({agent_id})")
            
            # Check agent health to verify it's accessible
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{agent_info.endpoint}/health")
                    if response.status_code != 200:
                        logger.warning(f"Agent health check failed: {response.status_code}")
                        return {
                            "status": "warning",
                            "agent_id": agent_id,
                            "message": "Agent registered but health check failed"
                        }
            except Exception as e:
                logger.warning(f"Agent health check failed: {str(e)}")
                return {
                    "status": "warning",
                    "agent_id": agent_id,
                    "message": "Agent registered but endpoint not reachable"
                }
                
            return {
                "status": "success",
                "agent_id": agent_id,
                "message": "Agent successfully registered"
            }
            
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to register agent: {str(e)}"
            }

class AgentDiscoveryTool(MCPTool):
    """Tool for discovering registered agents and their capabilities."""
    
    name = "discover_agents"
    description = "Discover registered agents and their capabilities"
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, capability_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover registered agents, optionally filtered by capability.
        
        Args:
            capability_filter: Optional filter to find agents with specific capabilities
            
        Returns:
            Dictionary with list of matching agents
        """
        try:
            # Placeholder for Supabase query
            # Here we would query the database for registered agents
            # For now, return a mock response
            agents = [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Personal Knowledge Agent",
                    "description": "Agent for accessing personal knowledge base",
                    "endpoint": "http://personal-agent:8002",
                    "capabilities": [
                        {
                            "name": "search_knowledge",
                            "description": "Search the knowledge base using semantic search",
                            "parameters": {
                                "query": "string",
                                "max_results": "integer",
                                "similarity_threshold": "float"
                            }
                        }
                    ],
                    "status": "active"
                }
            ]
            
            if capability_filter:
                agents = [
                    agent for agent in agents
                    if any(cap["name"] == capability_filter for cap in agent["capabilities"])
                ]
                
            return {
                "status": "success",
                "agents": agents,
                "count": len(agents)
            }
            
        except Exception as e:
            logger.error(f"Error discovering agents: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to discover agents: {str(e)}"
            }
EOF

# Create orchestration router.py
print_blue "Creating orchestration/src/router.py..."
create_file_heredoc "orchestration/src/router.py" << 'EOF'
"""
Router module for the orchestration system.

This module provides tools for routing requests to the appropriate agents
based on capabilities and availability.
"""
import httpx
import asyncio
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from fastmcp.tools import MCPTool
from loguru import logger
import backoff

class RouteRequestInput(BaseModel):
    """Input model for routing requests to agents."""
    capability: str = Field(..., description="The capability to route the request to")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the capability")
    preferred_agent_id: Optional[str] = Field(None, description="Optional preferred agent ID")
    timeout: Optional[float] = Field(5.0, description="Timeout for the request in seconds")

class RouteRequestTool(MCPTool):
    """Tool for routing requests to the appropriate agent based on capabilities."""
    
    name = "route_request"
    description = "Route a request to an agent with the requested capability"
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, route_input: RouteRequestInput) -> Dict[str, Any]:
        """
        Route a request to an agent with the specified capability.
        
        Args:
            route_input: Input with capability and parameters to route
            
        Returns:
            Response from the agent
        """
        try:
            # Find an agent with the required capability
            agent = await self._find_agent(route_input.capability, route_input.preferred_agent_id)
            
            if not agent:
                return {
                    "status": "error",
                    "message": f"No agent found with capability: {route_input.capability}"
                }
                
            # Route the request to the agent
            response = await self._call_agent(
                agent["endpoint"],
                route_input.capability,
                route_input.parameters,
                route_input.timeout
            )
            
            return {
                "status": "success",
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "result": response
            }
            
        except Exception as e:
            logger.error(f"Error routing request: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to route request: {str(e)}"
            }
            
    async def _find_agent(self, capability: str, preferred_agent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find an agent with the specified capability.
        
        Args:
            capability: The capability to search for
            preferred_agent_id: Optional preferred agent ID
            
        Returns:
            Agent information or None if no matching agent is found
        """
        # If preferred agent is specified, try to use it first
        if preferred_agent_id:
            # Placeholder for Supabase query to get the preferred agent
            # For now, return a mock response
            if preferred_agent_id == "00000000-0000-0000-0000-000000000001":
                return {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Personal Knowledge Agent",
                    "description": "Agent for accessing personal knowledge base",
                    "endpoint": "http://personal-agent:8002",
                    "capabilities": [
                        {
                            "name": "search_knowledge",
                            "description": "Search the knowledge base using semantic search",
                            "parameters": {
                                "query": "string",
                                "max_results": "integer",
                                "similarity_threshold": "float"
                            }
                        }
                    ],
                    "status": "active"
                }
        
        # Find agents with the required capability
        # Placeholder for Supabase query
        # Here we would query the database for agents with the capability
        # For now, return a mock response
        agents = [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "Personal Knowledge Agent",
                "description": "Agent for accessing personal knowledge base",
                "endpoint": "http://personal-agent:8002",
                "capabilities": [
                    {
                        "name": "search_knowledge",
                        "description": "Search the knowledge base using semantic search",
                        "parameters": {
                            "query": "string",
                            "max_results": "integer",
                            "similarity_threshold": "float"
                        }
                    }
                ],
                "status": "active"
            }
        ]
        
        matching_agents = [
            agent for agent in agents
            if any(cap["name"] == capability for cap in agent["capabilities"])
            and agent["status"] == "active"
        ]
        
        if not matching_agents:
            return None
            
        # TODO: Implement more sophisticated agent selection (load balancing, etc.)
        return matching_agents[0]
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _call_agent(
        self, 
        endpoint: str, 
        capability: str, 
        parameters: Dict[str, Any],
        timeout: float
    ) -> Any:
        """
        Call an agent with the specified capability and parameters.
        
        Args:
            endpoint: The agent's endpoint URL
            capability: The capability to call
            parameters: Parameters for the capability
            timeout: Request timeout in seconds
            
        Returns:
            Response from the agent
        """
        # Construct the MCP request
        mcp_request = {
            "name": capability,
            "parameters": parameters
        }
        
        # Send the request to the agent
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{endpoint}/mcp/tools",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Agent returned error: {response.status_code} - {response.text}")
                raise Exception(f"Agent returned error: {response.status_code}")
                
            return response.json()
EOF

# Create orchestration workflows.py
print_blue "Creating orchestration/src/workflows.py..."
create_file_heredoc "orchestration/src/workflows.py" << 'EOF'
"""
Workflow module for the orchestration system.

This module provides tools for defining and executing multi-agent workflows.
"""
import uuid
import json
import yaml
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from fastmcp.tools import MCPTool
from loguru import logger
from datetime import datetime
import backoff

from .router import RouteRequestTool, RouteRequestInput

# Models for workflow management
class WorkflowStep(BaseModel):
    """Model representing a step in a workflow."""
    id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Name of the step")
    description: str = Field(..., description="Description of what the step does")
    capability: str = Field(..., description="The agent capability to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Static parameters for the capability")
    parameter_mapping: Dict[str, str] = Field(default_factory=dict, description="Mapping from previous step outputs to parameters")
    preferred_agent_id: Optional[str] = Field(None, description="Optional preferred agent ID")
    timeout: float = Field(5.0, description="Timeout for the step in seconds")
    retry: Dict[str, Any] = Field(
        default_factory=lambda: {"max_attempts": 3, "backoff_factor": 2.0}, 
        description="Retry configuration"
    )

class WorkflowDefinition(BaseModel):
    """Model representing a workflow definition."""
    name: str = Field(..., description="Name of the workflow")
    description: str = Field(..., description="Description of what the workflow does")
    steps: List[WorkflowStep] = Field(..., description="Steps in the workflow")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Variables available to all steps")

class CreateWorkflowInput(BaseModel):
    """Input model for creating a workflow."""
    definition: WorkflowDefinition = Field(..., description="Workflow definition")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the workflow")

class ExecuteWorkflowInput(BaseModel):
    """Input model for executing a workflow."""
    workflow_id: str = Field(..., description="ID of the workflow to execute")
    input_variables: Dict[str, Any] = Field(default_factory=dict, description="Input variables for the workflow")
    timeout: float = Field(60.0, description="Overall timeout for the workflow in seconds")

class CreateWorkflowTool(MCPTool):
    """Tool for creating and saving workflow definitions."""
    
    name = "create_workflow"
    description = "Create and save a new workflow definition"
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, workflow_input: CreateWorkflowInput) -> Dict[str, Any]:
        """
        Create and save a new workflow definition.
        
        Args:
            workflow_input: Input with the workflow definition
            
        Returns:
            Dictionary with status and workflow ID
        """
        try:
            # Generate a unique ID for the workflow
            workflow_id = str(uuid.uuid4())
            
            # TODO: Store the workflow in the database (placeholder for Supabase)
            # For now, we'll just log it
            logger.info(f"Created new workflow: {workflow_input.definition.name} ({workflow_id})")
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "message": "Workflow created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create workflow: {str(e)}"
            }

class ListWorkflowsTool(MCPTool):
    """Tool for listing available workflows."""
    
    name = "list_workflows"
    description = "List available workflows with optional filtering"
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        List available workflows, optionally filtered by tags.
        
        Args:
            tags: Optional tags to filter workflows
            
        Returns:
            Dictionary with list of matching workflows
        """
        try:
            # TODO: Query workflows from the database (placeholder for Supabase)
            # For now, return a mock response
            workflows = [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Knowledge Search",
                    "description": "Search the knowledge base and process results",
                    "created_at": datetime.now().isoformat(),
                    "tags": ["knowledge", "search"]
                }
            ]
            
            if tags:
                workflows = [
                    workflow for workflow in workflows
                    if any(tag in workflow["tags"] for tag in tags)
                ]
                
            return {
                "status": "success",
                "workflows": workflows,
                "count": len(workflows)
            }
            
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to list workflows: {str(e)}"
            }

class ExecuteWorkflowTool(MCPTool):
    """Tool for executing a workflow."""
    
    name = "execute_workflow"
    description = "Execute a multi-agent workflow"
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, workflow_input: ExecuteWorkflowInput) -> Dict[str, Any]:
        """
        Execute a workflow with the given input variables.
        
        Args:
            workflow_input: Input with workflow ID and variables
            
        Returns:
            Dictionary with workflow execution results
        """
        try:
            # Get the workflow definition
            # TODO: Query the database for the workflow (placeholder for Supabase)
            # For now, return a mock workflow
            workflow_definition = WorkflowDefinition(
                name="Knowledge Search",
                description="Search the knowledge base and process results",
                steps=[
                    WorkflowStep(
                        id="search_step",
                        name="Search Knowledge",
                        description="Search the knowledge base for relevant information",
                        capability="search_knowledge",
                        parameters={
                            "max_results": 3,
                            "similarity_threshold": 0.7
                        },
                        parameter_mapping={
                            "query": "input.search_query"
                        },
                        preferred_agent_id="00000000-0000-0000-0000-000000000001"
                    )
                ],
                variables={}
            )
            
            # Prepare the execution context
            context = {
                "input": workflow_input.input_variables,
                "steps": {},
                "variables": workflow_definition.variables
            }
            
            # Execute each step in the workflow
            router = RouteRequestTool()
            step_results = {}
            
            for step in workflow_definition.steps:
                logger.info(f"Executing step: {step.name}")
                
                # Prepare parameters for the step
                parameters = step.parameters.copy()
                
                # Apply parameter mapping from context
                for param_name, mapping in step.parameter_mapping.items():
                    # Parse the mapping path (e.g., "input.search_query", "steps.step1.result.value")
                    path_parts = mapping.split(".")
                    
                    # Navigate through the context to get the value
                    value = context
                    for part in path_parts:
                        if part in value:
                            value = value[part]
                        else:
                            logger.warning(f"Mapping path not found: {mapping}")
                            value = None
                            break
                    
                    # Set the parameter value
                    if value is not None:
                        parameters[param_name] = value
                
                # Route the request to the appropriate agent
                route_input = RouteRequestInput(
                    capability=step.capability,
                    parameters=parameters,
                    preferred_agent_id=step.preferred_agent_id,
                    timeout=step.timeout
                )
                
                # Execute with retry logic
                max_attempts = step.retry["max_attempts"]
                backoff_factor = step.retry["backoff_factor"]
                
                for attempt in range(max_attempts):
                    try:
                        result = await router.execute(route_input)
                        if result["status"] == "success":
                            step_results[step.id] = result
                            # Update the context with the step result
                            context["steps"][step.id] = result
                            break
                        elif attempt < max_attempts - 1:
                            wait_time = backoff_factor ** attempt
                            logger.warning(f"Step failed, retrying in {wait_time}s: {result}")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"Step failed after {max_attempts} attempts: {result}")
                            return {
                                "status": "error",
                                "workflow_id": workflow_input.workflow_id,
                                "message": f"Step '{step.name}' failed after {max_attempts} attempts",
                                "partial_results": step_results
                            }
                    except Exception as e:
                        if attempt < max_attempts - 1:
                            wait_time = backoff_factor ** attempt
                            logger.warning(f"Step error, retrying in {wait_time}s: {str(e)}")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"Step error after {max_attempts} attempts: {str(e)}")
                            return {
                                "status": "error",
                                "workflow_id": workflow_input.workflow_id,
                                "message": f"Step '{step.name}' error after {max_attempts} attempts: {str(e)}",
                                "partial_results": step_results
                            }
            
            return {
                "status": "success",
                "workflow_id": workflow_input.workflow_id,
                "results": step_results,
                "output": self._extract_final_output(step_results, workflow_definition)
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                "status": "error",
                "workflow_id": workflow_input.workflow_id,
                "message": f"Failed to execute workflow: {str(e)}"
            }
    
    def _extract_final_output(self, step_results: Dict[str, Any], workflow_definition: WorkflowDefinition) -> Dict[str, Any]:
        """
        Extract the final output from the workflow execution results.
        
        Args:
            step_results: Results from each workflow step
            workflow_definition: The workflow definition
            
        Returns:
            Dictionary with the final output
        """
        # For now, we'll just return the result of the last step
        if workflow_definition.steps:
            last_step_id = workflow_definition.steps[-1].id
            if last_step_id in step_results:
                return step_results[last_step_id].get("result", {})
        
        return {}
EOF

# Create base agent files
print_blue "Creating base agent files..."

create_file_heredoc "agents/base/src/base_agent.py" << 'EOF'
"""
Base agent module that serves as a template for all specialized agents.

This module provides the foundation for creating specialized agents by defining
the basic MCP server structure and capability registration.
"""
import os
import asyncio
import httpx
from typing import Dict, List, Any, Optional, Callable, Awaitable
from fastmcp import FastMCP
from fastmcp.tools import MCPTool
from pydantic import BaseModel, Field
from loguru import logger
from dotenv import load_dotenv
import backoff

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.remove()
logger.add(
    "logs/agent.log",
    rotation="10 MB",
    level=logging_level,
    format="{time} {level} {message}",
)
logger.add(lambda msg: print(msg), level=logging_level)

class AgentInfo(BaseModel):
    """Model representing agent information for registration."""
    name: str
    description: str
    capabilities: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent:
    """Base agent class that all specialized agents should extend."""
    
    def __init__(self, name: str, description: str, port: int = 8001):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent's purpose
            port: Port for the MCP server to listen on
        """
        self.name = name
        self.description = description
        self.port = port
        self.capabilities = {}
        self.metadata = {}
        
        # Create the FastMCP application
        self.mcp = FastMCP(name)
        self.app = self.mcp.get_app()
        
        # Add default endpoints
        self._add_default_endpoints()
        
        # Register with orchestration on startup
        self.app.add_event_handler("startup", self._register_with_orchestration)
    
    def _add_default_endpoints(self):
        """Add default endpoints to the agent's FastAPI app."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint showing basic agent information."""
            return {
                "name": self.name,
                "description": self.description,
                "capabilities": list(self.capabilities.keys()),
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "agent": self.name,
                "capabilities_count": len(self.capabilities),
            }
    
    def register_capability(self, tool: MCPTool):
        """
        Register a capability with the agent.
        
        Args:
            tool: The MCP tool implementing the capability
        """
        self.mcp.add_tool(tool)
        self.capabilities[tool.name] = {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.get_parameters_schema(),
            "return_type": tool.get_return_type_schema(),
        }
        logger.info(f"Registered capability: {tool.name}")
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=5, max_time=30)
    async def _register_with_orchestration(self):
        """Register the agent with the orchestration service on startup."""
        try:
            orchestration_url = os.getenv("ORCHESTRATION_URL")
            if not orchestration_url:
                logger.warning("ORCHESTRATION_URL not set, skipping registration")
                return
                
            # Wait a bit to ensure the orchestration service is up
            await asyncio.sleep(5)
            
            # Get the host and port for the agent's endpoint
            # In production, this would be the externally accessible URL
            host = os.getenv("AGENT_HOST", "localhost")
            port = int(os.getenv("MCP_PORT", self.port))
            agent_endpoint = f"http://{host}:{port}"
            
            # Prepare registration payload
            agent_info = AgentInfo(
                name=self.name,
                description=self.description,
                capabilities=[capability for capability in self.capabilities.values()],
                metadata=self.metadata,
            )
            
            # Register with orchestration
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{orchestration_url}/mcp/tools",
                    json={
                        "name": "register_agent",
                        "parameters": {
                            "name": agent_info.name,
                            "description": agent_info.description,
                            "endpoint": agent_endpoint,
                            "capabilities": agent_info.capabilities,
                            "metadata": agent_info.metadata,
                        }
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        logger.info(f"Agent registered successfully: {result.get('agent_id')}")
                    else:
                        logger.warning(f"Agent registration warning: {result.get('message')}")
                else:
                    logger.error(f"Agent registration failed: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            raise
    
    def run(self):
        """Run the agent's MCP server."""
        import uvicorn
        logger.info(f"Starting {self.name} agent on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

# Create a basic agent instance for this module
agent = BaseAgent(
    name="Base Agent",
    description="Template agent for creating specialized agents",
    port=int(os.getenv("MCP_PORT", 8001))
)

# Export the FastAPI app for uvicorn
app = agent.app

if __name__ == "__main__":
    agent.run()
EOF

# Create capabilities.py
print_blue "Creating agents/base/src/capabilities.py..."
create_file_heredoc "agents/base/src/capabilities.py" << 'EOF'
"""
Capabilities module for the base agent.

This module provides classes and utilities for defining and registering
agent capabilities.
"""
from typing import Dict, List, Any, Optional, Type, TypeVar, Generic, Union
from pydantic import BaseModel, create_model, Field
from fastmcp.tools import MCPTool
from loguru import logger

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R', bound=BaseModel)

class Capability(MCPTool, Generic[T, R]):
    """
    Base class for agent capabilities.
    
    This class provides a standardized way to define agent capabilities
    with typed inputs and outputs.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a capability.
        
        Args:
            name: Name of the capability
            description: Description of what the capability does
        """
        self.name = name
        self.description = description
        
    async def execute(self, parameters: Any) -> Any:
        """
        Execute the capability with the given parameters.
        
        This method should be overridden by subclasses to implement the
        actual capability functionality.
        
        Args:
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability execution
        """
        raise NotImplementedError("Capability must implement execute method")

class CapabilityRegistry:
    """Registry for managing agent capabilities."""
    
    def __init__(self):
        """Initialize the capability registry."""
        self.capabilities: Dict[str, Capability] = {}
        
    def register(self, capability: Capability) -> None:
        """
        Register a capability with the registry.
        
        Args:
            capability: The capability to register
        """
        self.capabilities[capability.name] = capability
        logger.info(f"Registered capability: {capability.name}")
        
    def get(self, name: str) -> Optional[Capability]:
        """
        Get a capability by name.
        
        Args:
            name: Name of the capability to get
            
        Returns:
            The capability or None if not found
        """
        return self.capabilities.get(name)
        
    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all registered capabilities.
        
        Returns:
            List of capability information
        """
        return [
            {
                "name": capability.name,
                "description": capability.description,
                "parameters": capability.get_parameters_schema(),
                "return_type": capability.get_return_type_schema(),
            }
            for capability in self.capabilities.values()
        ]

class HealthCheckCapability(Capability):
    """Example capability that provides a health check."""
    
    def __init__(self):
        """Initialize the health check capability."""
        super().__init__(
            name="health_check",
            description="Check the health of the agent"
        )
        
    async def execute(self, parameters: Any = None) -> Dict[str, Any]:
        """
        Execute the health check capability.
        
        Args:
            parameters: Optional parameters (unused)
            
        Returns:
            Health check results
        """
        return {
            "status": "healthy",
            "version": "0.1.0",
            "capabilities": len(self._get_registry().list_all()),
        }
        
    def _get_registry(self) -> CapabilityRegistry:
        """
        Get the capability registry.
        
        This is a placeholder implementation that would be replaced
        with a reference to the actual registry in a real agent.
        
        Returns:
            The capability registry
        """
        registry = CapabilityRegistry()
        registry.register(self)
        return registry

# Example input and output models for a capability
class EchoInput(BaseModel):
    """Input model for the echo capability."""
    message: str = Field(..., description="Message to echo")

class EchoOutput(BaseModel):
    """Output model for the echo capability."""
    message: str = Field(..., description="Echoed message")
    timestamp: str = Field(..., description="Timestamp when the message was echoed")

class EchoCapability(Capability[EchoInput, EchoOutput]):
    """Example capability that echoes a message."""
    
    def __init__(self):
        """Initialize the echo capability."""
        super().__init__(
            name="echo",
            description="Echo a message back to the sender"
        )
        
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the echo capability.
        
        Args:
            parameters: Parameters for the capability
            
        Returns:
            Echoed message and timestamp
        """
        from datetime import datetime
        
        message = parameters.get("message", "")
        timestamp = datetime.now().isoformat()
        
        return {
            "message": message,
            "timestamp": timestamp,
        }
EOF

# Create knowledge.py
print_blue "Creating agents/base/src/knowledge.py..."
create_file_heredoc "agents/base/src/knowledge.py" << 'EOF'
"""
Knowledge module for the base agent.

This module provides classes and utilities for connecting to and
interacting with knowledge repositories.
"""
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from loguru import logger
import os
from dotenv import load_dotenv
import backoff

# Load environment variables
load_dotenv()

class SearchResult(BaseModel):
    """Model representing a single search result."""
    id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    content: str = Field(..., description="Content snippet from the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    similarity_score: float = Field(..., description="Similarity score of the document to the query")

class SearchResponse(BaseModel):
    """Model representing a search response."""
    query: str = Field(..., description="The search query")
    total_results: int = Field(..., description="Total number of matching results")
    results: List[SearchResult] = Field(default_factory=list, description="Search results")

class KnowledgeBase:
    """
    Base class for knowledge base connections.
    
    This class provides a standardized interface for connecting to and
    querying knowledge repositories.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the knowledge base connection.
        
        Args:
            connection_string: Optional connection string for the knowledge base
        """
        self.connection_string = connection_string or os.getenv("KNOWLEDGE_BASE_CONNECTION")
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def search(
        self, 
        query_text: str, 
        max_results: int = 3, 
        similarity_threshold: float = 0.0
    ) -> SearchResponse:
        """
        Search the knowledge base for documents matching the query.
        
        Args:
            query_text: The search query text
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score for results
            
        Returns:
            Search response with matching documents
        """
        # This is a placeholder implementation that should be overridden
        # by subclasses with actual knowledge base connections.
        logger.warning("Using placeholder knowledge base search")
        return SearchResponse(
            query=query_text,
            total_results=1,
            results=[
                SearchResult(
                    id="placeholder-doc-1",
                    title="Placeholder Document",
                    content="This is a placeholder document for testing the knowledge base search interface.",
                    metadata={"source": "placeholder", "type": "text"},
                    similarity_score=1.0
                )
            ]
        )
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def retrieve_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            The document or None if not found
        """
        # This is a placeholder implementation that should be overridden
        # by subclasses with actual knowledge base connections.
        logger.warning("Using placeholder document retrieval")
        return {
            "id": document_id,
            "title": "Placeholder Document",
            "content": "This is a placeholder document for testing the knowledge base interface.",
            "metadata": {"source": "placeholder", "type": "text"},
        }

class SupabaseKnowledgeBase(KnowledgeBase):
    """Knowledge base connection using Supabase and pgvector."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the Supabase knowledge base connection.
        
        Args:
            connection_string: Optional connection string for Supabase
        """
        super().__init__(connection_string)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase URL or key not set, using placeholder implementation")
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def search(
        self, 
        query_text: str, 
        max_results: int = 3, 
        similarity_threshold: float = 0.0
    ) -> SearchResponse:
        """
        Search the knowledge base using Supabase and pgvector.
        
        Args:
            query_text: The search query text
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score for results
            
        Returns:
            Search response with matching documents
        """
        try:
            # This is where you would implement the actual Supabase query
            # For now, returning a placeholder implementation 
            # TODO: Implement actual Supabase pgvector query
            logger.warning("Using placeholder Supabase search implementation")
            
            return SearchResponse(
                query=query_text,
                total_results=1,
                results=[
                    SearchResult(
                        id="supabase-doc-1",
                        title="Supabase Knowledge Document",
                        content="This is a placeholder document for testing the Supabase knowledge base search interface.",
                        metadata={"source": "supabase", "type": "text"},
                        similarity_score=0.85
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Error searching Supabase knowledge base: {str(e)}")
            raise
            
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def retrieve_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a document by ID from Supabase.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            The document or None if not found
        """
        try:
            # This is where you would implement the actual Supabase query
            # For now, returning a placeholder implementation
            # TODO: Implement actual Supabase document retrieval
            logger.warning("Using placeholder Supabase document retrieval")
            
            return {
                "id": document_id,
                "title": "Supabase Knowledge Document",
                "content": "This is a placeholder document for testing the Supabase knowledge base interface.",
                "metadata": {"source": "supabase", "type": "text"},
            }
            
        except Exception as e:
            logger.error(f"Error retrieving document from Supabase: {str(e)}")
            raise
            
def get_knowledge_base() -> KnowledgeBase:
    """
    Factory function to get the appropriate knowledge base instance.
    
    Returns:
        A knowledge base instance
    """
    # Check environment variables to decide which implementation to use
    use_supabase = os.getenv("USE_SUPABASE", "true").lower() == "true"
    
    if use_supabase:
        return SupabaseKnowledgeBase()
    else:
        return KnowledgeBase()
EOF

# Create personal agent files
print_blue "Creating personal agent files..."

create_file_heredoc "agents/personal/src/personal_agent.py" << 'EOF'
"""
Personal agent module for the multi-agent system.

This module implements a specialized agent for accessing and querying
the personal knowledge base.
"""
import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from fastmcp.tools import MCPTool
from pydantic import BaseModel, Field
from loguru import logger
from dotenv import load_dotenv
import backoff

# Add the base agent module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../agents/base/src"))

# Import from base agent
from base_agent import BaseAgent
from capabilities import Capability

# Import local modules
from .capabilities.search import SearchKnowledgeCapability
from .capabilities.document import GetDocumentCapability
from .capabilities.graph import QueryKnowledgeGraphCapability

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.remove()
logger.add(
    "logs/personal_agent.log",
    rotation="10 MB",
    level=logging_level,
    format="{time} {level} {message}",
)
logger.add(lambda msg: print(msg), level=logging_level)

class PersonalAgent(BaseAgent):
    """
    Specialized agent for accessing and querying the personal knowledge base.
    
    This agent provides capabilities for semantic search, document retrieval,
    and knowledge graph querying.
    """
    
    def __init__(self, port: int = 8002):
        """
        Initialize the personal agent.
        
        Args:
            port: Port for the MCP server to listen on
        """
        super().__init__(
            name="Personal Knowledge Agent",
            description="Agent for accessing and querying personal knowledge",
            port=port
        )
        
        # Set agent metadata
        self.metadata = {
            "knowledge_domain": "personal",
            "supports_semantic_search": True,
            "supports_graph_queries": True,
        }
        
        # Register capabilities
        self._register_capabilities()
        
    def _register_capabilities(self):
        """Register the agent's capabilities."""
        # Register search capability
        self.register_capability(SearchKnowledgeCapability())
        
        # Register document retrieval capability
        self.register_capability(GetDocumentCapability())
        
        # Register knowledge graph query capability
        self.register_capability(QueryKnowledgeGraphCapability())
        
        logger.info(f"Registered {len(self.capabilities)} capabilities")

# Create the personal agent
agent = PersonalAgent(port=int(os.getenv("MCP_PORT", 8002)))

# Export the FastAPI app for uvicorn
app = agent.app

if __name__ == "__main__":
    agent.run()
EOF

mkdir -p agents/personal/src/capabilities

# Create search capability
print_blue "Creating agents/personal/src/capabilities/search.py..."
create_file_heredoc "agents/personal/src/capabilities/search.py" << 'EOF'
"""
Search capability for the personal agent.

This module implements the capability for searching the personal knowledge base
using semantic search technology.
"""
import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from fastmcp.tools import MCPTool
import backoff

# Add the base agent module to the Python path
base_path = os.path.join(os.path.dirname(__file__), "../../../../base/src")
sys.path.append(os.path.abspath(base_path))

# Import from base agent
from capabilities import Capability
from knowledge import get_knowledge_base, SearchResponse

class SearchInput(BaseModel):
    """Input model for the search knowledge capability."""
    query: str = Field(..., description="Search query text")
    max_results: int = Field(3, description="Maximum number of results to return")
    similarity_threshold: float = Field(0.7, description="Minimum similarity score for results")

class SearchKnowledgeCapability(Capability):
    """
    Capability for searching the personal knowledge base.
    
    This capability allows querying the knowledge base using natural language
    and returns semantically relevant results.
    """
    
    def __init__(self):
        """Initialize the search knowledge capability."""
        super().__init__(
            name="search_knowledge",
            description="Search the knowledge base using semantic search"
        )
        
        # Initialize the knowledge base connection
        self.knowledge_base = get_knowledge_base()
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the search knowledge capability.
        
        Args:
            parameters: Parameters for the capability
                - query: Search query text
                - max_results: Maximum number of results to return
                - similarity_threshold: Minimum similarity score for results
            
        Returns:
            Search results matching the query
        """
        try:
            # Parse and validate input
            search_input = SearchInput(
                query=parameters.get("query", ""),
                max_results=parameters.get("max_results", 3),
                similarity_threshold=parameters.get("similarity_threshold", 0.7)
            )
            
            logger.info(f"Searching knowledge base: {search_input.query}")
            
            # Search the knowledge base
            result = await self.knowledge_base.search(
                query_text=search_input.query,
                max_results=search_input.max_results,
                similarity_threshold=search_input.similarity_threshold
            )
            
            logger.info(f"Found {result.total_results} results")
            
            # Format the response
            return {
                "query": result.query,
                "total_results": result.total_results,
                "results": [r.dict() for r in result.results]
            }
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return {
                "error": str(e),
                "query": parameters.get("query", ""),
                "total_results": 0,
                "results": []
            }
EOF

# Create document capability
print_blue "Creating agents/personal/src/capabilities/document.py..."
create_file_heredoc "agents/personal/src/capabilities/document.py" << 'EOF'
"""
Document capability for the personal agent.

This module implements the capability for retrieving documents from
the personal knowledge base.
"""
import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from fastmcp.tools import MCPTool
import backoff

# Add the base agent module to the Python path
base_path = os.path.join(os.path.dirname(__file__), "../../../../base/src")
sys.path.append(os.path.abspath(base_path))

# Import from base agent
from capabilities import Capability
from knowledge import get_knowledge_base

class DocumentInput(BaseModel):
    """Input model for the get document capability."""
    document_id: str = Field(..., description="ID of the document to retrieve")
    include_content: bool = Field(True, description="Whether to include the full content")

class GetDocumentCapability(Capability):
    """
    Capability for retrieving documents from the knowledge base.
    
    This capability allows fetching specific documents by ID, optionally
    including their full content.
    """
    
    def __init__(self):
        """Initialize the get document capability."""
        super().__init__(
            name="get_document",
            description="Retrieve a document from the knowledge base by ID"
        )
        
        # Initialize the knowledge base connection
        self.knowledge_base = get_knowledge_base()
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the get document capability.
        
        Args:
            parameters: Parameters for the capability
                - document_id: ID of the document to retrieve
                - include_content: Whether to include the full content
            
        Returns:
            The requested document
        """
        try:
            # Parse and validate input
            doc_input = DocumentInput(
                document_id=parameters.get("document_id", ""),
                include_content=parameters.get("include_content", True)
            )
            
            logger.info(f"Retrieving document: {doc_input.document_id}")
            
            # Retrieve the document
            document = await self.knowledge_base.retrieve_document(doc_input.document_id)
            
            # Filter content if requested
            if not doc_input.include_content and "content" in document:
                document["content"] = "[Content excluded]"
                
            logger.info(f"Retrieved document: {document.get('title', 'Unknown')}")
            
            return document
            
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return {
                "error": str(e),
                "document_id": parameters.get("document_id", ""),
                "message": "Failed to retrieve document"
            }
EOF

# Create graph capability
print_blue "Creating agents/personal/src/capabilities/graph.py..."
create_file_heredoc "agents/personal/src/capabilities/graph.py" << 'EOF'
"""
Knowledge graph capability for the personal agent.

This module implements the capability for querying the knowledge graph
to find relationships between entities.
"""
import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from fastmcp.tools import MCPTool
import backoff

# Add the base agent module to the Python path
base_path = os.path.join(os.path.dirname(__file__), "../../../../base/src")
sys.path.append(os.path.abspath(base_path))

# Import from base agent
from capabilities import Capability

class Entity(BaseModel):
    """Model representing an entity in the knowledge graph."""
    id: str = Field(..., description="Unique identifier for the entity")
    name: str = Field(..., description="Name of the entity")
    type: str = Field(..., description="Type of the entity")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity properties")

class Relationship(BaseModel):
    """Model representing a relationship in the knowledge graph."""
    id: str = Field(..., description="Unique identifier for the relationship")
    source_id: str = Field(..., description="ID of the source entity")
    target_id: str = Field(..., description="ID of the target entity")
    type: str = Field(..., description="Type of the relationship")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Relationship properties")

class GraphQueryInput(BaseModel):
    """Input model for the knowledge graph query capability."""
    query: str = Field(..., description="Natural language query")
    entity_types: List[str] = Field(default_factory=list, description="Entity types to include")
    relationship_types: List[str] = Field(default_factory=list, description="Relationship types to include")
    max_hops: int = Field(2, description="Maximum number of relationship hops")

class QueryKnowledgeGraphCapability(Capability):
    """
    Capability for querying the knowledge graph.
    
    This capability allows querying the knowledge graph using natural language
    to find relationships between entities.
    """
    
    def __init__(self):
        """Initialize the knowledge graph query capability."""
        super().__init__(
            name="query_knowledge_graph",
            description="Query the knowledge graph to find relationships between entities"
        )
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the knowledge graph query capability.
        
        Args:
            parameters: Parameters for the capability
                - query: Natural language query
                - entity_types: Entity types to include
                - relationship_types: Relationship types to include
                - max_hops: Maximum number of relationship hops
            
        Returns:
            Entities and relationships matching the query
        """
        try:
            # Parse and validate input
            graph_input = GraphQueryInput(
                query=parameters.get("query", ""),
                entity_types=parameters.get("entity_types", []),
                relationship_types=parameters.get("relationship_types", []),
                max_hops=parameters.get("max_hops", 2)
            )
            
            logger.info(f"Querying knowledge graph: {graph_input.query}")
            
            # TODO: Implement actual knowledge graph query
            # For now, returning placeholder data
            
            # Mock entities
            entities = [
                Entity(
                    id="entity-1",
                    name="GraphRAG",
                    type="Concept",
                    properties={"description": "Graph-based retrieval-augmented generation"}
                ),
                Entity(
                    id="entity-2",
                    name="Knowledge Graph",
                    type="Concept",
                    properties={"description": "A graph-structured knowledge representation"}
                ),
                Entity(
                    id="entity-3",
                    name="Vector Database",
                    type="Technology",
                    properties={"description": "Database optimized for vector similarity search"}
                )
            ]
            
            # Mock relationships
            relationships = [
                Relationship(
                    id="rel-1",
                    source_id="entity-1",
                    target_id="entity-2",
                    type="USES",
                    properties={"strength": 0.9}
                ),
                Relationship(
                    id="rel-2",
                    source_id="entity-1",
                    target_id="entity-3",
                    type="COMBINES_WITH",
                    properties={"strength": 0.8}
                )
            ]
            
            logger.info(f"Found {len(entities)} entities and {len(relationships)} relationships")
            
            return {
                "query": graph_input.query,
                "entities": [e.dict() for e in entities],
                "relationships": [r.dict() for r in relationships],
                "metadata": {
                    "max_hops": graph_input.max_hops,
                    "filtered_entity_types": graph_input.entity_types,
                    "filtered_relationship_types": graph_input.relationship_types
                }
            }
            
        except Exception as e:
            logger.error(f"Error querying knowledge graph: {str(e)}")
            return {
                "error": str(e),
                "query": parameters.get("query", ""),
                "entities": [],
                "relationships": [],
                "message": "Failed to query knowledge graph"
            }
EOF

# Create Supabase migration file
print_blue "Creating supabase/migrations/01_initial_schema.sql..."
create_file_heredoc "supabase/migrations/01_initial_schema.sql" << 'EOF'
-- Initial schema for the Second Me multi-agent system
-- To be run as a Supabase migration

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Schema for agent orchestration
CREATE SCHEMA IF NOT EXISTS orchestration;

-- Agent registry table
CREATE TABLE orchestration.agents (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    endpoint TEXT NOT NULL,
    capabilities JSONB,
    metadata JSONB,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ
);

-- Create index on agent capabilities for faster lookup
CREATE INDEX agents_capabilities_idx ON orchestration.agents USING GIN (capabilities);

-- Workflow definitions table
CREATE TABLE orchestration.workflows (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on workflow tags for faster filtering
CREATE INDEX workflows_tags_idx ON orchestration.workflows USING GIN (tags array_ops);

-- Workflow execution history table
CREATE TABLE orchestration.workflow_executions (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES orchestration.workflows(id),
    status TEXT NOT NULL DEFAULT 'pending',
    input_variables JSONB,
    results JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error TEXT
);

-- Schema for knowledge base
CREATE SCHEMA IF NOT EXISTS knowledge;

-- Documents table
CREATE TABLE knowledge.documents (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create vector index for similarity search
CREATE INDEX documents_embedding_idx ON knowledge.documents USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

-- Knowledge graph entities table
CREATE TABLE knowledge.entities (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    properties JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indices for entity lookup
CREATE INDEX entities_name_idx ON knowledge.entities (name);
CREATE INDEX entities_type_idx ON knowledge.entities (type);
CREATE INDEX entities_embedding_idx ON knowledge.entities USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

-- Knowledge graph relationships table
CREATE TABLE knowledge.relationships (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES knowledge.entities(id) ON DELETE CASCADE,
    target_id UUID REFERENCES knowledge.entities(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    properties JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indices for relationship lookup
CREATE INDEX relationships_source_idx ON knowledge.relationships (source_id);
CREATE INDEX relationships_target_idx ON knowledge.relationships (target_id);
CREATE INDEX relationships_type_idx ON knowledge.relationships (type);

-- Function to search documents by vector similarity
CREATE OR REPLACE FUNCTION knowledge.search_documents(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.title,
        d.content,
        d.metadata,
        1 - (d.embedding <-> query_embedding) AS similarity
    FROM knowledge.documents d
    WHERE 1 - (d.embedding <-> query_embedding) > match_threshold
    ORDER BY d.embedding <-> query_embedding
    LIMIT match_count;
END;
$;

-- Function to find paths in the knowledge graph
CREATE OR REPLACE FUNCTION knowledge.find_paths(
    start_entity_id UUID,
    end_entity_id UUID,
    max_hops INT DEFAULT 3
)
RETURNS TABLE (
    path_entities UUID[],
    path_relationships UUID[],
    path_length INT
)
LANGUAGE plpgsql
AS $
BEGIN
    -- Implementation would use a graph traversal algorithm
    -- This is a placeholder that would be replaced with a proper implementation
    RETURN QUERY SELECT 
        ARRAY[start_entity_id, end_entity_id]::UUID[] AS path_entities,
        ARRAY[]::UUID[] AS path_relationships,
        1 AS path_length
    LIMIT 1;
END;
$;

-- Function to update entity embeddings
CREATE OR REPLACE FUNCTION knowledge.update_entity_embedding(
    entity_id UUID,
    new_embedding VECTOR(1536)
)
RETURNS VOID
LANGUAGE plpgsql
AS $
BEGIN
    UPDATE knowledge.entities
    SET embedding = new_embedding, updated_at = NOW()
    WHERE id = entity_id;
END;
$;

-- Create row-level security policies
ALTER TABLE orchestration.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE orchestration.workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE orchestration.workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge.entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge.relationships ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY orchestration_agents_policy ON orchestration.agents
    FOR ALL TO authenticated USING (true);

CREATE POLICY orchestration_workflows_policy ON orchestration.workflows
    FOR ALL TO authenticated USING (true);

CREATE POLICY orchestration_workflow_executions_policy ON orchestration.workflow_executions
    FOR ALL TO authenticated USING (true);

CREATE POLICY knowledge_documents_policy ON knowledge.documents
    FOR ALL TO authenticated USING (true);

CREATE POLICY knowledge_entities_policy ON knowledge.entities
    FOR ALL TO authenticated USING (true);

CREATE POLICY knowledge_relationships_policy ON knowledge.relationships
    FOR ALL TO authenticated USING (true);
EOF

# Create a master script to create everything
print_blue "Creating master-create-project.sh..."
create_file_heredoc "../master-create-project.sh" << 'EOF'
#!/bin/bash
# Master script to create the entire Second Me project structure

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_green() {
    echo -e "${GREEN}$1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}$1${NC}"
}

print_red() {
    echo -e "${RED}$1${NC}"
}

print_blue() {
    echo -e "${BLUE}$1${NC}"
}

# Create the project directory
PROJECT_DIR="second-me-project"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

print_green "Creating Second Me project in $(pwd)"

# Run the first script to create the basic structure
print_blue "Running create-full-project.sh..."
bash ../create-full-project.sh

# Run the second script to create Python files
print_blue "Running create-python-files.sh..."
bash ../create-python-files.sh

# Make scripts executable
chmod +x scripts/setup.sh
chmod +x scripts/deploy.sh

print_green "All project files have been created successfully!"
print_yellow "Next steps:"
print_yellow "1. Edit .env with your Supabase credentials"
print_yellow "2. Run ./scripts/setup.sh to set up the environment"
print_yellow "3. Run docker-compose up -d to start the system"

cd ..
print_green "Done! Your project is now ready in the $PROJECT_DIR directory."
EOF

chmod +x ../master-create-project.sh

print_green "Creation of Python source files complete!"
print_green "Created master script: ../master-create-project.sh"
print_yellow "Run this script to create the entire project structure: bash ../master-create-project.sh"