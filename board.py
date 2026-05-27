#!/usr/bin/env python3

from Pieces import *

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
        elif (num_rows <= 0) or (num_cols <= 0):
            raise ValueError("The number of rows and number of columns must be greater than one.")
        elif (num_rows >= 16) or (num_cols >= 16):
            raise ValueError("The maximum number of rows and columns is 16.")

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.board = [[None for _ in range(self.num_rows)] for _ in range(self.num_cols)]

        self.piece_positions = {"white": {},
                                "black": {}
                                }

        self.king_positions = {}

    def check_position_exists(self, position):

        row, col = position

        if (row < 0) | (col < 0):
            raise ValueError("The row number and column number must be greater than one.")
        elif (row > self.num_rows - 1) | (col > self.num_cols - 1):
            raise ValueError("The column or row selected exceeds the board size.")

    def create_piece(self, piece_type, colour, position):

        if piece_type not in piece_types:
            raise NameError(f"That is not a valid piece type.")
        elif colour not in ("white", "black"):
            raise NameError("That is not a valid colour.")

        self.check_position_exists(position)

        row, col = position
        self.board[row][col] = piece_type(colour, self)

        self.piece_positions[colour].update({(row, col): self.board[row][col]})
        if piece_type == king:
            self.king_positions.update({colour: position})

    def remove_piece(self, position):

        self.check_position_exists(position)

        row, col = position
        self.board[row][col] = None

    def get_piece(self, position):

        self.check_position_exists(position)

        row, col = position
        return self.board[row][col]

    def move_piece(self, initial_position, final_position):

        self.check_position_exists(initial_position)

        self.check_position_exists(final_position)

        row_f, col_f = final_position

        self.board[row_f][col_f] = self.get_piece(initial_position)
        self.remove_piece(initial_position)

    def is_square_attacked(self, position, by_colour):

        self.check_position_exists(position)

        for cell in self.piece_positions[by_colour]:
            cell_contents = self.piece_positions[by_colour][cell]
            valid, _ = cell_contents.piece_specific_move_checks(list(cell), position, True)

            if valid == True:
                return True

        return False

    def king_in_check(self, colour):

        opposite_colour = "black" if colour == "white" else "black"

        return self.is_square_attacked(self.king_positions[colour], opposite_colour)

    def set_board(self):

        self.board = [[None for _ in range(self.num_rows)] for _ in range(self.num_cols)]

        self.create_piece(king, "white", [0, 4])

        self.create_piece(queen, "white", [0, 3])

        self.create_piece(rook, "white", [0, 0])
        self.create_piece(rook, "white", [0, self.num_cols-1])

        self.create_piece(bishop, "white", [0, 2])
        self.create_piece(bishop, "white", [0, self.num_cols-3])

        self.create_piece(knight, "white", [0, 1])
        self.create_piece(knight, "white", [0, self.num_cols-2])

        for i in range(self.num_rows):
            self.create_piece(pawn, "white", [1, i])

        self.mirror_board()

    def mirror_board(self):
        
        for col in range(self.num_cols):
            for row in range(self.num_rows):

                cell_contents = self.get_piece([row, col])

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
grid.create_piece(rook, "white", [1,1])
grid.create_piece(king, "white", [0,1])
grid.create_piece(rook, "black", [4,1])
grid.show_board()
grid.get_piece([1,1]).move_piece([1,1],[1,4],False)
grid.show_board()
