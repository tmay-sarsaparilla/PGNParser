
from chessplot.parse import parse_file
from chessplot.classes import Board


def play_game():
    tags, move_pairs = parse_file(file_path="C:/Users/Tim/Documents/test_match.pgn")
    white_to_move = True
    board = Board(tags=tags)
    move_count = 0
    for pair in move_pairs:
        move_count += 1
        moves = pair.split(" ")
        for move in moves:
            if move == "":
                continue
            elif move in ["1-0", "0-1", "1/2-1/2"]:
                break
            if white_to_move:
                move_string = f"{move_count}. {move}"
            else:
                move_string = f"{move_count}... {move}"

            board.execute_move(move_string=move, white_to_move=white_to_move)
            board.add_image(move_string=move_string)
            if white_to_move:
                white_to_move = False
            else:
                white_to_move = True

    board.create_gif()


def main():
    play_game()


if __name__ == "__main__":
    main()
