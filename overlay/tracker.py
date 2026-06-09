import subprocess
import time

import config
from gi.repository import GLib


def track_mouse(window):
    ai_x, ai_y = 150.0, 150.0
    lerp_speed = 0.5

    while True:
        try:
            if window.ai_target is not None:
                # AI has a target — lerp toward it, ignore real mouse
                target_x = window.ai_target[0] + config.CURSOR_PADDING_X
                target_y = window.ai_target[1] + config.CURSOR_PADDING_Y
            else:
                # No target — follow real mouse
                raw_output = subprocess.check_output(
                    ["hyprctl", "cursorpos"], text=True
                ).strip()
                real_x, real_y = raw_output.split(", ")
                target_x = (
                    int(real_x) - config.MONITOR_OFFSET_X + config.CURSOR_PADDING_X
                )
                target_y = (
                    int(real_y) - config.MONITOR_OFFSET_Y + config.CURSOR_PADDING_Y
                )

            ai_x += (target_x - ai_x) * lerp_speed
            ai_y += (target_y - ai_y) * lerp_speed

            GLib.idle_add(window.move_cursor, int(ai_x), int(ai_y))

        except Exception as error:
            print(f"[Mouse Tracker Error]: {error}")

        time.sleep(0.003)
