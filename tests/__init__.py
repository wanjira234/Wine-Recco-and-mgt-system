# This file ensures Python treats the directory as a package
# You can add any package-level imports or configurations here
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))