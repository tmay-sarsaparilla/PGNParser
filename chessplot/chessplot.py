"""Module for the ChessPlot class"""

import numpy as np
import re
import datetime
from typing import Tuple, List, Dict, TypeVar, Generic
from PIL import Image, ImageFont, ImageDraw
from .interpreter import _Interpreter


T = TypeVar("T")


class ChessPlot:
    """A class for plots of chess games.

    Attributes:
        _pgn (str): A path to a .pgn file to be plotted.
        _tags (dict): A set of metadata tags from the input .pgn file.
        _moves (list): A set of pairs of moves played during the game from the input .pgn file.
        _fen (str): A FEN string containing information on the starting position of the game.
        _piece_positions (str): A string denoting the starting position of the pieces.
        _white_to_move (bool): Indicator of whether it is white's move.
        _move_count (int): The current full move count of the game.
        _event (str): The event at which the game took place.
        _site (str): The location where the game took place.
        _date (str): The date on which the game took place. Unknown fields are populated with '??'.
        _event_round (str): The round in which the game took place.
        _white (str): The name of the player with the white pieces.
        _black (str): The name of the player with the black pieces.
        _white_elo (str): The Elo rating of the player with the white pieces.
        _black_elo (str): The Elo rating of the player with the black pieces.
        _result (str): The result of the game. Valid results are 1-0, 0-1, or 1/2-1/2.
        _formatted_date (str): A formatted version of the game date.
        _black_square_colour (str): A hex code for the colour of black squares in the plot.
        _white_square_colour (str): A hex code for the colour of white squares in the plot.
        _board_only (bool): Indicator of whether only the board should be plotted or not.
        _flip_perspective (bool): Indicator of whether the view perspective of the game should be flipped
        _plot_size (int): The size of the plot to be produced.
        _square_width (int): The width of squares on the board in the final plot.
        _display_notation (bool): Indicator of whether to display move notation on plots.
        _header_image (Image.Image): A header image for each frame of a plot.
        _move_text_font (ImageFont.truetype): A font for drawing move notations on plots.
        _unicode_font (ImageFont.truetype): A font for drawing pieces on the board.
        _square_name_font (ImageFont.truetype): A font for drawing the square coordinates on plots.
        _boards (list): A list of boards, one for each of the moves played during the game.
        _frames (list): A list of images, one for each of the moves played during the game.
    """

    __default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    __end_states = ["1-0", "0-1", "1/2-1/2"]

    def __init__(self, pgn: str) -> None:
        """
        Constructor for the ChessPlot class.

        Args:
            pgn (str): A path to a .pgn file to be plotted.
        """

        self._pgn = pgn
        self._tags, self._moves = self._parse_file(file_path=pgn)
        self._fen = self._get_tag_value(tag_key="FEN", default_value=ChessPlot.__default_fen)
        (
            self._piece_positions,
            self._white_to_move,
            self._move_count
        ) = self._parse_fen()
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
        self._black_square_colour = "#276996"
        self._white_square_colour = "#e2e7ee"
        self._board_only = None
        self._flip_perspective = None
        self._plot_size = None
        self._square_width = None
        self._display_notation = None
        self._start_frame = None
        self._end_frame = None
        self._header_image = None
        self._move_text_font = None
        self._unicode_font = None
        self._square_name_font = None
        self._boards = self._parse_moves()
        self._frames = []

    @staticmethod
    def _parse_file(file_path: str) -> Tuple[Dict[str, str], List[List[str]]]:
        """
        Parse a given file into a set of metadata tags and a move set.

        Args:
            file_path (str): A path to the .pgn file to be parsed.

        Returns:
            tags (dict): A dictionary of metadata tags and their values.
            moves (list): A list of pairs of ply played during the game.

        Raises:
            ValueError: If given file is not a .pgn | If file contains no move set
            FileNotFoundError: If given path is not valid
        """

        if not file_path.endswith(".pgn"):
            raise ValueError(f"File {file_path} is not a valid .pgn.")
        file = open(file_path, "r")
        tags = {}
        moves_string = ""
        for line in file:
            tag_search = re.search(r"\[(.*)]", line)
            if tag_search is not None:
                tag = tag_search.group(1)
                tag = tag.replace('"', "")
                key, value = tag.split(" ", 1)
                tags[key] = value
            else:  # extract move set
                moves_string += line
                if line.endswith(tuple(ChessPlot.__end_states)):
                    break
        if not moves_string:
            raise ValueError(f"File {file_path} contains no move set")

        moves_string = moves_string.replace("\n", " ")
        moves = [
            [ply for ply in move.strip().split(" ") if ply != ""]
            for move in re.split("\\d+\\.", moves_string) if move != ''
        ]
        moves = [move for move in moves if move]  # remove empty moves

        return tags, moves

    def _get_tag_value(self, tag_key: str, default_value: str = "") -> str:
        """
        Get the value corresponding to a given tag key.

        Args:
            tag_key (str): The key of the desired tag.
            default_value (str): The default value in the event that the tag is not present.
        """
        try:
            return self._tags[tag_key]
        except KeyError:
            return default_value

    def _parse_fen(self) -> Tuple[str, bool, int]:
        """
        Parse a given FEN string and return it's constituent elements.

        A FEN string consists of six parts:
            - Piece positions from white's perspective.
            - Active colour ("w" or "b").
            - Castling availability.
            - En passant target.
            - Half-move count.
            - Full move count.

        For full information, see: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation.

        Returns:
            piece_positions (str): A string denoting the position of all pieces on the board.
            white_to_move (bool): Indicator of whether it is white's move or not.
            move_number (int): The current move number of the game.

        Raises:
            ValueError: If the given FEN string is invalid.
        """

        try:
            fen_elements = self._fen.split(" ")
            piece_positions = fen_elements[0]
            active_colour = fen_elements[1]
            move_number = fen_elements[5]
            if active_colour == "w":
                white_to_move = True
            else:
                white_to_move = False
            return piece_positions, white_to_move, int(move_number)
        except ValueError:
            raise ValueError(f"{self._fen} is not a valid FEN string.")

    def _format_date(self) -> str:
        """
        Format game date.

        Returns:
            date (str): A formatted version of the original date field.
        """
        year, month, day = self._date.replace(".", "-").split("-")
        if year == "??":
            date = None
        elif month == "??":
            date = year
        elif day == "??":
            date = datetime.date(int(year), int(month), 1).strftime("%B %Y")
        else:
            date = datetime.date(int(year), int(month), int(day)).strftime("%A %d %B %Y")
        return date

    def _parse_moves(self) -> List[Tuple[str, np.ndarray]]:
        """
        Parse and execute a set of moves.

        Each ply is parsed by an interpreter object which executes the move
        and returns a game board to be plotted later.

        Returns:
            boards (list): A list of game boards
        """

        interpreter = _Interpreter(piece_positions=self._piece_positions)
        boards = [("", interpreter.get_board())]  # add starting position image
        for pair in self._moves:
            for ply in pair:
                if ply in ChessPlot.__end_states:
                    break
                if self._white_to_move:
                    ply_string = f"{self._move_count}. {ply}"
                else:
                    ply_string = f"{self._move_count}... {ply}"
                interpreter.execute_move(ply_string=ply, white_to_move=self._white_to_move)
                boards.append((ply_string, interpreter.get_board()))
                self._white_to_move = not self._white_to_move
            self._move_count += 1

        return boards

    @staticmethod
    def _scale_font(text: str, font_name: str, max_width: int, max_height: int) -> ImageFont.truetype:
        """
        Scale a font to fit a given piece of text within a bounding box.

        Args:
            text (str): The text to be fitted.
            font_name (str): The name of the font.
            max_width (int): The maximum width of the scaled text.
            max_height (int): The maximum height of the scaled text.

        Returns:
            font (ImageFont.truetype): A font object scaled to the correct size.
        """

        # TODO: Find a more optimal way of scaling fonts
        font_size = 12
        font = ImageFont.truetype(font=font_name, size=font_size)
        text_width, text_height = font.getsize(text=text)

        while text_width < max_width and text_height < max_height:
            font_size += 2
            font = ImageFont.truetype(font=font_name, size=font_size)
            text_width, text_height = font.getsize(text=text)

        return font

    def _draw_board(self, board: np.ndarray, ply_string: str = "") -> Image.Image:
        """
        Draw an image of a given game board.

        The image will be a 10x10 grid. If black_perspective is True, the board is flipped in the image.

        Args:
            board (np.ndarray): The game board to be drawn.
            ply_string (str): A string describing the ply being drawn e.g. 1. e4.

        Returns:
            image (Image.Image): An image of the board.
        """

        image = Image.new(mode="RGB", size=(self._square_width * 10, self._square_width * 10), color="white")
        draw = ImageDraw.ImageDraw(im=image)

        x_origin, y_origin = self._square_width, self._square_width

        # move text
        if self._display_notation:
            draw.text(
                xy=(x_origin, y_origin * 0.5),
                text=ply_string,
                align="left",
                font=self._move_text_font,
                fill="black"
            )

        if not self._flip_perspective:
            board = np.flip(board)

        for row in range(0, 8):
            for col in range(0, 8):
                piece = board[row, col]
                x = x_origin + self._square_width * col
                y = y_origin + self._square_width * row
                square_colour = self._white_square_colour if (row + col) % 2 == 0 else self._black_square_colour
                draw.rectangle(xy=((x, y), (x + self._square_width, y + self._square_width)), fill=square_colour)
                if piece is not None:
                    draw.text(  # add outline to piece
                        xy=(
                            x_origin + self._square_width * col + self._square_width * 0.5,
                            y_origin + self._square_width * row + self._square_width * 0.5
                        ),
                        text=piece.unicode,
                        anchor="mm",
                        align="center",
                        font=self._unicode_font,
                        fill="white",
                        stroke_width=3,
                    )
                    draw.text(
                        xy=(
                            x_origin + self._square_width * col + self._square_width * 0.5,
                            y_origin + self._square_width * row + self._square_width * 0.5
                        ),
                        text=piece.unicode,
                        anchor="mm",
                        align="center",
                        font=self._unicode_font,
                        fill="black",
                    )
                if col == 0:
                    if self._flip_perspective:
                        row_text = "12345678"[row]
                    else:
                        row_text = "12345678"[7 - row]
                    draw.text(
                        xy=(
                            x_origin - self._square_width * 0.5,
                            y_origin + self._square_width * row + self._square_width * 0.5
                        ),
                        text=row_text,
                        anchor="mm",
                        align="right",
                        font=self._square_name_font,
                        fill="black",
                        stroke_width=0
                    )
                if row == 7:
                    if self._flip_perspective:
                        col_text = "abcdefgh"[7 - col]
                    else:
                        col_text = "abcdefgh"[col]
                    draw.text(
                        xy=(
                            x_origin + self._square_width * col + self._square_width * 0.5,
                            y_origin + self._square_width * 8 + self._square_width * 0.5
                        ),
                        text=col_text,
                        anchor="mm",
                        align="center",
                        font=self._square_name_font,
                        fill="black",
                        stroke_width=0
                    )
        return image

    def _draw_header(self, header_width: int, header_height: int) -> Image.Image:
        """
        Draw a header for all frames including game metadata.

        Metadata includes:
            - Player names
            - Player Elo ratings
            - Game venue
            - Game date
            - Game result

        Args:
            header_width (int): The width of the header to be drawn.
            header_height (int): The height of the header to be drawn.

        Returns:
            image (Image.Image): An image of the header.
        """

        image = Image.new(mode="RGB", size=(header_width, header_height), color="white")
        draw = ImageDraw.ImageDraw(im=image)

        header_centre = header_width / 2

        # title text
        if self._white_elo != "" and self._black_elo != "":
            title_text = f"{self._white} ({self._white_elo}) - {self._black} ({self._black_elo})"
        else:
            title_text = f"{self._white} - {self._black}"

        title_font = self._scale_font(
            text=title_text,
            font_name="arial.ttf",
            max_width=int(header_width * 0.8),
            max_height=int(header_height * 0.5)
        )
        draw.text(
            xy=(header_centre, header_height * 0.4),
            text=title_text,
            anchor="ms",
            align="center",
            font=title_font,
            fill="black"
        )

        # sub-title text
        sub_title_text = f"{self._site}, {self._formatted_date}" if self._formatted_date is not None else self._site
        sub_title_font = self._scale_font(
            text=sub_title_text,
            font_name="ariali.ttf",
            max_width=int(header_width * 0.8),
            max_height=int(header_height * 0.25)
        )
        draw.text(
            xy=(header_centre, header_height * 0.7),
            text=sub_title_text,
            anchor="ms",
            align="center",
            font=sub_title_font,
            fill="black"
        )

        # result text
        result_text = self._result
        result_font = self._scale_font(
            text=result_text,
            font_name="arialbd.ttf",
            max_width=int(header_width * 0.8),
            max_height=int(header_height * 0.25)
        )
        draw.text(
            xy=(header_centre, header_height * 0.95),
            text=result_text,
            anchor="ms",
            align="center",
            font=result_font,
            fill="black"
        )

        return image

    def _draw(self, board: np.ndarray, ply_string: str = "") -> Image.Image:
        """
        Draw an image of the board in its current state.

        Args:
            board (np.ndarray): The game board state following the ply being drawn.
            ply_string (str): A string describing the ply being drawn.

        Returns:
            frame (Image.Image): An image depicting the game board in its current state.
        """

        board_image = self._draw_board(
            board=board,
            ply_string=ply_string,
        )

        if self._board_only:
            return board_image

        header_height = self._header_image.size[1]

        frame = Image.new(mode="RGB", size=(self._plot_size, self._plot_size + header_height), color="white")
        frame.paste(board_image, (0, header_height))
        frame.paste(self._header_image, (0, 0))

        return frame

    def _draw_frames(self) -> None:
        """
        Draw a list of frames, one for each ply played in the game.
        """

        if not self._board_only:
            header_height = int(self._plot_size * 0.15)
            self._header_image = self._draw_header(
                header_width=self._plot_size,
                header_height=header_height,
            )

        # Create fonts
        self._square_name_font = self._scale_font(
            text="a",
            font_name="arial.ttf",
            max_width=int(self._square_width * 0.4),
            max_height=int(self._square_width * 0.4)
        )
        self._unicode_font = self._scale_font(
            text="♔",
            font_name="seguisym.ttf",
            max_width=self._square_width,
            max_height=self._square_width
        )
        if self._display_notation:
            self._move_text_font = self._scale_font(
                text="1. e4",
                font_name="arial.ttf",
                max_width=int(self._square_width * 0.8),
                max_height=int(self._square_width * 0.8)
            )

        self._frames = []
        for ply_string, board in self._boards[self._start_frame:self._end_frame + 1]:
            self._frames.append(self._draw(board=board, ply_string=ply_string))

        return

    def _update_plot_settings(self, **kwargs: Generic[T]) -> bool:
        """
        Update plot settings.

        Only make updates if a change has occurred. If settings haven't changed, then we don't
        need to recreate frames.

        Args:
            **kwargs (dict): A set of keyword arguments containing various plot settings.

        Keyword Args:
            plot_size (int): The size of the plots to be created.
            board_only (bool): Indicator of whether only the board should be drawn.
            display_notation (bool): Indicator of whether to display notation.
            flip_perspective (bool): Indicator of whether the board perspective should be flipped.
            start_frame (int): The frame on which the plot should start.
            end_frame (int): The frame on which the plot should end.

        Returns:
            settings_change (bool): Indicator of whether any settings have changed.

        Raises:
            ValueError: If given plot size is too small or too large
        """

        settings_change = False

        plot_size = kwargs.pop("plot_size", 800)
        board_only = kwargs.pop("board_only", False)
        display_notation = kwargs.pop("display_notation", True)
        flip_perspective = kwargs.pop("flip_perspective", False)
        start_frame = kwargs.pop("start_frame", 0)
        end_frame = kwargs.pop("end_frame", None)

        end_frame = end_frame if end_frame is not None else len(self._boards) - 1

        if plot_size != self._plot_size or self._plot_size is None:
            if not 400 <= plot_size <= 1000:
                raise ValueError("Please choose a plot size between 400 and 1000.")
            self._plot_size = plot_size
            self._square_width = int(plot_size / 10)
            settings_change = True
        if board_only != self._board_only or self._board_only is None:
            self._board_only = board_only
            settings_change = True
        if display_notation != self._display_notation or self._display_notation is None:
            self._display_notation = display_notation
            settings_change = True
        if flip_perspective != self._flip_perspective or self._flip_perspective is None:
            self._flip_perspective = flip_perspective
            settings_change = True
        if start_frame != self._start_frame or self._start_frame is None:
            self._start_frame = start_frame
            settings_change = True
        if end_frame != self._end_frame or self._end_frame is None:
            self._end_frame = end_frame
            settings_change = True

        return settings_change

    def to_gif(self, save_path: str = None, duration: int = 2000, **kwargs: Generic[T]) -> None:
        """
        Save the ChessPlot to a gif at a given location.

        If the given location is None, the location of the input .pgn file will be used with the .gif extension.

        Args:
            save_path (str): A location where the produced .gif should be saved (default None).
            duration (int): The time in milliseconds each frame of the .gif should last (default 2000).

        Keyword Args:
            plot_size (int): The width each frame of the gif should be (default 800).
            board_only (bool): Indicator of whether only the board should be plotted (default False).
            display_notation (bool): Indicator of whether to display move notation on the plot (default True).
            flip_perspective (bool): Indicator of whether the board perspective should be flipped (default False).
            start_frame (int): The frame on which the gif should begin (default 0).
            end_frame (int) The frame on which the gif should end (default None).
        """

        settings_change = self._update_plot_settings(**kwargs)

        if settings_change:
            self._draw_frames()

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
        return

    def to_pdf(self, save_path: str = None, **kwargs: Generic[T]) -> None:
        """
        Save the ChessPlot to a pdf at a given location.

        If the given location is None, the location of the input .pgn file will be used with the .pdf extension.

        Args:
            save_path (str): A location where the produced .pdf should be saved.

        Keyword Args:
            plot_size (int): The width each frame of the gif should be (default 800).
            board_only (bool): Indicator of whether only the board should be plotted (default False).
            display_notation (bool): Indicator of whether to display move notation on the plot (default True).
            flip_perspective (bool): Indicator of whether the board perspective should be flipped (default False).
            start_frame (int): The frame on which the gif should begin (default 0).
            end_frame (int) The frame on which the gif should end (default None).
        """

        settings_change = self._update_plot_settings(**kwargs)

        if settings_change:
            self._draw_frames()

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
        return

    def to_png(self, frame: int, save_path: str = None, **kwargs: Generic[T]):
        """
        Save a ChessPlot frame to a .png file at a given location.

        If the given location is None, the location of the input .pgn file will be used with the .png extension.

        Args:
            frame (int): The frame to be plotted.
            save_path (str): A location where the produced .pdf should be saved.

        Keyword Args:
            plot_size (int): The width each frame of the gif should be (default 800).
            board_only (bool): Indicator of whether only the board should be plotted (default False).
            display_notation (bool): Indicator of whether to display move notation on the plot (default True).
            flip_perspective (bool): Indicator of whether the board perspective should be flipped (default False).
        """

        kwargs["start_frame"] = frame
        kwargs["end_frame"] = frame
        settings_change = self._update_plot_settings(**kwargs)

        if settings_change:
            self._draw_frames()

        if save_path is None:
            save_path = self._pgn.replace(".pgn", ".png")

        image = self._frames[0]
        image.save(fp=save_path, format="png")
        return
