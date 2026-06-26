#!/usr/bin/env python3

from board import chess_board

import json

from textual.app import App
from textual.containers import Grid
from textual.widgets import Footer, Header, Static
from textual.color import Color

with open("ui_style_sheet.json") as data:
    ui_style_sheet = json.load(data)

class ChessBoardGrid(Grid):

    def __init__(self, board, num_rows, num_cols, piece_symbols, board_colour):
        super().__init__(id = "chess_board_grid")
        self.board = board
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.piece_symbols = piece_symbols
        self.board_colour = board_colour

    def compose(self):

        self.styles.grid_size_columns = self.num_cols
        self.styles.grid_size_rows = self.num_rows

        for col in range(self.num_cols):
            for row in range(self.num_rows):

                cell_contents = self.board[col][row]

                if cell_contents == None:
                    piece_symbol = ""
                    piece_colour = None
                else:
                    piece_name = type(cell_contents).__name__
                    piece_colour = cell_contents.colour
                    piece_symbol = ui_style_sheet["piece_symbols"][self.piece_symbols][piece_name]

                cell = Static(piece_symbol, classes="cell")

                if piece_colour == "black":
                    r,g,b = ui_style_sheet["board_colours"][self.board_colour]["dark_piece_colour"]
                    cell.styles.color = Color(r, g, b)
                elif piece_colour == "white":
                    r,g,b = ui_style_sheet["board_colours"][self.board_colour]["light_piece_colour"]
                    cell.styles.color = Color(r, g, b)

                if (row + col) % 2:
                    r,g,b = ui_style_sheet["board_colours"][self.board_colour]["dark_square_colour"]
                    cell.styles.background = Color(r, g, b)
                else:
                    r,g,b = ui_style_sheet["board_colours"][self.board_colour]["light_square_colour"]
                    cell.styles.background = Color(r, g, b)

                yield cell

class ChessApp(App):

    CSS_PATH = "chess_board_cell.tcss"

    def compose(self):

        yield Header()
        yield Footer()

        self.chess_board = chess_board()
        self.chess_board.set_board()

        num_rows = self.chess_board.num_rows
        num_cols = self.chess_board.num_cols
        board = self.chess_board.board

        piece_style = "small"
        board_colour = "default"

        yield ChessBoardGrid(board, num_rows, num_cols, piece_style, board_colour)

    def on_mount(self):

        self.title = "CLI Chess"
        self.sub_title = "Chess in your terminal!"

if __name__ == "__main__":
    app = ChessApp()
    app.run()
