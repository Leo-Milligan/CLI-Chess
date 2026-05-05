#!/usr/bin/env python3

from Pieces.king import king
from Pieces.queen import queen
from Pieces.rook import rook
from Pieces.bishop import bishop
from Pieces.knight import knight
from Pieces.pawn import pawn


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

        self.create_piece(king, "white", 0, 4)

        self.create_piece(queen, "white", 0, 3)

        self.create_piece(rook, "white", 0, 0)
        self.create_piece(rook, "white", 0, self.num_cols-1)

        self.create_piece(bishop, "white", 0, 2)
        self.create_piece(bishop, "white", 0, self.num_cols-3)

        self.create_piece(knight, "white", 0, 1)
        self.create_piece(knight, "white", 0, self.num_cols-2)

        for i in range(self.num_rows):
            self.create_piece(pawn, "white", 1, i)

        





grid = chess_board()
grid.set_board()
print(grid.board)        

        
