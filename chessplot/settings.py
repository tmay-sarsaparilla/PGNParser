
import warnings
from dataclasses import dataclass


@dataclass(frozen=True)
class _Theme:
    """A class for ChessPlot themes."""
    black_square_colour: str
    white_square_colour: str


class _Settings:
    """A class for ChessPlot settings."""

    __themes = {
        "classic": _Theme(black_square_colour="#b06c4a", white_square_colour="#f7efeb"),
        "blue": _Theme(black_square_colour="#276996", white_square_colour="#e2e7ee"),
        "green": _Theme(black_square_colour="#5a9946", white_square_colour="#ebead8"),
    }

    def __init__(
            self,
            display_header: bool = True,
            flip_perspective: bool = False,
            plot_size: int = 800,
            display_notation: bool = True,
            start_frame: int = 0,
            end_frame: int = None,
            theme: str = "blue"
    ):
        """
        Constructor method for the _Settings class.

        Args:
            display_header (bool): Indicator for whether the plot header should be shown (default True).
            flip_perspective (bool): Indicator for whether the board perspective should be flipped (default False).
            plot_size (int): Width of the plot in mm (default 800).
            display_notation (bool): Indicator for whether ply should be notated on the plot (default True).
            start_frame (int): Frame the plot should start on (default 0).
            end_frame (int): Frame the plot should end on (default None).
            theme (_Theme): Theme to use for the plot (default "blue").
        """

        try:
            self.theme = _Settings.__themes[theme]
        except KeyError:
            self.theme = _Settings.__themes["blue"]
            warnings.warn(f"Warning: {theme} is not a recognised theme. Using default theme.")
        self.display_header = display_header
        self.flip_perspective = flip_perspective
        if not 400 <= plot_size <= 1000:
            raise ValueError("Please choose a plot size between 400 and 1000.")
        self.plot_size = plot_size
        self.square_width = int(plot_size / 10)
        self.display_notation = display_notation
        self.start_frame = start_frame
        self.end_frame = end_frame

    def __hash__(self):
        return hash(
            (
                self.theme,
                self.display_header,
                self.flip_perspective,
                self.plot_size,
                self.display_notation,
                self.start_frame,
                self.end_frame,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, _Settings):
            return NotImplemented
        return self.__hash__() == other.__hash__()

    def update_end_frame(self, end_frame: int):
        """Update the end_frame of a _Settings object.

        Args:
            end_frame (int): The new frame to end the plot on.
        """
        self.end_frame = end_frame
        return
