#!/usr/bin/env python
"""
GUI entry point for TFT AutoBot

Usage: python gui.py
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui_main import main

if __name__ == "__main__":
    main()