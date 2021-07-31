
from chessplot.parse import parse_file
from chessplot.classes import Board


def play_game():
    tags, move_pairs = parse_file(file_path="C:/Users/Tim/Documents/test_match_v02.pgn")
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

    board.create_gif()


def main():
    play_game()


if __name__ == "__main__":
    main()
