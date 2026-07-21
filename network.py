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
        self.app = app
        self.server = None
        self.client = None
        self.connection_made = False
        self.is_server = None
        self.move_callback = None

    def host_game(self, host, port):

        with threading.Lock():
            if self.running:
                return
            else:
                self.running = True
                self.app.screen.server_running =  True

        threading.Thread(target=self.server_loop, args=(host, port), daemon=True).start()

    def server_loop(self, host, port):

        try:
            self.is_server = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((host, port))
            self.server.listen(1)

            try:
                self.client, address = self.server.accept()
            except OSError:
                return

            self.connection_made = True
            self.app.call_from_thread(setattr, self.app.screen, "player_colour", "white")
            self.app.call_from_thread(setattr, self.app.screen, "connection_made", True)
            threading.Thread(target=self.listen_for_moves, daemon=True).start()

        except Exception as e:
            self.running = False
            self.app.call_from_thread(setattr, self.app.screen, "server_running", False)
            message = {"title": "", "message": str(e)}
            self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

            if self.server:
                self.server.close()
                self.server = None

    def connect_to_game(self, host, port):

        with threading.Lock():
            if self.running == True:
                return
            else:
                self.running = True
                self.app.screen.server_running =  True

        threading.Thread(target=self.connect_to_game_loop, args=(host, port), daemon=True).start()

    def connect_to_game_loop(self, host, port):

        try:
            self.is_server = False

            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))

            self.connection_made = True
            self.app.call_from_thread(setattr, self.app.screen, "player_colour", "black")
            self.app.call_from_thread(setattr, self.app.screen, "connection_made", True)

            threading.Thread(target=self.listen_for_moves, daemon=True).start()

        except Exception as e:
            self.running = False
            self.app.call_from_thread(setattr, self.app.screen, "server_running", False)
            message = {"title": "", "message": str(e)}
            self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)

            if self.client:
                self.client.close()
                self.client = None

    def listen_for_moves(self):

        while self.running:
            try:
                data = self.client.recv(1024).decode('utf-8')

                if not data:
                    message = {"title": "Connection Error:", "message": "Connection closed by opponent"}
                    self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)
                    break

                move_information = json.loads(data)

                if "piece_type_to_move" in move_information:
                    move_information["piece_type_to_move"] = self.convert_key_to_piece(move_information["piece_type_to_move"])

                if self.move_callback:
                    self.move_callback(move_information)

            except (ConnectionResetError, BrokenPipeError, OSError):
                message = {"title": "Connection:", "message": "Opponent disconnected."}
                self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)
                break

            except Exception as e:
                message = {"title": "", "message": str(e)}
                self.app.call_from_thread(setattr, self.app.screen, "pop_up_message", message)
                break

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

        with threading.Lock():
            self.running = False
            self.app.screen.server_running = False

        if self.client:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except:
                pass
            self.client = None

        if self.is_server and self.server:
            try:
                self.server.shutdown(socket.SHUT_RDWR)
                self.server.close()
            except:
                pass
            self.server = None

        self.connection_made = False

    def convert_piece_to_key(self, piece):

        for key in piece_mapping:
            if piece_mapping[key] == piece:
                return key

    def convert_key_to_piece(self, key):

        return piece_mapping.get(key)
