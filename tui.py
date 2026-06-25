#!/usr/bin/env python3

from board import chess_board

from textual.app import App
from textual.containers import Grid
from textual.widgets import Footer, Header, Static
from textual.color import Color

class ChessBoardGrid(Grid):

    def __init__(self, num_rows, num_cols):
        super().__init__(id = "chess_board_grid")
        self.num_rows = num_rows
        self.num_cols = num_cols

    def compose(self):

        self.styles.grid_size_columns = self.num_cols
        self.styles.grid_size_rows = self.num_rows

        for col in range(self.num_cols):
            for row in range(self.num_rows):

                cell = Static(classes="cell")

                if (row + col) % 2:
                    cell.styles.background = Color(150, 100, 60)
                else:
                    cell.styles.background = Color(210, 195, 180)

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

        yield ChessBoardGrid(num_rows, num_cols)

    def on_mount(self):

        self.title = "CLI Chess"
        self.sub_title = "Chess in your terminal!"

if __name__ == "__main__":
    app = ChessApp()
    app.run()
