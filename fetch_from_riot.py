#!/usr/bin/env python
"""
Fetch from Riot - Fetch TFT match data from Riot API entry point

This script fetches recent matches for a summoner and appends to logs/games.jsonl

Usage: python fetch_from_riot.py SUMMONER_NAME [PLATFORM]

Requirements:
  - RIOT_API_KEY in .env file or environment
  - Internet connection

Example:
  python fetch_from_riot.py "PlayerName" vn1
  python fetch_from_riot.py "PlayerName"  # Auto-detect platform
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fetch_from_riot import main

if __name__ == "__main__":
    main()
