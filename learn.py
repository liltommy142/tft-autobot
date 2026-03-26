#!/usr/bin/env python
"""
Meta Learner - Continuous learning system entry point

This script starts the autonomous meta learning system.
Usage: python learn.py
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from meta_learner import MetaLearner
from config import RIOT_API_KEY

if __name__ == "__main__":
    if not RIOT_API_KEY:
        print("ERROR: RIOT_API_KEY not set in .env file")
        sys.exit(1)
    
    learner = MetaLearner(RIOT_API_KEY)
    learner.learn_from_matches()
