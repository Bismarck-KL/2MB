import pygame

from utils.color import BG, TITLE, START_BASE, START_HOVER, QUIT_BASE, QUIT_HOVER, STATUS
from utils.ui import Button


class MenuScene:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font
        self.res_mgr = app.res_mgr


        # TO-DO(Qianrina): update the button layout, size and positions
        # button layout
        btn_w, btn_h = 260, 96
        center_x = app.WIDTH // 2
        center_y = app.HEIGHT // 2

        self.start_rect = pygame.Rect(center_x - btn_w - 20, center_y, btn_w, btn_h)
        self.quit_rect = pygame.Rect(center_x + 20, center_y, btn_w, btn_h)

        self.dev_game_rect = pygame.Rect(center_x + 20, center_y + btn_h + 20, btn_w, btn_h)
       
        # create Button components (images will be used if available)
        # get images defensively (loader may have set None for missing files)
        try:
            start_img = self.res_mgr.get_image("btn_start")
        except Exception:
            start_img = None
        try:
            quit_img = self.res_mgr.get_image("btn_quit")
        except Exception:
            quit_img = None

        self.start_button = Button(
            self.start_rect,
            text="Start",
            font=self.font,
            base_color=START_BASE,
            hover_color=START_HOVER,
            image=start_img,
        )
        self.quit_button = Button(
            self.quit_rect,
            text="Quit",
            font=self.font,
            base_color=QUIT_BASE,
            hover_color=QUIT_HOVER,
            image=quit_img,
        )
        self.dev_game_button = Button(
            self.dev_game_rect,
            text="Dev Game",
            font=self.font,
            base_color=START_BASE,
            hover_color=START_HOVER,
            image=None,
        )

        self.started = False

    def handle_event(self, event):
        if self.start_button.handle_event(event):
            # switch to Avatar Create scene when Start is clicked
            self.app.change_scene("AvatarCreateScene")
        if self.quit_button.handle_event(event):
            self.app.running = False
        if self.dev_game_button.handle_event(event):
            # switch to Game scene when Dev Game is clicked
            self.app.change_scene("GameScene")

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
        title_surf = self.title_font.render("Main Menu", True, TITLE)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2 - 140))
        self.screen.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.start_button.draw(self.screen, mouse_pos)
        self.quit_button.draw(self.screen, mouse_pos)
        self.dev_game_button.draw(self.screen, mouse_pos)

        if self.started:
            status_surf = self.font.render("Started!", True, STATUS)
            status_rect = status_surf.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2 + 140))
            self.screen.blit(status_surf, status_rect)

