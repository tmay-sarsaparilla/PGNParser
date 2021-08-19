
from .position import _Position


class _Ply:
    """Class representing a ply."""

    __row_names = "12345678"
    __col_names = "hgfedcba"

    def __init__(
            self,
            ply_string: str,
            piece_rank: str = None,
            piece_col: str = None,
            piece_row: str = None,
            new_col: str = None,
            new_row: str = None,
            promoted_piece_rank: str = None,
            castle_king_side: bool = False,
            castle_queen_side: bool = False,
            is_capture: bool = False
    ) -> None:
        self.ply_string = ply_string
        self.piece_rank = piece_rank
        self.piece_row = piece_row
        self.piece_col = piece_col
        self.piece_row_number = _Ply.__row_names.index(self.piece_row) if self.piece_row is not None else None
        self.piece_col_number = _Ply.__col_names.index(self.piece_col) if self.piece_col is not None else None
        if new_row is not None and new_col is not None:
            self.new_position = _Position(
                row=_Ply.__row_names.index(new_row),
                col=_Ply.__col_names.index(new_col)
            )
        else:
            self.new_position = None
        self.promoted_piece_rank = promoted_piece_rank
        self.castle_king_side = castle_king_side
        self.castle_queen_side = castle_queen_side
        self.is_capture = is_capture


class UnrecognisedPlyError(Exception):
    """
    Exception raised when a ply string is not recognised by the Interpreter.

    Args:
        ply_string (str): The unrecognised ply string.
        message (str): The error message to raise.
    """

    def __init__(self, ply_string: str, message: str = "Move string is not recognised"):
        self.ply_string = ply_string
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.ply_string}: {self.message}"
