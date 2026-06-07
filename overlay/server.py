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
    """
    Cleans up old socket connections, starts a local socket server,
    and handles incoming requests to show/hide thought bubbles.
    """
    # Remove any leftover socket files from previous crashes
    if os.path.exists(config.SOCKET_PATH):
        os.remove(config.SOCKET_PATH)

    # Setup the Unix domain socket server
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(config.SOCKET_PATH)
    server.listen(1)

    while True:
        # Wait until another program connects
        connection, _ = server.accept()

        with connection:
            try:
                # Read incoming payload
                data = connection.recv(1024).decode()
                payload = json.loads(data)

                command_type = payload.get("type")

                # Parse the incoming command and post UI updates to the main thread
                if command_type == "move":
                    GLib.idle_add(window.move_cursor, payload["x"], payload["y"])
                elif command_type == "bubble":
                    GLib.idle_add(window.show_bubble, payload["text"])
                elif command_type == "hide_bubble":
                    GLib.idle_add(window.hide_bubble)

            except Exception as error:
                print(f"[Socket Server Error]: {error}")
