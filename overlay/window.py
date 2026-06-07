"""
Builds and styles the transparent GTK overlay window.
This is strictly a UI file; it knows nothing about sockets or mouse tracking logic!
"""

import tempfile

import config
from gi.repository import GLib, Gtk, Gtk4LayerShell


class OverlayWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        # 1. Setup our Layer Shell properties (full-screen, non-blocking, on top)
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)

        # Stretch window to fill the entire display
        for edge in [
            Gtk4LayerShell.Edge.TOP,
            Gtk4LayerShell.Edge.LEFT,
            Gtk4LayerShell.Edge.BOTTOM,
            Gtk4LayerShell.Edge.RIGHT,
        ]:
            Gtk4LayerShell.set_anchor(self, edge, True)

        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)
        Gtk4LayerShell.set_exclusive_zone(self, -1)

        # 2. Window attributes
        self.set_focusable(False)
        self.set_can_focus(False)
        self.set_default_size(1920, 1080)
        self.set_opacity(1.0)

        # 3. Canvas Container (Fixed layout)
        self.fixed = Gtk.Fixed()
        self.fixed.set_focusable(False)
        self.set_child(self.fixed)

        # 4. Create and load our SVG cursor graphic
        self.temp_svg = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
        self.temp_svg.write(config.SVG_DATA)
        self.temp_svg.flush()

        self.cursor_widget = Gtk.Picture.new_for_filename(self.temp_svg.name)
        self.cursor_widget.set_size_request(24, 24)
        self.cursor_widget.set_focusable(False)
        self.cursor_widget.set_can_shrink(False)
        self.fixed.put(self.cursor_widget, 200, 200)

        # 5. Thought Bubble Label
        self.bubble = Gtk.Label(label="")
        self.bubble.set_css_classes(["bubble"])
        self.bubble.set_visible(False)
        self.bubble.set_focusable(False)
        self.fixed.put(self.bubble, 220, 180)

        # 6. Apply Stylesheets (CSS)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(config.UI_STYLESHEET)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Show the window to the world
        self.present()

        # Schedule the "click-through" trigger 500ms after rendering
        GLib.timeout_add(500, self._apply_click_through_region)

    def _apply_click_through_region(win):
        import cairo

        # layer_surface = Gtk4LayerShell.get_zwlr_layer_surface_v1(win)
        surface = win.get_surface()
        if surface:
            region = cairo.Region()
            surface.set_input_region(region)
            surface.queue_render()
        return False

    def move_cursor(self, x, y):
        """Repositions the cursor image and bubble relative to it."""
        self.fixed.move(self.cursor_widget, x, y)
        self.fixed.move(self.bubble, x + 20, y - 20)

    def show_bubble(self, text):
        """Displays text in the thought bubble."""
        self.bubble.set_label(text)
        self.bubble.set_visible(True)

    def hide_bubble(self):
        """Hides the thought bubble from view."""
        self.bubble.set_visible(False)
