#!/usr/bin/env python3

from board import chess_board
from Pieces import *

piece_mapping = {"K": king,
                 "Q": queen,
                 "R": rook,
                 "B": bishop,
                 "N": knight,
                 "P": pawn}

class game:
    def __init__(self, chess_board) -> None:
        self.turn_colour = "white"
        self.opposite_colour = "black"
        self.turn_number = 0
        self.captured_white_pieces = []
        self.captured_black_pieces = []
        self.history = []
        self.winner = None
        self.chess_board = chess_board

    def game_loop(self):

        self.chess_board.show_board()

        while True:
            initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece, castling_flag = self.get_move()

            self.chess_board.move_piece(initial_position, final_position)

            self.chess_board.show_board()

            check, _ = self.chess_board.king_in_check(self.opposite_colour)

            if check:
                print(f"{self.opposite_colour} king in check!")
                checkmate = self.chess_board.king_in_checkmate(self.opposite_colour)
            else:
                checkmate = False

            if checkmate:
                break

            self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour

    def get_move(self):

        while True:
            player_input = list(input("Enter move: ").strip(" +#!?"))

            if len(player_input) < 2:
                print("Move patterns must be at least two characters long.")
                continue

            initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece, castling_flag = self.is_castling(player_input)
            if castling_flag:
                break

            promotional_piece, remainder, error = self.get_promotional_piece(player_input)
            if error:
                print(error)
                continue

            take_piece_flag, remainder = self.get_take_piece_flag(remainder)

            final_position, remainder, error = self.find_final_position(remainder)
            if not final_position:
                print(error)
                continue

            piece_type_to_move, remainder = self.get_piece_type_from_input(remainder)

            initial_row, initial_col, error = self.get_ambiguity_clues(remainder)
            if error:
                print(error)
                continue

            initial_position, error = self.find_initial_position(piece_type_to_move, initial_row, initial_col, final_position, take_piece_flag)
            if not initial_position:
                if error:
                    print(error)
                continue

            break

        return (initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece, castling_flag)

    def find_initial_position(self, piece_type_to_move, initial_row, initial_col, final_position, take_piece_flag):

        possible_positions = []
        for key in self.chess_board.piece_positions[self.turn_colour]:

            if initial_row and key[0] != initial_row:
                continue
            elif initial_col and key[1] != initial_col:
                continue

            cell_contents = self.chess_board.piece_positions[self.turn_colour][key]

            if type(cell_contents) == piece_type_to_move:
                possible_positions.append(list(key))

        if len(possible_positions) == 0:
            return (None, f"There are no {self.turn_colour} {piece_type_to_move.__name__}s on the board.")

        for i in possible_positions.copy():

            cell_contents = self.chess_board.get_piece(i)

            valid, _ = cell_contents.check_move_validity(i, final_position, take_piece_flag)

            if valid == False:
                possible_positions.remove(i)

        if len(possible_positions) == 0:
            return (None, f"No {self.turn_colour} {piece_type_to_move.__name__}s can make this move.")

        if len(possible_positions) == 1:
            return (possible_positions[0], None)

        initial_position = self.remove_piece_ambiguity(possible_positions, piece_type_to_move)
        if initial_position == None:
            return (None, None)

        return (initial_position, None)

    def remove_piece_ambiguity(self, possible_initial_positions, piece_type_to_move):

        possible_positions_chess_notation = []
        for position in possible_initial_positions:
            position_chess_notation = self.coordinate_to_chess_notation(position)
            possible_positions_chess_notation.append(position_chess_notation)

        prompt = f"Move is ambiguous. Do you mean the {piece_type_to_move.__name__} at {possible_positions_chess_notation[0]} (0)"

        for i in range(len(possible_initial_positions[1:])):
            string_snippet = f" or at {possible_positions_chess_notation[i + 1]} ({i + 1})"
            prompt += string_snippet

        prompt += " or press (q) to re-enter move: "

        while True:
            user_choice = input(prompt).strip().lower()
            if user_choice == "q":
                break
            if user_choice.isdigit():
                user_choice = int(user_choice)
                if 0 <= user_choice <= (len(possible_initial_positions) - 1):
                    break

        if user_choice == "q":
            return None

        initial_position = possible_initial_positions[user_choice]

        return initial_position

    def coordinate_to_chess_notation(self, positon):

        row, col = positon

        row = row + 1
        col = chr(col + 97)

        position = str(col) + str(row)

        return position

    def find_final_position(self, player_input):

        digits = []
        characters = []

        if player_input[-2].isdigit():

            if len(player_input) < 3:
                return (None, player_input, "Invalid final position.")

            digits.append(player_input[-2])

            if not player_input[-1].isdigit():
                return (None, player_input, "Invalid final position.")

            digits.append(player_input[-1])

            if not player_input[-3].isalpha():
                return (None, player_input, "Invalid final position.")

            characters.append(player_input[-3])

            player_input = player_input[:-3]

        elif player_input[-2].isalpha():
            characters.append(player_input[-2])

            if not player_input[-1].isdigit():
                return (None, player_input, "Invalid final position.")

            digits.append(player_input[-1])

            player_input = player_input[:-2]
        else:
            return (None, player_input, "Invalid final position.")

        final_col = ord(characters[0]) - 97

        digits_string = ""
        for i in digits:
            digits_string += i

        final_row = int(digits_string) - 1

        final_position = [final_row, final_col]

        valid, error = self.chess_board.check_position_exists(final_position)
        if not valid:
            return (None, player_input, error)

        return (final_position, player_input, None)

    def get_piece_type_from_input(self, player_input):

        possible_piece = None

        if player_input:
            possible_piece = player_input[0]

        if possible_piece and possible_piece in piece_mapping:
            del player_input[0]
            piece_type_to_move = piece_mapping[possible_piece]
        else:
            piece_type_to_move = pawn

        return (piece_type_to_move, player_input)

    def get_ambiguity_clues(self, player_input):

        initial_row = None
        initial_col = None

        digits = []
        characters = []

        for i in player_input:
            if i.isdigit():
                digits.append(i)
            if i.isalpha():
                characters.append(i)

        if len(characters) > 1:
            return (None, None, "Invalid initial position")

        digits_string = ""
        for i in digits:
            digits_string += i

        if len(characters) == 1:
            initial_col = ord(characters[0]) - 97

            if 0 > initial_col > self.chess_board.num_cols:
                initial_col = None

        if digits:
            initial_row = int(digits_string) - 1

            if 0 > initial_row > self.chess_board.num_cols:
                initial_col = None

        return (initial_row, initial_col, None)

    def get_promotional_piece(self, player_input):

        if "=" in player_input:
            index = player_input.index("=")

            if index != len(player_input) -1:
                return (None, player_input, "A piece to promote to must be specified after a = symbol.")

            promotional_piece = player_input[-1]

            keys = list(piece_mapping.keys())
            keys_excluding_pawn = keys[:-1]

            if promotional_piece in keys_excluding_pawn:
                promotional_piece = piece_mapping[promotional_piece]
                player_input = player_input[:-2]

                return (promotional_piece, player_input, None)
            else:
                return (None, player_input, "The promotional piece is not valid.")

        return (None, player_input, None)


    def get_take_piece_flag(self, player_input):

        if "x" in player_input:
            take_piece_flag = True
            player_input.remove("x")
        elif "X" in player_input:
            take_piece_flag = True
            player_input.remove("X")
        else:
            take_piece_flag = False

        return(take_piece_flag, player_input)

    def is_castling(self, player_input):

        kingside_castling = ["o","-","o"]
        queenside_castling = ["o","-","o","-","o"]

        player_input_lower = [i.lower for i in player_input]

        if player_input_lower == kingside_castling:

            castling_flag = True
            initial_position = list(self.chess_board.king_positions(self.turn_colour))
            final_position = [initial_position[0], initial_position[1] + 2]
            take_piece_flag = False
            promotional_piece = False
            piece_type_to_move = king

            return(initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece, castling_flag)

        elif player_input_lower == queenside_castling:

            castling_flag = True
            initial_position = list(self.chess_board.king_positions(self.turn_colour))
            final_position = [initial_position[0], initial_position[1] - 2]
            take_piece_flag = False
            promotional_piece = False
            piece_type_to_move = king

            return(initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece, castling_flag)

        return (None, None, None, None, None, None)

chess_board = chess_board()
chess_board.set_board()
chess_game = game(chess_board)
chess_game.game_loop()
