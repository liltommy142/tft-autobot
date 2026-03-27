"""
update_meta.py - Script to update metadata files

Currently uses local example data. Can be extended to fetch from:
- Riot API for champion data
- Meta websites for composition meta
- Custom sources
"""
import json
import os
from typing import Any, List, Dict

from config import META_DIR


def ensure_dirs() -> None:
    """Create metadata directory if it doesn't exist."""
    os.makedirs(META_DIR, exist_ok=True)


def save_json(name: str, data: Any) -> None:
    """Save data to JSON file in metadata directory.
    
    Args:
        name: Filename in data/meta/
        data: Data to serialize to JSON
        
    Raises:
        OSError: If write fails
    """
    path = os.path.join(META_DIR, name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {path}")
    except OSError as e:
        raise OSError(f"Failed to save {path}: {e}")


def generate_example_comps() -> List[Dict[str, Any]]:
    """Generate example composition data.
    
    Returns:
        List of composition dictionaries
    """
    return [
        {
            "name": "AP Carry Ahri",
            "core_units": ["Ahri", "Annie", "Lulu"],
            "optional_units": ["Janna", "Sona", "Syndra"],
            "ideal_level": 8,
            "tags": ["fast8", "ap"],
            "meta_score": 5
        },
        {
            "name": "Bruiser Reroll Yasuo",
            "core_units": ["Yasuo", "Illaoi", "Vi"],
            "optional_units": ["LeeSin", "Sett", "Garen"],
            "ideal_level": 7,
            "tags": ["reroll", "frontline"],
            "meta_score": 3
        }
    ]


def generate_example_items() -> List[Dict[str, Any]]:
    """Generate example item data.
    
    Returns:
        List of item dictionaries
    """
    return [
        {
            "name": "Rabadon's Deathcap",
            "best_users": ["Ahri", "Syndra"],
            "note": "Increases ability power for AP carries."
        },
        {
            "name": "Jeweled Gauntlet",
            "best_users": ["Ahri", "Lulu"],
            "note": "Allows abilities to critically strike, great for AP carries."
        },
        {
            "name": "Titan's Resolve",
            "best_users": ["Yasuo", "Vi"],
            "note": "Ideal for fighters/bruisers who stack attacks."
        },
        {
            "name": "Bloodthirster",
            "best_users": ["Yasuo"],
            "note": "Omnivamp for frontline carries like Yasuo."
        }
    ]


def update_from_local_examples() -> None:
    """Update metadata from local example data.
    
    Future: Replace with actual API calls or web scraping.
    """
    print("Updating metadata from examples...")
    
    try:
        comps = generate_example_comps()
        save_json("comps_meta.json", comps)
        
        items = generate_example_items()
        save_json("items.json", items)
        
        patch_info = {
            "patch": "local-example",
            "source": "manual",
        }
        save_json("patch_info.json", patch_info)
        
        print("✓ Metadata update complete!")
    except Exception as e:
        print(f"✗ Error updating metadata: {e}")
        raise


def main() -> None:
    """Main entry point."""
    try:
        ensure_dirs()
        update_from_local_examples()
    except Exception as e:
        print(f"Failed to update meta: {e}")
        exit(1)
