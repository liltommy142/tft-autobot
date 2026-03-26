"""
cli_main.py - CLI interface for TFT assistant
"""
import os
import json
from typing import List, Optional

from core_models import GameState, UnitInstance
from core_engine import recommend_comps, econ_advice, recommend_items
from logger import log_game, read_logs
from config import (
    VALID_PLACEMENTS, DEFAULT_LEVEL, DEFAULT_GOLD, DEFAULT_HP,
    DEFAULT_ROUND, TOP_N_LOGS_TO_SHOW, MIN_STAR_LEVEL, MAX_STAR_LEVEL
)


def parse_units(raw: str) -> List[UnitInstance]:
    """Parse unit string into list of UnitInstance objects.
    
    Format: "Ahri2,Annie1,Yasuo2" or "Ahri,Annie,Yasuo"
    If no number, defaults to 1-star.
    
    Args:
        raw: Comma-separated string of units
        
    Returns:
        List of UnitInstance objects
        
    Raises:
        ValueError: If unit format is invalid
    """
    if not raw.strip():
        return []
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    units: List[UnitInstance] = []
    for p in parts:
        name = ""
        star = 1
        for i, ch in enumerate(p):
            if ch.isdigit():
                name = p[:i]
                star = int(p[i:])
                break
        if not name:
            name = p
        
        try:
            units.append(UnitInstance(name=name, star=star))
        except ValueError as e:
            print(f"Warning: Invalid unit '{p}': {e}")
            continue
    
    return units


def validate_placement(placement_str: str) -> Optional[int]:
    """Validate and convert placement string to int.
    
    Args:
        placement_str: String representation of placement (1-8)
        
    Returns:
        Integer placement or None if invalid
    """
    if not placement_str.strip():
        return None
    try:
        placement = int(placement_str.strip())
        if placement not in VALID_PLACEMENTS:
            print(f"Warning: Placement must be 1-8, got {placement}")
            return None
        return placement
    except ValueError:
        print(f"Warning: Invalid placement format: {placement_str}")
        return None


def validate_game_input(level: int, gold: int, hp: int) -> bool:
    """Validate game state inputs.
    
    Args:
        level: Player level (1-10)
        gold: Gold amount (>=0)
        hp: HP amount (>=0)
        
    Returns:
        True if all valid, False otherwise
    """
    errors = []
    if not (1 <= level <= 10):
        errors.append(f"Level must be 1-10, got {level}")
    if gold < 0:
        errors.append(f"Gold cannot be negative, got {gold}")
    if hp < 0:
        errors.append(f"HP cannot be negative, got {hp}")
    
    if errors:
        for e in errors:
            print(f"Warning: {e}")
        return False
    
    return True


def cli_log_game() -> None:
    """CLI interface to log a game."""
    print("--- Log game (nhập rỗng để bỏ qua) ---")
    patch = input(
        "Patch/id (mặc định fetched-auto): ").strip() or "fetched-auto"
    placement = validate_placement(input("Placement (1-8): ").strip())
    comp_name = input("Comp name (vd AP Carry Ahri): ").strip() or None
    final_board = input("Final board (vd: Ahri3,Annie2): ").strip()
    items_raw = input(
        "Items JSON (một dict champion->list), ví dụ {\"Ahri\":[\"Rabadon\"]}: ").strip()

    entry = {"patch": patch}
    if placement:
        entry["placement"] = placement
    if comp_name:
        entry["comp_name"] = comp_name
    if final_board:
        entry["final_board"] = [u.strip()
                                for u in final_board.split(",") if u.strip()]
    if items_raw:
        try:
            entry['items'] = json.loads(items_raw)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON for items: {e}")
            entry['items_raw'] = items_raw

    try:
        log_game(entry)
        print("Đã ghi log.")
    except Exception as e:
        print(f"Error: Không thể ghi log: {e}")


def main() -> None:
    """Main CLI loop."""
    print("=== TFT Rank Assistant v0 (modular) ===")

    cmd = input(
        "Chọn: (1) run assistant, (2) log game, (3) show logs: ").strip() or "1"
    if cmd == "2":
        cli_log_game()
        return
    if cmd == "3":
        logs = read_logs(TOP_N_LOGS_TO_SHOW)
        if not logs:
            print("Không có log nào.")
        else:
            for log_entry in logs:
                print(log_entry)
        return

    # Parse input with defaults
    try:
        level_input = input(f"Level hiện tại (mặc định {DEFAULT_LEVEL}): ").strip()
        level = int(level_input) if level_input else DEFAULT_LEVEL
        
        gold_input = input(f"Vàng hiện tại (mặc định {DEFAULT_GOLD}): ").strip()
        gold = int(gold_input) if gold_input else DEFAULT_GOLD
        
        hp_input = input(f"Máu hiện tại (mặc định {DEFAULT_HP}): ").strip()
        hp = int(hp_input) if hp_input else DEFAULT_HP
        
        round_ = input(f"Round (mặc định {DEFAULT_ROUND}): ").strip() or DEFAULT_ROUND
    except ValueError as e:
        print(f"Error: Invalid input format: {e}")
        return
    
    # Validate inputs
    if not validate_game_input(level, gold, hp):
        print("Please enter valid values.")
        return
    
    units_raw = input("Tướng đang có (vd: Ahri2,Annie1,Yasuo2): ").strip()

    try:
        gs = GameState(
            level=level,
            gold=gold,
            hp=hp,
            round=round_,
            units=parse_units(units_raw),
        )
    except ValueError as e:
        print(f"Error: Invalid game state: {e}")
        return

    # Get recommendations
    try:
        comps = recommend_comps(gs)
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        comps = []
    
    print("\n--- Gợi ý đội hình ---")
    if not comps:
        print("Chưa tìm được comp phù hợp (thiếu data hoặc chưa có core tướng).")
        target_comp = None
    else:
        for i, comp in enumerate(comps, 1):
            print(f"[{i}] {comp['name']} (ideal level {comp.get('ideal_level', 8)})")
            print("   Core:", ", ".join(comp.get("core_units", [])))
            print("   Optional:", ", ".join(comp.get("optional_units", [])))
        target_comp = comps[0]

    print("\n--- Kinh tế (econ) ---")
    econ = econ_advice(gs, target_comp)
    print("Hành động:", econ["action"])
    print("Lý do:", econ["reason"])

    print("\n--- Gợi ý trang bị (dựa trên comp #1) ---")
    item_sugs = recommend_items(gs, target_comp)
    if not item_sugs:
        print("Chưa có gợi ý (thiếu data item hoặc chưa chọn comp).")
    else:
        for s in item_sugs:
            print(f"{s['item']} -> {s['champion']} | {s['reason']}")


if __name__ == "__main__":
    main()
