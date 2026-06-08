"""
Listens for commands from external programs using local UNIX sockets.
This code runs in a separate background thread.
"""

import json
import os
import socket

import config
from gi.repository import GLib


def listen_for_commands(window):
    if os.path.exists(config.SOCKET_PATH):
        os.remove(config.SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(config.SOCKET_PATH)
    server.listen(1)

    while True:
        connection, _ = server.accept()
        with connection:
            buffer = ""
            while True:
                chunk = connection.recv(1024).decode()
                if not chunk:
                    break
                buffer += chunk
                # Process each complete line
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        command_type = payload.get("type")
                        if command_type == "move":
                            GLib.idle_add(
                                window.move_cursor, payload["x"], payload["y"]
                            )
                        elif command_type == "bubble":
                            GLib.idle_add(window.show_bubble, payload["text"])
                        elif command_type == "hide_bubble":
                            GLib.idle_add(window.hide_bubble)
                    except Exception as error:
                        print(f"[Socket Server Error]: {error}")
