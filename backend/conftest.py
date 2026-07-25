# backend/tests/conftest.py
import sys
import os

# This adds the backend/ folder to Python's path so tests can find auditor.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))