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

        self.app = app
        self.server = None
        self.client = None
        self.is_server = None
        self.move_callback = None

    def host_game(self, host, port):

        with threading.Lock():
            if self.app.network_running:
                return
            else:
                self.app.network_running =  True

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
                self.client.settimeout(1.0)
            except OSError:
                return

            self.app.call_from_thread(setattr, self.app, "connection_made", True)
            self.app.call_from_thread(setattr, self.app.screen, "player_colour", "white")

            threading.Thread(target=self.listen_for_moves, daemon=True).start()

        except Exception as e:
            self.app.network_running = False
            self.app.call_from_thread(setattr, self.app, "network_running", False)
            message = {"title": "", "message": str(e)}
            self.app.call_from_thread(setattr, self.app, "pop_up_message", message)

            if self.server:
                self.server.close()
                self.server = None

    def connect_to_game(self, host, port):

        with threading.Lock():
            if self.app.network_running == True:
                return
            else:
                self.app.network_running =  True

        threading.Thread(target=self.connect_to_game_loop, args=(host, port), daemon=True).start()

    def connect_to_game_loop(self, host, port):

        try:
            self.is_server = False

            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(1.0)
            self.client.connect((host, port))

            self.app.call_from_thread(setattr, self.app.screen, "player_colour", "black")
            self.app.call_from_thread(setattr, self.app, "connection_made", True)

            threading.Thread(target=self.listen_for_moves, daemon=True).start()

        except Exception as e:
            self.app.network_running = False
            self.app.call_from_thread(setattr, self.app, "network_running", False)
            message = {"title": "", "message": str(e)}
            self.app.call_from_thread(setattr, self.app, "pop_up_message", message)

            if self.client:
                self.client.close()
                self.client = None

    def listen_for_moves(self):

        while self.app.network_running:
            try:
                data = self.client.recv(1024).decode('utf-8')

                if not data:
                    message = {"title": "", "message": "Connection closed."}
                    self.app.call_from_thread(setattr, self.app, "pop_up_message", message)
                    self.handle_disconnection()
                    break

                move_information = json.loads(data)

                if "piece_type_to_move" in move_information:
                    move_information["piece_type_to_move"] = self.convert_key_to_piece(move_information["piece_type_to_move"])

                if self.move_callback:
                    self.app.call_from_thread(self.move_callback, move_information)

            except socket.timeout:
                continue

            except (ConnectionResetError, BrokenPipeError, OSError):
                message = {"title": "", "message": "Connection closed."}
                self.app.call_from_thread(setattr, self.app, "pop_up_message", message)
                self.handle_disconnection()
                break

            except Exception as e:
                message = {"title": "", "message": str(e)}
                self.app.call_from_thread(setattr, self.app, "pop_up_message", message)
                self.handle_disconnection()
                break

    def handle_disconnection(self):

        self.app.call_from_thread(self.close_connection)

        while len(self.app.screen_stack) > 2:
            self.app.call_from_thread(self.app.screen.dismiss)

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
                self.app.call_from_thread(setattr, self.app, "pop_up_message", message)

    def close_connection(self):

        self.app.network_running = False

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

        self.app.connection_made = False

    def convert_piece_to_key(self, piece):

        for key in piece_mapping:
            if piece_mapping[key] == piece:
                return key

    def convert_key_to_piece(self, key):

        return piece_mapping.get(key)
