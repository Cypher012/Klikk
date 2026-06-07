#!/usr/bin/env python3
"""
The Entry Point for our application.
Sets up the GTK Application context, initializes threads, and boots up the UI.
"""

import os
import threading

import gi

os.environ["GDK_BACKEND"] = "wayland"
gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk
from server import listen_for_commands
from tracker import track_mouse

# Import our custom modules
from window import OverlayWindow

# Force the GDK backend to use Wayland before loading GTK libraries


class OverlayApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.aicursor.overlay")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        # 1. Create the user interface
        window = OverlayWindow(app)

        # 2. Spin up our asynchronous background services (Passing our window reference)
        threading.Thread(target=track_mouse, args=(window,), daemon=True).start()
        threading.Thread(
            target=listen_for_commands, args=(window,), daemon=True
        ).start()


if __name__ == "__main__":
    app = OverlayApp()
    app.run()
