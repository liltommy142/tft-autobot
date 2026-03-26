import json
import os
from typing import Any, Dict, List, Optional

from core_models import GameState
from logger import read_logs
from config import (
    META_DIR, CORE_UNIT_MULTIPLIER, OPTIONAL_UNIT_MULTIPLIER,
    IDEAL_LEVEL_DEFAULT, PERSONAL_SCORE_MAX, PERSONAL_LOG_LIMIT,
    COMP_SCORE_THRESHOLD, TOP_N_COMPS,
    LOW_HP_THRESHOLD, HIGH_GOLD_THRESHOLD, MIN_LEVEL_TO_LEVEL_UP,
    ROLL_ACTION, LEVEL_ACTION, SAVE_ACTION
)


def load_json(name: str) -> Any:
    """Load JSON file from metadata directory with error handling.
    
    Args:
        name: Filename in data/meta/ directory
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = os.path.join(META_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Meta file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {path}: {e.msg}", e.doc, e.pos)


# --- Comp Recommender ---


def _personal_score(comp_name: Optional[str]) -> float:
    """Calculate personal performance score based on game logs.
    
    Args:
        comp_name: Composition name to look up
        
    Returns:
        Score from 0.0 to PERSONAL_SCORE_MAX (based on average placement)
    """
    if not comp_name:
        return 0.0
    try:
        logs = read_logs(limit=PERSONAL_LOG_LIMIT)
    except Exception:
        return 0.0
    
    if not logs:
        return 0.0
    placements = [
        g.get("placement")
        for g in logs
        if g.get("comp_name") == comp_name and isinstance(g.get("placement"), (int, float))
    ]
    if not placements:
        return 0.0
    avg_place = sum(placements) / len(placements)
    return max(0.0, PERSONAL_SCORE_MAX - avg_place)


def _score_comp(gs: GameState, comp: Dict[str, Any]) -> float:
    """Score a composition based on current game state.
    
    Scoring formula:
    - core_match: Number of owned core units × CORE_UNIT_MULTIPLIER
    - opt_match: Number of owned optional units × OPTIONAL_UNIT_MULTIPLIER
    - level_penalty: -(ideal_level - current_level) if ideal > current
    - meta_strength: Composition's meta score
    - personal: Player's historical performance with this comp
    
    Args:
        gs: Current game state
        comp: Composition data dict
        
    Returns:
        Total score
    """
    try:
        core_units = set(comp.get("core_units", []))
        optional_units = set(comp.get("optional_units", []))

        owned = {u.name for u in gs.units}

        core_match = len(core_units & owned) * CORE_UNIT_MULTIPLIER
        opt_match = len(optional_units & owned) * OPTIONAL_UNIT_MULTIPLIER

        ideal_level = comp.get("ideal_level", IDEAL_LEVEL_DEFAULT)
        level_penalty = max(0, ideal_level - gs.level)

        meta_strength = comp.get("meta_score", 0)
        personal = _personal_score(comp.get("name"))

        return core_match + opt_match - level_penalty + meta_strength + personal
    except Exception:
        return 0.0


def recommend_comps(gs: GameState, n: int = TOP_N_COMPS) -> List[Dict[str, Any]]:
    """Recommend top N compositions based on current game state.
    
    Args:
        gs: Current game state
        n: Number of recommendations (default: TOP_N_COMPS)
        
    Returns:
        List of composition dicts sorted by score (descending)
        
    Raises:
        FileNotFoundError: If comps_meta.json not found
        json.JSONDecodeError: If metadata is invalid
    """
    try:
        comps = load_json("comps_meta.json")
    except Exception as e:
        print(f"Error loading compositions: {e}")
        return []
    
    try:
        scored = [(_score_comp(gs, comp), comp) for comp in comps]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for s, c in scored[:n] if s > COMP_SCORE_THRESHOLD]
    except Exception as e:
        print(f"Error scoring compositions: {e}")
        return []


# --- Econ Advisor ---


def econ_advice(gs: GameState, target_comp: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """Give economic advice for current game state.
    
    Decision rules (in priority order):
    1. If HP <= LOW_HP_THRESHOLD: ROLL to stabilize and find 2-star units
    2. If Gold >= HIGH_GOLD_THRESHOLD and Level < MIN_LEVEL_TO_LEVEL_UP: LEVEL to improve odds
    3. Otherwise: SAVE to maintain flexibility
    
    Args:
        gs: Current game state
        target_comp: Target composition (can be None, doesn't affect decision)
        
    Returns:
        Dict with 'action' (ROLL/LEVEL/SAVE) and 'reason'
    """
    if gs.hp <= LOW_HP_THRESHOLD:
        return {
            "action": ROLL_ACTION,
            "reason": f"Máu thấp (<={LOW_HP_THRESHOLD}), cần ổn định board nhanh bằng cách roll tìm 2 sao.",
        }

    if gs.gold >= HIGH_GOLD_THRESHOLD and gs.level < MIN_LEVEL_TO_LEVEL_UP:
        return {
            "action": LEVEL_ACTION,
            "reason": f"Kinh tế tốt (>={HIGH_GOLD_THRESHOLD} vàng), ưu tiên lên cấp để tăng tỉ lệ tướng cao cost.",
        }

    return {
        "action": SAVE_ACTION,
        "reason": "Không quá yếu cũng không quá khỏe, giữ vàng để linh hoạt (có thể up cấp hoặc roll sau).",
    }


# --- Item Recommender ---


def recommend_items(gs: GameState, target_comp: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Recommend items for core champions in target composition.
    
    Args:
        gs: Current game state (unused, for API consistency)
        target_comp: Target composition with core_units
        
    Returns:
        List of dicts with 'item', 'champion', 'reason' fields
    """
    if not target_comp:
        return []
    
    try:
        items = load_json("items.json")
    except Exception as e:
        print(f"Error loading items: {e}")
        return []

    try:
        comp_cores = set(target_comp.get("core_units", []))

        suggestions: List[Dict[str, str]] = []
        for item in items:
            best_users = set(item.get("best_users", []))
            good_target = list(comp_cores & best_users)
            if good_target:
                suggestions.append({
                    "item": item.get("name", ""),
                    "champion": good_target[0],
                    "reason": item.get("note", ""),
                })

        return suggestions
    except Exception as e:
        print(f"Error recommending items: {e}")
        return []
