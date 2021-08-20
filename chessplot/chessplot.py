"""Module for the ChessPlot class"""

import numpy as np
from typing import Tuple, List, TypeVar, Generic
from PIL import Image, ImageFont, ImageDraw
from .interpreter import _Interpreter
from .parser import _Parser, _Metadata
from .settings import _Settings


T = TypeVar("T")


class ChessPlot:
    """A class for plots of chess games.

    Attributes:
        pgn (str): A path to a .pgn file to be plotted.
        metadata (_Metadata): A collection of metadata about the game.
        _settings (_Settings): A collection of settings for the plots to be generated.
        _header_image (Image.Image): A header image for each frame of a plot.
        _move_text_font (ImageFont.truetype): A font for drawing move notations on plots.
        _unicode_font (ImageFont.truetype): A font for drawing pieces on the board.
        _square_name_font (ImageFont.truetype): A font for drawing the square coordinates on plots.
        _boards (list): A list of boards, one for each of the moves played during the game.
        _frames (list): A list of images, one for each of the moves played during the game.
    """

    __end_states = ["1-0", "0-1", "1/2-1/2"]

    def __init__(self, pgn: str) -> None:
        """
        Constructor for the ChessPlot class.

        Args:
            pgn (str): A path to a .pgn file to be plotted.
        """

        self.pgn = pgn
        self.metadata = _Metadata()
        self._settings = _Settings()
        self._header_image = None
        self._move_text_font = None
        self._unicode_font = None
        self._square_name_font = None
        self._boards = self._create_boards()
        self._frames = []

    def _create_boards(self) -> List[Tuple[str, np.ndarray]]:
        """
        Parse and execute a set of moves.

        Each ply_string is parsed by an interpreter object which executes the move
        and returns a game board to be plotted later.

        Returns:
            boards (list): A list of game boards
        """

        parser = _Parser()
        self.metadata, moves = parser.parse_file(file_path=self.pgn, end_states=ChessPlot.__end_states)
        piece_positions, white_to_move, move_count = parser.parse_fen(fen=self.metadata.fen)

        interpreter = _Interpreter(piece_positions=piece_positions)
        boards = [("", interpreter.get_board())]  # add starting position image

        for pair in moves:
            for ply_string in pair:
                if ply_string in ChessPlot.__end_states:
                    break
                if white_to_move:
                    display_string = f"{move_count}. {ply_string}"
                else:
                    display_string = f"{move_count}... {ply_string}"

                ply = parser.parse_ply_string(ply_string=ply_string)
                interpreter.execute_ply(ply=ply, white_to_move=white_to_move)
                boards.append((display_string, interpreter.get_board()))
                white_to_move = not white_to_move
            move_count += 1

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

        image = Image.new(
            mode="RGB",
            size=(self._settings.square_width * 10, self._settings.square_width * 10),
            color="white"
        )
        draw = ImageDraw.ImageDraw(im=image)

        x_origin, y_origin = self._settings.square_width, self._settings.square_width

        # move text
        if self._settings.display_notation:
            draw.text(
                xy=(x_origin, y_origin * 0.5),
                text=ply_string,
                align="left",
                font=self._move_text_font,
                fill="black"
            )

        if not self._settings.flip_perspective:
            board = np.flip(board)

        for row in range(0, 8):
            for col in range(0, 8):
                piece = board[row, col]
                x = x_origin + self._settings.square_width * col
                y = y_origin + self._settings.square_width * row
                square_colour = self._settings.theme.white_square_colour if (row + col) % 2 == 0 \
                    else self._settings.theme.black_square_colour
                draw.rectangle(
                    xy=(
                        (x, y),
                        (x + self._settings.square_width, y + self._settings.square_width)
                    ),
                    fill=square_colour
                )
                if piece is not None:
                    draw.text(  # add outline to piece
                        xy=(
                            x_origin + self._settings.square_width * col + self._settings.square_width * 0.5,
                            y_origin + self._settings.square_width * row + self._settings.square_width * 0.5
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
                            x_origin + self._settings.square_width * col + self._settings.square_width * 0.5,
                            y_origin + self._settings.square_width * row + self._settings.square_width * 0.5
                        ),
                        text=piece.unicode,
                        anchor="mm",
                        align="center",
                        font=self._unicode_font,
                        fill="black",
                    )
                if col == 0:
                    if self._settings.flip_perspective:
                        row_text = "12345678"[row]
                    else:
                        row_text = "12345678"[7 - row]
                    draw.text(
                        xy=(
                            x_origin - self._settings.square_width * 0.5,
                            y_origin + self._settings.square_width * row + self._settings.square_width * 0.5
                        ),
                        text=row_text,
                        anchor="mm",
                        align="right",
                        font=self._square_name_font,
                        fill="black",
                        stroke_width=0
                    )
                if row == 7:
                    if self._settings.flip_perspective:
                        col_text = "abcdefgh"[7 - col]
                    else:
                        col_text = "abcdefgh"[col]
                    draw.text(
                        xy=(
                            x_origin + self._settings.square_width * col + self._settings.square_width * 0.5,
                            y_origin + self._settings.square_width * 8 + self._settings.square_width * 0.5
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
        if self.metadata.white_elo != "" and self.metadata.black_elo != "":
            title_text = f"{self.metadata.white} ({self.metadata.white_elo}) - " \
                         f"{self.metadata.black} ({self.metadata.black_elo})"
        else:
            title_text = f"{self.metadata.white} - {self.metadata.black}"

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
        sub_title_text = f"{self.metadata.site}, {self.metadata.date}" \
            if self.metadata.date is not None else self.metadata.site
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
        result_text = self.metadata.result
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

        if not self._settings.display_header:
            return board_image

        header_height = self._header_image.size[1]

        frame = Image.new(
            mode="RGB",
            size=(self._settings.plot_size, self._settings.plot_size + header_height),
            color="white"
        )
        frame.paste(board_image, (0, header_height))
        frame.paste(self._header_image, (0, 0))

        return frame

    def _draw_frames(self) -> None:
        """
        Draw a list of frames, one for each ply played in the game.
        """

        if self._settings.display_header:
            header_height = int(self._settings.plot_size * 0.15)
            self._header_image = self._draw_header(
                header_width=self._settings.plot_size,
                header_height=header_height,
            )

        # Create fonts
        self._square_name_font = self._scale_font(
            text="a",
            font_name="arial.ttf",
            max_width=int(self._settings.square_width * 0.4),
            max_height=int(self._settings.square_width * 0.4)
        )
        self._unicode_font = self._scale_font(
            text="♔",
            font_name="seguisym.ttf",
            max_width=self._settings.square_width,
            max_height=self._settings.square_width
        )
        if self._settings.display_notation:
            self._move_text_font = self._scale_font(
                text="1. e4",
                font_name="arial.ttf",
                max_width=int(self._settings.square_width * 0.8),
                max_height=int(self._settings.square_width * 0.8)
            )

        self._frames = []
        for ply_string, board in self._boards[self._settings.start_frame:self._settings.end_frame + 1]:
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
            theme (str): The theme to be used for the plot.

        Returns:
            settings_change (bool): Indicator of whether any settings have changed.
        """

        new_settings = _Settings(**kwargs)
        if new_settings.end_frame is None:
            new_settings.update_end_frame(end_frame=len(self._boards) - 1)

        if new_settings == self._settings:
            return False

        self._settings = new_settings

        return True

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
            theme (str): The theme to be used for the plot.
        """

        settings_change = self._update_plot_settings(**kwargs)

        if settings_change:
            self._draw_frames()

        if save_path is None:
            save_path = self.pgn.replace(".pgn", ".gif")

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
            theme (str): The theme to be used for the plot.
        """

        settings_change = self._update_plot_settings(**kwargs)

        if settings_change:
            self._draw_frames()

        if save_path is None:
            save_path = self.pgn.replace(".pgn", ".pdf")

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
            theme (str): The theme to be used for the plot.
        """

        kwargs["start_frame"] = frame
        kwargs["end_frame"] = frame
        settings_change = self._update_plot_settings(**kwargs)

        if settings_change:
            self._draw_frames()

        if save_path is None:
            save_path = self.pgn.replace(".pgn", ".png")

        image = self._frames[0]
        image.save(fp=save_path, format="png")
        return
