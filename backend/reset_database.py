#!/usr/bin/env python
"""
Database Reset Wrapper Script

This script is a simple wrapper to make it easier to run the database reset script
from the backend directory.

Usage:
    python reset_database.py [--reload] [--dump]
"""

import sys
from scripts.reset_db import main

if __name__ == "__main__":
    main()
