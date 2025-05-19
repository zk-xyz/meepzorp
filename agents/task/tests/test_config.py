import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
TEST_CONFIG = {
    "SUPABASE_URL": os.getenv("TEST_SUPABASE_URL", "http://localhost:54321"),
    "SUPABASE_KEY": os.getenv("TEST_SUPABASE_KEY", "test-key"),
    "AGENT_PORT": os.getenv("TEST_AGENT_PORT", "8003"),
    "ORCHESTRATION_URL": os.getenv("TEST_ORCHESTRATION_URL", "http://localhost:9810"),
    "LOG_LEVEL": "DEBUG"
}

# Test data
TEST_TASK = {
    "title": "Test Task",
    "description": "This is a test task",
    "status": "TODO",
    "priority": 1,
    "due_date": "2025-04-20T00:00:00Z",
    "assignee": "test-user",
    "project_id": "00000000-0000-0000-0000-000000000000",
    "tags": ["test", "example"]
}

# Test fixtures
TEST_FIXTURES = {
    "tasks": [
        TEST_TASK,
        {
            "title": "Another Test Task",
            "description": "This is another test task",
            "status": "IN_PROGRESS",
            "priority": 2,
            "due_date": "2025-04-25T00:00:00Z",
            "assignee": "test-user",
            "project_id": "00000000-0000-0000-0000-000000000000",
            "tags": ["test", "example"]
        }
    ]
} 