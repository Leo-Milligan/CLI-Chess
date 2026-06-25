#!/usr/bin/env python3

from board import chess_board

from textual.app import App
from textual.containers import Grid
from textual.widgets import Footer, Header, Static
from textual.color import Color

class ChessApp(App, chess_board):

    CSS_PATH = "chess_board_cell.tcss"

    def compose(self):

        yield Header()
        yield Footer()

        with Grid(id = "chess_board_grid"):
            pass

    def on_mount(self):

        self.title = "CLI Chess"
        self.sub_title = "Chess in your terminal!"

        self.chess_board = chess_board()
        self.chess_board.set_board()

        container = self.query_one("#chess_board_grid")
        container.styles.grid_size_columns = self.chess_board.num_cols
        container.styles.grid_size_rows = self.chess_board.num_rows

        for col in range(self.chess_board.num_cols):
            for row in range(self.chess_board.num_rows):

                cell = Static(classes="cell")

                if (row + col) % 2:
                    cell.styles.background = Color(150, 100, 60)
                else:
                    cell.styles.background = Color(210, 195, 180)

                container.mount(cell)

if __name__ == "__main__":
    app = ChessApp()
    app.run()
