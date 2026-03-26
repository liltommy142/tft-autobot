# TFT Rank Assistant (v0)
# Simple CLI tool to get composition, econ, and item suggestions.

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
import os


DATA_DIR = os.path.dirname(__file__)


def load_json(name: str) -> Any:
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class UnitInstance:
    name: str
    star: int = 1


@dataclass
class GameState:
    level: int
    gold: int
    hp: int
    round: str
    units: List[UnitInstance] = field(default_factory=list)


# --- Comp Recommender ---


def score_comp(gs: GameState, comp: Dict[str, Any]) -> int:
    core_units = set(comp.get("core_units", []))
    optional_units = set(comp.get("optional_units", []))

    owned = {u.name for u in gs.units}

    core_match = len(core_units & owned) * 3
    opt_match = len(optional_units & owned)

    # small penalty if comp is much higher level than current
    ideal_level = comp.get("ideal_level", 8)
    level_penalty = max(0, ideal_level - gs.level)

    return core_match + opt_match - level_penalty


def recommend_comps(gs: GameState, n: int = 3) -> List[Dict[str, Any]]:
    comps = load_json("data_comps.json")
    scored = [
        (score_comp(gs, comp), comp)
        for comp in comps
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for s, c in scored[:n] if s > 0]


# --- Econ Advisor ---


def econ_advice(gs: GameState, target_comp: Dict[str, Any] | None) -> Dict[str, str]:
    # Very simple rule-based econ
    if gs.hp <= 40:
        return {
            "action": "ROLL",
            "reason": "Máu thấp (<=40), cần ổn định board nhanh bằng cách roll tìm 2 sao."
        }

    if gs.gold >= 50 and gs.level < 8:
        return {
            "action": "LEVEL",
            "reason": "Kinh tế tốt (>=50 vàng), ưu tiên lên cấp để tăng tỉ lệ tướng cao cost."
        }

    return {
        "action": "SAVE",
        "reason": "Không quá yếu cũng không quá khỏe, giữ vàng để linh hoạt (có thể up cấp hoặc roll sau)."
    }


# --- Item Recommender ---


def recommend_items(gs: GameState, target_comp: Dict[str, Any] | None) -> List[Dict[str, str]]:
    items = load_json("data_items.json")
    if not target_comp:
        return []

    comp_cores = set(target_comp.get("core_units", []))

    suggestions = []
    for item in items:
        best_users = set(item.get("best_users", []))
        good_target = list(comp_cores & best_users)
        if good_target:
            suggestions.append({
                "item": item["name"],
                "champion": good_target[0],
                "reason": item.get("note", "")
            })

    return suggestions


# --- CLI ---


def parse_units(raw: str) -> List[UnitInstance]:
    # format: "Ahri2, Annie1, Yasuo2" or "Ahri,Annie,Yasuo"
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
        units.append(UnitInstance(name=name, star=star))
    return units


def main() -> None:
    print("=== TFT Rank Assistant v0 ===")
    level = int(input("Level hiện tại: ").strip() or "6")
    gold = int(input("Vàng hiện tại: ").strip() or "30")
    hp = int(input("Máu hiện tại: ").strip() or "70")
    round_ = input("Round (vd 3-2): ").strip() or "3-2"
    units_raw = input("Tướng đang có (vd: Ahri2,Annie1,Yasuo2): ").strip()

    gs = GameState(
        level=level,
        gold=gold,
        hp=hp,
        round=round_,
        units=parse_units(units_raw),
    )

    comps = recommend_comps(gs)
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
