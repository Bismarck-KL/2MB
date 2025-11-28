import pygame
import os

# only import what's needed here (scenes import their own colors)
from utils.color import BG, TITLE
from utils.loading import run_loading_with_callback
from utils.resource_manager import ResourceManager

# scenes are in their own modules to keep this file small
from menu_scene import MenuScene
from game_scene import GameScene
from avatar_create import AvatarCreateScene
from pose_editor_scene import PoseEditorScene
from tutorial_scene import TutorialScene


class Application:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("2MB - Menu")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.title_font = pygame.font.SysFont(None, 72)

    
        # resources
        images = {
            
            # TO-DO(Qianrina): upload the resources with correct paths
            "background": os.path.abspath(os.path.join("assets", "images", "background.png")),
            "game_background": os.path.abspath(os.path.join("assets", "images", "game_background.")),
            "avatar_create_background": os.path.abspath(os.path.join("assets", "images", "avatar_create_background.png")),
            "btn_start": os.path.abspath(os.path.join("assets", "images", "button_start.png")),
            "btn_quit": os.path.abspath(os.path.join("assets", "images", "button_quit.png")),
            "btn_back": os.path.abspath(os.path.join("assets", "images", "button_back.png")),
            "but_next": os.path.abspath(os.path.join("assets", "images", "button_next.png")),
            "button_prev": os.path.abspath(os.path.join("assets", "images", "button_prev.png")),
            #####
            
            # guides for capture UI (optional files under each player folder)
            # "player1_guide": os.path.abspath(os.path.join("assets", "photo", "player1", "guide.png")),
            # "player2_guide": os.path.abspath(os.path.join("assets", "photo", "player2", "guide.png")),
            # fallback/default tpose used by some scenes
            "default_tpose": os.path.abspath(os.path.join("assets", "photo", "tpose.png")),
            # Tutorial images
            "tutorial_jump": os.path.abspath(os.path.join("assets", "images","tutorial", "jump.gif")),
            "tutorial_punch": os.path.abspath(os.path.join("assets", "images","tutorial", "punch.gif")),
            "tutorial_kick": os.path.abspath(os.path.join("assets", "images","tutorial", "kick.gif")),
            "tutorial_block": os.path.abspath(os.path.join("assets", "images","tutorial", "block.gif")),

        }
        # Provide absolute paths to background music files so ResourceManager
        # can preload them. We include both the main game BGM and the
        # fighting-scene BGM so scenes can request the appropriate track.
        game_bgm = os.path.abspath(os.path.join('assets', 'sounds', 'game_bgm.mp3'))
        fighting_bgm = os.path.abspath(os.path.join('assets', 'sounds', 'fighting scene_bgm.mp3'))
        audio_files = {
            'game': game_bgm,
            'fighting': fighting_bgm,
        }

        self.res_mgr = ResourceManager(images=images, image_base_dir=None, audio_files=audio_files)

        self.running = True
        self.scene = None
        # register scene classes here so Application controls creation
        self.scene_registry = {
            "MenuScene": MenuScene,
            "GameScene": GameScene,
            "AvatarCreateScene": AvatarCreateScene,
            "PoseEditorScene": PoseEditorScene,
            "TutorialScene": TutorialScene,
        }

    def change_scene(self, scene_name: str):
        """Instantiate and switch to a scene by name from the registry."""
        cls = self.scene_registry.get(scene_name)
        if not cls:
            return

        # call on_exit on current scene if provided
        old_scene = self.scene
        try:
            if old_scene and hasattr(old_scene, "on_exit"):
                old_scene.on_exit()
        except Exception:
            # don't let cleanup errors break scene switching
            pass

        # instantiate new scene
        self.scene = cls(self)

        # call on_enter hook if provided
        try:
            if self.scene and hasattr(self.scene, "on_enter"):
                self.scene.on_enter()
        except Exception:
            # if the new scene fails to initialize hooks, keep running
            pass

    def load_resources(self):
        # Quick sanity-draw so the window is visible immediately on some systems
        try:
            self.screen.fill(BG)
            init_surf = self.title_font.render("Initializing...", True, TITLE)
            self.screen.blit(init_surf, init_surf.get_rect(
                center=(self.WIDTH // 2, self.HEIGHT // 2)))
            pygame.display.flip()
            # small pause to allow window manager to show the window
            pygame.time.delay(250)
        except Exception:
            pass

        run_loading_with_callback(
            surface=self.screen,
            loader=self.res_mgr.load_all,
            on_complete=self.res_mgr.finalize_and_play,
            title="Loading Resources",
            subtitle="Images and audio",
        )

    def run(self):
        # load resources first
        self.load_resources()

        # create initial scene via registry
        self.change_scene("MenuScene")

        # main loop
        print('[DEBUG] Application.run: start main loop')
        while self.running:
            # print(f'[DEBUG] Application.run: self.running={self.running}')
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('[DEBUG] Application.run: received pygame.QUIT')
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print('[DEBUG] Application.run: received ESC')
                    self.running = False
                else:
                    if self.scene:
                        # print(f'[DEBUG] Application.run: passing event {event} to scene.handle_event')
                        self.scene.handle_event(event)

            # 只在 running 為 True 時更新場景
            if self.running and self.scene:
                self.scene.update(dt)

            if self.scene:
                self.scene.render()

            pygame.display.flip()

        # clean shutdown
        pygame.quit()
        # Return instead of sys.exit() so stack traces and prints remain visible
        # when running from an interactive shell or debugger.
        return


def main():
    app = Application()
    try:
        app.run()
    except Exception:
        # Ensure any unexpected exceptions are printed to the console for debugging
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
