#!/usr/bin/env python3

class pawn:
    def __init__(self, colour, chess_board) -> None:
        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.chess_board = chess_board
        self.has_moved = False

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

        final_position_contents = self.chess_board.board[row_f][col_f]

        if final_position_contents and final_position_contents.colour == self.colour:
            return "Move obstructed."

        valid_diagonal_direction = (col_delta == 1 and abs(row_delta == 1))

        if valid_diagonal_direction and not final_position_contents:
            return "Invalid move for this piece."
        if valid_diagonal_direction and final_position_contents:
            if take_piece_flag == False:

                while True:
                    answer = input("Would you like to take the piece? (y/n) ").lower()
                    if answer in ("y", "n"):
                        break

                if answer == "n":
                    return "Move aborted."

            self.chess_board.remove_piece(row_i, col_i)
            self.chess_board.remove_piece(row_f, col_f)
            self.chess_board.create_piece(type(self), self.colour, row_f, col_f)
            self.has_moved = True
            return

        if final_position_contents:
            return "Move obstructed."

        if self.has_moved:
            if col_delta != 0 and row_delta != 1:
                return "Invalid move for this piece."
        elif not self.has_moved:
            if col_delta != 0 and row_delta > 2:
                return "Invalid move for this piece."

        col_step = col_delta / abs(col_delta) if col_delta != 0 else 0
        row_step = row_delta / abs(row_delta) if row_delta != 0 else 0

        intermediate_position = [row_i + row_step, col_i + col_step]

        while intermediate_position != final_position:
            intermediate_position_contents = self.chess_board.board[int(intermediate_position[0])][int(intermediate_position[1])]
            if not intermediate_position_contents:
                intermediate_position[0] += row_step
                intermediate_position[1] += col_step
                continue
            else:
                return "Move obstructed."

        self.chess_board.remove_piece(row_i, col_i)
        self.chess_board.create_piece(type(self), self.colour, row_f, col_f)
        self.has_moved = True
        return
