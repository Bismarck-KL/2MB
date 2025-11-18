import pygame

from utils.color import TITLE
from menu_scene import MenuScene

class AvatarCreateScene:
    """A simple placeholder game scene to demonstrate scene switching."""

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # return to menu
            self.app.scene = MenuScene(self.app)

    def update(self, dt):
        pass

    def render(self):
        # simple visual
        self.screen.fill((18, 24, 36))
        txt = self.title_font.render("Avatar Create Scene", True, TITLE)
        rect = txt.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
        self.screen.blit(txt, rect)

