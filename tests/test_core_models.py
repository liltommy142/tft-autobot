"""
test_core_models.py - Unit tests for core models
"""
import pytest
from core_models import UnitInstance, GameState


class TestUnitInstance:
    """Test UnitInstance model."""
    
    def test_unit_creation_with_name_only(self):
        """Test creating unit with default star level."""
        unit = UnitInstance(name="Ahri")
        assert unit.name == "Ahri"
        assert unit.star == 1
    
    def test_unit_creation_with_star(self):
        """Test creating unit with specific star level."""
        unit = UnitInstance(name="Ahri", star=2)
        assert unit.name == "Ahri"
        assert unit.star == 2
    
    def test_unit_invalid_star_too_low(self):
        """Test that star level < 1 raises error."""
        with pytest.raises(ValueError):
            UnitInstance(name="Ahri", star=0)
    
    def test_unit_invalid_star_too_high(self):
        """Test that star level > 3 raises error."""
        with pytest.raises(ValueError):
            UnitInstance(name="Ahri", star=4)


class TestGameState:
    """Test GameState model."""
    
    def test_game_state_creation(self):
        """Test creating valid game state."""
        gs = GameState(level=6, gold=30, hp=70, round="3-2")
        assert gs.level == 6
        assert gs.gold == 30
        assert gs.hp == 70
        assert gs.round == "3-2"
        assert gs.units == []
    
    def test_game_state_with_units(self):
        """Test creating game state with units."""
        units = [UnitInstance("Ahri", 2), UnitInstance("Annie", 1)]
        gs = GameState(level=6, gold=30, hp=70, round="3-2", units=units)
        assert len(gs.units) == 2
    
    def test_game_state_invalid_level_low(self):
        """Test that level < 1 raises error."""
        with pytest.raises(ValueError):
            GameState(level=0, gold=30, hp=70, round="3-2")
    
    def test_game_state_invalid_level_high(self):
        """Test that level > 10 raises error."""
        with pytest.raises(ValueError):
            GameState(level=11, gold=30, hp=70, round="3-2")
    
    def test_game_state_negative_gold(self):
        """Test that negative gold raises error."""
        with pytest.raises(ValueError):
            GameState(level=6, gold=-10, hp=70, round="3-2")
    
    def test_game_state_negative_hp(self):
        """Test that negative HP raises error."""
        with pytest.raises(ValueError):
            GameState(level=6, gold=30, hp=-10, round="3-2")
    
    def test_game_state_empty_round(self):
        """Test that empty round raises error."""
        with pytest.raises(ValueError):
            GameState(level=6, gold=30, hp=70, round="")


class TestCLIValidation:
    """Test CLI validation functions."""
    
    def test_validate_placement_valid(self, capfd):
        """Test valid placement."""
        from cli_main import validate_placement
        result = validate_placement("5")
        assert result == 5
    
    def test_validate_placement_edge_1(self, capfd):
        """Test placement 1."""
        from cli_main import validate_placement
        result = validate_placement("1")
        assert result == 1
    
    def test_validate_placement_edge_8(self, capfd):
        """Test placement 8."""
        from cli_main import validate_placement
        result = validate_placement("8")
        assert result == 8
    
    def test_validate_placement_invalid_low(self, capfd):
        """Test placement 0 (invalid)."""
        from cli_main import validate_placement
        result = validate_placement("0")
        assert result is None
        captured = capfd.readouterr()
        assert "must be 1-8" in captured.out
    
    def test_validate_placement_invalid_high(self, capfd):
        """Test placement 9 (invalid)."""
        from cli_main import validate_placement
        result = validate_placement("9")
        assert result is None
    
    def test_validate_placement_empty(self, capfd):
        """Test empty placement."""
        from cli_main import validate_placement
        result = validate_placement("")
        assert result is None
    
    def test_parse_units_single(self):
        """Test parsing single unit."""
        from cli_main import parse_units
        units = parse_units("Ahri2")
        assert len(units) == 1
        assert units[0].name == "Ahri"
        assert units[0].star == 2
    
    def test_parse_units_multiple(self):
        """Test parsing multiple units."""
        from cli_main import parse_units
        units = parse_units("Ahri2,Annie1,Yasuo2")
        assert len(units) == 3
        assert units[1].name == "Annie"
        assert units[1].star == 1
    
    def test_parse_units_no_star(self):
        """Test parsing unit without star (defaults to 1)."""
        from cli_main import parse_units
        units = parse_units("Ahri")
        assert len(units) == 1
        assert units[0].star == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
