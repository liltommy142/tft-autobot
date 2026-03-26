"""
logger.py - Game logging functionality
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List

from config import LOGS_DIR, LOG_FILE

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)


def log_game(entry: Dict[str, Any]) -> None:
    """Append a game record to logs/games.jsonl.
    
    Adds timestamp if missing and writes as JSONL format.
    
    Args:
        entry: Game record dict with game data
        
    Raises:
        IOError: If write to log file fails
    """
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except IOError as e:
        raise IOError(f"Failed to write to log file {LOG_FILE}: {e}")


def read_logs(limit: int = 1000) -> List[Dict[str, Any]]:
    """Read up to `limit` most recent game records.
    
    Reads JSONL file in reverse order (most recent first).
    Handles malformed JSON lines gracefully by skipping them.
    
    Args:
        limit: Maximum number of records to read
        
    Returns:
        List of game record dicts (most recent first)
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
    except IOError as e:
        print(f"Warning: Failed to read log file {LOG_FILE}: {e}")
        return []
    
    out: List[Dict[str, Any]] = []
    for line in lines:
        try:
            record = json.loads(line)
            out.append(record)
        except json.JSONDecodeError:
            # Skip malformed lines
            continue
    
    return out
