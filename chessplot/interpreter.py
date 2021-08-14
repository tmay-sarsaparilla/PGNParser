"""
Module containing all classes used by the chessplot package.
"""

import numpy as np
import re
from typing import List, Tuple
import copy


class _Position:
    """
    A class for piece positions.

    Attributes:
        _row (int): The row number of the position.
        _col (int): The column number of the position.
        _name (str): The name of the position e.g. 'a4'.
        _is_legal (bool): Indicator of whether the position is legal or not i.e. on the board.
    """

    __row_names = "12345678"
    __col_names = "hgfedcba"

    def __init__(self, row: int, col: int) -> None:
        """
        Constructor method for the _Position class.

        Args:
             row (int): Row number of the position.
             col (int): Column number of the position.
        """
        self._row = row
        self._col = col
        self._name = self._set_name()
        self._is_legal = self._check_legality()

    @property
    def row(self) -> int:
        """Get row."""
        return self._row

    @property
    def col(self) -> int:
        """Get col."""
        return self._col

    @property
    def name(self) -> str:
        """Get name."""
        return self._name

    @property
    def is_legal(self) -> bool:
        """Get is_legal."""
        return self._is_legal

    def __repr__(self) -> str:
        """Repr method for the Position class."""
        return repr(self.name)

    def __eq__(self, other: object) -> bool:
        """__eq__ method for the Position class."""
        if not isinstance(other, _Position):
            return NotImplemented(f"Cannot compare type Position with type {type(other)}.")
        if self.row == other.row and self.col == other.col:
            return True
        else:
            return False

    def _set_name(self) -> str:
        """Set the name of the position."""
        try:
            return self.__col_names[self.col] + self.__row_names[self.row]
        except IndexError:
            return ""

    def _check_legality(self) -> bool:
        """
        Check whether a position is legal.

        If a position lies off the board, it is illegal.
        """
        if self.row < 0 or self.row >= 8:
            return False
        elif self.col < 0 or self.col >= 8:
            return False
        else:
            return True


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
        """
        assert name.upper() in _Piece.__valid_piece_names, f"{name} is not a valid piece name"
        self._name = name
        self._is_white = True if name == name.upper() else False
        self._rank = name.upper()
        self._unicode = _Piece.__unicode_lookup[self.name]
        self.position = _Position(row=row, col=col)
        self.move_metric = self._set_move_metric()
        self._has_moved = False
        self.position_history = [(0, self.position)]

    def __repr__(self) -> str:
        """Repr method for the Piece class."""
        return repr(self.name)

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

    def __repr__(self) -> str:
        """Repr method for the Game class."""
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

    def execute_move(self, ply_string: str, white_to_move: bool) -> None:
        """
        Execute a given move.

        Args:
            ply_string (str): The move string to be executed e.g. 'Bxe4'.
            white_to_move (bool): Indicator of whether it's white's move or not.

        Raises:
            UnrecognisedPlyError: If the given ply string could not be parsed.
            InterpreterError: If the given ply could not be executed.
        """
        row_names = "12345678"
        col_names = "hgfedcba"

        # First parse the given move string
        castle_king_side = False
        castle_queen_side = False
        piece_rank = None
        piece_col = None
        piece_row = None
        new_col_str = None
        new_row_str = None
        promoted_piece_rank = None

        ply_string = ply_string.replace("+", "").replace("#", "")  # remove check indicators

        if re.match("^[a-h][1-8]$", string=ply_string):  # pawn move
            piece_rank = "P"
            new_col_str = ply_string[0]
            new_row_str = ply_string[1]
        elif re.match("^[a-h]x[a-h][1-8]$", string=ply_string):  # pawn capture
            piece_rank = "P"
            piece_col = ply_string[0]
            new_col_str = ply_string[2]
            new_row_str = ply_string[3]
        elif re.match("^[a-h][1-8]=[NBRQ]$", string=ply_string):  # pawn promotion
            piece_rank = "P"
            new_col_str = ply_string[0]
            new_row_str = ply_string[1]
            promoted_piece_rank = ply_string[3]
        elif re.match("^[a-h]x[a-h][1-8]=[NBRQ]$", string=ply_string):  # pawn promotion
            piece_rank = "P"
            piece_col = ply_string[0]
            new_col_str = ply_string[2]
            new_row_str = ply_string[3]
            promoted_piece_rank = ply_string[5]
        elif re.match("^[NBRQK][a-h][1-8]$", string=ply_string):  # piece move
            piece_rank = ply_string[0]
            new_col_str = ply_string[1]
            new_row_str = ply_string[2]
        elif re.match("^[NBRQK][a-h][a-h][1-8]$", string=ply_string):  # piece move, ambiguous column
            piece_rank = ply_string[0]
            piece_col = ply_string[1]
            new_col_str = ply_string[2]
            new_row_str = ply_string[3]
        elif re.match("^[NBRQK][1-8][a-h][1-8]$", string=ply_string):  # piece move, ambiguous row
            piece_rank = ply_string[0]
            piece_row = ply_string[1]
            new_col_str = ply_string[2]
            new_row_str = ply_string[3]
        elif re.match("^[NBRQK][a-h][1-8][a-h][1-8]$", string=ply_string):  # piece move, ambiguous row and column
            piece_rank = ply_string[0]
            piece_col = ply_string[1]
            piece_row = ply_string[2]
            new_col_str = ply_string[3]
            new_row_str = ply_string[4]
        elif re.match("^[NBRQK]x[a-h][1-8]$", string=ply_string):  # piece capture
            piece_rank = ply_string[0]
            new_col_str = ply_string[2]
            new_row_str = ply_string[3]
        elif re.match("^[NBRQK][a-h]x[a-h][1-8]$", string=ply_string):  # piece capture, ambiguous column:
            piece_rank = ply_string[0]
            piece_col = ply_string[1]
            new_col_str = ply_string[3]
            new_row_str = ply_string[4]
        elif re.match("^[NBRQK][1-8]x[a-h][1-8]$", string=ply_string):  # piece capture, ambiguous row:
            piece_rank = ply_string[0]
            piece_row = ply_string[1]
            new_col_str = ply_string[3]
            new_row_str = ply_string[4]
        elif re.match("^[NBRQK][a-h][1-8]x[a-h][1-8]$", string=ply_string):  # piece capture, ambiguous row and column:
            piece_rank = ply_string[0]
            piece_col = ply_string[1]
            piece_row = ply_string[2]
            new_col_str = ply_string[4]
            new_row_str = ply_string[5]
        elif re.match("^O-O$|^0-0$|^O-O-O$|^0-0-0$", string=ply_string):  # castle
            if ply_string == "O-O" or ply_string == "0-0":
                castle_king_side = True
            else:
                castle_queen_side = True
        else:
            raise UnrecognisedPlyError(ply_string=ply_string)

        if castle_king_side or castle_queen_side:
            self._castle(white_to_move=white_to_move, castle_king_side=castle_king_side)
            return

        new_col = int(col_names.index(new_col_str))
        new_row = int(row_names.index(new_row_str))
        new_position = _Position(row=new_row, col=new_col)
        is_capture = True if "x" in ply_string else False

        candidate_pieces = []
        for row in range(0, 8):
            for col in range(0, 8):
                piece = self._board[row, col]
                if piece is None:  # if square is empty, skip
                    continue
                if piece.is_white != white_to_move:  # if piece is the wrong colour, skip
                    continue
                is_candidate_piece = (
                        piece.rank == piece_rank
                        and new_position in piece.get_possible_positions(self._board, ply_number=self._ply_count)
                )
                if is_candidate_piece:
                    candidate_pieces.append(piece)

        if len(candidate_pieces) == 1:
            self._move_piece(
                piece=candidate_pieces[0],
                row=new_row,
                col=new_col,
                promoted_piece_rank=promoted_piece_rank,
                is_capture=is_capture
            )
            return
        elif len(candidate_pieces) >= 2:
            if piece_row is not None and piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.name == piece_col + piece_row
                ]
                self._move_piece(
                    piece=piece,
                    row=new_row,
                    col=new_col,
                    promoted_piece_rank=promoted_piece_rank,
                    is_capture=is_capture
                )
                return
            elif piece_row is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.row == int(row_names.index(piece_row))
                ]
                self._move_piece(
                    piece=piece,
                    row=new_row,
                    col=new_col,
                    promoted_piece_rank=promoted_piece_rank,
                    is_capture=is_capture
                )
                return
            elif piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.col == int(col_names.index(piece_col))
                ]
                self._move_piece(
                    piece=piece,
                    row=new_row,
                    col=new_col,
                    promoted_piece_rank=promoted_piece_rank,
                    is_capture=is_capture
                )
                return

        raise InterpreterError(ply_string=ply_string)

    def get_board(self) -> np.ndarray:
        """
        Get a copy of the current game board.

        Returns:
            (np.ndarray): Current game board.
        """

        return copy.deepcopy(self._board)


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
