"""
test_core_engine.py - Unit tests for core engine logic
"""
import pytest
from core_models import GameState, UnitInstance
from core_engine import econ_advice
from config import ROLL_ACTION, LEVEL_ACTION, SAVE_ACTION, LOW_HP_THRESHOLD, HIGH_GOLD_THRESHOLD


class TestEconAdvice:
    """Test economic decision making."""
    
    def test_econ_low_hp_triggers_roll(self):
        """Test that low HP triggers ROLL action."""
        gs = GameState(level=6, gold=50, hp=LOW_HP_THRESHOLD, round="4-1")
        econ = econ_advice(gs, None)
        assert econ["action"] == ROLL_ACTION
    
    def test_econ_very_low_hp_triggers_roll(self):
        """Test that very low HP triggers ROLL."""
        gs = GameState(level=6, gold=50, hp=1, round="4-1")
        econ = econ_advice(gs, None)
        assert econ["action"] == ROLL_ACTION
    
    def test_econ_high_hp_and_gold_triggers_level(self):
        """Test that high gold + decent level triggers LEVEL."""
        gs = GameState(level=7, gold=HIGH_GOLD_THRESHOLD, hp=70, round="4-1")
        econ = econ_advice(gs, None)
        assert econ["action"] == LEVEL_ACTION
    
    def test_econ_high_gold_at_level_8_triggers_save(self):
        """Test that being at level 8 with high gold doesn't trigger LEVEL."""
        gs = GameState(level=8, gold=HIGH_GOLD_THRESHOLD, hp=70, round="5-1")
        econ = econ_advice(gs, None)
        assert econ["action"] == SAVE_ACTION
    
    def test_econ_medium_gold_triggers_save(self):
        """Test that medium gold triggers SAVE."""
        gs = GameState(level=6, gold=30, hp=50, round="3-5")
        econ = econ_advice(gs, None)
        assert econ["action"] == SAVE_ACTION
    
    def test_econ_low_gold_triggers_save(self):
        """Test that low gold triggers SAVE."""
        gs = GameState(level=6, gold=10, hp=50, round="3-5")
        econ = econ_advice(gs, None)
        assert econ["action"] == SAVE_ACTION
    
    def test_econ_returns_reason(self):
        """Test that econ advice includes reason."""
        gs = GameState(level=6, gold=30, hp=50, round="3-5")
        econ = econ_advice(gs, None)
        assert "reason" in econ
        assert len(econ["reason"]) > 0


class TestEconEdgeCases:
    """Test edge cases for econ logic."""
    
    def test_econ_exactly_low_hp_threshold(self):
        """Test edge case: HP exactly at threshold."""
        gs = GameState(level=6, gold=30, hp=LOW_HP_THRESHOLD, round="3-5")
        econ = econ_advice(gs, None)
        assert econ["action"] == ROLL_ACTION
    
    def test_econ_just_above_low_hp_threshold(self):
        """Test edge case: HP just above threshold."""
        gs = GameState(level=6, gold=30, hp=LOW_HP_THRESHOLD + 1, round="3-5")
        econ = econ_advice(gs, None)
        # Should not ROLL if other conditions don't apply
        assert econ["action"] in [SAVE_ACTION]
    
    def test_econ_exactly_high_gold_threshold(self):
        """Test edge case: Gold exactly at threshold."""
        gs = GameState(level=7, gold=HIGH_GOLD_THRESHOLD, hp=70, round="4-1")
        econ = econ_advice(gs, None)
        assert econ["action"] == LEVEL_ACTION
    
    def test_econ_just_below_high_gold_threshold(self):
        """Test edge case: Gold just below threshold."""
        gs = GameState(level=7, gold=HIGH_GOLD_THRESHOLD - 1, hp=70, round="4-1")
        econ = econ_advice(gs, None)
        assert econ["action"] in [SAVE_ACTION]
    
    def test_econ_target_comp_ignored(self):
        """Test that target_comp parameter is ignored."""
        gs = GameState(level=6, gold=30, hp=50, round="3-5")
        target_comp = {"name": "Test", "core_units": ["A", "B"]}
        econ = econ_advice(gs, target_comp)
        # Should still give same result regardless of target_comp
        assert "action" in econ


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
