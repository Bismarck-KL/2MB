"""UI helper utilities for 2MB.

Provides reusable UI drawing functions such as draw_button.
"""
import pygame
from typing import Tuple, Optional

from utils.color import WHITE
from utils.color import HEALTH, HEALTH_BG, HEALTH_BORDER, HEALTH_YELLOW, HEALTH_RED


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
            # Scale the provided image to the button rectangle so it fits the button size.
            # We use smoothscale for a nicer result; this will stretch the image to fill the
            # rect. If you prefer to preserve aspect ratio, we can change this to fit + letterbox.
            try:
                img_surf = pygame.transform.smoothscale(self.image, (self.rect.width, self.rect.height))
                img_rect = img_surf.get_rect(center=self.rect.center)
                surface.blit(img_surf, img_rect)
            except Exception:
                # If scaling fails for any reason, fall back to blitting the original image
                try:
                    img_rect = self.image.get_rect(center=self.rect.center)
                    surface.blit(self.image, img_rect)
                except Exception:
                    # swallow errors to avoid crashing UI
                    pass
        else:
            draw_button(surface, self.rect, self.text, self.font, self.base_color, self.hover_color, mouse_pos)

    def handle_event(self, event) -> bool:
        """Return True if clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def draw_health_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    current: float,
    maximum: float,
    fg_color=HEALTH,
    bg_color=HEALTH_BG,
    border_color=HEALTH_BORDER,
    border_radius: int = 4,
):
    """Draw a horizontal health bar inside `rect`.

    - `current` and `maximum` can be ints or floats. Values are clamped.
    - Bar fills from left to right.
    """
    try:
        pct = 0.0
        if maximum and maximum > 0:
            pct = max(0.0, min(1.0, float(current) / float(maximum)))

        # dynamic foreground color when caller uses default HEALTH
        if fg_color == HEALTH:
            if pct < 0.3:
                fg = HEALTH_RED
            elif pct < 0.5:
                fg = HEALTH_YELLOW
            else:
                fg = HEALTH
        else:
            fg = fg_color

        # outer border
        pygame.draw.rect(surface, border_color, rect, border_radius=border_radius)

        # inner background (shrink by 2 px to show border)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(surface, bg_color, inner, border_radius=max(0, border_radius - 1))

        # filled portion
        fill_w = max(0, int(inner.width * pct))
        if fill_w > 0:
            fill_rect = pygame.Rect(inner.x, inner.y, fill_w, inner.height)
            pygame.draw.rect(surface, fg, fill_rect, border_radius=max(0, border_radius - 1))
    except Exception:
        # don't crash UI if drawing fails
        pass


__all__ = ["draw_button", "Button", "draw_health_bar"]
