#!/usr/bin/env python3

from Pieces import piece

class knight(piece):

    def piece_specific_move_checks(self, initial_position, final_position, take_piece_flag):

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
            return (False, "Move obstructed (hint: include 'x' to take a piece).", intermediate_position_list)

        return (True, None, intermediate_position_list)

    def get_moves_to_check(self, initial_position):

        final_positions_to_check = []

        row_i, col_i = initial_position

        for delta_row in (-2, 2):
            for delta_col in (-1, 1):
                row_f = row_i + delta_row
                col_f = col_i + delta_col

                valid, _ = self.chess_board.check_position_exists([row_f, col_f])

                if valid:
                    final_positions_to_check.append([row_f,col_f])

        for delta_row in (-1, 1):
            for delta_col in (-2, 2):
                row_f = row_i + delta_row
                col_f = col_i + delta_col

                valid, _ = self.chess_board.check_position_exists([row_f, col_f])

                if valid:
                    final_positions_to_check.append([row_f,col_f])

        return final_positions_to_check
