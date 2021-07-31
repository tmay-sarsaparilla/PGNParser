
from chessplot.parse import pgn_to_file


def main():
    pgn_to_file(
        file_path="C:/Users/Tim/Documents/test_match_v02.pgn",
        output_file_path="C:/Users/Tim/Documents/test_match_v02_output.pdf",
        output_file_format="pdf"
    )


if __name__ == "__main__":
    main()
