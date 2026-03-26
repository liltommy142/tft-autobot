"""
meta_learner.py - Continuous meta learning system

Automatically fetches match data from high-level players and learns meta patterns.

Features:
- Tracks patch updates
- Crawls Challenger/Grandmaster matches
- Analyzes comp winrates
- Auto-updates meta scores
- Maintains historical meta shifts
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

from config import META_DIR, RATE_LIMIT_DELAY, API_TIMEOUT, MAX_RETRIES
from logger import read_logs


# Load API key
def load_api_key() -> str:
    """Load Riot API key from .env or environment."""
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        # Try loading from .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("RIOT_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break
    if not api_key:
        raise RuntimeError("RIOT_API_KEY not found. Set it in .env or environment.")
    return api_key


API_KEY = load_api_key()
HEADERS = {"X-Riot-Token": API_KEY, "User-Agent": "tft-autobot/1.0"}


class MetaPatcher:
    """Track and detect patch updates."""
    
    PATCH_INFO_FILE = os.path.join(META_DIR, "patch_info.json")
    
    @classmethod
    def get_current_patch(cls, platform: str = "na1") -> str:
        """Get current patch from TFT-STATUS-V1 API.
        
        Args:
            platform: Platform code
            
        Returns:
            Patch version string
        """
        try:
            url = f"https://{platform}.api.riotgames.com/tft/status/v1/platform-data"
            r = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            
            # Extract patch from version string
            version = data.get("version", "unknown")
            return version
        except Exception as e:
            print(f"  ✗ Failed to get patch: {e}")
            return "unknown"
    
    @classmethod
    def is_patch_updated(cls, new_patch: str) -> bool:
        """Check if patch has been updated since last fetch.
        
        Args:
            new_patch: New patch version
            
        Returns:
            True if patch is different from saved patch
        """
        if not os.path.exists(cls.PATCH_INFO_FILE):
            return True
        
        try:
            with open(cls.PATCH_INFO_FILE, "r") as f:
                info = json.load(f)
                old_patch = info.get("patch", "unknown")
                return new_patch != old_patch
        except Exception:
            return True
    
    @classmethod
    def save_patch_info(cls, patch: str, meta_version: int) -> None:
        """Save current patch info and meta version.
        
        Args:
            patch: Patch version
            meta_version: Meta database version
        """
        os.makedirs(META_DIR, exist_ok=True)
        info = {
            "patch": patch,
            "meta_version": meta_version,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source": "riot-api"
        }
        with open(cls.PATCH_INFO_FILE, "w") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Saved patch info: v{patch}")


class HighEloMatcher:
    """Fetch and analyze matches from high-level players (Challenger/Grandmaster)."""
    
    PLATFORM_TO_REGION = {
        "na1": "americas",
        "euw1": "europe",
        "kr": "asia",
        "vn1": "asia",
    }
    
    def __init__(self, platform: str = "na1"):
        """Initialize matcher.
        
        Args:
            platform: Platform to fetch from
        """
        self.platform = platform
        self.region = self.PLATFORM_TO_REGION.get(platform, "americas")
        self.matches_cache: Dict[str, Any] = {}
    
    def get_grandmaster_players(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top grandmaster players.
        
        Args:
            limit: Max players to return
            
        Returns:
            List of player data dicts
        """
        try:
            url = f"https://{self.platform}.api.riotgames.com/tft/league/v1/grandmaster"
            r = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            
            entries = data.get("entries", [])
            return entries[:limit]
        except Exception as e:
            print(f"  ✗ Failed to get grandmaster players: {e}")
            return []
    
    def get_challenger_players(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top challenger players.
        
        Args:
            limit: Max players to return
            
        Returns:
            List of player data dicts
        """
        try:
            url = f"https://{self.platform}.api.riotgames.com/tft/league/v1/challenger"
            r = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            
            entries = data.get("entries", [])
            return entries[:limit]
        except Exception as e:
            print(f"  ✗ Failed to get challenger players: {e}")
            return []
    
    def get_recent_matches(self, puuid: str, count: int = 10) -> List[str]:
        """Get recent match IDs for a player.
        
        Args:
            puuid: Player UUID
            count: Number of matches
            
        Returns:
            List of match IDs
        """
        try:
            time.sleep(RATE_LIMIT_DELAY)
            url = f"https://{self.region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
            r = requests.get(url, headers=HEADERS, params={"count": count}, timeout=API_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  ✗ Failed to get matches for {puuid}: {e}")
            return []
    
    def get_match_details(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed match data.
        
        Args:
            match_id: Match ID
            
        Returns:
            Match data or None if failed
        """
        try:
            time.sleep(RATE_LIMIT_DELAY)
            url = f"https://{self.region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
            r = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  ✗ Failed to get match {match_id}: {e}")
            return None


class MetaAnalyzer:
    """Analyze match data to calculate comp winrates and meta scores."""
    
    @staticmethod
    def extract_comp_from_match(match: Dict[str, Any], puuid: str) -> Optional[Dict[str, Any]]:
        """Extract player's comp from match data.
        
        Args:
            match: Match data from API
            puuid: Player PUUID
            
        Returns:
            Comp info or None
        """
        try:
            info = match.get("info", {})
            participants = info.get("participants", [])
            
            # Find player
            player = next((p for p in participants if p.get("puuid") == puuid), None)
            if not player:
                return None
            
            placement = player.get("placement")
            units = player.get("units", [])
            
            # Extract comp core units
            comp_units = []
            for unit in units:
                cid = unit.get("character_id", "")
                name = cid.split("_", 1)[1] if "_" in cid else cid
                tier = unit.get("tier", 1)
                comp_units.append({
                    "name": name,
                    "tier": tier,
                    "items": unit.get("itemNames", [])
                })
            
            return {
                "placement": placement,
                "units": comp_units,
                "patch": info.get("game_variation", "unknown"),
                "timestamp": info.get("game_datetime")
            }
        except Exception as e:
            print(f"  ✗ Failed to extract comp: {e}")
            return None
    
    @staticmethod
    def get_comp_core_units(units: List[Dict[str, str]]) -> List[str]:
        """Get core units from a composition.
        
        Core = most starred unit + 2 other units.
        
        Args:
            units: List of units in comp
            
        Returns:
            List of core unit names
        """
        # Sort by tier (star level)
        sorted_units = sorted(units, key=lambda u: u.get("tier", 0), reverse=True)
        
        # Take top 3
        core = [u["name"] for u in sorted_units[:3]]
        return core


class MetaLearner:
    """Main meta learning system."""
    
    def __init__(self, platform: str = "na1"):
        """Initialize learner.
        
        Args:
            platform: Platform to learn from
        """
        self.platform = platform
        self.matcher = HighEloMatcher(platform)
        self.analyzer = MetaAnalyzer()
        self.patch_tracker = MetaPatcher()
        self.comp_stats: Dict[str, Dict[str, Any]] = {}
    
    def learn_from_matches(self, matches_per_player: int = 5, num_players: int = 20) -> None:
        """Learn meta from high-level players' matches.
        
        Args:
            matches_per_player: Number of recent matches per player
            num_players: Number of high-level players to analyze
        """
        print("\n🧠 Meta Learning System - Starting Analysis")
        print(f"   Platform: {self.platform}")
        
        # Get high-level players
        print(f"\n  Fetching top {num_players} Grandmaster players...")
        players = self.matcher.get_grandmaster_players(limit=num_players)
        
        if not players:
            print("    ✗ No players found")
            return
        
        print(f"    ✓ Found {len(players)} players")
        
        # Analyze matches for each player
        total_matches = 0
        comps_found = 0
        
        for i, player in enumerate(players, 1):
            puuid = player.get("summonerId")  # Note: TFT API uses summonerId
            if not puuid:
                continue
            
            print(f"\n  Player {i}/{len(players)}: {player.get('summonerName', 'Unknown')}")
            
            # Get recent matches
            match_ids = self.matcher.get_recent_matches(puuid, count=matches_per_player)
            if not match_ids:
                continue
            
            print(f"    Analyzing {len(match_ids)} matches...")
            
            # Analyze each match
            for match_id in match_ids:
                total_matches += 1
                match = self.matcher.get_match_details(match_id)
                if not match:
                    continue
                
                comp_info = self.analyzer.extract_comp_from_match(match, puuid)
                if not comp_info:
                    continue
                
                comps_found += 1
                self._record_comp_performance(comp_info)
        
        print(f"\n  📊 Analysis Complete")
        print(f"     - Matches analyzed: {total_matches}")
        print(f"     - Comps found: {comps_found}")
        print(f"     - Unique comps: {len(self.comp_stats)}")
    
    def _record_comp_performance(self, comp_info: Dict[str, Any]) -> None:
        """Record comp performance data.
        
        Args:
            comp_info: Comp data with placement
        """
        units = comp_info.get("units", [])
        placement = comp_info.get("placement", 8)
        
        core_units = self.analyzer.get_comp_core_units(units)
        if not core_units:
            return
        
        comp_key = "-".join(sorted(core_units))
        
        if comp_key not in self.comp_stats:
            self.comp_stats[comp_key] = {
                "core_units": core_units,
                "placements": [],
                "count": 0,
                "winrate": 0.0,
                "avg_placement": 0.0
            }
        
        self.comp_stats[comp_key]["placements"].append(placement)
        self.comp_stats[comp_key]["count"] += 1
        
        # Calculate stats
        placements = self.comp_stats[comp_key]["placements"]
        self.comp_stats[comp_key]["avg_placement"] = sum(placements) / len(placements)
        
        # Top 4 = win in TFT
        top_4_count = sum(1 for p in placements if p <= 4)
        self.comp_stats[comp_key]["winrate"] = top_4_count / len(placements)
    
    def calculate_meta_scores(self) -> List[Dict[str, Any]]:
        """Calculate meta scores based on analysis.
        
        Returns:
            List of comps with calculated meta scores
        """
        comps = []
        
        for comp_key, stats in self.comp_stats.items():
            if stats["count"] < 3:  # Need at least 3 samples
                continue
            
            # Meta score: 0-10 scale based on winrate
            # Formula: (winrate * 8) + (frequency_bonus * 2)
            winrate = stats["winrate"]
            frequency_bonus = min(2.0, stats["count"] / 50)  # Cap at 2 points
            meta_score = (winrate * 8) + frequency_bonus
            
            comps.append({
                "core_units": stats["core_units"],
                "name": " + ".join(stats["core_units"]),
                "meta_score": round(meta_score, 1),
                "winrate": round(stats["winrate"] * 100, 1),
                "sample_size": stats["count"],
                "avg_placement": round(stats["avg_placement"], 1),
                "tags": ["learned-from-api"],
            })
        
        # Sort by meta score
        comps.sort(key=lambda x: x["meta_score"], reverse=True)
        return comps
    
    def update_meta_database(self) -> None:
        """Update meta database with learned comps."""
        print("\n  💾 Updating meta database...")
        
        # Calculate meta scores
        learned_comps = self.calculate_meta_scores()
        
        print(f"     - Generated {len(learned_comps)} comps from analysis")
        
        # Load existing comps
        existing_file = os.path.join(META_DIR, "comps_meta.json")
        try:
            with open(existing_file, "r") as f:
                existing = json.load(f)
        except:
            existing = []
        
        # Merge: learned comps take priority, keep other existing comps
        learned_core_sets = {tuple(sorted(c["core_units"])) for c in learned_comps}
        
        merged = learned_comps + [
            c for c in existing 
            if tuple(sorted(c.get("core_units", []))) not in learned_core_sets
        ]
        
        # Save back
        os.makedirs(META_DIR, exist_ok=True)
        with open(existing_file, "w") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        
        print(f"     ✓ Updated {existing_file}")
        print(f"       Total comps in meta: {len(merged)}")


def main() -> None:
    """Main entry point - learn meta and update database."""
    try:
        # Check for patch update
        print("🔄 TFT Meta Learner - Continuous Learning System")
        print("\n1️⃣ Checking for patch updates...")
        
        current_patch = MetaPatcher.get_current_patch()
        print(f"   Current patch: {current_patch}")
        
        if not MetaPatcher.is_patch_updated(current_patch):
            print("   ℹ️  Same patch as last update, skipping meta analysis")
            return
        
        print("   ✓ New patch detected - starting analysis")
        
        # Learn meta
        print("\n2️⃣ Learning from high-level players (Grandmaster)...")
        learner = MetaLearner(platform="na1")
        learner.learn_from_matches(matches_per_player=5, num_players=20)
        
        # Update database
        print("\n3️⃣ Updating meta database...")
        learner.update_meta_database()
        
        # Save patch info
        meta_version = len(learner.calculate_meta_scores())
        MetaPatcher.save_patch_info(current_patch, meta_version)
        
        print("\n✅ Meta learning complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
