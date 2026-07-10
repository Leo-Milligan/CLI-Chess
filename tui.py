#!/usr/bin/env python3

from board import chess_board
from game import game
from Pieces import *

from textual import on
from textual.app import App
from textual.containers import Grid, HorizontalGroup
from textual.widgets import Static, Input, Label, Button, Footer, DataTable
from textual.color import Color
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen

import copy
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

class GameOverScreen(ModalScreen):

    def __init__(self, game_over_message):

        super().__init__()
        self.game_over_message = game_over_message

    def compose(self):

        with Grid(id="dialog"):
            yield Label(self.game_over_message, id="message")
            yield Button("Quit", variant="error", id="quit")
            yield Button("Restart", variant="success", id="restart")
            yield Button("Review", variant="primary", id="review")

    def on_button_pressed(self, event):

        if event.button.id == "quit":
            self.dismiss("quit")
        elif event.button.id == "restart":
            self.dismiss("restart")
        elif event.button.id == "review":
            self.dismiss("review")

class StatusBar(Static):

    def compose(self):

        with HorizontalGroup():
            yield TurnLabel()
            yield Label("Enter Move: ", id = "command_line_prompt")
            yield Input(compact = True, id = "command_line")

        yield Label(id = "message_line")

class CapturedPiecesDisplay(Label):

    captured_piece_list = reactive([])

    def __init__(self, id):

        super().__init__(id=id)
        self.piece_type_counts = {"king": 0, "queen": 0, "rook": 0, "bishop": 0, "knight": 0, "pawn": 0}

    def watch_captured_piece_list(self):

        string = ""

        self.update_piece_type_counts()

        for piece_type in self.piece_type_counts:
            if self.piece_type_counts[piece_type] > 0:
                piece_symbol = ui_style_sheet["piece_symbols"]["small"][piece_type]
                number_of_pieces = self.piece_type_counts[piece_type]
                string += f"{piece_symbol} x{number_of_pieces} "

        self.update(string)

    def update_piece_type_counts(self):

        self.piece_type_counts = {"king": 0, "queen": 0, "rook": 0, "bishop": 0, "knight": 0, "pawn": 0}

        for piece in self.captured_piece_list:
            piece_name = type(piece).__name__
            if piece_name in list(self.piece_type_counts):
                self.piece_type_counts[piece_name] += 1

class MoveDataTable(DataTable):

    move_notation_history = reactive({"white": [],
                                      "black": []})

    def watch_move_notation_history(self):

        self.clear()

        for i in range(len(self.move_notation_history["white"])):

            row_number = i + 1
            current_white_move = self.move_notation_history["white"][i] if i < len(self.move_notation_history["white"]) else ""
            current_black_move = self.move_notation_history["black"][i] if i < len(self.move_notation_history["black"]) else ""

            self.add_row(row_number,current_white_move,current_black_move)

    def on_mount(self):
        self.add_columns(("Turn", "turn"),
                         ("W", "white"),
                         ("B", "black"))
        self.can_focus = False
        self.cursor_type = "row"

class ChessApp(App):

    CSS_PATH = "chess_board_cell.tcss"
    BINDINGS = [("a", "advance_move", "Advance Move"),
                ("u", "undo_move", "Undo Move"),
                ("q", "exit_review_mode", "Exit Review Mode")]

    def __init__(self):

        super().__init__()
        self.chess_board = chess_board()
        self.game = game(self.chess_board)
        self.pending_question_information = None
        self.cached_move_information = None
        self.last_game_over_message = None
        self.review_mode = False

    def compose(self):

        num_rows = self.chess_board.num_rows
        num_cols = self.chess_board.num_cols

        self.chess_board.set_board()
        board = self.chess_board.board

        piece_style = "small"
        board_colour = "default"

        yield CapturedPiecesDisplay(id="black_captured_pieces_display")
        yield ChessBoardGrid(board, num_rows, num_cols, piece_style, board_colour)
        yield MoveDataTable()
        yield CapturedPiecesDisplay(id="white_captured_pieces_display")
        yield StatusBar()

    def action_exit_review_mode(self):
        self.exit_review_mode()

    def action_advance_move(self):

        self.game.advance_once_using_move_delta()
        self.refresh_bindings()
        self.query_one(ChessBoardGrid).update_board()
        self.query_one(TurnLabel).turn_colour = self.game.turn_colour
        self.query_one("#white_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_white_pieces.copy()
        self.query_one("#black_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_black_pieces.copy()
        if self.game.move_number > 1:
            self.query_one(MoveDataTable).move_cursor(row = self.game.move_number // 2 - 1)

    def action_undo_move(self):

        self.game.undo_once_using_move_delta()
        self.refresh_bindings()
        self.query_one(ChessBoardGrid).update_board()
        self.query_one(TurnLabel).turn_colour = self.game.turn_colour
        self.query_one("#white_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_white_pieces.copy()
        self.query_one("#black_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_black_pieces.copy()
        if self.game.move_number > 1:
            self.query_one(MoveDataTable).move_cursor(row = self.game.move_number // 2 - 1)

    def check_action(self, action, parameters):

        if action == "exit_review_mode" and not self.review_mode:
            return False
        if action == "advance_move" and self.game.move_number == (len(self.game.move_history) + 1):
            return None
        if action == "undo_move" and self.game.move_number == 1:
            return None
        return True

    def on_mount(self):

        self.query_one(TurnLabel).turn_colour = self.game.turn_colour
        self.chess_board.update_castle_flag()

    @on(Input.Submitted)
    async def handle_user_input(self):

        self.clear_message()

        command_line = self.query_one(Input)
        player_input = command_line.value.strip(" +#!?")
        command_line.value = ""

        if self.pending_question_information:
            move_information = self.game.interperate_user_preferences_answer(player_input, self.cached_move_information, self.pending_question_information)
            self.query_one(TurnLabel).turn_colour = self.game.turn_colour
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

            if question_information["question_id"] == "draw_offer":
                self.game.turn_colour, self.game.opposite_colour = self.game.opposite_colour, self.game.turn_colour
                self.query_one(TurnLabel).turn_colour = self.game.turn_colour

            return
        else:
            self.query_one("#command_line_prompt", Label).update("Enter Move: ")
            self.pending_question_information = None
            self.cached_move_information = None

        result = self.game.apply_move(move_information)

        self.query_one(ChessBoardGrid).update_board()
        self.query_one(TurnLabel).turn_colour = self.game.turn_colour
        self.query_one("#white_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_white_pieces.copy()
        self.query_one("#black_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_black_pieces.copy()
        self.query_one(MoveDataTable).move_notation_history = copy.deepcopy(self.game.move_notation_history)
        if self.game.move_number > 1:
            self.query_one(MoveDataTable).move_cursor(row = self.game.move_number // 2 - 1)

        self.check_for_game_end(result)

        if result["message"]:
            await self.display_message(result["message"])

    def check_for_game_end(self, result):

        if result["resign"]:
            message = f"{self.game.winner.capitalize()} Wins!"
        elif result["checkmate"]:
            message = f"{self.game.winner.capitalize()} Wins!"
        elif result["draw"]:
            message = "Game ends in a draw!"
        else:
            return

        self.last_game_over_message = message
        self.push_screen(GameOverScreen(message), self.handle_game_over)


    def handle_game_over(self, choice):

        if choice == "quit":
            self.exit()
        elif choice == "restart":
            self.game.reset_game()
            self.query_one(ChessBoardGrid).update_board()
            self.query_one(TurnLabel).turn_colour = self.game.turn_colour
            self.query_one("#white_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_white_pieces.copy()
            self.query_one("#black_captured_pieces_display", CapturedPiecesDisplay).captured_piece_list = self.game.captured_black_pieces.copy()
            self.query_one(MoveDataTable).move_notation_history = copy.deepcopy(self.game.move_notation_history)
            if self.game.move_number > 1:
                self.query_one(MoveDataTable).move_cursor(row = self.game.move_number // 2 - 1)
        elif choice == "review":
            self.enter_review_mode()

    async def display_message(self, message):

        message_line = self.query_one("#message_line", Label)
        message_line.update(message)

        self.set_timer(2.5, self.clear_message)

    def clear_message(self):
        message_line = self.query_one("#message_line", Label)
        message_line.update("")

    def enter_review_mode(self):

        self.query_one(StatusBar).display = False

        if not self.query(Footer):
            self.mount(Footer())

        self.review_mode = True

    def exit_review_mode(self):

        self.query_one(StatusBar).display = True

        footer = self.query(Footer)
        if footer:
            footer.remove()

        self.review_mode = False

        self.push_screen(GameOverScreen(self.last_game_over_message), self.handle_game_over)

if __name__ == "__main__":
    app = ChessApp()
    app.run()
