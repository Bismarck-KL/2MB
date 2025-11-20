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


class Application:
	def __init__(self, width=1600, height=900):
		pygame.init()
		self.WIDTH = width
		self.HEIGHT = height
		self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
		pygame.display.set_caption("2MB - Menu")

		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont(None, 48)
		self.title_font = pygame.font.SysFont(None, 72)

        # TO-DO(Qianrina): upload the resources with correct paths
		# resources
		images = {
			"background": os.path.join("assets", "images", "background.png"),
			"btn_start": os.path.join("assets", "images", "button_start.png"),
			"btn_quit": os.path.join("assets", "images", "button_quit.png"),
		}
		self.res_mgr = ResourceManager(images=images, image_base_dir=None, audio_path=None)

		self.running = True
		self.scene = None
		# register scene classes here so Application controls creation
		self.scene_registry = {
			"MenuScene": MenuScene,
			"GameScene": GameScene,
			"AvatarCreateScene": AvatarCreateScene,
		}

	def change_scene(self, scene_name: str):
		"""Instantiate and switch to a scene by name from the registry."""
		cls = self.scene_registry.get(scene_name)
		if not cls:
			return
		self.scene = cls(self)

	def load_resources(self):
		# Quick sanity-draw so the window is visible immediately on some systems
		try:
			self.screen.fill(BG)
			init_surf = self.title_font.render("Initializing...", True, TITLE)
			self.screen.blit(init_surf, init_surf.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
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
		while self.running:
			dt = self.clock.tick(60) / 1000.0

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					self.running = False
				else:
					if self.scene:
						self.scene.handle_event(event)

			if self.scene:
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

