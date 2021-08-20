
from .position import _Position


class _Ply:
    """Class representing a ply.

    Attributes:
        ply_string (str): The string representation of the ply.
        piece_rank (str): The rank of the piece being moved.
        piece_col (str): The initial column of the piece being moved.
        piece_row (str): The initial row of the piece being moved.
        piece_row_number (int): The initial row number of the piece being moved.
        piece_col_number (int): The initial column number of the piece being moved.
        new_position (_Position): The new position of the piece.
        promoted_piece_rank (str): The rank of the piece promoted to during the move (if any).
        castle_king_side (bool): Indicator of whether the ply is a king-side castle.
        castle_queen_side (bool): Indicator of whether the ply is a queen-side castle.
        is_capture (bool): Indicator of whether the ply is a capture.
    """

    __row_names = "12345678"
    __col_names = "hgfedcba"

    def __init__(
            self,
            ply_string: str,
            piece_rank: str = None,
            piece_col: str = None,
            piece_row: str = None,
            new_position_name: str = None,
            promoted_piece_rank: str = None,
            castle_king_side: bool = False,
            castle_queen_side: bool = False,
            is_capture: bool = False
    ) -> None:
        """Constructor method for the _Ply class.

        Args:
            ply_string (str): The string representation of the ply.
            piece_rank (str): The rank of the piece being moved (default None).
            piece_col (str): The initial column of the piece being moved (default None).
            piece_row (str): The initial row of the piece being moved (default None).
            new_position_name (str): The name of the new position of the piece (default None).
            promoted_piece_rank (str): The rank of the piece promoted to during the move (if any) (default None).
            castle_king_side (bool): Indicator of whether the ply is a king-side castle (default False).
            castle_queen_side (bool): Indicator of whether the ply is a queen-side castle (default False).
            is_capture (bool): Indicator of whether the ply is a capture (default False).
        """
        self.ply_string = ply_string
        self.piece_rank = piece_rank
        self.piece_row = piece_row
        self.piece_col = piece_col
        self.piece_row_number = _Ply.__row_names.index(self.piece_row) if self.piece_row is not None else None
        self.piece_col_number = _Ply.__col_names.index(self.piece_col) if self.piece_col is not None else None
        if new_position_name is not None:
            self.new_position = _Position.from_name(name=new_position_name)
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
