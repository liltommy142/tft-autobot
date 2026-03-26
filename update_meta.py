#!/usr/bin/env python
"""
Update Meta - Metadata initialization entry point

This script initializes or updates metadata files.
Usage: python update_meta.py
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from update_meta import main

if __name__ == "__main__":
    main()
