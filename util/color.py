"""Color constants for the 2MB project.

Place shared colors here so they can be imported across modules.
"""

# Basic
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Background and UI
BG = (20, 20, 20)
TITLE = (240, 240, 240)

# Start button
START_BASE = (30, 144, 255)  # dodgerblue
START_HOVER = (65, 150, 255)

# Quit button
QUIT_BASE = (200, 40, 40)
QUIT_HOVER = (220, 70, 70)

# Misc
STATUS = (200, 200, 200)

COLORS = {
    "white": WHITE,
    "black": BLACK,
    "bg": BG,
    "title": TITLE,
    "start_base": START_BASE,
    "start_hover": START_HOVER,
    "quit_base": QUIT_BASE,
    "quit_hover": QUIT_HOVER,
    "status": STATUS,
}

__all__ = [
    "WHITE",
    "BLACK",
    "BG",
    "TITLE",
    "START_BASE",
    "START_HOVER",
    "QUIT_BASE",
    "QUIT_HOVER",
    "STATUS",
    "COLORS",
]
