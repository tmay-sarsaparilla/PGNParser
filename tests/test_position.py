
import pytest
from chessplot.position import _Position


class TestPosition:
    def test_set_name_valid(self):
        """Test that the position name is set correctly for a valid position."""
        position = _Position(row=0, col=0)
        assert position._set_name() == "h1"

    def test_set_name_invalid(self):
        """Test that the position name is set to None for invalid positions."""
        position = _Position(row=8, col=8)
        assert position._set_name() is None

    def test_check_legality_true(self):
        """Test that the _check_legality method returns True for legal positions."""
        position = _Position(row=0, col=0)
        assert position._check_legality() is True

    def test_check_legality_false(self):
        """Test that the _check_legality method returns False for illegal positions."""
        position = _Position(row=8, col=8)
        assert position._check_legality() is False

    def test_equality_true(self):
        """Test that different positions with the same row and col are equal."""
        position1 = _Position(row=2, col=2)
        position2 = _Position(row=2, col=2)
        assert position1 == position2

    def test_equality_false(self):
        """Test that different positions with different row and col are not equal."""
        position1 = _Position(row=2, col=2)
        position2 = _Position(row=2, col=3)
        assert position1 != position2

    def test_from_name_valid(self):
        """Test that the from_name class method returns a _Position with the correct row and col for a valid name."""
        position = _Position.from_name(name="h1")
        assert position.row == 0 and position.col == 0

    def test_from_name_invalid(self):
        """Test that the from_name class method raises a ValueError when given an invalid name or None."""
        with pytest.raises(ValueError):
            position = _Position.from_name(name="invalid")

        with pytest.raises(ValueError):
            position = _Position.from_name(name=None)

