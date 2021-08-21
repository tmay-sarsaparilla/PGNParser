
import pytest
import numpy as np
from chessplot.position import _Position
from chessplot.piece import _Piece


class TestPiece:

    def test_piece_name_invalid(self):
        """Test that a ValueError is raised if a given name is invalid."""
        with pytest.raises(ValueError):
            piece = _Piece(name="J", row=0, col=0)

    def test_is_white_set_correctly(self):
        """Test that the is_white property is set correctly."""
        black_pawn = _Piece(name="p", row=0, col=0)
        white_pawn = _Piece(name="P", row=0, col=0)
        assert black_pawn.is_white is False and white_pawn.is_white is True

    def test_set_move_metric_white_pawn(self):
        """Test that the move metric is set correctly for a white pawn."""
        piece = _Piece(name="P", row=0, col=0)
        assert piece._set_move_metric() == [(1, 0)]

    def test_set_move_metric_black_pawn(self):
        """Test that the move metric is set correctly for a black pawn."""
        piece = _Piece(name="p", row=0, col=0)
        assert piece._set_move_metric() == [(-1, 0)]

    def test_set_move_metric_piece(self):
        """Test that the move metric is set correctly for a piece."""
        piece = _Piece(name="B", row=0, col=0)
        assert piece._set_move_metric() == [(1, 1), (-1, 1), (-1, -1), (1, -1)]

    def test_update_position(self):
        """Test that the update_position method updates the _has_moved and position_history attributes correctly."""
        piece = _Piece(name="P", row=0, col=0)
        piece.update_position(row=1, col=0, ply_number=1)
        position = _Position(row=1, col=0)
        assert piece._has_moved is True and piece.position_history[-1] == (1, position)

    def test_get_situational_directions_piece(self):
        """Test that the _get_situational_directions method returns an empty list for a piece."""
        piece = _Piece(name="N", row=0, col=0)
        situational_directions = piece._get_situational_directions(board=np.empty((8, 8)), ply_number=1)
        assert situational_directions == []

    def test_get_situational_directions_pawn(self):
        pass
