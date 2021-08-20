"""
Module containing all classes used by the chessplot package.
"""

import numpy as np
import copy
import re
from .piece import _Piece
from .ply import _Ply, UnrecognisedPlyError


class _Interpreter:
    """
    A class for interpreting chess moves.

    Attributes:
        _piece_positions (str): A string denoting the starting position of the game.
        _board (np.ndarray): The game board.
        _ply_count (int): A count of the number of moves played in the game.
    """

    def __init__(self, piece_positions: str) -> None:
        """
        Constructor method for the _Interpreter class.

        Args:
            piece_positions (str): A string describing the initial state of the board.
        """
        self._piece_positions = piece_positions
        self._board = self._generate_board()
        self._ply_count = 0

    def __str__(self) -> str:
        print_grid = np.vstack(([["h", "g", "f", "e", "d", "c", "b", "a"]], self._board))
        print_grid = np.hstack((print_grid, [[" "], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"], ["8"]]))
        return str(np.flip(print_grid)).replace("None", " - ") + "\n"

    def _generate_board(self) -> np.ndarray:
        """
        Generate a board from a given FEN code.

        Returns:
            board (np.ndarray): An 8x8 array populated with Pieces depicting the game board.
        """
        board = np.empty((8, 8), dtype=_Piece)

        row = 7
        col = 7
        for char in self._piece_positions:
            if char == "/":
                row -= 1
                col = 7
            elif str.isdigit(char):
                col -= int(char)
            else:
                board[row, col] = _Piece(name=char, row=row, col=col)
                col -= 1

        return board

    def _move_piece(
            self,
            piece: _Piece,
            row: int,
            col: int,
            promoted_piece_rank: str = None,
            is_capture: bool = False
    ) -> None:
        """
        Move a piece on the board.

        Args:
            piece (_Piece): The piece to be moved.
            row (int): The row number to move the piece to.
            col (int): The column number to move the piece to.
            promoted_piece_rank (str): Rank of piece to promote to (default None).
            is_capture (bool): Indicator for whether the move is a capture or not (default False).
        """
        current_row = piece.position.row
        current_col = piece.position.col

        if is_capture and self._board[row, col] is None:
            en_passant = True
        else:
            en_passant = False

        self._ply_count += 1
        self._board[current_row, current_col] = None
        piece.update_position(row=row, col=col, ply_number=self._ply_count)
        if promoted_piece_rank is not None:  # if pawn promotion, create a new piece at the new position
            new_piece_name = promoted_piece_rank.lower() if not piece.is_white else promoted_piece_rank
            new_piece = _Piece(name=new_piece_name, row=row, col=col)
            self._board[row, col] = new_piece
        else:  # otherwise move the existing piece
            self._board[row, col] = piece

        if en_passant:
            self._board[current_row, col] = None  # if en passant capture, remove the captured piece
        return

    def _castle(self, white_to_move: bool, castle_king_side: bool) -> None:
        """
        Execute castling of pieces on given side and for given colour.

        Args:
            white_to_move (bool): Indicator of whether it's white's move or not.
            castle_king_side (bool): Indicator of whether to castle king-side or not.
        """
        if white_to_move:
            king = self._board[0, 3]
            if castle_king_side:
                rook = self._board[0, 0]
            else:
                rook = self._board[0, 7]
        else:
            king = self._board[7, 3]
            if castle_king_side:
                rook = self._board[7, 0]
            else:
                rook = self._board[7, 7]

        if castle_king_side:
            self._move_piece(piece=king, row=king.position.row, col=king.position.col - 2)
            self._move_piece(piece=rook, row=rook.position.row, col=rook.position.col + 2)
        else:
            self._move_piece(piece=king, row=king.position.row, col=king.position.col + 2)
            self._move_piece(piece=rook, row=rook.position.row, col=rook.position.col - 3)

        return

    def execute_ply(self, ply: _Ply, white_to_move: bool) -> None:
        """
        Execute a given ply.

        Args:
            ply (_Ply): The ply to be executed.
            white_to_move (bool): Indicator of whether it's white's move or not.

        Raises:
            InterpreterError: If the given ply could not be executed.
        """

        if ply.castle_king_side or ply.castle_queen_side:
            self._castle(white_to_move=white_to_move, castle_king_side=ply.castle_king_side)
            return

        candidate_pieces = []
        for row in range(0, 8):
            for col in range(0, 8):
                piece = self._board[row, col]
                if piece is None:  # if square is empty, skip
                    continue
                if piece.is_white != white_to_move:  # if piece is the wrong colour, skip
                    continue
                is_candidate_piece = (
                        piece.rank == ply.piece_rank
                        and ply.new_position in piece.get_possible_positions(self._board, ply_number=self._ply_count)
                )
                if is_candidate_piece:
                    candidate_pieces.append(piece)

        if len(candidate_pieces) == 1:
            self._move_piece(
                piece=candidate_pieces[0],
                row=ply.new_position.row,
                col=ply.new_position.col,
                promoted_piece_rank=ply.promoted_piece_rank,
                is_capture=ply.is_capture
            )
            return
        elif len(candidate_pieces) >= 2:
            if ply.piece_row is not None and ply.piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.name == ply.piece_col + ply.piece_row
                ]
                self._move_piece(
                    piece=piece,
                    row=ply.new_position.row,
                    col=ply.new_position.col,
                    promoted_piece_rank=ply.promoted_piece_rank,
                    is_capture=ply.is_capture
                )
                return
            elif ply.piece_row is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.row == ply.piece_row_number
                ]
                self._move_piece(
                    piece=piece,
                    row=ply.new_position.row,
                    col=ply.new_position.col,
                    promoted_piece_rank=ply.promoted_piece_rank,
                    is_capture=ply.is_capture
                )
                return
            elif ply.piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.col == ply.piece_col_number
                ]
                self._move_piece(
                    piece=piece,
                    row=ply.new_position.row,
                    col=ply.new_position.col,
                    promoted_piece_rank=ply.promoted_piece_rank,
                    is_capture=ply.is_capture
                )
                return

        raise InterpreterError(ply_string=ply.ply_string)

    def get_board(self) -> np.ndarray:
        """
        Get a copy of the current game board.

        Returns:
            (np.ndarray): Current game board.
        """

        return copy.deepcopy(self._board)


class InterpreterError(Exception):
    """
    Exception raised when the Interpreter cannot execute a given ply.

    Args:
        ply_string (str): The ply which could not be executed.
        message (str): The error message to raise.
    """

    def __init__(self, ply_string: str, message: str = "Could not execute given move"):
        self.ply_string = ply_string
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.ply_string}: {self.message}"
