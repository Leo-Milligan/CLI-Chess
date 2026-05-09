#!/usr/bin/env python3

class rook:
    def __init__(self, colour, board) -> None:
        self.colour = colour
        self.board = board

    def __str__(self) -> str:
        return f"{self.colour}_{self.__class__.__name__}"

    def move_piece(self, initial_position, final_position, take_piece_flag):

        if final_position == initial_position:
            return "Final position is the same as initial position."

        row_i, col_i = initial_position
        row_f, col_f = final_position

        if any(col < 0 for col in (col_i, col_f, row_i, row_f)) | \
        any(col > self.board.num_cols for col in (col_i, col_f)) | \
        any(row > self.board.num_rows for row in (row_i, row_f)):
            return "This is not a valid position on the board."

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        if (col_delta != 0) | (row_delta != 0):
            return "Invalid move for this piece."

        col_step = col_delta / abs(col_delta)
        row_step = row_delta / abs(row_delta)

        intermediate_position = [row_i + row_step, col_i + col_step]

        while intermediate_position != final_position:
            intermediate_position_contents = self.board[intermediate_position[0]][intermediate_position[1]]

            if intermediate_position_contents == None:
                intermediate_position[0] += row_step
                intermediate_position[1] += col_step
                continue
            else:
                return "Move obstructed."

        initial_position_contents = self.board[row_i][col_i]
        final_position_contents = self.board[row_f][col_f]

        if final_position_contents == None:
            self.board.remove_piece(row_i, col_i)
            final_position_contents = initial_position_contents
        elif final_position_contents == self.colour:
            return "Move obstructed."

        if take_piece_flag == False:

            valid_answer = False
            while valid_answer == False:
                answer = input("Would you like to take the piece? (y/n)").lower()
                if (answer == "y") | (answer == "n"):
                    valid_answer = True

            if valid_answer == "n":
                return "Move aborted."

        self.board.remove_piece(row_i, col_i)
        final_position_contents = initial_position_contents
