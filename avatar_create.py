import pygame

from utils.color import BG, TITLE, QUIT_BASE, QUIT_HOVER
from utils.ui import Button


# TO-DO(FAMA): implement actual avatar creation flow and UI
class AvatarCreateScene:
    """A simple placeholder game scene to demonstrate scene switching.

    Adds a small 'Back' button to return to the main menu.
    """

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font
        self.res_mgr = app.res_mgr

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
        # keyboard: Esc returns to menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_scene("MenuScene")

        # back button click
        if self.back_button.handle_event(event):
            self.app.change_scene("MenuScene")

    def update(self, dt):
        pass

    def render(self):

        # draw background image or color
        try:
            bg_image = self.res_mgr.get_image("avatar_create_background")
            if bg_image:
                # protect against invalid surfaces
                scaled = pygame.transform.smoothscale(
                    bg_image, (self.app.WIDTH, self.app.HEIGHT)
                )
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.fill(BG)
        except Exception:
            # fallback: plain background color
            self.screen.fill(BG)

        # simple visual
        txt = self.title_font.render("Avatar Create Scene", True, TITLE)
        rect = txt.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
        self.screen.blit(txt, rect)

        # draw back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)
