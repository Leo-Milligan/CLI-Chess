#!/usr/bin/env python3

class piece:
    def __init__(self, colour, chess_board) -> None:
        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.chess_board = chess_board
        self.has_moved = False
