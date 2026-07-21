#!/usr/bin/env python3

import socket
import threading
import json

from Pieces import *

piece_mapping = {"K": king,
                 "Q": queen,
                 "R": rook,
                 "B": bishop,
                 "N": knight,
                 "P": pawn}

class network:

    def __init__(self, app):

        self.running = False
        self.kill = False

        self.app = app
        self.server = None
        self.client = None
        self.connection_made = False
        self.is_server = None

        self.move_callback = None

    def host_game(self, host, port):

        if self.running:
            return

        threading.Thread(target=self.server_loop, args=(host, port), daemon=True).start()

    def server_loop(self, host, port):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            self.server.bind((host, port))
            self.running = True
            self.is_server = True
            self.server.listen(1)

            self.client, address = self.server.accept()
            self.connection_made = True
            self.app.call_from_thread(setattr, self.app.screen, "player_colour", "white")
            self.app.call_from_thread(setattr, self.app.screen, "connection_made", True)
            threading.Thread(target=self.listen_for_moves, daemon=True).start()
            self.server.close()

        except Exception as e:
            message = {"title": "", "message": str(e)}
            self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

    def connect_to_game(self, host, port):

        threading.Thread(target=self.connect_to_game_loop, args=(host, port), daemon=True).start()

    def connect_to_game_loop(self, host, port):

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            self.connection_made = True
            self.app.call_from_thread(setattr, self.app.screen, "player_colour", "black")
            self.app.call_from_thread(setattr, self.app.screen, "connection_made", True)
            self.running = True
            self.is_server = False
            threading.Thread(target=self.listen_for_moves, daemon=True).start()

        except Exception as e:
            message = {"title": str(e), "message": "Check your entered IP address."}
            self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

    def listen_for_moves(self):

        while self.running:
            try:
                data = self.client.recv(1024).decode('utf-8')

                if not data:
                    message = {"title": "Connection Error:", "message": "Connection closed by opponent"}
                    self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

                move_information = json.loads(data)

                if "piece_type_to_move" in move_information:
                    move_information["piece_type_to_move"] = self.convert_key_to_piece(move_information["piece_type_to_move"])

                if self.move_callback:
                    self.move_callback(move_information)

            except Exception as e:
                message = {"title": "", "message": str(e)}
                self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

    def send_move(self, move_information):

        if self.client:
            try:
                data = move_information.copy()

                if "piece_type_to_move" in move_information:
                    data["piece_type_to_move"] = self.convert_piece_to_key(move_information["piece_type_to_move"])

                encoded_move_information = json.dumps(data).encode("utf-8")
                self.client.sendall(encoded_move_information)

            except Exception as e:
                message = {"title": "", "message": str(e)}
                self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

    def close_connection(self):
        self.running = False
        self.connection_made = False

        if self.client:
            try:
                self.client.close()
            except:
                pass

        if self.is_server and self.server:
            try:
                self.server.close()
            except:
                pass

    def convert_piece_to_key(self, piece):

        for key in piece_mapping:
            if piece_mapping[key] == piece:
                return key

    def convert_key_to_piece(self, key):

        return piece_mapping.get(key)
