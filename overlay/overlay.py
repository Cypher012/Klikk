#!/usr/bin/env python3
import os
import tempfile
import time

import gi

os.environ["GDK_BACKEND"] = "wayland"

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")

import json
import socket
import threading

from gi.repository import GLib, Gtk, Gtk4LayerShell

SOCKET_PATH = "/tmp/aicursor.sock"

SVG_DATA = b"""<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 2L20 12L12 13.5L8 21L4 2Z" fill="#60a5fa" stroke="#1d4ed8" stroke-width="1.5"/>
</svg>"""


class OverlayWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.LEFT, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)
        Gtk4LayerShell.set_exclusive_zone(self, -1)

        self.set_focusable(False)
        self.set_can_focus(False)
        self.set_default_size(1920, 1080)
        self.set_opacity(1.0)

        self.fixed = Gtk.Fixed()
        self.fixed.set_focusable(False)
        self.set_child(self.fixed)

        # Write SVG to temp file
        self.svg_file = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
        self.svg_file.write(SVG_DATA)
        self.svg_file.flush()

        # AI cursor using Picture widget
        self.cursor_widget = Gtk.Picture.new_for_filename(self.svg_file.name)
        self.cursor_widget.set_size_request(24, 24)
        self.cursor_widget.set_focusable(False)
        self.cursor_widget.set_can_shrink(False)
        self.fixed.put(self.cursor_widget, 200, 200)

        # Thought bubble
        self.bubble = Gtk.Label(label="")
        self.bubble.set_css_classes(["bubble"])
        self.bubble.set_visible(False)
        self.bubble.set_focusable(False)
        self.fixed.put(self.bubble, 220, 180)

        css = Gtk.CssProvider()
        css.load_from_string("""
            window { background: transparent; }
            .bubble {
                background: rgba(0,0,0,0.8);
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.present()

        def apply_input_region(win):
            import cairo

            layer_surface = Gtk4LayerShell.get_zwlr_layer_surface_v1(win)
            print(f"Layer surface: {layer_surface}")
            surface = win.get_surface()
            if surface:
                region = cairo.Region()
                surface.set_input_region(region)
                surface.queue_render()
            return False

        GLib.timeout_add(500, apply_input_region, self)

        threading.Thread(target=self.listen_socket, daemon=True).start()
        threading.Thread(target=self.track_mouse, daemon=True).start()

    def track_mouse(self):
        import subprocess

        ai_x, ai_y = 150.0, 150.0
        speed = 0.4
        offset_x, offset_y = 40, 40

        # Your external monitor offset from hyprctl monitors
        monitor_x, monitor_y = 2530, 536

        while True:
            try:
                out = subprocess.check_output(
                    ["hyprctl", "cursorpos"], text=True
                ).strip()
                real_x, real_y = out.split(", ")

                # Convert absolute to relative monitor coordinates
                rel_x = int(real_x) - monitor_x + offset_x
                rel_y = int(real_y) - monitor_y + offset_y

                # Lerp
                ai_x += (rel_x - ai_x) * speed
                ai_y += (rel_y - ai_y) * speed

                GLib.idle_add(self.move_cursor, int(ai_x), int(ai_y))
            except Exception as e:
                print(f"Mouse track error: {e}")
            time.sleep(0.004)

    def move_cursor(self, x, y):
        self.fixed.move(self.cursor_widget, x, y)
        self.fixed.move(self.bubble, x + 20, y - 20)

    def show_bubble(self, text):
        self.bubble.set_label(text)
        self.bubble.set_visible(True)

    def hide_bubble(self):
        self.bubble.set_visible(False)

    def listen_socket(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(1)

        while True:
            conn, _ = server.accept()
            with conn:
                data = conn.recv(1024).decode()
                try:
                    msg = json.loads(data)
                    if msg["type"] == "move":
                        GLib.idle_add(self.move_cursor, msg["x"], msg["y"])
                    elif msg["type"] == "bubble":
                        GLib.idle_add(self.show_bubble, msg["text"])
                    elif msg["type"] == "hide_bubble":
                        GLib.idle_add(self.hide_bubble)
                except Exception as e:
                    print(f"Error: {e}")


class OverlayApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.aicursor.overlay")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        OverlayWindow(app)


if __name__ == "__main__":
    app = OverlayApp()
    app.run()
