"""UI helper utilities for 2MB.

Provides reusable UI drawing functions such as draw_button.
"""
import pygame
from typing import Tuple, Optional

from utils.color import WHITE


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


class Button:
    """Simple Button component that supports image or text buttons.

    Responsibilities:
    - Hold visual state (image or colors)
    - Render itself
    - Detect clicks
    """

    def __init__(self, rect: pygame.Rect, text: str = "", font: Optional[pygame.font.Font] = None,
                 base_color=(30, 144, 255), hover_color=(65, 150, 255), image: Optional[pygame.Surface] = None):
        self.rect = rect
        self.text = text
        self.font = font or pygame.font.SysFont(None, 36)
        self.base_color = base_color
        self.hover_color = hover_color
        self.image = image

    def draw(self, surface: pygame.Surface, mouse_pos):
        if self.image:
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
        else:
            draw_button(surface, self.rect, self.text, self.font, self.base_color, self.hover_color, mouse_pos)

    def handle_event(self, event) -> bool:
        """Return True if clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


__all__ = ["draw_button", "Button"]
