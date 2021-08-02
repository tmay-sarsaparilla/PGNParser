
import argparse
import sys
from .classes import ChessPlot


def main(args):
    """Parse inputted arguments and call the pgn_to_file function"""
    parser = argparse.ArgumentParser(description="Chessplot", usage="Reads and plots PGN files to .gif or .pdf")
    parser.add_argument("-file_path", "--fp", type=str, required=True, help="Location of PGN file to be parsed")
    parser.add_argument(
        "-save_path",
        "--sp",
        type=str,
        default=None,
        required=False,
        help="Location of the plot file to be created"
    )
    args = parser.parse_args(args)

    print(f"Processing PGN file: {args.file_path}")
    plot = ChessPlot(pgn=args.file_path)
    if args.save_path is None:
        pass
    elif args.save_path.endswith(".gif"):
        plot.to_gif(save_path=args.save_path)
    elif args.save_path.endswith(".pdf"):
        plot.to_pdf(save_path=args.save_path)
    else:
        raise ValueError(f"Invalid save path file type. Choose either .gif or .pdf.")

    print(f"Created .{args.output_file_format} file: {args.output_file_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
