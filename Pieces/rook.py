#!/usr/bin/env python3

class rook:
    def __init__(self, colour, chess_board) -> None:
        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.chess_board = chess_board

    def move_piece(self, initial_position, final_position, take_piece_flag):
        if final_position == initial_position:
            return "Final position is the same as initial position."

        row_i, col_i = initial_position
        row_f, col_f = final_position

        if any(dimension < 0 for dimension in (col_i, col_f, row_i, row_f)) | \
        any(col > (self.chess_board.num_cols -1) for col in (col_i, col_f)) | \
        any(row > (self.chess_board.num_rows -1) for row in (row_i, row_f)):
            return "This is not a valid position on the board."

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        if not ((col_delta == 0) ^ (row_delta == 0)):
            return "Invalid move for this piece."

        col_step = col_delta / abs(col_delta) if col_delta != 0 else 0
        row_step = row_delta / abs(row_delta) if row_delta != 0 else 0

        intermediate_position = [row_i + row_step, col_i + col_step]

        while intermediate_position != final_position:
            intermediate_position_contents = self.chess_board.board[int(intermediate_position[0])][int(intermediate_position[1])]
            if intermediate_position_contents == None:
                intermediate_position[0] += row_step
                intermediate_position[1] += col_step
                continue
            else:
                return "Move obstructed."

        final_position_contents = self.chess_board.board[row_f][col_f]

        if final_position_contents == None:
            self.chess_board.remove_piece(row_i, col_i)
            self.chess_board.create_piece(type(self), self.colour, row_f, col_f)
            return
        elif final_position_contents == self.colour:
            return "Move obstructed."

        if take_piece_flag == False:

            valid_answer = False
            while valid_answer == False:
                answer = input("Would you like to take the piece? (y/n)").lower()
                if (answer == "y") | (answer == "n"):
                    valid_answer = True

            if answer == "n":
                return "Move aborted."

        self.chess_board.remove_piece(row_i, col_i)
        self.chess_board.remove_piece(row_f, col_f)
        self.chess_board.create_piece(type(self), self.colour, row_f, col_f)
