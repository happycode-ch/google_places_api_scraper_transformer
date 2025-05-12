#!/usr/bin/env python3
"""
AI-driven development file
Purpose: Test script to verify that the virtual environment is set up correctly
Module: Google_Places_API_Scraper/test_env.py
Dependencies: All project dependencies
"""

import sys
import importlib
from typing import List, Dict, Tuple


def check_dependencies() -> Tuple[List[str], List[str]]:
    """
    Check if all required dependencies are installed.
    
    Returns:
        Tuple containing lists of successfully imported and failed imports
    """
    dependencies = [
        "requests",
        "dotenv",
        "click",
        "pandas",
        "streamlit",
        "pydeck"
    ]
    
    successful = []
    failed = []
    
    for dep in dependencies:
        try:
            if dep == "dotenv":
                # Special case for python-dotenv
                importlib.import_module("dotenv")
            else:
                importlib.import_module(dep)
            successful.append(dep)
        except ImportError:
            failed.append(dep)
    
    return successful, failed


def print_environment_info() -> None:
    """Print information about the Python environment."""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    successful, failed = check_dependencies()
    
    print("\nDependency Status:")
    print(f"✅ Successfully imported: {', '.join(successful)}")
    
    if failed:
        print(f"❌ Failed to import: {', '.join(failed)}")
    else:
        print("All dependencies successfully imported!")


if __name__ == "__main__":
    print("Google Places API Scraper - Environment Test")
    print("=" * 50)
    print_environment_info() 