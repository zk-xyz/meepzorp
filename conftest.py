"""
Pytest configuration file.
"""
import os
import sys

# Add the project root directory to the Python path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)
# Ensure creative_director package is discoverable when running tests without installation
CREATIVE_DIR = os.path.join(ROOT_DIR, "agents", "creative_director", "src")
sys.path.insert(0, CREATIVE_DIR)

