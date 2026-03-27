#!/usr/bin/env python
"""
Meta Learner Scheduler - Automation entry point

This script schedules meta learning tasks.
Usage: python schedule.py [mode] [interval] [check_interval]
  mode: 'once' | 'test' | 'daemon'
  interval: Hours between learning cycles (default: 6)
  check_interval: Seconds between checks in daemon mode (default: 60)
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from learner_scheduler import LearnerScheduler
from config import RIOT_API_KEY

if __name__ == "__main__":
    if not RIOT_API_KEY:
        print("ERROR: RIOT_API_KEY not set in .env file")
        sys.exit(1)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    check_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    
    scheduler = LearnerScheduler(interval_hours=interval)
    
    if mode == "once":
        scheduler.run_learning()
    elif mode == "test":
        scheduler.run_learning(dry_run=True)
    elif mode == "daemon":
        scheduler.run_continuous(check_interval_seconds=check_interval)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
