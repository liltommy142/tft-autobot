#!/usr/bin/env python
"""
Fetch Meta - Fetch metadata from online sources entry point

This script fetches meta data from online sources (Riot DD, tactics.tools, etc).
Usage: python fetch_meta.py
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fetch_meta import main

if __name__ == "__main__":
    main()
