import pygame
import os

from utils.color import BG, TITLE,START_BASE,START_HOVER, QUIT_BASE, QUIT_HOVER
from utils.ui import Button


class TutorialScene:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font
        self.res_mgr = app.res_mgr


        # TO-DO(Qianrina): update the button layout, size and positions
        # button layout
        start_btn_w, start_btn_h = 140, 48
        back_btn_w, back_btn_h = 140, 48
        self.start_rect = pygame.Rect(app.WIDTH - start_btn_w - 20, 20, start_btn_w, start_btn_h)
        self.back_rect = pygame.Rect(20, 20, back_btn_w, back_btn_h)

       
        # create Button components (images will be used if available)
        # get images defensively (loader may have set None for missing files)
        try:
            start_img = self.res_mgr.get_image("btn_start")
        except Exception:
            start_img = None
        try:
            back_img = self.res_mgr.get_image("btn_back")
        except Exception:
            back_img = None


        self.start_button = Button(
            self.start_rect,
            text="Start",
            font=self.font,
            base_color=START_BASE,
            hover_color=START_HOVER,
            image=start_img,
        )
        self.back_button  = Button(
            self.back_rect,
            text="Back",
            font=self.font,
            base_color=QUIT_BASE,
            hover_color=QUIT_HOVER,
            image=back_img,
        )

        self.started = False

    def handle_event(self, event):
        if self.start_button.handle_event(event):
            # switch to Game scene when Start is clicked
            self.app.change_scene("GameScene")
        if self.back_button.handle_event(event):
            self.app.change_scene("MenuScene")
    def on_enter(self):
        # play menu background music (prefer ResourceManager if available)
        try:
            # If ResourceManager has preloaded audio loaders, prefer using it
            if hasattr(self, 'res_mgr') and getattr(self.res_mgr, 'audio_loaders', None):
                try:
                    print("MenuScene: playing music via ResourceManager")
                    # finalize & play the named 'game' track (will fall back inside RM if missing)
                    self.res_mgr.finalize_and_play('game')
                except Exception:
                    print("MenuScene: ResourceManager failed to play music, falling back to local mixer")
                    # fall back to direct mixer below
                    pass
            else:
                # ensure mixer is initialized then load and play the file directly
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                except Exception:
                    try:
                        pygame.mixer.init()
                    except Exception:
                        pass

                music_path = os.path.join('assets', 'sounds', 'game_bgm.mp3')
                if os.path.exists(music_path):
                    try:
                        pygame.mixer.music.load(music_path)
                        pygame.mixer.music.set_volume(0.5)
                        # fade in over 500ms
                        pygame.mixer.music.play(-1, 0.0, 500)
                    except Exception as e:
                        print(f"MenuScene: failed to play music '{music_path}':", e)
                else:
                    print(f"MenuScene: music file not found: {music_path}")
        except Exception:
            pass

    def on_exit(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.fadeout(500)
        except Exception:
            pass

    def update(self, dt):
        pass

    def render(self):
        # draw background image or color
        try:
            bg_image = self.res_mgr.get_image("background")
            if bg_image:
                # protect against invalid surfaces
                scaled = pygame.transform.smoothscale(bg_image, (self.app.WIDTH, self.app.HEIGHT))
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.fill(BG)
        except Exception:
            # fallback: plain background color
            self.screen.fill(BG)

        # title
        title_surf = self.title_font.render("Tutorial", True, TITLE)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 70))
        self.screen.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)
        self.start_button.draw(self.screen, mouse_pos)




