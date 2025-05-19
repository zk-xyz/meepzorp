#!/bin/bash
# Script to rename "second-me-project" to "meepzorp" in all files

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

# Check if we're in the mcp-implementation directory
if [ ! -d "second-me-project" ]; then
    print_red "This script should be run from the mcp-implementation directory (where the second-me-project directory is)."
    print_yellow "Current directory: $(pwd)"
    exit 1
fi

print_green "Renaming 'second-me-project' to 'meepzorp' in all files..."

# Rename the directory itself
print_blue "Renaming directory..."
mv second-me-project meepzorp

# Navigate to the meepzorp directory
cd meepzorp

# Find all files and update references
print_blue "Updating references in files..."

# Update references in all text files (excluding binary files and some specific directories)
find . -type f -not -path "*/\.*" -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/logs/*" -not -path "*/data/*" | xargs grep -l "second-me" | while read file; do
    print_yellow "Updating file: $file"
    # Replace references with sed
    sed -i 's/second-me-project/meepzorp/g' "$file"
    sed -i 's/second-me/meepzorp/g' "$file"
    sed -i 's/Second Me/Meepzorp/g' "$file"
    sed -i 's/Second-Me/Meepzorp/g' "$file"
done

# Update Docker container names in docker-compose.yml
print_blue "Updating Docker container names..."
sed -i 's/second-me-orchestration/meepzorp-orchestration/g' docker-compose.yml
sed -i 's/second-me-base-agent/meepzorp-base-agent/g' docker-compose.yml
sed -i 's/second-me-personal-agent/meepzorp-personal-agent/g' docker-compose.yml
sed -i 's/second-me-redis/meepzorp-redis/g' docker-compose.yml
sed -i 's/second-me-ui/meepzorp-ui/g' docker-compose.yml
sed -i 's/second-me-network/meepzorp-network/g' docker-compose.yml

# Update Docker volume names
print_blue "Updating Docker volume names..."
sed -i 's/orchestration_data/meepzorp_orchestration_data/g' docker-compose.yml
sed -i 's/base_agent_data/meepzorp_base_agent_data/g' docker-compose.yml
sed -i 's/personal_agent_data/meepzorp_personal_agent_data/g' docker-compose.yml
sed -i 's/redis_data/meepzorp_redis_data/g' docker-compose.yml
sed -i 's/ui_node_modules/meepzorp_ui_node_modules/g' docker-compose.yml

# Update README.md
print_blue "Updating README.md..."
if [ -f "README.md" ]; then
    sed -i 's/# Second Me: Multi-Agent Claude Environment/# Meepzorp: Multi-Agent Claude Environment/g' README.md
    sed -i 's/The Second Me project/The Meepzorp project/g' README.md
    sed -i 's/git clone https:\/\/github.com\/yourusername\/second-me-project.git/git clone https:\/\/github.com\/yourusername\/meepzorp.git/g' README.md
    sed -i 's/cd second-me-project/cd meepzorp/g' README.md
fi

# Update any GitHub workflow files
if [ -d ".github/workflows" ]; then
    print_blue "Updating GitHub workflow files..."
    find .github/workflows -type f -name "*.yml" | xargs sed -i 's/second-me/meepzorp/g'
fi

# Update the Python imports in source files (if they reference the project name)
print_blue "Updating Python imports..."
find . -name "*.py" | xargs grep -l "second-me" | while read file; do
    print_yellow "Updating imports in: $file"
    sed -i 's/from second_me/from meepzorp/g' "$file"
    sed -i 's/import second_me/import meepzorp/g' "$file"
done

# Go back to the parent directory
cd ..

print_green "Renaming complete! Your project is now called 'meepzorp'."
print_yellow "Next steps:"
print_yellow "1. Navigate to the meepzorp directory: cd meepzorp"
print_yellow "2. Configure your .env file: cp .env.example .env"
print_yellow "3. Run the setup script: ./scripts/setup.sh"
print_yellow "4. Start the system: docker-compose up -d"