"""
Shared configurations and assets for the AI Cursor project.
Keeping this separate prevents raw text assets from cluttering our code files.
"""

import os

# Socket Configuration
SOCKET_PATH = "/tmp/aicursor.sock"

# Multi-monitor Setup (Hyprland Absolute Coordinates)
MONITOR_OFFSET_X = 2530
MONITOR_OFFSET_Y = 536

# Visual offsets to keep the AI cursor near (but not directly under) your mouse
CURSOR_PADDING_X = 40
CURSOR_PADDING_Y = 40

# Custom cursor SVG graphic
SVG_DATA = b"""<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 2L20 12L12 13.5L8 21L4 2Z" fill="#60a5fa" stroke="#1d4ed8" stroke-width="1.5"/>
</svg>"""

# CSS styling for the transparent canvas and the bubble
UI_STYLESHEET = """
window {
    background: transparent;
}
.bubble {
    background: rgba(0,0,0,0.8);
    color: white;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}
"""
