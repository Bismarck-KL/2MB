"""Loading screen utilities.

Provides functions to draw a full-screen loading scene, a loading bar,
loading text and percentage. Designed to be reusable from any Pygame scene.

API
- draw_loading_bar(surface, rect, progress, ...)
- draw_loading_screen(surface, progress, title=..., subtitle=..., fonts=..., colors=...)

When run as a script this file shows a small demo animation (useful for manual testing).
"""
from __future__ import annotations

import pygame
from typing import Tuple, Optional

from util.color import BG, TITLE, START_BASE, START_HOVER, QUIT_BASE, WHITE, STATUS


def draw_loading_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    progress: float,
    bar_color: Tuple[int, int, int] = START_BASE,
    bar_bg: Tuple[int, int, int] = (50, 50, 50),
    border_radius: int = 8,
):
    """Draw a horizontal loading bar into rect.

    progress: 0..100 (will be clamped)
    """
    progress = max(0.0, min(100.0, float(progress)))
    pygame.draw.rect(surface, bar_bg, rect, border_radius=border_radius)

    inner_w = int((rect.width - 4) * (progress / 100.0))
    if inner_w > 0:
        inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, inner_w, rect.height - 4)
        pygame.draw.rect(surface, bar_color, inner_rect, border_radius=border_radius)


def draw_loading_screen(
    surface: pygame.Surface,
    progress: float,
    title: str = "Loading",
    subtitle: Optional[str] = None,
    *,
    bg_color: Tuple[int, int, int] = BG,
    text_color: Tuple[int, int, int] = TITLE,
    bar_color: Tuple[int, int, int] = START_BASE,
    bar_bg: Tuple[int, int, int] = (50, 50, 50),
    percent_color: Tuple[int, int, int] = WHITE,
    title_font: Optional[pygame.font.Font] = None,
    percent_font: Optional[pygame.font.Font] = None,
):
    """Render a full-screen loading scene on `surface` with given progress (0..100).

    This will fill the surface with a background, draw the title, an optional
    subtitle, a centered loading bar and the percentage text below it.
    """
    w, h = surface.get_size()

    # background
    surface.fill(bg_color)

    # subtle center glow (a translucent circle) to give depth
    glow = pygame.Surface((w, h), flags=pygame.SRCALPHA)
    glow.fill((0, 0, 0, 0))
    pygame.draw.circle(glow, (255, 255, 255, 12), (w // 2, h // 2), int(min(w, h) * 0.45))
    surface.blit(glow, (0, 0))

    # fonts
    if title_font is None:
        title_font = pygame.font.SysFont(None, 56)
    if percent_font is None:
        percent_font = pygame.font.SysFont(None, 32)

    # title
    title_surf = title_font.render(title, True, text_color)
    title_rect = title_surf.get_rect(center=(w // 2, h // 2 - 80))
    surface.blit(title_surf, title_rect)

    # subtitle
    if subtitle:
        sub_font = pygame.font.SysFont(None, 28)
        sub_surf = sub_font.render(subtitle, True, STATUS)
        sub_rect = sub_surf.get_rect(center=(w // 2, h // 2 - 40))
        surface.blit(sub_surf, sub_rect)

    # loading bar
    bar_w = int(w * 0.5)
    bar_h = 36
    bar_rect = pygame.Rect((w - bar_w) // 2, h // 2, bar_w, bar_h)
    draw_loading_bar(surface, bar_rect, progress, bar_color=bar_color, bar_bg=bar_bg)

    # percent text
    pct_text = f"{int(max(0, min(100, progress)))}%"
    pct_surf = percent_font.render(pct_text, True, percent_color)
    pct_rect = pct_surf.get_rect(center=(w // 2, h // 2 + bar_h + 30))
    surface.blit(pct_surf, pct_rect)


__all__ = ["draw_loading_bar", "draw_loading_screen"]


if __name__ == "__main__":
    # Small demo when run directly. This opens a window and increments progress.
    pygame.init()
    size = (900, 600)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Loading")
    clock = pygame.time.Clock()

    progress = 0.0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        progress += 0.4
        if progress > 100.0:
            progress = 100.0

        draw_loading_screen(screen, progress, title="Loading Scene", subtitle="Preparing resources...")
        pygame.display.flip()
        clock.tick(60)

        if progress >= 100.0:
            pygame.time.delay(600)
            running = False

    pygame.quit()
