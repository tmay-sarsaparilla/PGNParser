
import re
from chessplot.classes import Board


def get_moves_from_string(game_string):
    move_pairs = [pair.strip() for pair in re.split("\\d+\\.", game_string) if pair != '']
    return move_pairs


def main():
    game_string = "1.e4 c6 2.d4 d5 3.e5 Bf5 4.Bd3 Bxd3 5.Qxd3 e6 6.f4 c5 7.c3 Nc6 8.Nf3 Qb6 9.0-0 Nh6 10.b3 cxd4 11.cxd4 Nf5 12.Bb2 Rc8 13.a3 Ncxd4 14.Nxd4 Bc5 15.Rd1 Nxd4 16.Bxd4 Bxd4+ 17.Qxd4 Rc1 18.Kf2 Rxd1 19.Qxb6 axb6 20.Ke2 Rc1 21.Kd2 Rg1 22.g3 Kd7 23.a4 Rc8 24.b4 Rcc1 0-1"
    move_pairs = get_moves_from_string(game_string)
    white_to_move = True
    board = Board()
    move_count = 0
    for pair in move_pairs:
        move_count += 1
        moves = pair.split(" ")
        for move in moves:
            if move == "1-0":
                print("White wins")
                return
            elif move == "0-1":
                print("Black wins")
                board.create_gif()
                return
            elif move == "½–½":
                print("Draw")
                return

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


if __name__ == "__main__":
    main()
