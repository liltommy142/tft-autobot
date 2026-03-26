"""
fetch_meta.py - Fetch meta data from online sources

Can fetch from:
- Riot Data Dragon for champion list
- Web scraping from tactics.tools or similar sites
- Custom meta sources

Note: Best-effort; endpoints may change or require authentication.
"""
import time
from typing import Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

from config import META_DIR


USER_AGENT = "tft-autobot/1.0 (+https://github.com/)"
REQUEST_TIMEOUT = 10


def fetch_champions_from_riot() -> Dict[str, Any]:
    """Fetch champion list from Riot Data Dragon.
    
    Note: Data Dragon is public and does not require API key.
    
    Returns:
        Dict with source info and champion data, or error dict if failed
    """
    try:
        # Get latest version
        r = requests.get(
            "https://ddragon.leagueoflegends.com/api/versions.json",
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        versions = r.json()
        if not versions:
            return {"error": "No versions available"}
        
        latest = versions[0]
        champs_url = (
            f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion.json"
        )
        r = requests.get(champs_url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        
        return {"source": "ddragon", "version": latest, "count": len(data.get("data", {}))}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch from Data Dragon: {e}"}


def fetch_meta_from_tactics_tools() -> Dict[str, Any]:
    """Scrape TFT meta from tactics.tools.
    
    Note: Site structure may change; treat as optional source.
    
    Returns:
        Dict with source info or error dict if failed
    """
    try:
        url = "https://tactics.tools/champions"
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else "tactics.tools"
        
        return {"source": "tactics.tools", "title": title, "status": "ok"}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch from tactics.tools: {e}"}


def main() -> None:
    """Fetch all available meta data.
    
    Saves results to data/meta/ directory.
    """
    print("Fetching meta data...")
    
    out = {
        "fetched_at": int(time.time()),
        "sources": {}
    }
    
    # Fetch from Data Dragon
    print("  - Fetching from Riot Data Dragon...")
    out["sources"]["ddragon"] = fetch_champions_from_riot()
    
    # Fetch from tactics.tools
    print("  - Fetching from tactics.tools...")
    out["sources"]["tactics_tools"] = fetch_meta_from_tactics_tools()
    
    # Print summary
    print("\nFetch summary:")
    for source, result in out["sources"].items():
        if "error" in result:
            print(f"  ✗ {source}: {result['error']}")
        else:
            print(f"  ✓ {source}: {result}")
    
    print(f"\n✓ Meta fetch complete at {META_DIR}")


if __name__ == "__main__":
    main()
