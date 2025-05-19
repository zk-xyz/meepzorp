#!/bin/bash
# Script to create all directories and files for the Second Me multi-agent project
# This script populates all files with their content

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

# Create a file with content
create_file() {
    local file_path=$1
    local content=$2
    
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$file_path")"
    
    # Create file with content
    echo "$content" > "$file_path"
    print_yellow "Created file: $file_path"
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

# Main project directory
PROJECT_DIR="second-me-project"

print_green "Creating project structure for $PROJECT_DIR..."

# Create the main project directory
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Create all the required directories
print_yellow "Creating directory structure..."

mkdir -p .github/workflows
mkdir -p docs/architecture
mkdir -p docs/api
mkdir -p docs/guides
mkdir -p orchestration/src
mkdir -p orchestration/tests
mkdir -p orchestration/config
mkdir -p agents/base/src
mkdir -p agents/base/tests
mkdir -p agents/personal/src/capabilities
mkdir -p agents/personal/tests
mkdir -p knowledge/processors
mkdir -p knowledge/graph
mkdir -p knowledge/embeddings
mkdir -p ui/src/components
mkdir -p ui/src/pages
mkdir -p supabase/migrations
mkdir -p supabase/functions
mkdir -p supabase/seed
mkdir -p scripts
mkdir -p logs
mkdir -p data/orchestration
mkdir -p data/personal_agent

print_green "Directory structure created successfully!"
print_blue "Creating files with content..."

# 1. .gitignore
create_file_heredoc ".gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
venv/
.venv/

# Docker
.docker/
docker-volumes/

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.sqlite
*.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
coverage/

# Distribution
dist/
build/

# Temporary files
tmp/
temp/

# Data files (consider if you want to include these)
data/
*.csv
*.json

# Supabase
.supabase/
EOF

# 2. README.md
create_file_heredoc "README.md" << 'EOF'
# Second Me: Multi-Agent Claude Environment

A system enabling multiple specialized Claude agents to collaborate on tasks through the Model Context Protocol (MCP).

## 🌟 Vision

The Second Me project creates an environment where:

- Multiple specialized Claude agents collaborate on complex tasks
- Each agent has specific capabilities and knowledge domains
- Agents share information through a standardized protocol
- Documentation is easily added to enhance agent capabilities
- Personalized agents reflect your knowledge and style
- The system is managed through a unified interface
- GitHub integration allows for version control and sharing

## 🏗️ Architecture

The system follows a modular architecture with these main components:

### Agent Orchestration System

Coordinates communication between specialized agents and manages workflows.

- Central MCP server that routes requests
- Agent registry for capability discovery
- Workflow definition and execution engine
- Context management system

### Specialized Agent Framework

Provides the foundation for creating domain-specific agents.

- Base agent template for extending
- Capability definition system
- Knowledge base connector
- Inter-agent communication protocol

### Knowledge Repository System

Stores and retrieves information for agent consumption.

- Vector database (Supabase with pgvector)
- Document processing pipeline
- Knowledge graph (GraphRAG approach)
- Documentation augmentation system

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 16+ (for UI)
- Supabase account

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/second-me-project.git
   cd second-me-project
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the system:
   ```bash
   docker-compose up -d
   ```

4. Access the management interface:
   ```
   http://localhost:3000
   ```

## 🧩 Components

### Orchestration

The orchestration service manages the agent ecosystem, routing requests and handling workflows.

### Base Agent

The foundation for all specialized agents, providing standard interfaces and communication protocols.

### Knowledge Repository

A combination of vector database and knowledge graph for storing and retrieving information.

### Management UI

A web interface for monitoring and managing the agent ecosystem.

## 📚 Documentation

Full documentation is available in the `docs/` directory:

- Architecture diagrams and descriptions
- API documentation
- User and developer guides

## 👥 Contributing

Contributions are welcome! Please check out our [contributing guidelines](CONTRIBUTING.md).

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [MCP (Model Context Protocol)](https://github.com/anthropics/anthropic-tools)
- [ElizaOS](link-to-elizaos)
- [ChromaDB](https://github.com/chroma-core/chroma)
EOF

# 3. docker-compose.yml
create_file_heredoc "docker-compose.yml" << 'EOF'
version: '3.8'

services:
  # Orchestration service
  orchestration:
    build:
      context: ./orchestration
      dockerfile: Dockerfile
    container_name: second-me-orchestration
    restart: unless-stopped
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - MCP_PORT=8000
      - LOG_LEVEL=info
    ports:
      - "${ORCHESTRATION_PORT:-8000}:8000"
    volumes:
      - ./orchestration:/app
      - orchestration_data:/data
    networks:
      - second-me-network
    depends_on:
      - redis

  # Base agent template (used for development/testing)
  base-agent:
    build:
      context: ./agents/base
      dockerfile: Dockerfile
    container_name: second-me-base-agent
    restart: unless-stopped
    environment:
      - ORCHESTRATION_URL=http://orchestration:8000
      - MCP_PORT=8001
      - LOG_LEVEL=info
    ports:
      - "${BASE_AGENT_PORT:-8001}:8001"
    volumes:
      - ./agents/base:/app
      - base_agent_data:/data
    networks:
      - second-me-network
    depends_on:
      - orchestration

  # Personal knowledge agent
  personal-agent:
    build:
      context: ./agents/personal
      dockerfile: Dockerfile
    container_name: second-me-personal-agent
    restart: unless-stopped
    environment:
      - ORCHESTRATION_URL=http://orchestration:8000
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - MCP_PORT=8002
      - LOG_LEVEL=info
    ports:
      - "${PERSONAL_AGENT_PORT:-8002}:8002"
    volumes:
      - ./agents/personal:/app
      - personal_agent_data:/data
    networks:
      - second-me-network
    depends_on:
      - orchestration

  # Redis for caching and pub/sub
  redis:
    image: redis:alpine
    container_name: second-me-redis
    restart: unless-stopped
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    networks:
      - second-me-network

  # UI Management interface
  ui:
    build:
      context: ./ui
      dockerfile: Dockerfile
    container_name: second-me-ui
    restart: unless-stopped
    environment:
      - ORCHESTRATION_URL=http://orchestration:8000
      - NODE_ENV=production
    ports:
      - "${UI_PORT:-3000}:3000"
    volumes:
      - ./ui:/app
      - ui_node_modules:/app/node_modules
    networks:
      - second-me-network
    depends_on:
      - orchestration

networks:
  second-me-network:
    driver: bridge

volumes:
  orchestration_data:
  base_agent_data:
  personal_agent_data:
  redis_data:
  ui_node_modules:
EOF

# 4. .env.example
create_file_heredoc ".env.example" << 'EOF'
# Environment configuration for Second Me Multi-Agent System
# Copy this file to .env and fill in the values

# Orchestration Service
ORCHESTRATION_PORT=8000
LOG_LEVEL=info

# Agent Ports
BASE_AGENT_PORT=8001
PERSONAL_AGENT_PORT=8002

# Redis Cache
REDIS_PORT=6379

# UI
UI_PORT=3000

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-key

# Knowledge Base
USE_SUPABASE=true
KNOWLEDGE_BASE_CONNECTION=

# Agent Endpoint Configuration
# In production, set this to the externally accessible hostname
AGENT_HOST=localhost
EOF

# 5. GitHub Actions Workflow
create_file_heredoc ".github/workflows/docker-build.yml" << 'EOF'
name: Docker Build and Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest flake8
        pip install -r orchestration/requirements.txt
        pip install -r agents/base/requirements.txt
        pip install -r agents/personal/requirements.txt
        
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        
    - name: Test with pytest
      run: |
        pytest
        
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Build orchestration image
      uses: docker/build-push-action@v4
      with:
        context: ./orchestration
        push: false
        tags: second-me-orchestration:latest
        
    - name: Build base agent image
      uses: docker/build-push-action@v4
      with:
        context: ./agents/base
        push: false
        tags: second-me-base-agent:latest
        
    - name: Build personal agent image
      uses: docker/build-push-action@v4
      with:
        context: ./agents/personal
        push: false
        tags: second-me-personal-agent:latest
EOF

# Continue with more files...
print_blue "Creating orchestration files..."

# 6. Orchestration Dockerfile
create_file_heredoc "orchestration/Dockerfile" << 'EOF'
FROM python:3.11-slim-bookworm AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 7. Orchestration requirements.txt
create_file_heredoc "orchestration/requirements.txt" << 'EOF'
fastapi==0.103.1
uvicorn==0.23.2
pydantic==2.3.0
httpx==0.24.1
fastmcp==0.1.0
python-dotenv==1.0.0
redis==5.0.0
supabase==1.0.3
asyncpg==0.28.0
pyyaml==6.0.1
loguru==0.7.0
backoff==2.2.1
websockets==11.0.3
jinja2==3.1.2
jsonschema==4.19.0
cryptography==41.0.3
pytest==7.4.2
EOF

# Continue with all the Python files...

print_blue "Creating orchestration source files..."

# Due to the length constraints, I'll create just a few key files here
# You would need to continue this pattern for all files

create_file_heredoc "orchestration/src/main.py" << 'EOF'
"""
Main entry point for the orchestration MCP server.
This module initializes the FastMCP server and registers all available tools.
"""
import os
import logging
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastmcp import FastMCP
from fastmcp.tools import MCPTool
from dotenv import load_dotenv
from loguru import logger

from .registry import AgentRegistryTool, AgentDiscoveryTool
from .router import RouteRequestTool
from .workflows import ExecuteWorkflowTool, CreateWorkflowTool, ListWorkflowsTool

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.remove()
logger.add(
    "logs/orchestration.log",
    rotation="10 MB",
    level=logging_level,
    format="{time} {level} {message}",
)
logger.add(lambda msg: print(msg), level=logging_level)

# Create the FastMCP application
mcp = FastMCP("AgentOrchestration")
app = mcp.get_app()

# Configure CORS
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to responses."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Register tools
mcp.add_tool(AgentRegistryTool())
mcp.add_tool(AgentDiscoveryTool())
mcp.add_tool(RouteRequestTool())
mcp.add_tool(ExecuteWorkflowTool())
mcp.add_tool(CreateWorkflowTool())
mcp.add_tool(ListWorkflowsTool())

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "orchestration",
    }

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint showing basic service information."""
    return {
        "name": "Agent Orchestration Service",
        "description": "Coordinates communication between specialized agents and manages workflows.",
        "documentation": "/docs",
    }

# Error handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_PORT", 8000))
    logger.info(f"Starting orchestration MCP server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
EOF

# Base agent files
print_blue "Creating base agent files..."

create_file_heredoc "agents/base/Dockerfile" << 'EOF'
FROM python:3.11-slim-bookworm AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Run the application
CMD ["uvicorn", "src.base_agent:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

create_file_heredoc "agents/base/requirements.txt" << 'EOF'
fastapi==0.103.1
uvicorn==0.23.2
pydantic==2.3.0
httpx==0.24.1
fastmcp==0.1.0
python-dotenv==1.0.0
supabase==1.0.3
asyncpg==0.28.0
pyyaml==6.0.1
loguru==0.7.0
backoff==2.2.1
websockets==11.0.3
jsonschema==4.19.0
cryptography==41.0.3
pytest==7.4.2
EOF

# Additional key files for the setup, deployment scripts, etc.
print_blue "Creating script files..."

create_file_heredoc "scripts/setup.sh" << 'EOF'
#!/bin/bash
# Setup script for the Second Me multi-agent system

# Exit on error
set -e

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Check for prerequisites
check_prerequisites() {
    print_green "Checking prerequisites..."
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        print_red "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check for Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_red "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        print_red "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    print_green "All prerequisites are installed."
}

# Setup environment
setup_environment() {
    print_green "Setting up environment..."
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_yellow "Creating .env file from example..."
        cp .env.example .env
        print_yellow "Please edit the .env file with your configuration."
    else
        print_yellow ".env file already exists. Skipping..."
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p data/orchestration
    mkdir -p data/personal_agent
    
    print_green "Environment setup complete."
}

# Setup Python virtual environments
setup_python_venv() {
    print_green "Setting up Python virtual environments..."
    
    # Create virtual environment for orchestration
    if [ ! -d "orchestration/venv" ]; then
        print_yellow "Creating virtual environment for orchestration..."
        python3 -m venv orchestration/venv
        
        print_yellow "Installing orchestration dependencies..."
        orchestration/venv/bin/pip install -r orchestration/requirements.txt
    else
        print_yellow "Orchestration virtual environment already exists. Skipping..."
    fi
    
    # Create virtual environment for base agent
    if [ ! -d "agents/base/venv" ]; then
        print_yellow "Creating virtual environment for base agent..."
        python3 -m venv agents/base/venv
        
        print_yellow "Installing base agent dependencies..."
        agents/base/venv/bin/pip install -r agents/base/requirements.txt
    else
        print_yellow "Base agent virtual environment already exists. Skipping..."
    fi
    
    # Create virtual environment for personal agent
    if [ ! -d "agents/personal/venv" ]; then
        print_yellow "Creating virtual environment for personal agent..."
        python3 -m venv agents/personal/venv
        
        print_yellow "Installing personal agent dependencies..."
        agents/personal/venv/bin/pip install -r agents/personal/requirements.txt
    else
        print_yellow "Personal agent virtual environment already exists. Skipping..."
    fi
    
    print_green "Python virtual environments setup complete."
}

# Build Docker images
build_docker_images() {
    print_green "Building Docker images..."
    
    docker-compose build
    
    print_green "Docker images built successfully."
}

# Main function
main() {
    print_green "Setting up the Second Me multi-agent system..."
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Setup Python virtual environments
    setup_python_venv
    
    # Build Docker images
    build_docker_images
    
    print_green "Setup complete! You can now start the system with 'docker-compose up -d'"
}

# Run main function
main
EOF

create_file_heredoc "scripts/deploy.sh" << 'EOF'
#!/bin/bash
# Deployment script for the Second Me multi-agent system

# Exit on error
set -e

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Check for prerequisites
check_prerequisites() {
    print_green "Checking prerequisites..."
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        print_red "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check for Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_red "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_red ".env file does not exist. Please run setup.sh first."
        exit 1
    fi
    
    print_green "All prerequisites are available."
}

# Pull latest changes
pull_latest() {
    print_green "Pulling latest changes from repository..."
    
    git pull
    
    print_green "Latest changes pulled successfully."
}

# Build Docker images
build_images() {
    print_green "Building Docker images..."
    
    docker-compose build
    
    print_green "Docker images built successfully."
}

# Deploy the system
deploy_system() {
    print_green "Deploying the system..."
    
    # Stop any running containers
    print_yellow "Stopping running containers..."
    docker-compose down
    
    # Start the system
    print_yellow "Starting the system..."
    docker-compose up -d
    
    print_green "System deployed successfully."
}

# Show system status
show_status() {
    print_green "System status:"
    
    docker-compose ps
    
    print_yellow "Logs can be viewed with 'docker-compose logs -f'"
}

# Main function
main() {
    print_green "Deploying the Second Me multi-agent system..."
    
    # Check prerequisites
    check_prerequisites
    
    # Pull latest changes
    pull_latest
    
    # Build Docker images
    build_images
    
    # Deploy the system
    deploy_system
    
    # Show system status
    show_status
    
    print_green "Deployment complete!"
}

# Run main function
main
EOF

# Create a README for next steps
create_file_heredoc "NEXT_STEPS.md" << 'EOF'
# Next Steps for Your Multi-Agent System Project

Congratulations! You've set up the basic structure for your Second Me multi-agent system. Here are the next steps to fully implement the system:

## 1. Complete Missing Files

The script created some key files, but not all of them due to length constraints. You'll need to complete these files:

- `orchestration/src/registry.py`
- `orchestration/src/router.py`
- `orchestration/src/workflows.py`
- `agents/base/src/base_agent.py`
- `agents/base/src/capabilities.py`
- `agents/base/src/knowledge.py`
- `agents/personal/src/personal_agent.py`
- `agents/personal/src/capabilities/search.py`
- `agents/personal/src/capabilities/document.py`
- `agents/personal/src/capabilities/graph.py`
- `supabase/migrations/01_initial_schema.sql`

You can copy these files from the Claude conversation or implement them according to your requirements.

## 2. Configure Supabase

1. Create a new Supabase project (if you don't have one)
2. Run the database migrations in `supabase/migrations/`
3. Update your `.env` file with the Supabase connection details

## 3. Make Scripts Executable

```bash
chmod +x scripts/setup.sh
chmod +x scripts/deploy.sh
```

## 4. Run the Setup Script

```bash
./scripts/setup.sh
```

## 5. Start the System

```bash
docker-compose up -d
```

## 6. Test the API

Access the orchestration API at http://localhost:8000/docs

## 7. Expand the System

- Add more specialized agents
- Enhance the knowledge graph implementation
- Develop the UI for system management
- Implement advanced workflow patterns

## Reference Documentation

- [MCP (Model Context Protocol)](https://github.com/anthropics/anthropic-tools)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.io/docs)
- [Docker Documentation](https://docs.docker.com/)

Good luck with your multi-agent system!
EOF

# Make script files executable
chmod +x scripts/setup.sh
chmod +x scripts/deploy.sh

print_green "Project structure setup complete!"
print_yellow "NOTE: Not all files have been fully created due to length constraints."
print_green "Check NEXT_STEPS.md for instructions on completing the project."