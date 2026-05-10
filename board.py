#!/usr/bin/env python3

from Pieces.king import king
from Pieces.queen import queen
from Pieces.rook import rook
from Pieces.bishop import bishop
from Pieces.knight import knight
from Pieces.pawn import pawn

piece_types = [king,
               queen,
               rook,
               bishop,
               knight,
               pawn]

piece_symbols = {"white": {"king": "♔",
                           "queen": "♕",
                           "rook": "♖",
                           "bishop": "♗",
                           "knight": "♘",
                           "pawn": "♙"
                           },

                 "black": {"king": "♚",
                           "queen": "♛",
                           "rook": "♜",
                           "bishop": "♝",
                           "knight": "♞",
                           "pawn": "♟"}
                 }

class chess_board:
    def __init__(self, num_rows = 8, num_cols = 8) -> None:

        if not isinstance(num_rows, int) or not isinstance(num_cols, int):
            raise TypeError("The number of rows and number of columns must be integers.")
        elif (num_rows <= 0) | (num_cols <= 0):
            raise ValueError("The number of rows and number of columns must be greater than one.")
        elif (num_rows >= 16) | (num_cols >= 16):
            raise ValueError("The maximum number of rows and columns is 16.")

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.board = [[None for _ in range(self.num_rows)] for _ in range(self.num_cols)]

    def create_piece(self, piece_type, colour, row, col):
      
        if piece_type not in piece_types:
            raise NameError(f"That is not a valid piece type.")
        elif colour not in ("white", "black"):
            raise NameError("That is not a valid colour.")
        elif (row < 0) | (col < 0):
            raise ValueError("The row number and column number must be greater than one.")
        elif (row > self.num_rows - 1) | (col > self.num_cols - 1):
            raise NameError("The column or row selected exceeds the board size.")

        self.board[row][col] = piece_type(colour, self)

    def remove_piece(self, row, col):

        if (row <= 0) | (col <= 0):
            raise ValueError("The row number and column number must be greater than one.")
        elif (row > self.num_rows) | (col > self.num_cols):
            raise NameError("The column or row selected exceeds the board size.")

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

        self.mirror_board()

    def mirror_board(self):
        
        for col in range(self.num_cols):
            for row in range(self.num_rows):

                cell_contents = self.board[col][row]

                if  cell_contents == None:
                    continue

                piece_type = type(cell_contents)
                colour = cell_contents.colour

                if (colour == "white") & piece_type in piece_types:
                    self.create_piece(piece_type, "black", self.num_cols-col-1, row)

    def show_board(self):

        # printing top line
        string = ""
        for _ in range(self.num_rows):
            string += "+---"
        string += "+"
        print(string)

        # printing main body
        for col in range(self.num_cols):
            string = ""
            for row in range(self.num_rows):

                cell_contents = self.board[col][row]

                if cell_contents == None:
                    piece_symbol = " "
                else:
                    piece_name = cell_contents.piece_name
                    piece_colour = cell_contents.colour
                    piece_symbol = piece_symbols[piece_colour][piece_name]

                string += f"| {piece_symbol} "
            string += "|"
            print(string)

            string = ""
            for _ in range(self.num_rows):
                string += "+---"
            string += "+"
            print(string)

grid = chess_board()
grid.set_board()
grid.show_board()
