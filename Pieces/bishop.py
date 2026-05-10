#!/usr/bin/env python3

class bishop:
    def __init__(self, colour, board) -> None:
        self.colour = colour
        self.piece_name = self.__class__.__name__
        self.board = board
