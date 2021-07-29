
import re


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

    move_pairs = [pair.strip() for pair in re.split("\\d+\\.", moves) if pair != '']

    return tags, move_pairs
