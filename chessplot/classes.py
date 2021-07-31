
import numpy as np
import re
import datetime
from PIL import Image, ImageDraw, ImageFont


class Piece:
    """Class for pieces"""

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
        assert name.upper() in Piece.__valid_piece_names, f"{name} is not a valid piece name"
        self._name = name
        self._is_white = True if name == name.upper() else False
        self._rank = name.upper()
        self._unicode = Piece.__unicode_lookup[self.name]
        self.position = Position(row=row, col=col)
        self.move_metric = self.set_move_metric()
        self._has_moved = False
        self._position_history = [self.position]

    def __repr__(self):
        return repr(self.name)

    @property
    def name(self):
        """Get function for the 'name' property"""
        return self._name

    @property
    def is_white(self):
        """Get function for the 'is_white' property"""
        return self._is_white

    @property
    def rank(self):
        return self._rank

    @property
    def unicode(self):
        return self._unicode

    def set_move_metric(self):
        """Set the list of move metrics for the piece"""
        if self.rank == "P":
            if self.is_white:
                return [(1, 0)]
            else:
                return [(-1, 0)]
        else:
            return Piece.__move_metrics[self.rank]

    def update_position(self, row, col):
        """Update the position of a piece with a new position"""
        self.position = Position(row=row, col=col)
        self._position_history.append(self.position)
        self._has_moved = True
        return

    def get_situational_directions(self, board):
        """Get a list of situational directions

        These include:
        - Pawn moving two squares on its first move
        - Pawn capturing a piece
        - Pawn capturing a piece en passant
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
            elif position_inhabitant.is_white != self.is_white:  # if the piece is of the opposite colour
                situational_directions.append(direction)         # a capture is possible

        # TODO: Implement en passant
        return situational_directions

    def get_possible_positions(self, board):
        """Determine all possible legal positions which the piece can move to"""
        max_move = 1 if self.rank in ["P", "N", "K"] else 7
        situational_directions = self.get_situational_directions(board=board)
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
    """Class for piece positions"""

    __row_names = "12345678"
    __col_names = "hgfedcba"

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.name = self.set_name()
        self.is_legal = self.check_legality()

    def __repr__(self):
        return repr(self.name)

    def __eq__(self, other):
        if self.row == other.row and self.col == other.col:
            return True
        else:
            return False

    def set_name(self):
        """Set the name of the position"""
        try:
            return self.__col_names[self.col] + self.__row_names[self.row]
        except IndexError:
            return ""

    def check_legality(self):
        """Check whether a position is legal"""
        if self.row < 0 or self.row >= 8:
            return False
        elif self.col < 0 or self.col >= 8:
            return False
        else:
            return True


class Board:

    __default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    def __init__(self, tags):
        (
            self.fen,
            self.event,
            self.site,
            self.date,
            self.event_round,
            self.white,
            self.black,
            self.white_elo,
            self.black_elo,
            self.result
        ) = self.get_metadata(tags=tags)
        self.formatted_date = self.format_date()
        self.grid = self.generate_board()
        self.images = [self.generate_image()]

    def __repr__(self):
        print_grid = np.vstack(([["h", "g", "f", "e", "d", "c", "b", "a"]], self.grid))
        print_grid = np.hstack((print_grid, [[" "], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"], ["8"]]))
        return str(np.flip(print_grid)).replace("None", " - ") + "\n"

    @staticmethod
    def get_metadata(tags):
        """Get metadata from a set of tags"""
        def get_tag(tag_key, default_value=""):
            try:
                return tags[tag_key]
            except KeyError:
                return default_value

        fen = get_tag(tag_key="FEN", default_value=Board.__default_fen)
        event = get_tag(tag_key="Event")
        site = get_tag(tag_key="Site")
        date = get_tag(tag_key="Date")
        event_round = get_tag(tag_key="Round")
        white = get_tag(tag_key="White", default_value="Unknown")
        black = get_tag(tag_key="Black", default_value="Unknown")
        white_elo = get_tag(tag_key="WhiteELO")
        black_elo = get_tag(tag_key="BlackELO")
        result = get_tag(tag_key="Result")
        return fen, event, site, date, event_round, white, black, white_elo, black_elo, result

    def format_date(self):
        """Format game date"""
        year, month, day = self.date.split(".")
        if year == "??":
            date = None
        elif month == "??":
            date = year
        elif day == "??":
            date = datetime.date(int(year), int(month), 0).strftime("%A %d %B %Y")
        else:
            date = datetime.date(int(year), int(month), int(day)).strftime("%A %d %B %Y")
        return date

    def generate_board(self):
        """Generate a board from a given FEN code"""
        board = np.empty((8, 8), dtype=Piece)

        row = 7
        col = 7
        for char in self.fen:
            if char == "/":
                row -= 1
                col = 7
            elif str.isdigit(char):
                col -= int(char)
            else:
                board[row, col] = Piece(name=char, row=row, col=col)
                col -= 1

        return board

    def move_piece(self, piece, row, col, promoted_piece_rank=None):
        """Move a piece on the grid"""
        current_row = piece.position.row
        current_col = piece.position.col

        self.grid[current_row, current_col] = None
        piece.update_position(row=row, col=col)
        if promoted_piece_rank is not None:  # if pawn promotion, create a new piece at the new position
            new_piece_name = promoted_piece_rank.lower() if not piece.is_white else promoted_piece_rank
            new_piece = Piece(name=new_piece_name, row=row, col=col)
            self.grid[row, col] = new_piece
        else:  # otherwise move the existing piece
            self.grid[row, col] = piece
        return

    def castle(self, white_to_move, castle_king_side):
        """Executing castling of pieces on given side and for given colour"""
        if white_to_move:
            king = self.grid[0, 3]
            if castle_king_side:
                rook = self.grid[0, 0]
            else:
                rook = self.grid[0, 7]
        else:
            king = self.grid[7, 3]
            if castle_king_side:
                rook = self.grid[7, 0]
            else:
                rook = self.grid[7, 7]

        if castle_king_side:
            self.move_piece(piece=king, row=king.position.row, col=king.position.col - 2)
            self.move_piece(piece=rook, row=rook.position.row, col=rook.position.col + 2)
        else:
            self.move_piece(piece=king, row=king.position.row, col=king.position.col + 2)
            self.move_piece(piece=rook, row=rook.position.row, col=rook.position.col - 3)

        return

    def execute_move(self, move_string, white_to_move):
        """Parse a given move and execute it"""
        row_names = "12345678"
        col_names = "hgfedcba"

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
            self.castle(white_to_move=white_to_move, castle_king_side=castle_king_side)
            return

        new_col = int(col_names.index(new_col_str))
        new_row = int(row_names.index(new_row_str))
        new_position = Position(row=new_row, col=new_col)

        candidate_pieces = []
        for row in range(0, 8):
            for col in range(0, 8):
                piece = self.grid[row, col]
                if piece is None:  # if square is empty, skip
                    continue
                if piece.is_white != white_to_move:  # if piece is the wrong colour, skip
                    continue
                if piece.rank == piece_rank and new_position in piece.get_possible_positions(self.grid):
                    candidate_pieces.append(piece)

        if len(candidate_pieces) == 1:
            self.move_piece(
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
                self.move_piece(piece=piece, row=new_row, col=new_col, promoted_piece_rank=promoted_piece_rank)
                return
            elif piece_row is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.row == int(row_names.index(piece_row))
                ]
                self.move_piece(piece=piece, row=new_row, col=new_col, promoted_piece_rank=promoted_piece_rank)
                return
            elif piece_col is not None:
                piece, = [
                    piece for piece in candidate_pieces
                    if piece.position.col == int(col_names.index(piece_col))
                ]
                self.move_piece(piece=piece, row=new_row, col=new_col, promoted_piece_rank=promoted_piece_rank)
                return

        raise ValueError(f"Invalid move: {move_string}")

    def generate_image(self, move_string=""):
        """Generate an image of the board in its current state"""
        image = Image.new(mode="RGB", size=(600, 700), color="white")
        unicode_font = ImageFont.truetype("seguisym.ttf", 50)
        black_square_colour = "#276996"
        white_square_colour = "#e2e7ee"
        draw = ImageDraw.ImageDraw(im=image)

        x_origin, y_origin = 60, 160

        # title text
        title_font = ImageFont.truetype("arial.ttf", 30)
        if self.white_elo != "" and self.black_elo != "":
            title_text = f"{self.white}({self.white_elo}) - {self.black}({self.black_elo})"
        else:
            title_text = f"{self.white} - {self.black}"
        draw.text(
            xy=(x_origin + 240, y_origin - 120),
            text=title_text,
            anchor="ms",
            align="center",
            font=title_font,
            fill="black"
        )

        # sub-title text
        sub_title_font = ImageFont.truetype("ariali.ttf", 20)
        sub_title_text = f"{self.site}, {self.formatted_date}" if self.formatted_date is not None else self.site
        draw.text(
            xy=(x_origin + 240, y_origin - 100),
            text=sub_title_text,
            anchor="ms",
            align="center",
            font=sub_title_font,
            fill="black"
        )

        # result text
        result_font = ImageFont.truetype("arialbd.ttf", 20)
        result_text = self.result
        draw.text(
            xy=(x_origin + 240, y_origin - 80),
            text=result_text,
            anchor="ms",
            align="center",
            font=result_font,
            fill="black"
        )

        # move text
        move_text_font = ImageFont.truetype("arial.ttf", 20)
        draw.text(
            xy=(x_origin, y_origin - 40),
            text=move_string,
            align="left",
            font=move_text_font,
            fill="black"
        )

        for i in range(0, 8):
            for j in range(0, 8):
                piece = self.grid[7-i, 7-j]
                x = x_origin + 60 * j
                y = y_origin + 60 * i
                square_colour = white_square_colour if (i + j) % 2 == 0 else black_square_colour
                draw.rectangle(xy=((x, y), (x + 60, y + 60)), fill=square_colour)
                if piece is not None:
                    draw.text(
                        xy=(x_origin + 60 * j + 30, y_origin + 60 * i + 30),
                        text=piece.unicode,
                        anchor="mm",
                        align="center",
                        font=unicode_font,
                        fill="black"
                    )
                if i == 0:
                    draw.text(
                        xy=(x_origin - 30, y_origin + 60 * j + 30),
                        text="12345678"[7-j],
                        anchor="mm",
                        align="right",
                        font=move_text_font,
                        fill="black",
                        stroke_width=0
                    )
                if j == 7:
                    draw.text(
                        xy=(x_origin + 60 * i + 30, y_origin + 60 * 8 + 30),
                        text="abcdefgh"[i],
                        anchor="mm",
                        align="center",
                        font=move_text_font,
                        fill="black",
                        stroke_width=0
                    )

        return image

    def add_image(self, move_string=""):
        """Add to the list of board images"""
        self.images.append(self.generate_image(move_string=move_string))
        return

    def to_file(self, file_path, file_format):
        """Create a file of the supplied format"""
        if file_format == "gif":
            save_images = self.images + [self.images[-1]]  # add last element twice before loop restarts
            save_images[0].save(
                fp=file_path,
                format=file_format,
                save_all=True,
                append_images=save_images[1:],
                duration=2000,  # 1 second per loop
                loop=0  # infinite loop
            )
        elif file_format == "pdf":
            save_images = self.images
            save_images[0].save(
                fp=file_path,
                format=file_format,
                save_all=True,
                append_images=save_images[1:],
                resolution=1800
            )
        else:
            raise ValueError(f"File format '{file_format}' is not supported. Please choose either 'gif' or 'pdf'")
        return
