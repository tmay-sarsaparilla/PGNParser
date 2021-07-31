
import re
from .classes import Board


def parse_file(file_path):
    """Parse a given file into a set of metadata tags and a move set"""
    file = open(file_path, "r")
    tags = {}
    moves = None
    for line in file:
        if line[0] == "[":  # extract metadata tags
            for char in ["[", "]", '"', "\n"]:
                line = line.replace(char, "")

            key, value = line.split(" ", 1)
            tags[key] = value
        else:  # extract move set
            moves = file.read()
            break
    if moves is None:
        raise ValueError(f"File {file_path} contains no move set")

    moves = moves.replace("\n", " ")
    move_pairs = [pair.strip() for pair in re.split("\\d+\\.", moves) if pair != '']

    return tags, move_pairs


def pgn_to_file(file_path, output_file_path, output_file_format):
    """Generate an image file from a given PGN file"""
    tags, move_pairs = parse_file(file_path=file_path)
    white_to_move = True
    board = Board(tags=tags)
    move_count = 0
    for pair in move_pairs:
        move_count += 1
        moves = [move for move in pair.split(" ") if move != ""]
        for move in moves:
            if move in ["1-0", "0-1", "1/2-1/2"]:
                break
            if white_to_move:
                move_string = f"{move_count}. {move}"
            else:
                move_string = f"{move_count}... {move}"

            board.execute_move(move_string=move, white_to_move=white_to_move)
            board.add_image(move_string=move_string)
            white_to_move = not white_to_move

    board.to_file(file_path=output_file_path, file_format=output_file_format)
    return
