"""
fetch_from_riot.py - Fetch TFT match data from Riot API

Fetches recent matches for a summoner and appends to logs/games.jsonl

Usage:
  python fetch_from_riot.py SUMMONER_NAME [PLATFORM]

Requirements:
  - RIOT_API_KEY environment variable or .env file
  - Python requests library

Notes:
  - Respects Riot API rate limits (429 handling)
  - Supports 12 common platforms with auto-detection
"""
import os
import sys
import time
import json
from typing import Optional, List, Dict, Any

import requests

from config import (
    LOG_FILE, LOGS_DIR, RATE_LIMIT_DELAY, API_TIMEOUT, 
    MAX_RETRIES, MAX_RECENT_MATCHES, RIOT_API_KEY
)

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

if not RIOT_API_KEY:
    sys.exit("RIOT_API_KEY not set in .env or environment variables.")

HEADERS = {"X-Riot-Token": RIOT_API_KEY, "User-Agent": "tft-autobot/1.0"}

# Platform lists to try for auto-detect (common platforms)
PLATFORMS_TRY = [
    "vn1", "na1", "euw1", "eun1", "kr", "jp1", "oc1", "br1", "la1", "la2", "tr1", "ru"
]

# Minimal platform -> regional mapping for match endpoints
PLATFORM_TO_REGION: Dict[str, str] = {
    # Americas
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "oc1": "americas",
    # Europe
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
    # Asia
    "kr": "asia",
    "jp1": "asia",
    "vn1": "asia",
    "sg1": "asia",
    "ph2": "asia",
}


def riot_get(url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = MAX_RETRIES) -> Dict[str, Any]:
    """Make GET request to Riot API with rate limit handling.
    
    Args:
        url: API endpoint URL
        params: Query parameters
        max_retries: Maximum retry attempts
        
    Returns:
        JSON response data
        
    Raises:
        SystemExit: On persistent failure
    """
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=API_TIMEOUT)
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise SystemExit(f"Failed to GET {url}: {e}")
            time.sleep(1 + attempt)
            continue
        
        # Handle rate limiting
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", "1"))
            print(f"  Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after + 0.5)
            continue
        
        # Handle server errors
        if r.status_code >= 500:
            if attempt == max_retries - 1:
                raise SystemExit(f"Server error: {r.status_code}")
            time.sleep(1 + attempt)
            continue
        
        # Success or client error
        try:
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            if e.response.status_code in (404, 403):
                return {}  # Not found/forbidden
            raise SystemExit(f"HTTP {r.status_code}: {url}")
    
    raise SystemExit(f"Failed to GET {url} after {max_retries} attempts")


def get_summoner_by_name(platform: str, name: str) -> Dict[str, Any]:
    """Fetch summoner info by name.
    
    Args:
        platform: Platform code (e.g., 'vn1','na1')
        name: Summoner name
        
    Returns:
        Summoner data dict
    """
    url = f"https://{platform}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{name}"
    return riot_get(url)


def try_autodetect_platform(name: str, platforms: List[str]) -> Optional[str]:
    """Auto-detect platform by trying multiple platforms.
    
    Args:
        name: Summoner name
        platforms: List of platforms to try
        
    Returns:
        Platform code if found, None if not found on any platform
    """
    for p in platforms:
        try:
            resp = get_summoner_by_name(p, name)
            if resp and resp.get("puuid"):
                print(f"✓ Auto-detected platform: {p}")
                return p
        except SystemExit:
            # Skip non-existent summoner
            continue
        except Exception as e:
            print(f"  Warning: Error checking platform {p}: {e}")
            continue
    return None


def get_recent_match_ids(region: str, puuid: str, count: int = MAX_RECENT_MATCHES) -> List[str]:
    """Fetch recent match IDs for a player.
    
    Args:
        region: Regional cluster (e.g., 'americas', 'europe', 'asia')
        puuid: Player UUID
        count: Number of matches to fetch
        
    Returns:
        List of match IDs
    """
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
    return riot_get(url, params={"start": 0, "count": count})


def get_match(region: str, match_id: str) -> Dict[str, Any]:
    """Fetch match data.
    
    Args:
        region: Regional cluster
        match_id: Match ID
        
    Returns:
        Match data dict
    """
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    return riot_get(url)


def summarize_match_for_puuid(match: Dict[str, Any], puuid: str) -> Optional[Dict[str, Any]]:
    """Extract player's match summary from full match data.
    
    Args:
        match: Full match data
        puuid: Player PUUID
        
    Returns:
        Summarized match dict or None if player not found
    """
    try:
        info = match.get("info", {})
        participants = info.get("participants", [])
        me = next((p for p in participants if p.get("puuid") == puuid), None)
        if not me:
            return None
        
        placement = me.get("placement")
        units = me.get("units", [])
        final_board = []
        items: Dict[str, List[str]] = {}
        
        for u in units:
            cid = u.get("character_id") or ""
            name = cid.split("_", 1)[1] if "_" in cid else cid
            star = u.get("tier", 1) or 1
            final_board.append(f"{name}{star}")
            champ_items = u.get("itemNames") or []
            items[name] = champ_items

        return {
            "patch": info.get("game_variation") or "unknown",
            "placement": placement,
            "comp_name": None,
            "final_board": final_board,
            "items": items,
            "timestamp": info.get("game_datetime")
        }
    except Exception as e:
        print(f"  Warning: Failed to summarize match: {e}")
        return None


def append_logs(entries: List[Dict[str, Any]]) -> None:
    """Append match entries to JSONL log file.
    
    Args:
        entries: List of match summary dicts
    """
    if not entries:
        return
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"✓ Appended {len(entries)} matches to {LOG_FILE}")
    except IOError as e:
        print(f"✗ Failed to write matches: {e}")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python fetch_from_riot.py SUMMONER_NAME [PLATFORM]")
        sys.exit(1)
    
    summoner = sys.argv[1]
    platform_arg = sys.argv[2] if len(sys.argv) > 2 else os.getenv("PLATFORM")

    # Determine platform
    platform = platform_arg
    if not platform:
        print(f"Platform not provided, attempting auto-detect for '{summoner}'...")
        platform = try_autodetect_platform(summoner, PLATFORMS_TRY)
        if not platform:
            sys.exit(f"✗ Could not find '{summoner}' on any platform. Provide PLATFORM in .env or as arg.")

    region = PLATFORM_TO_REGION.get(platform.lower())
    if not region:
        available = ", ".join(PLATFORM_TO_REGION.keys())
        sys.exit(f"✗ Unknown platform '{platform}'. Available: {available}")

    print(f"Fetching summoner '{summoner}' on {platform} (region {region})")
    
    try:
        summ = get_summoner_by_name(platform, summoner)
    except SystemExit as e:
        sys.exit(f"✗ {e}")
    
    puuid = summ.get("puuid")
    if not puuid:
        sys.exit(f"✗ PUUID not found for '{summoner}'")

    print(f"✓ Found PUUID: {puuid}")
    
    # Fetch recent matches
    try:
        ids = get_recent_match_ids(region, puuid, count=MAX_RECENT_MATCHES)
    except SystemExit as e:
        sys.exit(f"✗ {e}")
    
    print(f"Found {len(ids)} recent matches")

    # Fetch and summarize each match
    entries = []
    for mid in ids:
        time.sleep(RATE_LIMIT_DELAY)
        try:
            m = get_match(region, mid)
            if m:
                s = summarize_match_for_puuid(m, puuid)
                if s:
                    entries.append(s)
        except SystemExit:
            continue
        except Exception as e:
            print(f"  Warning: Failed to fetch {mid}: {e}")

    # Write to logs
    append_logs(entries)


if __name__ == "__main__":
    main()
