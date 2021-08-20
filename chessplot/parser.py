
import re
import datetime
from typing import Tuple, Dict, List
from .ply import _Ply, UnrecognisedPlyError


class _Metadata:
    """Class for representing a set of PGN tag metadata."""

    __default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self, tags: Dict[str, str] = None):

        if tags is None:
            tags = {}

        self.event = tags.pop("Event", "")
        self.site = tags.pop("Site", "")
        self.date = self._format_date(date=tags.pop("Date", "??.??.??"))
        self.event_round = tags.pop("Round", "")
        self.white = tags.pop("White", "Unknown")
        self.black = tags.pop("Black", "Unknown")
        self.white_elo = tags.pop("WhiteElo", "")
        self.black_elo = tags.pop("BlackElo", "")
        self.result = tags.pop("Result", "")
        self.fen = tags.pop("FEN", _Metadata.__default_fen)

    @staticmethod
    def _format_date(date: str) -> str:
        """
        Format game date.

        Args:
            date (str): An un-formatted date string from pgn tag.

        Returns:
            date (str): A formatted version of the original date field.
        """
        year, month, day = date.replace(".", "-").split("-")
        if year == "??":
            formatted_date = None
        elif month == "??":
            formatted_date = year
        elif day == "??":
            formatted_date = datetime.date(int(year), int(month), 1).strftime("%B %Y")
        else:
            formatted_date = datetime.date(int(year), int(month), int(day)).strftime("%A %d %B %Y")
        return formatted_date


class _Parser:
    """A class for parsing PGN files and chess ply."""

    @staticmethod
    def parse_file(file_path: str, end_states: List[str]) -> Tuple[_Metadata, List[List[str]]]:
        """
        Parse a given file into a set of metadata tags and a move set.

        Args:
            file_path (str): A path to the .pgn file to be parsed.
            end_states (list): A list of strings which denote the end of a game e.g. 1-0.

        Returns:
            (_Metadata): A collection of metadata about the game.
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
                if line.endswith(tuple(end_states)):
                    break
        if not moves_string:
            raise ValueError(f"File {file_path} contains no move set")

        moves_string = moves_string.replace("\n", " ")
        moves = [
            [ply for ply in move.strip().split(" ") if ply != ""]
            for move in re.split("\\d+\\.", moves_string) if move != ''
        ]
        moves = [move for move in moves if move]  # remove empty moves

        return _Metadata(tags=tags), moves

    @staticmethod
    def parse_fen(fen: str) -> Tuple[str, bool, int]:
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

        Args:
            fen (str): A FEN string to be parsed.

        Returns:
            piece_positions (str): A string denoting the position of all pieces on the board.
            white_to_move (bool): Indicator of whether it is white's move or not.
            move_number (int): The current move number of the game.

        Raises:
            ValueError: If the given FEN string is invalid.
        """

        try:
            fen_elements = fen.split(" ")
            piece_positions = fen_elements[0]
            active_colour = fen_elements[1]
            move_number = fen_elements[5]
            if active_colour == "w":
                white_to_move = True
            else:
                white_to_move = False
            return piece_positions, white_to_move, int(move_number)
        except ValueError:
            raise ValueError(f"{fen} is not a valid FEN string.")

    @staticmethod
    def parse_ply_string(ply_string: str) -> _Ply:
        """Parse a given ply string and return a _Ply object.

        Checks for castling moves (king-side and queen-side) and then all other move types.

        These include:
            - Pawn and piece moves e.g. e4, Be4.
            - Captures e.g. exd4, Rxc3.
            - Pawn promotions e.g. e8=Q.
            - Disambiguated piece moves e.g. N1e4, Nce4, Nc3e4.

        Args:
            ply_string (str): A string representation of the ply e.g. e4.

        Returns:
            (_Ply): A ply object representing the ply.

        Raises:
            UnrecognisedPlyError: If the given ply_string is not in a recognised format.
        """

        ply_elements = {"ply_string": ply_string}

        if re.match("^O-O$|^0-0$", string=ply_string):  # castle king-side
            ply_elements["castle_king_side"] = True
            return _Ply(**ply_elements)

        if re.match("^O-O-O$|^0-0-0$", string=ply_string):  # castle queen-side
            ply_elements["castle_queen_side"] = True
            return _Ply(**ply_elements)

        match = re.match("^([NBRKQ]?)([a-h]?)([1-8]?)(x?)([a-h][1-8])(=[NBRQ])?", ply_string)  # standard move

        if not match:
            raise UnrecognisedPlyError(ply_string=ply_string)

        ply_elements["new_position_name"] = match.group(5)  # set the new piece position
        ply_elements["piece_rank"] = match.group(1) if match.group(1) else "P"  # set the piece rank
        if match.group(2):  # set if optional column identifier is provided
            ply_elements["piece_col"] = match.group(2)
        if match.group(3):  # set if optional row identifier is provided
            ply_elements["piece_row"] = match.group(3)
        if match.group(4):  # set if ply contains a capture indicator
            ply_elements["is_capture"] = True
        if match.group(6):  # set if ply contains a piece promotion
            ply_elements["promoted_piece_rank"] = match.group(6)[1]

        return _Ply(**ply_elements)
