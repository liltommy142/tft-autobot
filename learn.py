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
from config import RIOT_API_KEY, LEARNING_PLATFORM

if __name__ == "__main__":
    if not RIOT_API_KEY:
        print("Error: RIOT_API_KEY not set. Please create a .env file from .env.example "
              "and add your Riot API key.")
        sys.exit(1)
    
    learner = MetaLearner(platform=LEARNING_PLATFORM)
    learner.learn_from_matches()
