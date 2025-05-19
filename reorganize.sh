#!/bin/bash

# Exit on error
set -e

echo "Starting directory reorganization..."

# Create temporary directory for reorganization
mkdir -p /tmp/meepzorp_reorg

# Move everything from nested meepzorp directories to tmp
echo "Moving files from nested directories..."
if [ -d "meepzorp/meepzorp" ]; then
    cp -r meepzorp/meepzorp/* /tmp/meepzorp_reorg/
fi

# Move docs to the correct location
echo "Consolidating docs..."
mkdir -p /tmp/meepzorp_reorg/docs
if [ -d "meepzorp/docs" ]; then
    cp -r meepzorp/docs/* /tmp/meepzorp_reorg/docs/
fi
if [ -d "meepzorp/meepzorp/docs" ]; then
    cp -r meepzorp/meepzorp/docs/* /tmp/meepzorp_reorg/docs/
fi

# Move core files to tmp if they exist in nested directories
echo "Moving core files..."
for file in .env .env.example requirements.txt README.md docker-compose.yml .gitignore; do
    if [ -f "meepzorp/$file" ]; then
        cp "meepzorp/$file" "/tmp/meepzorp_reorg/"
    fi
done

# Create new directory structure
echo "Creating new directory structure..."
mkdir -p /tmp/meepzorp_reorg/agents
mkdir -p /tmp/meepzorp_reorg/tests
mkdir -p /tmp/meepzorp_reorg/supabase
mkdir -p /tmp/meepzorp_reorg/ui

# Move agents if they exist
if [ -d "meepzorp/agents" ]; then
    cp -r meepzorp/agents/* /tmp/meepzorp_reorg/agents/
fi

# Move tests if they exist
if [ -d "meepzorp/tests" ]; then
    cp -r meepzorp/tests/* /tmp/meepzorp_reorg/tests/
fi

# Move supabase if it exists
if [ -d "meepzorp/supabase" ]; then
    cp -r meepzorp/supabase/* /tmp/meepzorp_reorg/supabase/
fi

# Move UI if it exists
if [ -d "meepzorp/ui" ]; then
    cp -r meepzorp/ui/* /tmp/meepzorp_reorg/ui/
fi

# Backup original meepzorp directory
echo "Creating backup..."
mv meepzorp meepzorp_backup_$(date +%Y%m%d_%H%M%S)

# Move reorganized structure to meepzorp
echo "Moving reorganized structure to final location..."
mkdir -p meepzorp
mv /tmp/meepzorp_reorg/* meepzorp/

# Cleanup
rm -rf /tmp/meepzorp_reorg

echo "Directory reorganization complete!"
echo "Original directory backed up as meepzorp_backup_*"
echo "Please verify the new structure and update any necessary import paths." 