
import argparse
import sys

from .parse import pgn_to_file


def main(args):
    """Parse inputted arguments and call the pgn_to_file function"""
    parser = argparse.ArgumentParser(description="Chessplot", usage="Reads and plots PGN files to .gif or .pdf")
    parser.add_argument("-file_path", type=str, required=True, help="Location of PGN file to be parsed")
    parser.add_argument("-output_file_path", type=str, required=True, help="Location of the plot file to be created")
    parser.add_argument(
        "-output_file_format",
        type=str,
        required=True,
        help="Format of output file. Valid formats: 'gif', 'pdf'"
    )
    args = parser.parse_args(args)

    pgn_to_file(
        file_path=args.file_path,
        output_file_path=args.output_file_path,
        output_file_format=args.output_file_format
    )


if __name__ == "__main__":
    main(sys.argv[1:])
