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