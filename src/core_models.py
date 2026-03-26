"""
core_models.py - Data models for game state and unit instances
"""
from dataclasses import dataclass, field
from typing import List
from config import DEFAULT_STAR_LEVEL, MIN_STAR_LEVEL, MAX_STAR_LEVEL


@dataclass
class UnitInstance:
    """Represents a single unit (champion) in player's board.
    
    Attributes:
        name: Champion name (e.g., "Ahri", "Annie")
        star: Star level (1-3, representing tier of units)
    """
    name: str
    star: int = DEFAULT_STAR_LEVEL

    def __post_init__(self) -> None:
        """Validate star level."""
        if not (MIN_STAR_LEVEL <= self.star <= MAX_STAR_LEVEL):
            raise ValueError(f"Star level must be {MIN_STAR_LEVEL}-{MAX_STAR_LEVEL}, got {self.star}")


@dataclass
class GameState:
    """Represents current game state.
    
    Attributes:
        level: Player level (1-10)
        gold: Current gold amount
        hp: Current hit points
        round: Current round (e.g., "3-2", "4-3")
        units: List of units currently owned
    """
    level: int
    gold: int
    hp: int
    round: str
    units: List[UnitInstance] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate game state values."""
        if not (1 <= self.level <= 10):
            raise ValueError(f"Level must be 1-10, got {self.level}")
        if self.gold < 0:
            raise ValueError(f"Gold cannot be negative, got {self.gold}")
        if self.hp < 0:
            raise ValueError(f"HP cannot be negative, got {self.hp}")
        if not isinstance(self.round, str) or not self.round.strip():
            raise ValueError(f"Round must be non-empty string, got {self.round}")
