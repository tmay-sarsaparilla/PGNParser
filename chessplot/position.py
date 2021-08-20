"""Module for defining positions"""


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

    @classmethod
    def from_name(cls, name: str):
        """Class method for constructing a _Position from its name."""

        col_str, row_str = list(name)
        row = cls.__row_names.index(row_str)
        col = cls.__col_names.index(col_str)
        return cls(row=row, col=col)

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

    def __str__(self) -> str:
        return self.name

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
