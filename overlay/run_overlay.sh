#!/usr/bin/env bash
LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so.1.3.0 GDK_BACKEND=wayland python3 "$(dirname "$0")/main.py"
