"""
fetch_from_riot.py - Fetch TFT match data from Riot API using Riot ID

Usage:
  python fetch_from_riot.py "Name#Tag" [PLATFORM]
  Ví dụ: python fetch_from_riot.py "Anh Hai#0142" vn1
"""
import os
import sys
import time
import json
import urllib.parse
from typing import Optional, List, Dict, Any
import requests

# Load configuration
try:
    from config import (
        LOG_FILE, LOGS_DIR, RATE_LIMIT_DELAY, API_TIMEOUT,
        MAX_RETRIES, MAX_RECENT_MATCHES, RIOT_API_KEY
    )
except ImportError:
    LOG_FILE, LOGS_DIR = "logs/games.jsonl", "logs"
    RATE_LIMIT_DELAY, API_TIMEOUT = 1.2, 10
    MAX_RETRIES, MAX_RECENT_MATCHES = 3, 10
    RIOT_API_KEY = os.getenv("RIOT_API_KEY")

os.makedirs(LOGS_DIR, exist_ok=True)

if not RIOT_API_KEY:
    sys.exit("Error: RIOT_API_KEY is missing. Check your .env file.")

HEADERS = {"X-Riot-Token": RIOT_API_KEY, "User-Agent": "tft-autobot/1.0"}

PLATFORM_TO_REGION: Dict[str, str] = {
    "na1": "americas", "br1": "americas", "la1": "americas", "la2": "americas", "oc1": "americas",
    "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe",
    "kr": "asia", "jp1": "asia", 
    "vn1": "sea", "sg1": "sea", "ph2": "sea", "th2": "sea", "tw2": "sea"
}


def riot_get(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Helper to handle requests and rate limiting."""
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, headers=HEADERS,
                             params=params, timeout=API_TIMEOUT)

            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 2))
                print(f"  Rate limited (429), waiting {wait}s...")
                time.sleep(wait + 0.5)
                continue

            if r.status_code == 404:
                return {}

            if r.status_code == 403:
                print(f"  Forbidden (403): Your API Key does not have access to {url}")
                return {}

            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Error calling {url}: {e}")
                return {}
            time.sleep(1.5)
    return {}


def get_puuid_by_riot_id(region: str, game_name: str, tag_line: str) -> Optional[str]:
    """Retrieve PUUID from Riot ID using Account-V1 API."""
    safe_name = urllib.parse.quote(game_name)
    safe_tag = urllib.parse.quote(tag_line)

    # Account-V1 on 'sea' cluster often returns 403 for development keys.
    # Using 'asia' cluster as a global gateway to resolve PUUID for SEA players.
    account_region = "asia" if region == "sea" else region
    
    url = f"https://{account_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{safe_name}/{safe_tag}"

    resp = riot_get(url)
    return resp.get("puuid")



def get_recent_match_ids(region: str, puuid: str, count: int = MAX_RECENT_MATCHES) -> List[str]:
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
    return riot_get(url, params={"start": 0, "count": count}) or []


def get_match(region: str, match_id: str) -> Dict[str, Any]:
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    return riot_get(url)


def summarize_match_for_puuid(match: Dict[str, Any], puuid: str) -> Optional[Dict[str, Any]]:
    if not match or "info" not in match:
        return None
    try:
        info = match.get("info", {})
        me = next((p for p in info.get("participants", [])
                  if p.get("puuid") == puuid), None)
        if not me:
            return None

        # Extract unit list (remove TFT13_ prefix)
        final_board = []
        for u in me.get("units", []):
            char_id = u['character_id']
            name = char_id.split('_')[-1] if '_' in char_id else char_id
            final_board.append(f"{name}{u['tier']}")

        return {
            "patch": info.get("game_version", "unknown"),
            "placement": me.get("placement"),
            "final_board": final_board,
            "timestamp": info.get("game_datetime")
        }
    except Exception as e:
        print(f"Summarize error: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python fetch_from_riot.py 'Name#Tag' [platform]")

    riot_id = sys.argv[1]
    if "#" not in riot_id:
        sys.exit("Error: Riot ID must be in 'Name#Tag' format (e.g., 'Anh Hai#0142')")

    game_name, tag_line = riot_id.rsplit("#", 1)

    platform = sys.argv[2] if len(sys.argv) > 2 else "vn1"
    region = PLATFORM_TO_REGION.get(platform.lower())

    if not region:
        sys.exit(
            f"Error: Platform '{platform}' not supported. Try: vn1, na1, kr...")

    print(f"--- Searching for {riot_id} in {region} region ---")
    puuid = get_puuid_by_riot_id(region, game_name, tag_line)

    if not puuid:
        sys.exit(
            f"Error: PUUID not found for {riot_id}. Check the Name#Tag or region.")

    match_ids = get_recent_match_ids(region, puuid)
    if not match_ids:
        print("No recent matches found.")
        return

    print(f"Found {len(match_ids)} matches. Fetching details...")

    new_entries = []
    for mid in match_ids:
        print(f" -> Processing match: {mid}")
        match_data = get_match(region, mid)
        summary = summarize_match_for_puuid(match_data, puuid)
        if summary:
            new_entries.append(summary)
        time.sleep(RATE_LIMIT_DELAY)  # Avoid rate limit bans

    if new_entries:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"✓ Success! Saved {len(new_entries)} matches to {LOG_FILE}")


if __name__ == "__main__":
    main()
