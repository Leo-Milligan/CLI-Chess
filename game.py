#!/usr/bin/env python3

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
        self.moves_since_capture_or_pawn_move = 0

        self.captured_white_pieces = []
        self.captured_black_pieces = []
        self.move_history = []
        self.position_history_for_draw_viability = []

        self.winner = None
        self.game_resigned = False

        self.draw = False
        self.draw_offered = False
        self.immediate_draw_possible = False

        self.chess_board = chess_board

    def interperet_move_notation(self, player_input):

        if len(player_input) == 1 and player_input[0].lower() == "r":
            return {"valid": True, "resign": True, "draw_offer": False}

        if len(player_input) == 1 and player_input[0].lower() == "d":
            return {"valid": True, "resign": False, "draw_offer": True}

        if len(player_input) < 2:
            return {"valid": False, "error": "Move patterns must be at least two characters long."}

        move_information = {}

        move_information["resign"] = False
        move_information["draw_offer"] = False

        castling_flag, side, error = self.check_for_castling(player_input)
        move_information["castling_flag"] = castling_flag
        if error:
            return {"valid": False, "error": error}
        if castling_flag:
            return {"valid": True, "castling_flag": True, "side": side, "resign": False, "draw_offer": False}

        promotional_piece, remainder, error = self.get_promotional_piece(player_input)
        move_information["promotional_piece"] = promotional_piece
        if error:
            return {"valid": False, "error": error}

        take_piece_flag, remainder = self.get_take_piece_flag(remainder)
        move_information["take_piece_flag"] = take_piece_flag

        final_position, remainder, error = self.find_final_position(remainder)
        move_information["final_position"] = final_position
        if not final_position:
            return {"valid": False, "error": error}

        piece_type_to_move, remainder = self.get_piece_type_from_input(remainder)
        move_information["piece_type_to_move"] = piece_type_to_move

        initial_row, initial_col, error = self.get_ambiguity_clues(remainder)
        if error:
            return {"valid": False, "error": error}

        initial_position, error = self.find_initial_position(piece_type_to_move, initial_row, initial_col, final_position)
        move_information["initial_position"] = initial_position
        if not initial_position:
            return {"valid": False, "error": error}

        if type(initial_position[0]) == int:
            if piece_type_to_move == pawn:
                initial_position_contents = self.chess_board.get_piece(initial_position)
                move_information["en_passant_flag"] = initial_position_contents.get_en_passant_flag(initial_position, final_position, True)
            else:
                move_information["en_passant_flag"] = False

        move_information["valid"] = True

        return move_information

    def apply_move(self, move_information):

        result = {"check": False, "checkmate": False, "resign": False, "draw": False, "message": ""}

        if move_information["resign"]:
            self.winner = self.opposite_colour
            self.game_resigned = True
            result["resign"] = True
            return result
        elif move_information["draw_offer"] and self.immediate_draw_possible:
            self.draw = True
            result["draw"] = True
            return result

        move_delta = self.move_controller(move_information)
        self.chess_board.update_castle_flag()
        self.move_history.append(move_delta)

        self.move_number += 1

        if move_delta["captured_piece_information"]["captured_piece"]:
            if self.turn_colour == "white":
                self.captured_black_pieces.append(move_delta["captured_piece_information"]["captured_piece"])
            else:
                self.captured_white_pieces.append(move_delta["captured_piece_information"]["captured_piece"])

        position_overview = self.get_position_overview()

        self.update_counters_for_draw(move_information, position_overview)

        check, _ = self.chess_board.king_in_check(self.opposite_colour)
        result["check"] = check

        if check:
            result["message"] = f"{self.opposite_colour} king in check!"
            checkmate = self.chess_board.king_in_checkmate(self.opposite_colour)
        else:
            checkmate = False

        result["checkmate"] = checkmate

        if checkmate:
            result["message"] = f"{self.opposite_colour} king in checkmate!"
            self.winner = self.turn_colour
            return result

        is_draw, message = self.check_for_draw(self.turn_colour)
        result["draw"]= is_draw
        if is_draw:
            result["message"] = message
            return result

        for position in self.chess_board.piece_positions[self.opposite_colour]:
            piece = self.chess_board.get_piece(position)
            if type(piece) == pawn:
                piece.en_passant_vulnerable_flag = False

        self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour

        return result

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

        return (possible_positions, None)

    def get_user_preferences_question(self, move_information):

        if move_information["draw_offer"] and not self.immediate_draw_possible:
            question_id = "draw_offer"
            question = "Opponent wants to draw, do you accept? (y/n): "
            valid_answers = ["y", "n"]

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        if move_information.get("castling_flag") is not False or \
           move_information.get("resign") is not False:
            return None

        final_position_contents = self.chess_board.get_piece(move_information["final_position"])

        if self.turn_colour == "white":
            moving_to_last_row = True if move_information["final_position"][0] == (self.chess_board.num_rows - 1) else False
        else:
            moving_to_last_row = True if move_information["final_position"][0] == 0 else False


        if type(move_information["initial_position"][0]) != int:
            question_id = "piece_ambiguity"
            question = self.generate_ambiguity_question(move_information["initial_position"], move_information["piece_type_to_move"])

            valid_answers = ["x"]
            for i in range(len(move_information["initial_position"])):
                valid_answers.append(str(i))

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        elif final_position_contents and final_position_contents.colour != self.turn_colour and move_information["take_piece_flag"] == False:
            question_id = "take_piece"
            question = "Do you want to take the piece (y/n): "
            valid_answers = ["y", "n"]

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        elif move_information["en_passant_flag"] == True and move_information["take_piece_flag"] == False:
            question_id = "take_en_passant"
            question = "Do you want to capture en passant (y/n): "
            valid_answers = ["y", "n"]

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        elif not final_position_contents and move_information["take_piece_flag"] == True and move_information["en_passant_flag"] == False:
            question_id = "move_without_take"
            question = "Square is empty, do you want to continue (y/n): "
            valid_answers = ["y", "n"]

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        elif move_information["promotional_piece"] and (not moving_to_last_row or not move_information["piece_type_to_move"] == pawn):
            question_id = "skip_promotion"
            question = "Promotion not possible, do you want to continue (y/n): "
            valid_answers = ["y", "n"]

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        elif move_information["piece_type_to_move"] == pawn and moving_to_last_row and not move_information["promotional_piece"]:
            question_id = "confirm_promotion"
            question = "Promote to Queen (Q), Rook (R), Bishop (B), Knight (N), or press (x) to re-enter move: "

            keys = list(piece_mapping.keys())
            keys_excluding_pawn_and_king = [k for k in keys if k not in ("K", "P")]

            valid_answers = keys_excluding_pawn_and_king
            valid_answers.append("x")

            return {"question_id": question_id, "question": question, "valid_answers": valid_answers}

        else:
            return None

    def generate_ambiguity_question(self, possible_initial_positions, piece_type_to_move):

        possible_positions_chess_notation = []
        for position in possible_initial_positions:
            position_chess_notation = self.coordinate_to_chess_notation(position)
            possible_positions_chess_notation.append(position_chess_notation)

        prompt = f"Do you mean the {piece_type_to_move.__name__} at {possible_positions_chess_notation[0]} (0)"

        for i in (range(len(possible_initial_positions) - 1)):
            string_snippet = f" or at {possible_positions_chess_notation[i + 1]} ({i + 1})"
            prompt += string_snippet

        prompt += " or press (x) to re-enter move: "

        return prompt

    def interperate_user_preferences_answer(self, player_input, move_information, question_information):

        player_input = player_input.lower()

        if question_information["question_id"] ==  "draw_offer":
            if player_input == "y":
                self.immediate_draw_possible = True
                self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour
            elif player_input == "n":
                move_information["valid"] = False
                self.turn_colour, self.opposite_colour = self.opposite_colour, self.turn_colour

        elif question_information["question_id"] ==  "piece_ambiguity":
            possible_initial_positions = move_information["initial_position"]

            if player_input == "x":
                move_information["valid"] = False

            try:
                int(player_input)
            except:
                return move_information

            if 0 <= int(player_input) <= (len(possible_initial_positions) - 1):
                initial_position = possible_initial_positions[int(player_input)]
                move_information["initial_position"] = initial_position

                if move_information["piece_type_to_move"] == pawn:
                    initial_position_contents = self.chess_board.get_piece(move_information["initial_position"])
                    move_information["en_passant_flag"] = initial_position_contents.get_en_passant_flag(move_information["initial_position"], move_information["final_position"], True)
                else:
                    move_information["en_passant_flag"] = False

        elif question_information["question_id"] ==  "take_piece":
            if player_input == "y":
                move_information["take_piece_flag"] = True
            elif player_input == "n":
                move_information["valid"] = False

        elif question_information["question_id"] ==  "take_en_passant":
            if player_input == "y":
                move_information["take_piece_flag"] = True
            elif player_input == "n":
                move_information["valid"] = False

        elif question_information["question_id"] ==  "move_without_take":
            if player_input == "y":
                move_information["take_piece_flag"] = False
            elif player_input == "n":
                move_information["valid"] = False

        elif question_information["question_id"] ==  "skip_promotion":
            if player_input == "y":
                move_information["promotional_piece"] = None
            elif player_input == "n":
                move_information["valid"] = False

        elif question_information["question_id"] ==  "confirm_promotion":
            keys = list(piece_mapping.keys())
            keys_excluding_pawn_and_king = [k for k in keys if k not in ("K", "P")]

            if player_input in keys_excluding_pawn_and_king:
                move_information["promotional_piece"] = piece_mapping[player_input]
            elif player_input == "x":
                move_information["valid"] = False

        return move_information

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

        kingside_castling = ['o','-','o']
        queenside_castling = ['o','-','o','-','o']

        side = None

        player_input_lower = [i.lower() for i in player_input]

        if player_input_lower == kingside_castling:
            castling_flag = True
            side = "kingside"
            if self.chess_board.check_castle_validity(side, self.turn_colour):
                return castling_flag, side, None
            else:
                return castling_flag, side, "Castling not valid."

        elif player_input_lower == queenside_castling:
            castling_flag = True
            side = "queenside"
            if self.chess_board.check_castle_validity(side, self.turn_colour):
                return castling_flag, side, None
            else:
                return castling_flag, side, "Castling not valid."

        else:
            return False, None, None    

    def get_move_delta(self, move_information, move_delta):

        initial_position = move_information["initial_position"]
        final_position = move_information["final_position"]

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if not move_delta:
            move_delta = {"piece_information_initial": {"piece": None, "piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "piece_information_final": {"piece": None, "piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "captured_piece_flag": None,
                        "captured_piece_information": {"captured_piece": None, "captured_piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "castling_flag": None,
                        "castling_information": {"side": None, "rook": None, "king": None, "rook_initial_position": None, "king_initial_position": None, "rook_final_position": None, "king_final_position": None},
                        "game_metadata": {"move_number": None, "turn_colour": None}
                        }

            move_delta["piece_information_initial"]["piece"] = initial_position_contents

            move_delta["piece_information_initial"]["piece_position"] = initial_position

            move_delta["piece_information_initial"]["piece_flags"]["has_moved"] = initial_position_contents.has_moved
            if type(initial_position_contents) == pawn:
                move_delta["piece_information_initial"]["piece_flags"]["en_passant_vulnerable_flag"] = initial_position_contents.en_passant_vulnerable_flag
            elif type(initial_position_contents) == rook:
                move_delta["piece_information_initial"]["piece_flags"]["can_castle_if_valid"] = initial_position_contents.can_castle_if_valid

            if final_position_contents:
                move_delta["captured_piece_flag"] = True

                move_delta["captured_piece_information"]["captured_piece"] = final_position_contents
                move_delta["captured_piece_information"]["captured_piece_position"] = final_position

                move_delta["captured_piece_information"]["piece_flags"]["has_moved"] = final_position_contents.has_moved
                if type(final_position_contents) == pawn:
                    move_delta["captured_piece_information"]["piece_flags"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag

            move_delta["game_metadata"]["move_number"] = self.move_number
            move_delta["game_metadata"]["turn_colour"] = self.turn_colour

        elif move_delta:
            move_delta["piece_information_final"]["piece"] = final_position_contents

            move_delta["piece_information_final"]["piece_position"] = final_position

            move_delta["piece_information_final"]["piece_flags"]["has_moved"] = final_position_contents.has_moved
            if type(initial_position_contents) == pawn:
                move_delta["piece_information_final"]["piece_flags"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag
            elif type(initial_position_contents) == rook:
                move_delta["piece_information_initial"]["piece_flags"]["can_castle_if_valid"] = initial_position_contents.can_castle_if_valid

        return move_delta

    def get_move_delta_en_passant(self, move_information, move_delta):

        initial_position = move_information["initial_position"]
        final_position = move_information["final_position"]

        initial_position_contents = self.chess_board.get_piece(initial_position)
        final_position_contents = self.chess_board.get_piece(final_position)

        if not move_delta:
            move_delta = {"piece_information_initial": {"piece": None, "piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "piece_information_final": {"piece": None, "piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "captured_piece_flag": None,
                        "captured_piece_information": {"captured_piece": None, "captured_piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "castling_flag": None,
                        "castling_information": {"side": None, "rook": None, "king": None, "rook_initial_position": None, "king_initial_position": None, "rook_final_position": None, "king_final_position": None},
                        "game_metadata": {"move_number": None, "turn_colour": None}
                        }

            move_delta["piece_information_initial"]["piece"] = initial_position_contents

            move_delta["piece_information_initial"]["piece_position"] = initial_position

            move_delta["piece_information_initial"]["piece_flags"]["has_moved"] = initial_position_contents.has_moved
            if type(initial_position_contents) == pawn:
                move_delta["piece_information_initial"]["piece_flags"]["en_passant_vulnerable_flag"] = initial_position_contents.en_passant_vulnerable_flag
            elif type(initial_position_contents) == rook:
                move_delta["piece_information_initial"]["piece_flags"]["can_castle_if_valid"] = initial_position_contents.can_castle_if_valid

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
            move_delta["game_metadata"]["turn_colour"] = self.turn_colour

        elif move_delta:
            move_delta["piece_information_final"]["piece"] = final_position_contents

            move_delta["piece_information_final"]["piece_position"] = final_position

            move_delta["piece_information_final"]["piece_flags"]["has_moved"] = final_position_contents.has_moved
            if type(initial_position_contents) == pawn:
                move_delta["piece_information_final"]["piece_flags"]["en_passant_vulnerable_flag"] = final_position_contents.en_passant_vulnerable_flag
            elif type(initial_position_contents) == rook:
                move_delta["piece_information_initial"]["piece_flags"]["can_castle_if_valid"] = initial_position_contents.can_castle_if_valid

        return move_delta
    
    def get_move_delta_castling(self, move_information, move_delta):

        if not move_delta:
            move_delta = {"piece_information_initial": {"piece": None, "piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "piece_information_final": {"piece": None, "piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "captured_piece_flag": None,
                        "captured_piece_information": {"captured_piece": None, "captured_piece_position": None, "piece_flags": {"has_moved": None, "en_passant_vulnerable_flag": None, "can_castle_if_valid": None}},
                        "castling_flag": None,
                        "castling_information": {"side": None, "rook": None, "king": None, "rook_initial_position": None, "king_initial_position": None, "rook_final_position": None, "king_final_position": None},
                        "game_metadata": {"move_number": None, "turn_colour": None}
                        }
                        
            move_delta["castling_flag"] = True
            move_delta["castling_information"]["side"] = move_information["side"]
            move_delta["castling_information"]["king_initial_position"] = list(self.chess_board.king_positions[self.turn_colour])
            move_delta["castling_information"]["rook_initial_position"] = list(self.chess_board.find_rook_to_castle(move_information["side"], self.turn_colour))
            move_delta["king"] = self.chess_board.get_piece(move_delta["castling_information"]["king_initial_position"])
            move_delta["rook"] = self.chess_board.get_piece(move_delta["castling_information"]["rook_initial_position"])

            move_delta["game_metadata"]["move_number"] = self.move_number
            move_delta["game_metadata"]["turn_colour"] = self.turn_colour

        elif move_delta:

            row, col = move_delta["castling_information"]["king_initial_position"]

            if move_delta["castling_information"]["side"] == "kingside":

                move_delta["castling_information"]["king_final_position"] = [row, col+2]
                move_delta["castling_information"]["rook_final_position"] = [row, col+1]

            elif move_delta["castling_information"]["side"] == "queenside":

                move_delta["castling_information"]["king_final_position"] = [row, col-2]
                move_delta["castling_information"]["rook_final_position"] = [row, col-1]


        return move_delta
  
    def move_controller(self, move_information):

        if move_information["castling_flag"]:
            move_delta_initial = self.get_move_delta_castling(move_information, None)
            self.chess_board.move_piece_with_castle(move_information["side"], self.turn_colour)
            move_delta = self.get_move_delta_castling(move_information, move_delta_initial)

        elif move_information["piece_type_to_move"] == pawn and move_information["promotional_piece"]:
            move_delta_initial = self.get_move_delta(move_information, None)
            self.chess_board.move_piece_with_promotion( move_information["initial_position"], move_information["final_position"], move_information["promotional_piece"])
            move_delta = self.get_move_delta(move_information, move_delta_initial)

        elif move_information["piece_type_to_move"] == pawn and move_information["en_passant_flag"]:
            move_delta_initial = self.get_move_delta_en_passant(move_information, None)
            self.chess_board.move_piece_with_en_passant(move_information["initial_position"], move_information["final_position"])
            move_delta = self.get_move_delta_en_passant(move_information, move_delta_initial)

        else:
            move_delta_initial = self.get_move_delta(move_information, None)
            self.chess_board.move_piece(move_information["initial_position"], move_information["final_position"])
            move_delta = self.get_move_delta(move_information, move_delta_initial)

        return move_delta

    def get_position_overview(self):

        piece_positions = self.chess_board.piece_positions

        position_overview = {"white": {},
                             "black": {}
                             }

        for colour in list(piece_positions):
            for position in list(piece_positions[colour]):

                piece = piece_positions[colour][position]

                if type(piece) == pawn:
                    en_passant_vulnerable_flag = piece.en_passant_vulnerable_flag
                    position_overview[colour][position] = {"piece_type": type(piece), "en_passant_vulnerable_flag": en_passant_vulnerable_flag}
                elif type(piece) == rook:
                    can_castle_if_valid = piece.can_castle_if_valid
                    position_overview[colour][position] = {"piece_type": type(piece), "can_castle_if_valid": can_castle_if_valid}
                else:
                    position_overview[colour][position] = {"piece_type": type(piece)}

        return position_overview

    def update_counters_for_draw(self, move_information, position_overview):

            if move_information["castling_flag"]:
                self.moves_since_capture_or_pawn_move += 1
            elif move_information["take_piece_flag"]:
                self.moves_since_capture_or_pawn_move = 0
            elif move_information["piece_type_to_move"] == pawn:
                self.moves_since_capture_or_pawn_move = 0
            else:
                self.moves_since_capture_or_pawn_move += 1

            if move_information["castling_flag"]:
                self.position_history_for_draw_viability = []
            elif move_information["take_piece_flag"]:
                self.position_history_for_draw_viability = []
            elif move_information["piece_type_to_move"] == pawn:
                self.position_history_for_draw_viability = []
            elif move_information["promotional_piece"]:
                self.position_history_for_draw_viability = []
            else:
                self.position_history_for_draw_viability.append(position_overview)

    def check_for_draw(self, colour):

        if self.moves_since_capture_or_pawn_move >= 50:
            self.immediate_draw_possible = True

        repeated_position_flag = self.check_for_repeated_position()
        if repeated_position_flag:
            self.immediate_draw_possible = True

        insufficient_material = self.check_for_insufficient_material()
        if insufficient_material:
            return (True, "Draw due to insufficiant material.")

        stalemate = self.check_for_stalemate(colour)
        if stalemate:
            return (True, f"Draw due to {colour} being in stalemate.")

        return (False, None)

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

            if valid_final_positions:
                return False

        return True

    def check_for_repeated_position(self):

        if len(self.position_history_for_draw_viability) < 3:
            return False

        current_position_overview = self.position_history_for_draw_viability.pop()

        counter = 0

        for position_overview in list(self.position_history_for_draw_viability):

            if position_overview == current_position_overview:
                counter += 1

            if counter >= 2:
                return True

        return False

    def reset_game(self):

        for _ in self.move_history:
            self.undo_once_using_move_delta()

        self.turn_colour = "white"
        self.opposite_colour = "black"

        self.move_number = 1
        self.moves_since_capture_or_pawn_move = 0

        self.captured_white_pieces = []
        self.captured_black_pieces = []
        self.move_history = []
        self.position_overview_history = []
        self.position_history_for_draw_viability = []

        self.winner = None
        self.game_resigned = False

        self.draw = False
        self.draw_offered = False
        self.immediate_draw_possible = False

    def undo_once_using_move_delta(self):

        current_move_number = self.move_number

        if current_move_number == 1:
            return

        move_delta = self.move_history[current_move_number - 2]

        self.move_number = move_delta["game_metadata"]["move_number"]
        self.turn_colour = move_delta["game_metadata"]["turn_colour"]
        self.opposite_colour = "white" if self.turn_colour == "black" else "black"

        if move_delta["castling_flag"]:
            king_piece = move_delta["castling_information"]["king"]
            king_initial_position = move_delta["castling_information"]["king_initial_position"]
            king_final_position = move_delta["castling_information"]["king_final_position"]

            rook_piece = move_delta["castling_information"]["rook"]
            rook_initial_position = move_delta["castling_information"]["rook_initial_position"]
            rook_final_position = move_delta["castling_information"]["rook_final_position"]

            self.chess_board.remove_piece(king_final_position)
            self.chess_board.remove_piece(rook_final_position)

            self.chess_board.insert_piece(king_piece, king_initial_position)
            self.chess_board.insert_piece(rook_piece, rook_initial_position)

            king_piece.has_moved = False
            rook_piece.has_moved = False
            rook_piece.can_castle_if_valid = True

            return

        initial_position = move_delta["piece_information_initial"]["piece_position"]
        final_position = move_delta["piece_information_final"]["piece_position"]

        initial_piece = move_delta["piece_information_initial"]["piece"]

        self.chess_board.remove_piece(final_position)
        self.chess_board.insert_piece(initial_piece, initial_position)

        for piece_flag_name in move_delta["piece_information_initial"]["piece_flags"]:
            piece_flag = move_delta["piece_information_initial"]["piece_flags"][piece_flag_name]

            if piece_flag is not None:
                setattr(initial_piece, piece_flag_name, piece_flag)

        if move_delta["captured_piece_flag"]:
            captured_piece = move_delta["captured_piece_information"]["captured_piece"]
            captured_piece_position = move_delta["captured_piece_information"]["captured_piece_position"]

            if move_delta["game_metadata"]["turn_colour"] == "white":
                self.captured_black_pieces.remove(captured_piece)
            elif move_delta["game_metadata"]["turn_colour"] == "black":
                self.captured_white_pieces.remove(captured_piece)

            self.chess_board.insert_piece(captured_piece, captured_piece_position)

            for piece_flag_name in move_delta["captured_piece_information"]["piece_flags"]:
                piece_flag = move_delta["captured_piece_information"]["piece_flags"][piece_flag_name]

                if piece_flag is not None:
                    setattr(captured_piece, piece_flag_name, piece_flag)

    def advance_once_using_move_delta(self):

        current_move_number = self.move_number

        if current_move_number == (len(self.move_history) + 1):
            return

        move_delta = self.move_history[current_move_number - 1]

        self.move_number = move_delta["game_metadata"]["move_number"] + 1
        last_move_colour = move_delta["game_metadata"]["turn_colour"]
        self.turn_colour = "white" if last_move_colour == "black" else "black"
        self.opposite_colour = "white" if self.turn_colour == "black" else "black"

        if move_delta["castling_flag"]:
            king_piece = move_delta["castling_information"]["king"]
            king_initial_position = move_delta["castling_information"]["king_initial_position"]
            king_final_position = move_delta["castling_information"]["king_final_position"]

            rook_piece = move_delta["castling_information"]["rook"]
            rook_initial_position = move_delta["castling_information"]["rook_initial_position"]
            rook_final_position = move_delta["castling_information"]["rook_final_position"]

            self.chess_board.remove_piece(king_initial_position)
            self.chess_board.remove_piece(rook_initial_position)

            self.chess_board.insert_piece(king_piece, king_final_position)
            self.chess_board.insert_piece(rook_piece, rook_final_position)

            king_piece.has_moved = True
            rook_piece.has_moved = True
            rook_piece.can_castle_if_valid = False

            return

        if move_delta["captured_piece_flag"]:
            captured_piece = move_delta["captured_piece_information"]["captured_piece"]
            captured_piece_position = move_delta["captured_piece_information"]["captured_piece_position"]

            if move_delta["game_metadata"]["turn_colour"] == "white":
                self.captured_black_pieces.append(captured_piece)
            elif move_delta["game_metadata"]["turn_colour"] == "black":
                self.captured_white_pieces.append(captured_piece)

            self.chess_board.remove_piece(captured_piece_position)

        initial_position = move_delta["piece_information_initial"]["piece_position"]
        final_position = move_delta["piece_information_final"]["piece_position"]

        initial_piece = move_delta["piece_information_initial"]["piece"]

        self.chess_board.remove_piece(initial_position)
        self.chess_board.insert_piece(initial_piece, final_position)

        for piece_flag_name in move_delta["piece_information_final"]["piece_flags"]:
            piece_flag = move_delta["piece_information_final"]["piece_flags"][piece_flag_name]

            if piece_flag is not None:
                setattr(initial_piece, piece_flag_name, piece_flag)

