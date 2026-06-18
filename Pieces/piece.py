#!/usr/bin/env python3

class piece:

    def __init__(self, colour, chess_board):

        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.chess_board = chess_board
        self.has_moved = False

    def generic_move_checks(self, initial_position, final_position):

        if final_position == initial_position:
            return (False, "Final position is the same as initial position.")

        final_position_contents = self.chess_board.get_piece(final_position)

        if final_position_contents and final_position_contents.colour == self.colour:
            return (False, "Move obstructed.")

        return (True, None)

    def check_move_validity(self, initial_position, final_position, take_piece_flag):

        valid, error = self.generic_move_checks(initial_position, final_position)
        if valid is not True:
            return (False, error)

        valid, error, _ = self.piece_specific_move_checks(initial_position, final_position, take_piece_flag)
        if valid is not True:
            return (False, error)

        pinned_piece = self.chess_board.is_piece_pinned(initial_position)
        if pinned_piece:
            return(False, "Invalid move: piece is pinned.")

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        own_king_in_check, _ = self.chess_board.king_in_check(initial_position_contents.colour)
        if own_king_in_check:

            self.chess_board.move_piece(initial_position, final_position)

            king_in_check, _ = self.chess_board.king_in_check(initial_position_contents.colour)

            self.chess_board.remove_piece(initial_position)
            self.chess_board.remove_piece(final_position)

            self.chess_board.insert_piece(initial_position_contents, initial_position)
            self.chess_board.insert_piece(final_position_contents, final_position)

            if king_in_check:
                return (False, "Invalid move: defend your king!")

        return (True, None)


    def piece_specific_move_checks(self, initial_position, final_position, take_piece_flag):
        raise NotImplementedError("Override in Subclass")
