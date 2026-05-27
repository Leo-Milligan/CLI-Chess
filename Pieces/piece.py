#!/usr/bin/env python3

class piece:

    def __init__(self, colour, chess_board) -> None:

        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.chess_board = chess_board
        self.has_moved = False

    def generic_move_checks(self, initial_position, final_position):

        if final_position == initial_position:
            return False, "Final position is the same as initial position."

        final_position_contents = self.chess_board.get_piece(final_position)

        if final_position_contents and final_position_contents.colour == self.colour:
            return False, "Move obstructed."

        return True, None

    def move_piece(self, initial_position, final_position, take_piece_flag):

        pre_move_initial_position_contents = self.chess_board.get_piece(initial_position)
        pre_move_final_position_contents = self.chess_board.get_piece(final_position)

        valid, error = self.generic_move_checks(initial_position, final_position)
        if valid is not True:
            print(error)
            return

        valid, error = self.piece_specific_move_checks(initial_position, final_position, take_piece_flag)
        if valid is not True:
            print(error)
            return

        self.chess_board.move_piece(initial_position, final_position)

        own_king_in_check = self.chess_board.king_in_check(self.colour)
        if own_king_in_check:
            print("Invalid move: defend your king!")

            row_i, col_i = initial_position
            row_f, col_f = final_position

            self.chess_board.board[row_i][col_i] = pre_move_initial_position_contents
            self.chess_board.board[row_f][col_f] = pre_move_final_position_contents
            return

        pre_move_initial_position_contents.has_moved = True

        self.chess_board.piece_positions.pop(tuple(initial_position), None)
        self.chess_board.piece_positions.pop(tuple(final_position), None)
        self.chess_board.piece_positions.update({tuple(final_position): pre_move_initial_position_contents})

        if pre_move_initial_position_contents.name == "king":
            self.chess_board.king_postions.update({pre_move_initial_position_contents.colour: tuple(initial_position)})

    def piece_specific_move_checks(self, initial_position, final_position, take_piece_flag):
        raise NotImplementedError("Override in Subclass")
