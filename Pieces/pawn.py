#!/usr/bin/env python3

from Pieces import piece

class pawn(piece):

    def __init__(self, colour, chess_board) -> None:
        super().__init__(colour, chess_board)
        self.en_passant_vulnerable_flag = False

    def piece_specific_move_checks(self, initial_position, final_position, take_piece_flag):

        intermediate_position_list = []

        row_i, col_i = initial_position
        row_f, col_f = final_position

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if initial_position_contents.colour == "black":
            corrected_row_delta = -row_delta
        else:
            corrected_row_delta = row_delta

        valid_diagonal_direction = (abs(col_delta) == 1) and (corrected_row_delta == 1)

        if valid_diagonal_direction and not final_position_contents:

            en_passant_flag = self.get_en_passant_flag(initial_position, final_position, take_piece_flag)

            if en_passant_flag == False:
                return (False, "Invalid move for this piece.", intermediate_position_list)
            else:
                return (True, None, intermediate_position_list)

        if valid_diagonal_direction and final_position_contents:
            if take_piece_flag == False:
                return (False, "Move obstructed (hint: include 'x' to take a piece).", intermediate_position_list)

            return (True, None, intermediate_position_list)

        if final_position_contents:
            return (False, "Move obstructed.", intermediate_position_list)

        if self.has_moved:
            if col_delta != 0 or corrected_row_delta != 1:
                return (False, "Invalid move for this piece.", intermediate_position_list)
        elif not self.has_moved:
            if col_delta != 0 or corrected_row_delta > 2:
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

        return (True, None, intermediate_position_list)

    def get_en_passant_flag(self, initial_position, final_position, take_piece_flag):

        if take_piece_flag == False:
            return False

        row_i, col_i = initial_position
        row_f, col_f = final_position

        col_delta = col_f - col_i
        row_delta = row_f - row_i

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if initial_position_contents.colour == "black":
            corrected_row_delta = -row_delta
        else:
            corrected_row_delta = row_delta

        valid_diagonal_direction = (abs(col_delta) == 1) and (corrected_row_delta == 1)

        if not valid_diagonal_direction or final_position_contents:
            return False

        adjacent_position = [initial_position[0], initial_position[1] + col_delta]

        valid, _ = self.chess_board.check_position_exists(adjacent_position)
        if not valid:
            return False

        cell_contents = self.chess_board.get_piece(adjacent_position)

        if type(cell_contents) != pawn:
            return False
        elif cell_contents.en_passant_vulnerable_flag != True:
            return False
        else:
            return True
