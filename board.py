#!/usr/bin/env python3

from Pieces.pawn import pawn
from Pieces.rook import rook
from Pieces.bishop import bishop
from Pieces.knight import knight
from Pieces.king import king
from Pieces.queen import queen

class chess_board:
    def __init__(self, num_rows = 8, num_cols = 8) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.board = [[None for _ in range(self.num_rows)] for _ in range(self.num_cols)]

    def create_piece(self, piece_type, colour, row, col):
        self.board[row][col] = piece_type(colour)

    def remove_piece(self, row, col):
        self.board[row][col] = None

    def set_board(self):
        self.board = [[None for _ in range(self.num_rows)] for _ in range(self.num_cols)]

        for i in range(self.num_rows):
            self.create_piece(pawn, "white", 1, i)
