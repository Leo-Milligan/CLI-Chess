#!/usr/bin/env python3

from Pieces import piece

class knight(piece):

    def piece_specfic_move_checks(self, initial_position, final_position, take_piece_flag):

        intermediate_position_list = []

        row_i, col_i = initial_position
        row_f, col_f = final_position

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        if not (
                (abs(col_delta) == 2) and (abs(row_delta) == 1) or
                (abs(col_delta) == 1) and (abs(row_delta) == 2)
        ):
            return (False, "Invalid move for this piece.", intermediate_position_list)

        final_position_contents = self.chess_board.get_piece(final_position)

        if not final_position_contents:
            return (True, None, intermediate_position_list)

        if take_piece_flag == False:

            while True:
                answer = input("Would you like to take the piece? (y/n) ").lower()
                if answer in ("y", "n"):
                    break

            if answer == "n":
                return (False, "Move aborted.", intermediate_position_list)

        return (True, None, intermediate_position_list)
