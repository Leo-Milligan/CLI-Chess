#!/usr/bin/env python3

class knight:
    def __init__(self, colour, chess_board) -> None:
        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.chess_board = chess_board

    def move_piece(self, initial_position, final_position, take_piece_flag):
        if final_position == initial_position:
            return "Final position is the same as initial position."

        row_i, col_i = initial_position
        row_f, col_f = final_position

        final_position_contents = self.chess_board.board[row_f][col_f]

        if final_position_contents and final_position_contents.colour == self.colour:
            return "Move obstructed."

        if any(dimension < 0 for dimension in (col_i, col_f, row_i, row_f)) | \
        any(col > (self.chess_board.num_cols -1) for col in (col_i, col_f)) | \
        any(row > (self.chess_board.num_rows -1) for row in (row_i, row_f)):
            return "This is not a valid position on the board."

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        if not (
                (abs(col_delta) == 2) and (abs(row_delta) == 1) or
                (abs(col_delta) == 1) and (abs(row_delta) == 2)
        ):
            return "Invalid move for this piece."


        if not final_position_contents:
            self.chess_board.board[row_f][col_f] = self.chess_board.board[row_i][col_i]
            self.chess_board.remove_piece(row_i, col_i)
            return

        if take_piece_flag == False:

            while True:
                answer = input("Would you like to take the piece? (y/n) ").lower()
                if answer in ("y", "n"):
                    break

            if answer == "n":
                return "Move aborted."

        self.chess_board.board[row_f][col_f] = self.chess_board.board[row_i][col_i]
        self.chess_board.remove_piece(row_i, col_i)
