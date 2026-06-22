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
    def __init__(self, chess_board):
        self.turn_colour = "white"
        self.opposite_colour = "black"
        self.move_number = 1
        self.captured_white_pieces = []
        self.captured_black_pieces = []
        self.move_history = []
        self.winner = None
        self.game_resigned = False
        self.draw = False
        self.draw_offered = False
        self.chess_board = chess_board

    def game_loop(self):
        self.chess_board.show_board()

        while True:
            if self.draw_offered == True:
                self.draw_offered = False

                while True:
                    draw_response = input("Opponent has offered a draw. Do you wish to accept it (y/n): ").strip()
                    if draw_response in ("y", "n"):
                        break

                if draw_response == "y":
                    print("Game ends in a draw!")
                    self.draw = True
                    break

                elif draw_response == "n":
                    self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour
                    continue

            is_draw, message = self.check_for_draw(self.turn_colour)
            if is_draw:
                print(message)
                break

            while True:
                player_input = list(input("Enter move: ").strip(" +#!?"))

                move_information = self.interperet_move_notation(player_input)

                if not move_information["valid"]:
                    if move_information["error"]:
                        print(move_information["error"])
                    continue

                break

            if move_information["resign"] == True:
                print(f"{self.turn_colour} resigns!")
                self.game_resigned = True
                self.winner = self.opposite_colour
                break

            if move_information["draw_offer"] == True:
                self.draw_offered = True
                self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour
                continue

            move_delta = self.move_controller(move_information)

            self.chess_board.show_board()

            self.move_history.append(move_delta)

            if move_delta["captured_piece_information"]["captured_piece"]:
                if self.turn_colour == "white":
                    self.captured_black_pieces.append(move_delta["captured_piece_information"]["captured_piece"])
                else:
                    self.captured_white_pieces.append(move_delta["captured_piece_information"]["captured_piece"])

            check, _ = self.chess_board.king_in_check(self.opposite_colour)

            if check:
                print(f"{self.opposite_colour} king in check!")
                checkmate = self.chess_board.king_in_checkmate(self.opposite_colour)
            else:
                checkmate = False

            if checkmate:
                self.winner = self.turn_colour
                print(f"{self.opposite_colour} king in checkmate!")
                break

            for position in self.chess_board.piece_positions[self.opposite_colour]:
                piece = self.chess_board.get_piece(position)
                if type(piece) == pawn:
                    piece.en_passant_vulnerable_flag = False

            self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour
            self.move_number += 1

    def interperet_move_notation(self, player_input):

        if len(player_input) == 1 and player_input[0].lower() == "r":
            return {"valid": True, "resign": True, "draw_offer": False}

        if len(player_input) == 1 and player_input[0].lower() == "d":
            return {"valid": True, "resign": False, "draw_offer": True}

        if len(player_input) < 2:
            return {"valid": False, "error": "Move patterns must be at least two characters long."}

        castling_flag, error = self.check_for_castling(player_input)
        if error:
            return {"valid": False, "error": error}
        if castling_flag:
            return {"valid": True, "castling_flag": True}

        promotional_piece, remainder, error = self.get_promotional_piece(player_input)
        if error:
            return {"valid": False, "error": error}

        take_piece_flag, remainder = self.get_take_piece_flag(remainder)

        final_position, remainder, error = self.find_final_position(remainder)
        if not final_position:
            return {"valid": False, "error": error}

        piece_type_to_move, remainder = self.get_piece_type_from_input(remainder)

        initial_row, initial_col, error = self.get_ambiguity_clues(remainder)
        if error:
            return {"valid": False, "error": error}

        initial_position, error = self.find_initial_position(piece_type_to_move, initial_row, initial_col, final_position)
        if not initial_position:
            if error:
                return {"valid": False, "error": error}
            elif not error:
                return {"valid": False, "error": None}

        if piece_type_to_move == pawn:
            initial_position_contents = self.chess_board.get_piece(initial_position)
            en_passant_flag = initial_position_contents.get_en_passant_flag(initial_position, final_position, True)
        else:
            en_passant_flag = False

        take_piece_flag, promotional_piece, abort_move = self.confirm_user_preferences(final_position, take_piece_flag, piece_type_to_move, promotional_piece, en_passant_flag)
        if abort_move == True:
            return {"valid": False, "error": None}

        return {"valid": True, "resign": False, "draw_offer": False, "initial_position": initial_position, "final_position": final_position, "take_piece_flag": take_piece_flag, "piece_type_to_move": piece_type_to_move, "promotional_piece": promotional_piece, "castling_flag": castling_flag, "en_passant_flag": en_passant_flag}

    def find_initial_position(self, piece_type_to_move, initial_row, initial_col, final_position):

        possible_positions = []
        for key in self.chess_board.piece_positions[self.turn_colour]:

            if initial_row is not None and key[0] != initial_row:
                continue
            elif initial_col is not None and key[1] != initial_col:
                continue

            cell_contents = self.chess_board.piece_positions[self.turn_colour][key]

            if type(cell_contents) == piece_type_to_move:
                possible_positions.append(list(key))

        if len(possible_positions) == 0:
            return (None, f"There are no {self.turn_colour} {piece_type_to_move.__name__}s on the board.")

        for i in possible_positions.copy():

            cell_contents = self.chess_board.get_piece(i)

            valid, _ = cell_contents.check_move_validity(i, final_position, True)

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

        prompt += " or press (x) to re-enter move: "

        while True:
            user_choice = input(prompt).strip().lower()
            if user_choice == "x":
                break
            if user_choice.isdigit():
                user_choice = int(user_choice)
                if 0 <= user_choice <= (len(possible_initial_positions) - 1):
                    break

        if user_choice == "x":
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

            if (index + 1) == len(player_input):
                return (None, player_input, "A piece to promote to must be specified after the '=' symbol.")

            promotional_piece = player_input[index + 1]

            keys = list(piece_mapping.keys())
            keys_excluding_pawn_and_king = [k for k in keys if k not in ("K", "P")]

            if promotional_piece in keys_excluding_pawn_and_king:
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

    def check_for_castling(self, player_input):

        kingside_castling = ["o","-","o"]
        queenside_castling = ["o","-","o","-","o"]

        player_input_lower = [i.lower for i in player_input]

        if player_input_lower == kingside_castling:
            castling_flag = True
            return castling_flag, None
        elif player_input_lower == queenside_castling:
            castling_flag = True
            return castling_flag, None
        else:
            castling_flag = False

        return castling_flag, None

    def confirm_user_preferences(self, final_position, take_piece_flag, piece_type_to_move, promotional_piece, en_passant_flag):

        abort_move = False

        final_position_contents = self.chess_board.get_piece(final_position)

        if final_position_contents and final_position_contents != self.turn_colour and take_piece_flag == False:
            while True:
                answer = input("Do you want to take the piece (y/n): ").lower().strip()

                if answer == "y":
                    take_piece_flag = True
                    break
                if answer == "n":
                    abort_move = True
                    break

        if en_passant_flag == True and take_piece_flag == False:
            while True:
                answer = input("Do you want to capture en passant (y/n): ").lower().strip()

                if answer == "y":
                    take_piece_flag = True
                    break
                if answer == "n":
                    abort_move = True
                    break

        if not final_position_contents and take_piece_flag == True and en_passant_flag == False:
            while True:
                answer = input("The destination square is empty, do you want to continue (y/n): ").lower().strip()

                if answer == "y":
                    take_piece_flag = False
                    break
                if answer == "n":
                    abort_move = True
                    break

        if self.turn_colour == "white":
            moving_to_last_row = True if final_position[0] == (self.chess_board.num_rows - 1) else False
        else:
            moving_to_last_row = True if final_position[0] == 0 else False

        if promotional_piece and (not moving_to_last_row or not piece_type_to_move == pawn):
            promotional_piece = None

            while True:
                answer = input("Promoting this piece is not possible, do you want to continue (y/n): ").lower().strip()

                if answer == "y":
                    break
                if answer == "n":
                    abort_move = True
                    break

        keys = list(piece_mapping.keys())
        keys_excluding_pawn_and_king = [k for k in keys if k not in ("K", "P")]

        if piece_type_to_move == pawn and moving_to_last_row and not promotional_piece:

            while True:
                answer = input("Promote to Queen (Q), Rook (R), Bishop (B), Knight (N), or press (x) to re-enter move: ").upper().strip()

                if answer in keys_excluding_pawn_and_king:
                    promotional_piece = piece_mapping[answer]
                    break
                if answer == "X":
                    abort_move = True
                    break

        return (take_piece_flag, promotional_piece, abort_move)

    def get_move_delta(self, initial_position, final_position, move_delta):

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if not move_delta:
            move_delta = {"initial_position": None,
                        "final_position": None,
                        "piece_flags_initial": {"has_moved": None, "en_passant_vulnerable_flag": None},
                        "piece_flags_final": {"has_moved": None, "en_passant_vulnerable_flag": None},
                        "captured_piece_flag": None,
                        "captured_piece_information": {"captured_piece": None,"captured_piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None}},
                        "promotion_piece_flag": None,
                        "promotion_piece_information": {"promotion_piece": None,"promotion_piece_position": None, "piece_flags": {"has_moved": None}},
                        "game_metadata": {"move_number": None, "colour_to_move": None}
                        }

            move_delta["initial_position"] = initial_position
            move_delta["final_position"] = final_position

            move_delta["piece_flags_initial"]["has_moved"] = initial_position_contents.has_moved

            if type(initial_position_contents) == pawn:
                move_delta["piece_flags_initial"]["en_passant_vulnerable_flag"] = initial_position_contents.en_passant_vulnerable_flag

            if final_position_contents:
                move_delta["captured_piece_flag"] = True

                move_delta["captured_piece_information"]["captured_piece"] = final_position_contents
                move_delta["captured_piece_information"]["captured_piece_position"] = final_position
                move_delta["captured_piece_information"]["piece_flags"]["has_moved"] = final_position_contents.has_moved

                if type(final_position_contents) == pawn:
                    move_delta["captured_piece_information"]["piece_flags"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag

            move_delta["game_metadata"]["move_number"] = self.move_number
            move_delta["game_metadata"]["colour_to_move"] = self.turn_colour

        elif move_delta:
            move_delta["piece_flags_final"]["has_moved"] = final_position_contents.has_moved
            if type(final_position_contents) == pawn:
                move_delta["piece_flags_final"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag

        return move_delta

    def get_move_delta_promotion(self, initial_position, final_position, promotional_piece, move_delta):

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if not move_delta:
            move_delta = {"initial_position": None,
                        "final_position": None,
                        "piece_flags_initial": {"has_moved": None, "en_passant_vulnerable_flag": None},
                        "piece_flags_final": {"has_moved": None, "en_passant_vulnerable_flag": None},
                        "captured_piece_flag": None,
                        "captured_piece_information": {"captured_piece": None,"captured_piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None}},
                        "promotion_piece_flag": None,
                        "promotion_piece_information": {"promotion_piece": None,"promotion_piece_position": None, "piece_flags": {"has_moved": None}},
                        "game_metadata": {"move_number": None, "colour_to_move": None}
                        }

            move_delta["initial_position"] = initial_position
            move_delta["final_position"] = final_position

            move_delta["piece_flags_initial"]["has_moved"] = initial_position_contents.has_moved
            move_delta["piece_flags_final"]["has_moved"] = True

            if type(initial_position_contents) == pawn:
                move_delta["piece_flags_initial"]["en_passant_vulnerable_flag"] = initial_position_contents.en_passant_vulnerable_flag

            if final_position_contents:
                move_delta["captured_piece_flag"] = True

                move_delta["captured_piece_information"]["captured_piece"] = final_position_contents
                move_delta["captured_piece_information"]["captured_piece_position"] = final_position
                move_delta["captured_piece_information"]["piece_flags"]["has_moved"] = final_position_contents.has_moved

                if type(final_position_contents) == pawn:
                    move_delta["captured_piece_information"]["piece_flags"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag

            move_delta["game_metadata"]["move_number"] = self.move_number
            move_delta["game_metadata"]["colour_to_move"] = self.turn_colour

        elif move_delta:
            move_delta["piece_flags_final"]["has_moved"] = final_position_contents.has_moved
            move_delta["promotion_piece_flag"] = True
            move_delta["promotion_piece_information"]["promotion_piece"] = final_position_contents
            move_delta["promotion_piece_information"]["promotion_piece_position"] = final_position
            move_delta["promotion_piece_information"]["piece_flags"]["has_moved"] = final_position_contents.has_moved

        return move_delta

    def get_move_delta_en_passant(self, initial_position, final_position, move_delta):

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if not move_delta:
            move_delta = {"initial_position": None,
                         "final_position": None,
                         "piece_flags_initial": {"has_moved": None, "en_passant_vulnerable_flag": None},
                         "piece_flags_final": {"has_moved": None, "en_passant_vulnerable_flag": None},
                         "captured_piece_flag": None,
                         "captured_piece_information": {"captured_piece": None,"captured_piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None}},
                         "promotion_piece_flag": None,
                         "promotion_piece_information": {"promotion_piece": None,"promotion_piece_position": None, "piece_flags": {"has_moved": None}},
                         "game_metadata": {"move_number": None, "colour_to_move": None}
                         }

            move_delta["initial_position"] = initial_position
            move_delta["final_position"] = final_position

            move_delta["piece_flags_initial"]["has_moved"] = initial_position_contents.has_moved

            if type(initial_position_contents) == pawn:
                move_delta["piece_flags_initial"]["en_passant_vulnerable_flag"] = initial_position_contents.en_passant_vulnerable_flag

            _, col_i = initial_position
            _, col_f = final_position

            col_delta = col_f - col_i

            adjacent_position = [initial_position[0], initial_position[1] + col_delta]
            adjacent_position_contents = self.chess_board.get_piece(adjacent_position)

            move_delta["captured_piece_flag"] = True
            move_delta["captured_piece_information"]["captured_piece"] = adjacent_position_contents
            move_delta["captured_piece_information"]["captured_piece_position"] = adjacent_position
            move_delta["captured_piece_information"]["piece_flags"]["has_moved"] = adjacent_position_contents.has_moved
            move_delta["captured_piece_information"]["piece_flags"]["en_passant_vulnerable_flag"] = True

            move_delta["game_metadata"]["move_number"] = self.move_number
            move_delta["game_metadata"]["colour_to_move"] = self.turn_colour

        elif move_delta:
            move_delta["piece_flags_final"]["has_moved"] = final_position_contents.has_moved
            if type(final_position_contents) == pawn:
                move_delta["piece_flags_final"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag

        return move_delta

    def move_controller(self, move_information):

        if move_information["castling_flag"]:
            print("This is where we should call the castle move function")

        elif move_information["piece_type_to_move"] == pawn and move_information["promotional_piece"]:
            move_delta_initial = self.get_move_delta_promotion(move_information["initial_position"], move_information["final_position"], move_information["promotional_piece"], None)
            self.chess_board.move_piece_with_promotion( move_information["initial_position"], move_information["final_position"], move_information["promotional_piece"])
            move_delta = self.get_move_delta_promotion(move_information["initial_position"], move_information["final_position"], move_information["promotional_piece"], move_delta_initial)

        elif move_information["piece_type_to_move"] == pawn and move_information["en_passant_flag"]:
            move_delta_initial = self.get_move_delta_en_passant(move_information["initial_position"], move_information["final_position"], None)
            self.chess_board.move_piece_with_en_passant(move_information["initial_position"], move_information["final_position"])
            move_delta = self.get_move_delta_en_passant(move_information["initial_position"], move_information["final_position"], move_delta_initial)

        else:
            move_delta_initial = self.get_move_delta(move_information["initial_position"], move_information["final_position"], None)
            self.chess_board.move_piece(move_information["initial_position"], move_information["final_position"])
            move_delta = self.get_move_delta(move_information["initial_position"], move_information["final_position"], move_delta_initial)

        return move_delta

    def check_for_draw(self, colour):

        insufficient_material = self.check_for_insufficient_material()
        if insufficient_material:
            return True, "Draw due to insufficiant material."

        stalemate = self.check_for_stalemate(colour)
        if stalemate:
            return True, f"Draw due to {colour} being in stalemate."

        return False, None

    def check_for_insufficient_material(self):

        white_pieces = []
        black_pieces = []

        for position in self.chess_board.piece_positions["white"]:
            piece = type(self.chess_board.piece_positions["white"][position])

            if piece == bishop:
                white_bishop_position = position
                white_bishop_cell_colour = self.chess_board.get_cell_colour(white_bishop_position)

            white_pieces.append(piece)

        for position in self.chess_board.piece_positions["black"]:
            piece = type(self.chess_board.piece_positions["black"][position])

            if piece == bishop:
                black_bishop_position = position
                black_bishop_cell_colour = self.chess_board.get_cell_colour(black_bishop_position)

            black_pieces.append(piece)

        if len(white_pieces) > 2 or len(black_pieces) > 2:
            return False

        if set(white_pieces) == {king}:
            if (set(black_pieces) == {king}
               or set(black_pieces) == {king, bishop}
               or set(black_pieces) == {king, knight}):
                return True

        elif set(black_pieces) == {king}:
            if (set(white_pieces) == {king}
               or set(white_pieces) == {king, bishop}
               or set(white_pieces) == {king, knight}):
                return True

        elif set(white_pieces) == {king, bishop} and set(black_pieces) == {king, bishop}:
            if white_bishop_cell_colour == black_bishop_cell_colour:
                return True

        return False

    def check_for_stalemate(self, colour):

        for position in list(self.chess_board.piece_positions[colour]):
            piece = self.chess_board.piece_positions[colour][position]

            valid_final_positions = piece.get_possible_moves(position)
            #print(f"valid_final_positions: {valid_final_positions}")

            if valid_final_positions:
                return False

        return True

chess_board = chess_board()
chess_board.set_board()
chess_game = game(chess_board)
chess_game.game_loop()
