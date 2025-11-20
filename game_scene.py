import pygame

from utils.color import BG, TITLE, QUIT_BASE, QUIT_HOVER, HEALTH, HEALTH_BG
from utils.ui import Button, draw_health_bar
from classes.player import Player

# mediapipe capture helpers
try:
    from utils.mediapipe_capture import (
        start_mediapipe_capture,
        stop_mediapipe_capture,
        initialize_mediapipe,
    )
    from utils.loading import run_loading_with_callback
except Exception:
    # allow project to run even if opencv/mediapipe not available at import time
    def start_mediapipe_capture():
        print("start_mediapipe_capture: mediapipe capture not available")

    def stop_mediapipe_capture():
        pass

    def initialize_mediapipe(report, stop_event=None):
        # fake progress for the loading UI when mediapipe isn't installed
        import time

        for p in range(0, 101, 10):
            if stop_event is not None and stop_event.is_set():
                break
            try:
                report(float(p))
            except Exception:
                pass
            time.sleep(0.05)

    def run_loading_with_callback(surface, loader, on_complete=None, **kwargs):
        # Minimal fallback: call loader synchronously and then on_complete
        try:
            try:
                loader(lambda p: None, None)
            except TypeError:
                loader(lambda p: None)
        except Exception:
            pass
        if on_complete:
            try:
                on_complete()
            except Exception:
                pass


class GameScene:
    """A simple placeholder game scene to demonstrate scene switching."""

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

        # player entity
        # create player 1 at the bottom left
        self.player_1 = Player(app, 0, image_key="player1")
        # create player 2 at the bottom right
        self.player_2 = Player(app, 1, image_key="player2")

    def on_enter(self):
        """Called when the scene becomes active. Start mediapipe capture in a new window."""
        try:
            # show the project's loading UI while we initialize mediapipe
            run_loading_with_callback(
                surface=self.screen,
                loader=initialize_mediapipe,
                on_complete=start_mediapipe_capture,
                title="Initializing Camera",
                subtitle="Preparing MediaPipe...",
            )
        except Exception as e:
            print("GameScene: failed to initialize mediapipe capture:", e)

    def on_exit(self):
        """Called when leaving the scene. Stop the mediapipe capture."""
        try:
            stop_mediapipe_capture()
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # return to menu
            self.app.change_scene("MenuScene")

        # back button click
        if self.back_button.handle_event(event):
            self.app.change_scene("MenuScene")

    def update(self, dt):
        # update player
        self.player_1.update(dt)
        self.player_2.update(dt)    

    def render(self):
        # simple visual

        # draw background image or color
        try:
            bg_image = self.res_mgr.get_image("game_background")
            if bg_image:
                # protect against invalid surfaces
                scaled = pygame.transform.smoothscale(bg_image, (self.app.WIDTH, self.app.HEIGHT))
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.fill(BG)
        except Exception:
            # fallback: plain background color
            self.screen.fill(BG)


        txt = self.title_font.render("Game Scene", True, TITLE)
        rect = txt.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
        self.screen.blit(txt, rect)

        # draw back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)

        # draw player on top
        self.player_1.draw(self.screen)
        self.player_2.draw(self.screen)

        # draw HUD health bars for both players (top-left and top-right)
        try:
            w_margin = 16
            h_margin = 100
            bar_w = 360
            bar_h = 20
            # player 1 left
            p1_rect = pygame.Rect(w_margin, h_margin, bar_w, bar_h)
            draw_health_bar(self.screen, p1_rect, self.player_1.health_points, self.player_1.max_health_points)
            # label
            lbl1 = self.font.render("P1", True, TITLE)
            self.screen.blit(lbl1, (p1_rect.right + 8, h_margin - 2))

            # player 2 right
            p2_rect = pygame.Rect(self.app.WIDTH - w_margin - bar_w, h_margin, bar_w, bar_h)
            draw_health_bar(self.screen, p2_rect, self.player_2.health_points, self.player_2.max_health_points)
            lbl2 = self.font.render("P2", True, TITLE)
            lbl2_rect = lbl2.get_rect()
            self.screen.blit(lbl2, (p2_rect.left - lbl2_rect.width - 8, h_margin - 2))
        except Exception:
            pass
