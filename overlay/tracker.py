"""
Handles tracking the physical mouse cursor.
This code runs in a separate background thread.
"""

import subprocess
import time

import config
from gi.repository import GLib


def track_mouse(window):
    """
    Infinite loop that queries the real cursor position and smoothly
    drifts (lerps) the AI cursor toward it.
    """
    # Current animated position of our AI cursor
    ai_x, ai_y = 150.0, 150.0

    # Easing speed (0.4 means cover 40% of remaining distance per tick)
    lerp_speed = 0.5

    while True:
        try:
            # Ask Hyprland where the real cursor is
            raw_output = subprocess.check_output(
                ["hyprctl", "cursorpos"], text=True
            ).strip()

            real_x, real_y = raw_output.split(", ")

            # Calculate screen coordinates relative to our target monitor
            target_x = int(real_x) - config.MONITOR_OFFSET_X + config.CURSOR_PADDING_X
            target_y = int(real_y) - config.MONITOR_OFFSET_Y + config.CURSOR_PADDING_Y

            # Linear Interpolation math for that smooth "gliding" effect
            ai_x += (target_x - ai_x) * lerp_speed
            ai_y += (target_y - ai_y) * lerp_speed

            # Ask GTK's main thread to move our widgets when it is free
            GLib.idle_add(window.move_cursor, int(ai_x), int(ai_y))

        except Exception as error:
            print(f"[Mouse Tracker Error]: {error}")

        # Standard delay to run at ~250 updates per second
        time.sleep(0.003)
