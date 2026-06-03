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
        self.turn_number = 0
        self.captured_white_pieces = []
        self.captured_black_pieces = []
        self.history = []
        self.winner = None
        self.chess_board = chess_board

    def get_move(self):
        while True:
            player_input = input("Enter move: ").strip(" +#!?")
            player_input_lower = player_input.lower()

            player_input = list(player_input)
            player_input_lower = list(player_input_lower)

            if len(player_input) < 2:
                print("Move patterns must be at least two characters long.")
                continue

            # check for castling
            kingside_castling = ["o","-","o"]
            queenside_castling = ["o","-","o","-","o"]

            if player_input_lower == kingside_castling:
                castling_flag = True
                initial_position = list(self.chess_board.king_positions(self.turn_colour))
                final_position = [initial_position[0], initial_position[1] + 2]
                take_piece_flag = False
                promotional_piece = False
                break
            elif player_input_lower == queenside_castling:
                castling_flag = True
                initial_position = list(self.chess_board.king_positions(self.turn_colour))
                final_position = [initial_position[0], initial_position[1] - 2]
                take_piece_flag = False
                promotional_piece = False
                break
            else:
                castling_flag = False

            # check for promotion
            if "=" in player_input:
               index = player_input.index("=")

               if index != len(player_input) -1:
                   print("A piece to promote to must be specified after an = symbol.")
                   continue

               promotional_piece = player_input[-1]

               keys = list(piece_mapping.keys())
               if promotional_piece in keys[:-1]:
                   promotional_piece = piece_mapping[promotional_piece]
                   player_input = player_input[:-2]
               else:
                   print("The promotional piece is not valid.")
                   continue
            else:
                promotional_piece = None

            # check for take piece flag
            if "x" in player_input:
                take_piece_flag = True
                player_input.remove("x")
            elif "X" in player_input:
                take_piece_flag = True
                player_input.remove("X")
            else:
                take_piece_flag = False

            # retrieve the final position from the remaining contents
            second_last_character = player_input[-2]

            if second_last_character.isdigit():
                final_position = player_input[-3:]
                final_position[-2] = final_position[-2] + final_position[-1]
                del final_position[-1]
                player_input = player_input[:-3]
            else:
                final_position = player_input[-2:]
                player_input = player_input[:-2]

            # chess notation goes (col,row) while board indexing gose (row,col)
            final_position.reverse()

            if final_position[1].isalpha():
                final_position[1] = ord(final_position[1]) - 97
            else:
                print("Invalid final position.")
                continue

            if final_position[0].isdigit():
                final_position[0] = int(final_position[0]) - 1
            else:
                print("Invalid final position.")
                continue

            valid, error = self.chess_board.check_position_exists(final_position)
            if not valid:
                print(error)
                continue

            if tuple(final_position) in self.chess_board.piece_positions[self.turn_colour]:
                print("Final position contains a piece of the same colour.")
                continue

            # retrieves the piece type from the remaining contents
            try:
                possible_piece = player_input[0]
                del player_input[0]
            except:
                possible_piece = "P"

            if possible_piece in piece_mapping:
                piece_type_to_move = piece_mapping[possible_piece]
            else:
                piece_type_to_move = pawn

            # retrieve any clues to solve piece ambiguity problems
            initial_row = None
            initial_col = None

            remaining_digits = []
            remaining_characters = []

            for i in player_input:
                if i.isdigit():
                    remaining_digits.append(i)
                if i.isalpha():
                    remaining_characters.append(i)

            if len(remaining_characters) > 1:
                print("Invalid initial position")
                continue

            digits_string = ""
            for i in remaining_digits:
                digits_string += i

            if len(remaining_characters) == 1:
                initial_col = ord(remaining_characters[0]) - 97

            if remaining_digits:
                initial_row = int(digits_string) - 1

            initial_position, error = self.find_initial_position(piece_type_to_move, initial_row, initial_col, final_position)

            if not initial_position:
                if error:
                    print(error)
                continue

            break

        return (initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece)

    def find_initial_position(self, piece_type_to_move, initial_row, initial_col, final_position):

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

        for i in possible_positions:
            if i == final_position:
                possible_positions.remove(i)

        if len(possible_positions) == 0:
            return (None, "Final position equals intial position")

        for i in possible_positions:
            cell_contents = self.chess_board.piece_positions[self.turn_colour][tuple(i)]

            valid, _, _ = cell_contents.piece_specific_move_checks(i, final_position, True)

            if not valid:
                possible_positions.remove(i)
                continue

            pinned_piece = self.chess_board.is_piece_pinned(i)

            if pinned_piece:
                possible_positions.remove(i)
                continue

        if len(possible_positions) == 0:
            return (None, f"No {self.turn_colour} {piece_type_to_move.__name__}s can make this move")

        if len(possible_positions) == 1:
            return (possible_positions[0], None)

        prompt = f"Move is ambiguous. Do you mean the {piece_type_to_move.name} at {possible_positions[0]} (0)"

        for i in possible_positions[0:]:
            string_snippet = f" or at {possible_positions[i]} (i)"
            prompt += string_snippet

        prompt += " or press (q) to re-enter move: "

        while True:
            user_choice = input(prompt).strip().lower()
            if user_choice == "q":
                break
            if user_choice.isdigit():
                user_choice = int(user_choice)
                if 0 <= user_choice <= (len(possible_positions) - 1):
                    break

        if user_choice == "q":
            return (None, None)

        return (possible_positions[user_choice], None)

chess_board = chess_board()
chess_board.create_piece(rook, "white", [2,4])
chess_board.create_piece(king, "white", [4,4])
chess_board.create_piece(king, "black", [6,6])
chess_board.show_board()
game_loop = game(chess_board)
initial_position, final_position, take_piece_flag, piece_type_to_move, promotional_piece = game_loop.get_move()
print(initial_position)
print(final_position)
print(take_piece_flag)
print(piece_type_to_move)
