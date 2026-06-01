#!/usr/bin/env python3

from Pieces import piece

class queen(piece):

    def piece_specific_move_checks(self, initial_position, final_position, take_piece_flag):

        intermediate_position_list = []

        row_i, col_i = initial_position
        row_f, col_f = final_position

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        is_straight = (col_delta == 0) or (row_delta == 0)
        is_diagonal = abs(col_delta) == abs(row_delta)

        if not (is_straight or is_diagonal):
            return (False, "Invalid move for this piece.", intermediate_position_list)

        col_step = int(col_delta / abs(col_delta)) if col_delta != 0 else 0
        row_step = int(row_delta / abs(row_delta)) if row_delta != 0 else 0

        intermediate_position = [row_i + row_step, col_i + col_step]

        while intermediate_position != final_position:
            intermediate_position_list.append(intermediate_position)
            intermediate_position_contents = self.chess_board.get_piece(intermediate_position)
            if not intermediate_position_contents:
                intermediate_position[0] += row_step
                intermediate_position[1] += col_step
                continue
            else:
                return (False, "Move obstructed.", intermediate_position_list)

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
