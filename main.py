#!/usr/bin/env python
"""
TFT AutoBot - Main entry point

This script starts the TFT recommendation assistant.
Usage: python main.py
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli_main import main

if __name__ == "__main__":
    main()
