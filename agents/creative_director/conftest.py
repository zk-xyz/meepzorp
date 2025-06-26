import os
import sys

# Ensure the src directory is on the path for local test execution
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(CURRENT_DIR, 'src')
sys.path.insert(0, SRC_DIR)

