#!/usr/bin/env python3

from board import chess_board
from game import game

from asyncio import sleep
from textual import on
from textual.app import App
from textual.containers import Grid, HorizontalGroup
from textual.widgets import Static, Input, Label
from textual.color import Color
from textual.reactive import reactive

import json

with open("ui_style_sheet.json") as data:
    ui_style_sheet = json.load(data)

class Cell(Static):

    def __init__(self, board, board_colour, piece_symbols, row, col):
        super().__init__(classes = "cell")
        self.board = board
        self.piece_symbols = piece_symbols
        self.board_colour = board_colour
        self.row = row
        self.col = col

    def colour_cell(self):
        if (self.row + self.col) % 2:
            self.styles.background = Color.parse(ui_style_sheet["board_colours"][self.board_colour]["dark_square_colour"])
        else:
            self.styles.background = Color.parse(ui_style_sheet["board_colours"][self.board_colour]["light_square_colour"])

    def populate_cell(self):

        cell_contents = self.board[self.col][self.row]

        if cell_contents == None:
            piece_symbol = ""
            piece_colour = None
        else:
            piece_name = type(cell_contents).__name__
            piece_colour = cell_contents.colour
            piece_symbol = ui_style_sheet["piece_symbols"][self.piece_symbols][piece_name]

        self.update(piece_symbol)

        if piece_colour == "black":
            self.styles.color = Color.parse(ui_style_sheet["board_colours"][self.board_colour]["dark_piece_colour"])
        elif piece_colour == "white":
            self.styles.color = Color.parse(ui_style_sheet["board_colours"][self.board_colour]["light_piece_colour"])

class ChessBoardGrid(Grid):

    def __init__(self, board, num_rows, num_cols, piece_symbols, board_colour):
        super().__init__(id = "chess_board_grid")
        self.board = board
        self.game = game
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.piece_symbols = piece_symbols
        self.board_colour = board_colour

    def compose(self):

        self.styles.grid_size_columns = self.num_cols
        self.styles.grid_size_rows = self.num_rows

        for col in range(self.num_cols):
            for row in range(self.num_rows):
                cell = Cell(self.board, self.board_colour, self.piece_symbols, row, col)
                cell.colour_cell()
                cell.populate_cell()
                yield cell

    def update_board(self):
        for cell in self.query(Cell):
            cell.populate_cell()

class TurnLabel(Label):

    turn_colour = reactive("white")

    def watch_turn_colour(self):
        self.update(f" {"W" if self.turn_colour == "white" else "B"} | ")

class ChessApp(App):

    CSS_PATH = "chess_board_cell.tcss"

    def __init__(self):

        super().__init__()
        self.chess_board = chess_board()
        self.game = game(self.chess_board)
        self.pending_question_information = None
        self.cached_move_information = None

    def compose(self):

        num_rows = self.chess_board.num_rows
        num_cols = self.chess_board.num_cols

        self.chess_board.set_board()
        board = self.chess_board.board

        piece_style = "small"
        board_colour = "default"

        yield ChessBoardGrid(board, num_rows, num_cols, piece_style, board_colour)

        with HorizontalGroup(id = "status_bar"):
            yield TurnLabel()
            yield Label("Enter Move: ", id = "command_line_prompt")
            yield Input(compact = True, id = "command_line")

        yield Label(id = "message_line")

    def on_mount(self):

        self.query_one(TurnLabel).turn_colour = self.game.turn_colour


    @on(Input.Submitted)
    async def handle_user_input(self):

        self.clear_message()

        command_line = self.query_one(Input)
        player_input = command_line.value.strip(" +#!?")
        command_line.value = ""

        if self.pending_question_information:
            move_information = self.game.interperate_user_preferences_answer(player_input, self.cached_move_information, self.pending_question_information)
        else:
            move_information = self.game.interperet_move_notation(list(player_input))

        if not move_information["valid"]:
            self.query_one("#command_line_prompt", Label).update("Enter Move: ")
            self.pending_question_information = None
            self.cached_move_information = None

            if move_information.get("error") is not None:
                await self.display_message(move_information["error"])

            return

        question_information = self.game.get_user_preferences_question(move_information)
        if question_information:
            self.query_one("#command_line_prompt", Label).update(question_information["question"])
            self.pending_question_information = question_information
            self.cached_move_information = move_information
            return
        else:
            self.query_one("#command_line_prompt", Label).update("Enter Move: ")
            self.pending_question_information = None
            self.cached_move_information = None

        result = self.game.apply_move(move_information)

        chess_board = self.query_one(ChessBoardGrid)
        chess_board.update_board()

        self.query_one(TurnLabel).turn_colour = self.game.turn_colour

        if result["message"]:
            await self.display_message(result["message"])

    async def display_message(self, message):

        message_line = self.query_one("#message_line", Label)
        message_line.update(message)

        self.set_timer(2.5, self.clear_message)

    def clear_message(self):
        message_line = self.query_one("#message_line", Label)
        message_line.update("")

if __name__ == "__main__":
    app = ChessApp()
    app.run()
