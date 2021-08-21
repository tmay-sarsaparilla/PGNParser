"""Module for defining pieces"""

import numpy as np
from typing import List, Tuple
from .position import _Position


class _Piece:
    """
    A class for chess pieces.

    Attributes:
        _name (str): The name of the piece e.g. 'P' is a white pawn.
        _is_white (bool): Indicator for whether the piece is white or not.
        _rank (str): The rank of a piece e.g. 'R' for rook, 'B' for bishop etc.
        _unicode (str): Unicode representation of the piece.
        position (_Position): Current position of the piece.
        move_metric (list): List of directions the piece can move in.
        _has_moved (bool): Indicator of whether the piece has moved or not.
        position_history (tuple): Tuple of positions the piece has occupied and the move number.
    """

    __valid_piece_names = ["P", "N", "B", "R", "Q", "K"]

    __rook_move_metric = [(1, 0), (0, 1), (0, -1), (-1, 0)]
    __bishop_move_metric = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

    __move_metrics = {
        "N": [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)],
        "B": __bishop_move_metric,
        "R": __rook_move_metric,
        "Q": __bishop_move_metric + __rook_move_metric,
        "K": __bishop_move_metric + __rook_move_metric
    }

    __unicode_lookup = {
        "K": "♔",
        "Q": "♕",
        "R": "♖",
        "B": "♗",
        "N": "♘",
        "P": "♙",
        "k": "♚",
        "q": "♛",
        "r": "♜",
        "b": "♝",
        "n": "♞",
        "p": "♟"
    }

    def __init__(self, name: str, row: int, col: int) -> None:
        """
        Constructor method for the _Piece class.

        Args:
            name (str): Name of the piece e.g. 'P' is a white pawn.
            row (int): Row number of the piece's position.
            col (int): Column number of the piece's position.

        Raises:
            ValueError: If given name is not a valid piece name.
        """
        if name.upper() not in _Piece.__valid_piece_names:
            raise ValueError(f"{name} is not a valid piece name")
        self._name = name
        self._is_white = True if name == name.upper() else False
        self._rank = name.upper()
        self._unicode = _Piece.__unicode_lookup[self.name]
        self.position = _Position(row=row, col=col)
        self.move_metric = self._set_move_metric()
        self._has_moved = False
        self.position_history = [(0, self.position)]

    def __str__(self) -> str:
        return self.unicode

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """Get name."""
        return self._name

    @property
    def is_white(self) -> bool:
        """Get is_white."""
        return self._is_white

    @property
    def rank(self) -> str:
        """Get rank."""
        return self._rank

    @property
    def unicode(self) -> str:
        """Get unicode."""
        return self._unicode

    def _set_move_metric(self) -> List[Tuple[int, int]]:
        """
        Set the list of move metrics for the piece.

        Returns:
            (list): A list of possible directions the piece can move in.
        """
        if self.rank == "P":
            if self.is_white:
                return [(1, 0)]
            else:
                return [(-1, 0)]
        else:
            return _Piece.__move_metrics[self.rank]

    def update_position(self, row: int, col: int, ply_number: int) -> None:
        """
        Update the position of a piece with a new position.

        Args:
            row (int): Row number of the new position.
            col (int): Column number of the new position.
            ply_number (int): The number of ply played in the game so far.
        """
        self.position = _Position(row=row, col=col)
        self.position_history.append((ply_number, self.position))
        self._has_moved = True
        return

    def _get_situational_directions(self, board: np.ndarray, ply_number: int) -> List[Tuple[int, int]]:
        """
        Get a list of situational directions.

        These include:
            - Pawn moving two squares on its first move
            - Pawn capturing a piece
            - Pawn capturing a piece en passant

        Args:
            board (np.ndarray): The game board.
            ply_number (int): The current ply number.

        Returns:
            situational_directions (list): A list of directions the piece can move in.
        """
        if self.rank != "P":  # pieces other than pawns have no additional directions
            return []

        situational_directions = []
        if not self._has_moved:  # pawn can move forward two squares on its first move
            if self.is_white:
                if board[self.position.row + 1, self.position.col] is None:  # but only if it isn't blocked in
                    situational_directions.append((2, 0))
            else:
                if board[self.position.row - 1, self.position.col] is None:
                    situational_directions.append((-2, 0))

        capture_moves = [(1, -1), (1, 1)] if self.is_white else [(-1, -1), (-1, 1)]

        for direction in capture_moves:  # diagonal moves only possible when capturing a piece
            position = _Position(
                row=self.position.row + direction[0],
                col=self.position.col + direction[1]
            )
            if not position.is_legal:
                continue
            position_inhabitant = board[position.row, position.col]

            if position_inhabitant is None:  # if there is no piece, skip
                continue
            if position_inhabitant.is_white != self.is_white:  # if the piece is of the opposite colour
                situational_directions.append(direction)  # a capture is possible

        # En passant only applies to pawns on the 6th row (for white) and the 3rd row (for black)
        if self.is_white:
            en_passant_applicable = self.position.row == 4
        else:
            en_passant_applicable = self.position.row == 3
        if not en_passant_applicable:
            return situational_directions

        for direction in capture_moves:
            position = _Position(  # check adjacent squares in the same column as the pawn
                row=self.position.row,
                col=self.position.col + direction[1]
            )
            if not position.is_legal:
                continue

            position_inhabitant = board[position.row, position.col]
            if position_inhabitant is None:  # if there is no piece skip
                continue

            can_capture = (
                    position_inhabitant.is_white != self.is_white  # opponent colour
                    and position_inhabitant.rank == "P"  # is a pawn
                    and len(position_inhabitant.position_history) == 2  # has only moved once
                    and position_inhabitant.position_history[-1][0] == ply_number  # has just moved
            )
            if can_capture:
                if direction not in situational_directions:
                    situational_directions.append(direction)
        return situational_directions

    def get_possible_positions(self, board: np.ndarray, ply_number: int) -> List[_Position]:
        """
        Determine all possible legal positions which the piece can move to.

        Args:
            board (np.ndarray): The game board.
            ply_number (int): The current move number.

        Returns:
            possible_positions (list): A list of possible positions the piece can move to.
        """
        max_move = 1 if self.rank in ["P", "N", "K"] else 7
        situational_directions = self._get_situational_directions(board=board, ply_number=ply_number)
        possible_positions = []
        for direction in self.move_metric + situational_directions:
            for i in range(1, max_move + 1):
                new_position = _Position(
                    row=self.position.row + i * direction[0],
                    col=self.position.col + i * direction[1]
                )
                if not new_position.is_legal:
                    break

                position_inhabitant = board[new_position.row, new_position.col]

                if position_inhabitant is None:  # position is empty
                    possible_positions.append(new_position)  # add as candidate position and continue
                    continue
                elif position_inhabitant.is_white != self.is_white:  # pieces are of opposite colour
                    if self.rank == "P" and new_position.col == self.position.col:  # pawn can't capture forwards
                        break
                    possible_positions.append(new_position)  # add as candidate position then stop
                    break
                else:
                    # pieces are of same colour, stop
                    break

        return possible_positions
