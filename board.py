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
            return (False, "The row number and column number must be greater than one.")
        elif (row > self.num_rows - 1) | (col > self.num_cols - 1):
            return (False, "The column or row selected exceeds the board size.")
        else:
            return (True, None)

    def create_piece(self, piece_type, colour, position):

        if piece_type not in piece_types:
            raise NameError(f"That is not a valid piece type.")
        elif colour not in ("white", "black"):
            raise NameError("That is not a valid colour.")

        valid, error = self.check_position_exists(position)
        if valid == False:
            raise ValueError(error)

        row, col = position
        self.board[row][col] = piece_type(colour, self)

        self.piece_positions[colour].update({(row, col): self.board[row][col]})
        if piece_type == king:
            self.king_positions.update({colour: tuple(position)})

    def remove_piece(self, position):

        valid, error = self.check_position_exists(position)
        if valid == False:
            raise ValueError(error)

        position_contents = self.get_piece(position)

        row, col = position
        self.board[row][col] = None

        if position_contents == None:
            return

        self.piece_positions[position_contents.colour].pop(tuple(position), None)

        if position_contents.piece_name == "king":
            self.king_positions.pop(position_contents.colour, None)

    def insert_piece(self, piece, position):

        valid, error = self.check_position_exists(position)
        if valid == False:
            raise ValueError(error)

        if piece == None:
            self.remove_piece(position)
            return

        if type(piece) not in piece_types:
            raise NameError(f"That is not a valid piece type.")

        row, col = position
        self.board[row][col] = piece

        self.piece_positions[piece.colour].update({tuple(position): piece})

        if piece.piece_name == "king":
            self.king_positions.update({piece.colour: tuple(position)})

    def get_piece(self, position):

        valid, error = self.check_position_exists(position)
        if valid == False:
            raise ValueError(error)

        row, col = position
        return self.board[row][col]

    def move_piece(self, initial_position, final_position):

        valid, error = self.check_position_exists(initial_position)
        if valid == False:
            raise ValueError(error)

        valid, error = self.check_position_exists(final_position)
        if valid == False:
            raise ValueError(error)

        initial_position_contents = self.get_piece(initial_position)

        self.remove_piece(initial_position)
        self.remove_piece(final_position)

        self.insert_piece(initial_position_contents, final_position)

    def is_square_attacked(self, position, by_colour):

        valid, error = self.check_position_exists(position)
        if valid == False:
            raise ValueError(error)

        attacking_cells = []

        for cell in self.piece_positions[by_colour]:
            cell_contents = self.piece_positions[by_colour][cell]
            valid, _, _ = cell_contents.piece_specific_move_checks(list(cell), list(position), True)
            if valid == True:
                attacking_cells.append(cell)

        cell_is_attacked = True if attacking_cells else False
        return (cell_is_attacked, attacking_cells)

    def king_in_check(self, colour):

        opposite_colour = "black" if colour == "white" else "white"

        if colour not in self.king_positions:
            raise ValueError(f"Board does not conain a {colour} king.")

        cell_is_attacked, attacking_cells =  self.is_square_attacked(self.king_positions[colour], opposite_colour)

        return (cell_is_attacked, attacking_cells)

    def king_in_checkmate(self, colour):

        king_position = list(self.king_positions[colour])
        opposite_colour = "black" if colour == "white" else "white"

        cell_is_attacked, attacking_cells =  self.is_square_attacked(king_position, opposite_colour)
        if not cell_is_attacked:
            return False

        king_row, king_col = king_position
        possible_safe_positions = []

        for delta_row in [-1, 0, 1]:
            for delta_col in [-1, 0, 1]:

                row = king_row + delta_row
                col = king_col + delta_col
                position = [row, col]

                valid, _ = self.check_position_exists(position)
                if not valid:
                    continue

                position_contents = self.get_piece(position)
                if position_contents and position_contents.colour == colour:
                    continue

                possible_safe_positions.append(position)

        for position in possible_safe_positions:
            initial_position_contents = self.get_piece(king_position)
            final_position_contents = self.get_piece(position)

            self.move_piece(king_position, position)

            king_in_check, _ = self.king_in_check(colour)

            self.remove_piece(king_position)
            self.remove_piece(position)

            self.insert_piece(initial_position_contents, king_position)
            self.insert_piece(final_position_contents, position)

            if not king_in_check:
                return False

        total_intermediate_positions = []
        for attacking_cell in attacking_cells:

            attacking_cell_contents = self.get_piece(attacking_cell)

            _, _, intermediate_position_list = attacking_cell_contents.piece_specific_move_checks(attacking_cell, king_position, True)

            intermediate_position_list.append(list(attacking_cell))
            for item in intermediate_position_list:
                total_intermediate_positions.append(item)

        for friendly_piece_position in list(self.piece_positions[colour]):

            friendly_piece = self.get_piece(friendly_piece_position)

            if friendly_piece.piece_name == "king":
                continue

            pinned_piece = self.is_piece_pinned(friendly_piece_position)
            if pinned_piece:
                continue

            for position in total_intermediate_positions:

                initial_position_contents = self.get_piece(friendly_piece_position)
                final_position_contents = self.get_piece(position)

                valid, _ = initial_position_contents.move_piece(friendly_piece_position, position, True)
                if not valid:
                    continue

                king_in_check, _ = self.king_in_check(colour)

                self.remove_piece(friendly_piece_position)
                self.remove_piece(position)

                self.insert_piece(initial_position_contents, friendly_piece_position)
                self.insert_piece(final_position_contents, position)

                if not king_in_check:
                    return False

        return True

    def is_piece_pinned(self, position):

        valid, error = self.check_position_exists(position)
        if valid == False:
            raise ValueError(error)

        position_contents = self.get_piece(position)
        if position_contents == None:
            raise ValueError("There is no piece in this square.")

        _, initial_attacking_cells = self.king_in_check(position_contents.colour)

        self.remove_piece(position)

        king_in_check, final_attacking_cells = self.king_in_check(position_contents.colour)

        self.insert_piece(position_contents, position)

        if king_in_check and len(final_attacking_cells) > len(initial_attacking_cells):
            return True
        else:
            return False

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
