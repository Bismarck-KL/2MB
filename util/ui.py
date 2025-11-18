"""UI helper utilities for 2MB.

Provides reusable UI drawing functions such as draw_button.
"""
import pygame
from typing import Tuple

from util.color import WHITE


def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    base_color: Tuple[int, int, int],
    hover_color: Tuple[int, int, int],
    mouse_pos: Tuple[int, int],
    text_color: Tuple[int, int, int] = WHITE,
    border_radius: int = 8,
):
    """Draw a rounded rectangle button with centered text.

    Parameters
    - surface: target surface
    - rect: pygame.Rect for button position / size
    - text: label string
    - font: pygame font used for label
    - base_color: color when not hovered
    - hover_color: color when hovered
    - mouse_pos: current mouse position to detect hover
    - text_color: color for button text (default WHITE)
    - border_radius: corner radius for rectangle
    """
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    txt_surf = font.render(text, True, text_color)
    txt_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, txt_rect)


__all__ = ["draw_button"]
