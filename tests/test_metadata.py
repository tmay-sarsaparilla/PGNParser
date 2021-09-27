
import pytest
from chessplot.parser import _Metadata


class TestMetadata:

    test_data = [
        ("??.??.??", None),
        ("2021.??.??", "2021"),
        ("2021.08.??", "August 2021"),
        ("2021.08.29", "Sunday 29 August 2021"),
        ("2021-08-29", "Sunday 29 August 2021")
    ]

    @pytest.mark.parametrize("date, expected", test_data)
    def test_format_date(self, date, expected):
        """Test that the _format_date method returns the correctly formatted date."""
        metadata = _Metadata()
        assert metadata._format_date(date=date) == expected
