#!/usr/bin/env python3

from Pieces import piece

class king(piece):

    def __init__(self, colour, chess_board):
        super().__init__(colour, chess_board)
        self.can_castle_if_valid = False

    def piece_specific_move_checks(self, initial_position, final_position, take_piece_flag):

        intermediate_position_list = []

        row_i, col_i = initial_position
        row_f, col_f = final_position

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        if (abs(col_delta) > 1) or (abs(row_delta) > 1):
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
            return (False, "Move obstructed (hint: include 'x' to take a piece).", intermediate_position_list)

        return (True, None, intermediate_position_list)

    def get_moves_to_check(self, initial_position):

        final_positions_to_check = []

        row_i, col_i = initial_position

        for delta_row in [-1, 0, 1]:
            for delta_col in [-1, 0, 1]:

                if delta_row == delta_col == 0:
                    continue

                row_f = row_i + delta_row
                col_f = col_i + delta_col

                valid, _ = self.chess_board.check_position_exists([row_f, col_f])

                if valid:
                    final_positions_to_check.append([row_f, col_f])

        return final_positions_to_check
