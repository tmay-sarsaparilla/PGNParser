
import numpy as np
import re
import datetime
from PIL import Image, ImageDraw, ImageFont


class Piece:
    """
    A class for chess pieces.

    Attributes:
        _name (str): The name of the piece e.g. 'P' is a white pawn.
        _is_white (bool): Indicator for whether the piece is white or not.
        _rank (str): The rank of a piece e.g. 'R' for rook, 'B' for bishop etc.
        _unicode (str): Unicode representation of the piece.
        position (Position): Current position of the piece.
        move_metric (list): List of directions the piece can move in.
        _has_moved (bool): Indicator of whether the piece has moved or not.
        _position_history (tuple): Tuple of positions the piece has occupied and the move number.
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

    def __init__(self, name, row, col):
        """
        Constructor method for the Piece class.

        Parameters:
            name (str): Name of the piece e.g. 'P' is a white pawn.
            row (int): Row number of the piece's position.
            col (int): Column number of the piece's position.
        """
        assert name.upper() in Piece.__valid_piece_names, f"{name} is not a valid piece name"
        self._name = name
        self._is_white = True if name == name.upper() else False
        self._rank = name.upper()
        self._unicode = Piece.__unicode_lookup[self.name]
        self.position = Position(row=row, col=col)
        self.move_metric = self.set_move_metric()
        self._has_moved = False
        self._position_history = [(0, self.position)]

    def __repr__(self):
        """Repr method for the Piece class."""
        return repr(self.name)

    @property
    def name(self):
        """Get function for the 'name' property."""
        return self._name

    @property
    def is_white(self):
        """Get function for the 'is_white' property."""
        return self._is_white

    @property
    def rank(self):
        """Get function for the 'rank' property."""
        return self._rank

    @property
    def unicode(self):
        """Get function for the 'unicode' property."""
        return self._unicode

    def set_move_metric(self):
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
            return Piece.__move_metrics[self.rank]

    def update_position(self, row, col, move_number):
        """
        Update the position of a piece with a new position.

        Parameters:
            row (int): Row number of the new position.
            col (int): Column number of the new position.
            move_number (int): The current move number in the game.
        """
        self.position = Position(row=row, col=col)
        self._position_history.append((move_number, self.position))
        self._has_moved = True
        return

    def get_situational_directions(self, board, move_number):
        """
        Get a list of situational directions.

        These include:
        - Pawn moving two squares on its first move
        - Pawn capturing a piece
        - Pawn capturing a piece en passant

        Parameters:
            board (np.ndarray): The game board.
            move_number (int): The current move number.

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
            position = Position(
                row=self.position.row + direction[0],
                col=self.position.col + direction[1]
            )
            if not position.is_legal:
                continue
            position_inhabitant = board[position.row, position.col]

            if position_inhabitant is None:  # if there is no piece, skip
                continue
            if position_inhabitant.is_white != self.is_white:  # if the piece is of the opposite colour
                situational_directions.append(direction)       # a capture is possible

        # En passant only applies to pawns on the 6th row (for white) and the 3rd row (for black)
        if (self.is_white and self.position.row != 5) or (not self.is_white and self.position.row != 2):
            return situational_directions
        for direction in capture_moves:
            position = Position(  # check adjacent squares in the same column as the pawn
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
                    and position_inhabitant.position_history[-1][0] == move_number  # has just moved
            )
            if can_capture:
                if direction not in situational_directions:
                    situational_directions.append(direction)
        return situational_directions

    def get_possible_positions(self, board, move_number):
        """
        Determine all possible legal positions which the piece can move to.

        Parameters:
            board (np.ndarray): The game board.
            move_number (int): The current move number.

        Returns:
            possible_positions (list): A list of possible positions the piece can move to.
        """
        max_move = 1 if self.rank in ["P", "N", "K"] else 7
        situational_directions = self.get_situational_directions(board=board, move_number=move_number)
        possible_positions = []
        for direction in self.move_metric + situational_directions:
            for i in range(1, max_move + 1):
                new_position = Position(
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


class Position:
    """
    A class for piece positions.

    Attributes:
        row (int): The row number of the position.
        col (int): The column number of the position.
        name (str): The name of the position e.g. 'a4'.
        is_legal (bool): Indicator of whether the position is legal or not i.e. on the board.
    """

    __row_names = "12345678"
    __col_names = "hgfedcba"

    def __init__(self, row, col):
        """
        Constructor method for the Position class.

        Parameters:
             row (int): Row number of the position.
             col (int): Column number of the position.
        """
        self.row = row
        self.col = col
        self.name = self._set_name()
        self.is_legal = self._check_legality()

    def __repr__(self):
        """Repr method for the Position class."""
        return repr(self.name)

    def __eq__(self, other):
        """__eq__ method for the Position class."""
        if self.row == other.row and self.col == other.col:
            return True
        else:
            return False

    def _set_name(self):
        """Set the name of the position."""
        try:
            return self.__col_names[self.col] + self.__row_names[self.row]
        except IndexError:
            return ""

    def _check_legality(self):
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


class Game:
    """
    A class for chess games.

    Attributes:
        _fen (str): A FEN string for the starting position of the game.
        _event (str): The event the game was played at.
        _site (str): The location the game was played at.
        _date (str): The date the game was played on.
        _formatted_date (str): A formatted version of the date.
        _event_round (str): The round of the event the game was played in.
        _white (str): The name of the player with the white pieces.
        _black (str): The name of the player with the black pieces.
        _white_elo (str): The Elo rating of the player with the white pieces.
        _black_elo (str): The Elo rating of the player with the black pieces.
        _result (str): The final result of the game.
        _board (np.ndarray): The game board.
        _move_count (int): A count of the number of moves played in the game.
    """

    __default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    def __init__(self, tags):
        """
        Constructor method for the Game class.

        Parameters:
            tags (dict): A dictionary of metadata tags from a .pgn file.
        """
        self._tags = tags
        self._fen = self._get_tag_value(tag_key="FEN", default_value=Game.__default_fen)
        self._event = self._get_tag_value(tag_key="Event")
        self._site = self._get_tag_value(tag_key="Site")
        self._date = self._get_tag_value(tag_key="Date")
        self._event_round = self._get_tag_value(tag_key="Round")
        self._white = self._get_tag_value(tag_key="White", default_value="Unknown")
        self._black = self._get_tag_value(tag_key="Black", default_value="Unknown")
        self._white_elo = self._get_tag_value(tag_key="WhiteElo")
        self._black_elo = self._get_tag_value(tag_key="BlackElo")
        self._result = self._get_tag_value(tag_key="Result")
        self._formatted_date = self._format_date()
        self._board = self._generate_board()
        self._move_count = 0

    def __repr__(self):
        """Repr method for the Game class."""
        print_grid = np.vstack(([["h", "g", "f", "e", "d", "c", "b", "a"]], self._board))
        print_grid = np.hstack((print_grid, [[" "], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"], ["8"]]))
        return str(np.flip(print_grid)).replace("None", " - ") + "\n"

    def _get_tag_value(self, tag_key, default_value=""):
        """
        Get the value corresponding to a given tag key.

        Parameters:
            tag_key (str): The key of the desired tag.
            default_value (str): The default value in the event that the tag is not present.
        """
        try:
            return self._tags[tag_key]
        except KeyError:
            return default_value

    def _format_date(self):
        """
        Format game date.

        Returns:
            date (str): A formatted version of the original date field.
        """
        year, month, day = self._date.split(".")
        if year == "??":
            date = None
        elif month == "??":
            date = year
        elif day == "??":
            date = datetime.date(int(year), int(month), 0).strftime("%A %d %B %Y")
        else:
            date = datetime.date(int(year), int(month), int(day)).strftime("%A %d %B %Y")
        return date

    def _generate_board(self):
        """
        Generate a board from a given FEN code.

        Returns:
            board (np.ndarray): An 8x8 array populated with Pieces depicting the game board.
        """
        board = np.empty((8, 8), dtype=Piece)

        row = 7
        col = 7
        for char in self._fen:
            if char == "/":
                row -= 1
                col = 7
            elif str.isdigit(char):
                col -= int(char)
            else:
                board[row, col] = Piece(name=char, row=row, col=col)
                col -= 1

        return board

    def _move_piece(self, piece, row, col, promoted_piece_rank=None):
        """
        Move a piece on the board.

        Parameters:
            piece (Piece): The piece to be moved.
            row (int): The row number to move the piece to.
            col (int): The column number to move the piece to.
            promoted_piece_rank (str): Rank of piece to promote to (if any).
        """
        current_row = piece.position.row
        current_col = piece.position.col

        self._board[current_row, current_col] = None
        piece.update_position(row=row, col=col, move_number=self._move_count)
        if promoted_piece_rank is not None:  # if pawn promotion, create a new piece at the new position
            new_piece_name = promoted_piece_rank.lower() if not piece.is_white else promoted_piece_rank
            new_piece = Piece(name=new_piece_name, row=row, col=col)
            self._board[row, col] = new_piece
        else:  # otherwise move the existing piece
            self._board[row, col] = piece
        self._move_count += 1
        return

    def _castle(self, white_to_move, castle_king_side):
        """
        Execute castling of pieces on given side and for given colour.

        Parameters:
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

    def execute_move(self, move_string, white_to_move):
        """
        Execute a given move.

        Parameters:
            move_string (str): The move string to be executed e.g. 'Bxe4'.
            white_to_move (bool): Indicator of whether it's white's move or not.

        Raises:
            ValueError: If move string if the format of the string is not recognised or if the move cannot be executed.
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

        if re.match("[a-h][1-8]", string=move_string):  # pawn move
            piece_rank = "P"
            new_col_str = move_string[0]
            new_row_str = move_string[1]
        elif re.match("[a-h]x[a-h][1-8]", string=move_string):  # pawn capture
            piece_rank = "P"
            piece_col = move_string[0]
            new_col_str = move_string[2]
            new_row_str = move_string[3]
        elif re.match("[a-h][1-8]=[NBRQ]", string=move_string):  # pawn promotion
            piece_rank = "P"
            new_col_str = move_string[0]
            new_row_str = move_string[1]
            promoted_piece_rank = move_string[3]
        elif re.match("[a-h]x[a-h][1-8]=[NBRQ]", string=move_string):  # pawn promotion
            piece_rank = "P"
            piece_col = move_string[0]
            new_col_str = move_string[2]
            new_row_str = move_string[3]
            promoted_piece_rank = move_string[5]
        elif re.match("[NBRQK][a-h][1-8]", string=move_string):  # piece move
            piece_rank = move_string[0]
            new_col_str = move_string[1]
            new_row_str = move_string[2]
        elif re.match("[NBRQK][a-h][a-h][1-8]", string=move_string):  # piece move, ambiguous column
            piece_rank = move_string[0]
            piece_col = move_string[1]
            new_col_str = move_string[2]
            new_row_str = move_string[3]
        elif re.match("[NBRQK][1-8][a-h][1-8]", string=move_string):  # piece move, ambiguous row
            piece_rank = move_string[0]
            piece_row = move_string[1]
            new_col_str = move_string[2]
            new_row_str = move_string[3]
        elif re.match("[NBRQK][a-h][1-8][a-h][1-8]", string=move_string):  # piece move, ambiguous row and column
            piece_rank = move_string[0]
            piece_col = move_string[1]
            piece_row = move_string[2]
            new_col_str = move_string[3]
            new_row_str = move_string[4]
        elif re.match("[NBRQK]x[a-h][1-8]", string=move_string):  # piece capture
            piece_rank = move_string[0]
            new_col_str = move_string[2]
            new_row_str = move_string[3]
        elif re.match("[NBRQK][a-h]x[a-h][1-8]", string=move_string):  # piece capture, ambiguous column:
            piece_rank = move_string[0]
            piece_col = move_string[1]
            new_col_str = move_string[3]
            new_row_str = move_string[4]
        elif re.match("[NBRQK][1-8]x[a-h][1-8]", string=move_string):  # piece capture, ambiguous row:
            piece_rank = move_string[0]
            piece_row = move_string[1]
            new_col_str = move_string[3]
            new_row_str = move_string[4]
        elif re.match("[NBRQK][a-h][1-8]x[a-h][1-8]", string=move_string):  # piece capture, ambiguous row and column:
            piece_rank = move_string[0]
            piece_col = move_string[1]
            piece_row = move_string[2]
            new_col_str = move_string[4]
            new_row_str = move_string[5]
        elif re.match("O-O|0-0", string=move_string):  # castle
            if move_string == "O-O" or move_string == "0-0":
                castle_king_side = True
            else:
                castle_queen_side = True
        else:
            raise ValueError(f"Unrecognised move_string: {move_string}")

        if castle_king_side or castle_queen_side:
            self._castle(white_to_move=white_to_move, castle_king_side=castle_king_side)
            return

        new_col = int(col_names.index(new_col_str))
        new_row = int(row_names.index(new_row_str))
        new_position = Position(row=new_row, col=new_col)

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
                        and new_position in piece.get_possible_positions(self._board, move_number=self._move_count)
                )
                if is_candidate_piece:
                    candidate_pieces.append(piece)

        if len(candidate_pieces) == 1:
            self._move_piece(
                piece=candidate_pieces[0],
                row=new_row,
                col=new_col,
                promoted_piece_rank=promoted_piece_rank
            )
            return
        elif len(candidate_pieces) >= 2:
            if piece_row is not None and piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.name == piece_col + piece_row
                ]
                self._move_piece(piece=piece, row=new_row, col=new_col, promoted_piece_rank=promoted_piece_rank)
                return
            elif piece_row is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.row == int(row_names.index(piece_row))
                ]
                self._move_piece(piece=piece, row=new_row, col=new_col, promoted_piece_rank=promoted_piece_rank)
                return
            elif piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.col == int(col_names.index(piece_col))
                ]
                self._move_piece(piece=piece, row=new_row, col=new_col, promoted_piece_rank=promoted_piece_rank)
                return

        raise ValueError(f"Invalid move: {move_string}")

    def draw_board(self, move_string=""):
        """
        Draw an image of the board in its current state.

        Parameter:
            move_string (str): A string describing the move being drawn.

        Returns:
            frame (Image): An image depicting the game board in its current state.
        """
        square_width = 60
        frame = Image.new(mode="RGB", size=(square_width * 10, int(square_width * 11.667)), color="white")
        unicode_font = ImageFont.truetype("seguisym.ttf", 50)
        black_square_colour = "#276996"
        white_square_colour = "#e2e7ee"
        draw = ImageDraw.ImageDraw(im=frame)

        x_origin, y_origin = square_width, square_width * 2.667

        # title text
        title_font = ImageFont.truetype("arial.ttf", 24)
        if self._white_elo != "" and self._black_elo != "":
            title_text = f"{self._white} ({self._white_elo}) - {self._black} ({self._black_elo})"
        else:
            title_text = f"{self._white} - {self._black}"
        draw.text(
            xy=(x_origin + square_width * 4, y_origin - square_width * 2),
            text=title_text,
            anchor="ms",
            align="center",
            font=title_font,
            fill="black"
        )

        # sub-title text
        sub_title_font = ImageFont.truetype("ariali.ttf", 18)
        sub_title_text = f"{self._site}, {self._formatted_date}" if self._formatted_date is not None else self._site
        draw.text(
            xy=(x_origin + square_width * 4, y_origin - square_width * 1.5),
            text=sub_title_text,
            anchor="ms",
            align="center",
            font=sub_title_font,
            fill="black"
        )

        # result text
        result_font = ImageFont.truetype("arialbd.ttf", 18)
        result_text = self._result
        draw.text(
            xy=(x_origin + square_width * 4, y_origin - square_width * 1),
            text=result_text,
            anchor="ms",
            align="center",
            font=result_font,
            fill="black"
        )

        # move text
        move_text_font = ImageFont.truetype("arial.ttf", 20)
        draw.text(
            xy=(x_origin, y_origin - square_width * 0.667),
            text=move_string,
            align="left",
            font=move_text_font,
            fill="black"
        )

        for i in range(0, 8):
            for j in range(0, 8):
                piece = self._board[7 - i, 7 - j]
                x = x_origin + square_width * j
                y = y_origin + square_width * i
                square_colour = white_square_colour if (i + j) % 2 == 0 else black_square_colour
                draw.rectangle(xy=((x, y), (x + square_width, y + square_width)), fill=square_colour)
                if piece is not None:
                    draw.text(
                        xy=(
                            x_origin + square_width * j + square_width * 0.5,
                            y_origin + square_width * i + square_width * 0.5
                        ),
                        text=piece.unicode,
                        anchor="mm",
                        align="center",
                        font=unicode_font,
                        fill="black"
                    )
                if i == 0:
                    draw.text(
                        xy=(x_origin - square_width * 0.5, y_origin + square_width * j + square_width * 0.5),
                        text="12345678"[7-j],
                        anchor="mm",
                        align="right",
                        font=move_text_font,
                        fill="black",
                        stroke_width=0
                    )
                if j == 7:
                    draw.text(
                        xy=(
                            x_origin + square_width * i + square_width * 0.5,
                            y_origin + square_width * 8 + square_width * 0.5
                        ),
                        text="abcdefgh"[i],
                        anchor="mm",
                        align="center",
                        font=move_text_font,
                        fill="black",
                        stroke_width=0
                    )
        return frame


class ChessPlot:
    """A class for plots of chess games.

    Attributes:
        _pgn (str): A path to a .pgn file to be plotted.
        _tags (dict): A set of metadata tags from the input .pgn file.
        _move_pairs (list): A set of pairs of moves played during the game from the input .pgn file.
        _frames (list): A list of images, one for each of the moves played during the game.
    """
    def __init__(self, pgn):
        """
        Constructor for the ChessPlot class.

        Parameters:
            pgn (str): A path to a .pgn file to be plotted.
        """
        self._pgn = pgn
        self._tags, self._move_pairs = self._parse_file(file_path=pgn)
        self._frames = self._draw_frames()

    @staticmethod
    def _parse_file(file_path):
        """
        Parse a given file into a set of metadata tags and a move set.

        Parameters:
            file_path (str): A path to the .pgn file to be parsed.

        Returns:
            tags (dict): A dictionary of metadata tags and their values.
            move_pairs (list): A list of pairs of moves played during the game.
        """
        file = open(file_path, "r")
        tags = {}
        moves = None
        for line in file:
            if line[0] == "[":  # extract metadata tags
                for char in ["[", "]", '"', "\n"]:
                    line = line.replace(char, "")

                key, value = line.split(" ", 1)
                tags[key] = value
            else:  # extract move set
                moves = file.read()
                break
        if moves is None:
            raise ValueError(f"File {file_path} contains no move set")

        moves = moves.replace("\n", " ")
        move_pairs = [
            [move for move in pair.strip().split(" ") if move != ""]
            for pair in re.split("\\d+\\.", moves) if pair != ''
        ]

        return tags, move_pairs

    def _draw_frames(self):
        """
        Draw a list of frames, one for each move played in the game.

        Returns:
            frames (list): A list of frames, one for each move in the game.
        """
        white_to_move = True
        game = Game(tags=self._tags)
        frames = [game.draw_board()]  # add starting position image
        move_count = 0
        for pair in self._move_pairs:
            move_count += 1
            for move in pair:
                if move in ["1-0", "0-1", "1/2-1/2"]:
                    break
                if white_to_move:
                    move_string = f"{move_count}. {move}"
                else:
                    move_string = f"{move_count}... {move}"

                game.execute_move(move_string=move, white_to_move=white_to_move)
                frames.append(game.draw_board(move_string=move_string))
                white_to_move = not white_to_move
        return frames

    def to_gif(self, save_path=None, duration=2000):
        """
        Save the ChessPlot to a gif at a given location.

        If the given location is None, the location of the input .pgn file will be used with the .gif extension.

        Parameters:
            save_path (str): A location where the produced .gif should be saved.
            duration (int): The time in milliseconds each frame of the .gif should last.
        """
        if save_path is None:
            save_path = self._pgn.replace(".pgn", ".gif")
        save_images = self._frames + [self._frames[-1]]  # add last element twice before loop restarts
        save_images[0].save(
            fp=save_path,
            format="gif",
            save_all=True,
            append_images=save_images[1:],
            duration=duration,  # 1 second per loop
            loop=0  # infinite loop
        )

    def to_pdf(self, save_path=None):
        """
        Save the ChessPlot to a pdf at a given location.

        If the given location is None, the location of the input .pgn file will be used with the .pdf extension.

        Parameters:
            save_path (str): A location where the produced .pdf should be saved.
        """
        if save_path is None:
            save_path = self._pgn.replace(".pgn", ".pdf")
        save_images = self._frames
        save_images[0].save(
            fp=save_path,
            format="pdf",
            save_all=True,
            append_images=save_images[1:],
            resolution=1800
        )

    def show(self):
        """Show all frames of a game."""
        for frame in self._frames:
            frame.show()
