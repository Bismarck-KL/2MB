import pygame

from utils.color import TITLE, QUIT_BASE, QUIT_HOVER
from utils.ui import Button


class GameScene:
    """A simple placeholder game scene to demonstrate scene switching."""

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font

        # back button (top-left)
        self.back_rect = pygame.Rect(20, 20, 140, 48)
        self.back_button = Button(
            self.back_rect,
            text="Back",
            font=self.font,
            base_color=QUIT_BASE,
            hover_color=QUIT_HOVER,
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # return to menu
            self.app.change_scene("MenuScene")

        # back button click
        if self.back_button.handle_event(event):
            self.app.change_scene("MenuScene")

    def update(self, dt):
        pass

    def render(self):
        # simple visual
        self.screen.fill((18, 24, 36))
        txt = self.title_font.render("Game Scene", True, TITLE)
        rect = txt.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
        self.screen.blit(txt, rect)

        # draw back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)
