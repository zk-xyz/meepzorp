#!/usr/bin/env python3
"""
Script to run SQL migrations against Supabase database.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_supabase_headers():
    """Get headers for Supabase API calls."""
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_key:
        raise ValueError("SUPABASE_KEY environment variable must be set")
    
    return {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def run_migration(migration_file: Path) -> None:
    """Run a single migration file."""
    logger.info(f"Running migration: {migration_file.name}")
    
    try:
        # Read migration SQL
        sql = migration_file.read_text()
        
        # Get Supabase URL and headers
        supabase_url = os.getenv("SUPABASE_URL")
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable must be set")
            
        headers = get_supabase_headers()
        
        # Call the Supabase SQL API
        response = requests.post(
            f"{supabase_url}/rest/v1/",
            headers=headers,
            json={"query": sql}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully applied migration: {migration_file.name}")
        else:
            logger.error(f"Failed to apply migration: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error applying migration {migration_file.name}: {str(e)}")
        sys.exit(1)

def main():
    """Main migration function."""
    # Load environment variables
    load_dotenv()
    
    try:
        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / "migrations"
        
        if not migrations_dir.exists():
            logger.error(f"Migrations directory not found: {migrations_dir}")
            sys.exit(1)
        
        # Get all .sql files
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.warning("No migration files found")
            sys.exit(0)
        
        # Run each migration
        for migration_file in migration_files:
            run_migration(migration_file)
            
        logger.info("All migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 