import pygame
import os

from utils.color import BG, TITLE,START_BASE,START_HOVER, QUIT_BASE, QUIT_HOVER,NEXT_BASE,NEXT_HOVER,PREV_BASE,PREV_HOVER
from utils.ui import Button
from utils.gif_player import GifPlayer


class TutorialScene:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font
        self.res_mgr = app.res_mgr


        # TO-DO(Qianrina): update the button layout, size and positions
        # button layout
        start_btn_w, start_btn_h = 116, 127
        back_btn_w, back_btn_h = 116, 127
        next_btn_w, next_btn_h = 116, 127
        prev_btn_w, prev_btn_h = 116, 127

        self.start_rect = pygame.Rect(app.WIDTH - start_btn_w - 20, 20, start_btn_w, start_btn_h)
        self.back_rect = pygame.Rect(20, 20, back_btn_w, back_btn_h)

        # bottom left and right for prev/next (if needed in future)
        self.prev_rect = pygame.Rect(20, app.HEIGHT/2 - (127/2), prev_btn_w, prev_btn_h)
        self.next_rect = pygame.Rect(app.WIDTH - next_btn_w - 20, app.HEIGHT/2 - (127/2), next_btn_w, next_btn_h)
        
       

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
        try:         
            next_img = self.res_mgr.get_image("btn_next")
        except Exception:
            next_img = None
        try:
            prev_img = self.res_mgr.get_image("btn_prev")
        except Exception:
            
            prev_img = None

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
        self.next_button  = Button(
            self.next_rect, 
            text="Next",
            font=self.font,
            base_color=NEXT_BASE,
            hover_color=NEXT_HOVER,
            image=next_img,
        )
        self.prev_button  = Button(
            self.prev_rect,
            text="Prev",
            font=self.font, 
            base_color=PREV_BASE,
            hover_color=PREV_HOVER,
            image=prev_img,
        )

        # Load tutorial assets. If an asset is a GIF file we create a GifPlayer
        # instance which will produce animated frames; otherwise we use the
        # already-loaded pygame.Surface returned by ResourceManager.
        def _load_asset(key):
            # prefer the raw mapped path so we can detect GIFs
            path = None
            try:
                path = self.res_mgr.images_map.get(key)
            except Exception:
                path = None

            if path and isinstance(path, str) and path.lower().endswith('.gif'):
                try:
                    gp = GifPlayer(path)
                    if gp.is_valid():
                        return gp
                except Exception:
                    # fall back to static surface
                    pass

            # default: return static surface (may be None)
            try:
                return self.res_mgr.get_image(key)
            except Exception:
                return None

        self.tutorial_images = {
            "jump": _load_asset("tutorial_jump"),
            "punch": _load_asset("tutorial_punch"),
            "kick": _load_asset("tutorial_kick"),
            "block": _load_asset("tutorial_block"),
        }
        self.current_tutorial = "jump"
        self.current_tutorial_image = self.tutorial_images.get(self.current_tutorial)
        

        self.started = False

    def handle_event(self, event):
        if self.start_button.handle_event(event):
            # switch to Game scene when Start is clicked
            self.app.change_scene("GameScene")
        if self.back_button.handle_event(event):
            self.app.change_scene("MenuScene")
        if self.next_button.handle_event(event):
            # switch to next tutorial image
            keys = list(self.tutorial_images.keys())
            try:
                idx = keys.index(self.current_tutorial)
                idx = (idx + 1) % len(keys)
                self.current_tutorial = keys[idx]
            except Exception:
                self.current_tutorial = keys[0]
        if self.prev_button.handle_event(event):
            # switch to previous tutorial image
            keys = list(self.tutorial_images.keys())
            try:
                idx = keys.index(self.current_tutorial)
                idx = (idx - 1) % len(keys)
                self.current_tutorial = keys[idx]
            except Exception:
                self.current_tutorial = keys[0]

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

        # Ensure tutorial GIFs start from the beginning and play when entering the scene
        try:
            for val in self.tutorial_images.values():
                if hasattr(val, 'reset'):
                    try:
                        val.reset()
                    except Exception:
                        pass
                if hasattr(val, 'play'):
                    try:
                        val.play()
                    except Exception:
                        pass
        except Exception:
            pass

    def on_exit(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.fadeout(500)
        except Exception:
            pass

    def update(self, dt):
        # advance GIF players if present
        try:
            val = self.tutorial_images.get(self.current_tutorial)
            if hasattr(val, 'update'):
                try:
                    val.update(dt)
                except Exception:
                    pass
        except Exception:
            pass

    def render(self):
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

        # draw current tutorial image in center
        try:
            val = self.tutorial_images.get(self.current_tutorial)
            img = None
            # GifPlayer exposes get_surface(); static surfaces are blitted directly
            if val is None:
                img = None
            elif hasattr(val, 'get_surface'):
                try:
                    img = val.get_surface()
                except Exception:
                    img = None
            else:
                img = val

            if img:
                # Scale the tutorial image to at most 60% of the screen while
                # preserving aspect ratio. Do not upscale small images.
                orig_w, orig_h = img.get_size()
                max_w = int(self.app.WIDTH * 0.6)
                max_h = int(self.app.HEIGHT * 0.6)
                # guard against zero sizes
                if orig_w <= 0 or orig_h <= 0:
                    scaled_img = img
                else:
                    scale = min(max_w / orig_w, max_h / orig_h, 1.0)
                    new_w = max(1, int(orig_w * scale))
                    new_h = max(1, int(orig_h * scale))
                    if new_w != orig_w or new_h != orig_h:
                        try:
                            scaled_img = pygame.transform.smoothscale(img, (new_w, new_h))
                        except Exception:
                            scaled_img = pygame.transform.scale(img, (new_w, new_h))
                    else:
                        scaled_img = img

                img_rect = scaled_img.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
                self.screen.blit(scaled_img, img_rect)
        except Exception:
            # if anything goes wrong drawing the tutorial image, ignore and continue
            pass
        

        # title
        title_surf = self.title_font.render("Tutorial", True, TITLE)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 70))
        self.screen.blit(title_surf, title_rect)

        # show the name of current tutorial
        try:
            tutorial_name = self.current_tutorial.capitalize()
            tutorial_surf = self.font.render(f"{tutorial_name}", True, TITLE)
            tutorial_rect = tutorial_surf.get_rect(center=(self.app.WIDTH // 2, 120))
            self.screen.blit(tutorial_surf, tutorial_rect)
        except Exception:
            pass

        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)
        self.start_button.draw(self.screen, mouse_pos)
        self.next_button.draw(self.screen, mouse_pos)
        self.prev_button.draw(self.screen, mouse_pos)





