
import sys
import pygame
import time
import os
# Import color constants
from utils.color import (
	BG,
	TITLE,
	START_BASE,
	START_HOVER,
	QUIT_BASE,
	QUIT_HOVER,
	STATUS,
)
# Import utility functions
from utils.loading import draw_loading_screen, run_loading_with_callback
from utils.ui import draw_button, Button
from utils.resource_manager import ResourceManager


def main():
	pygame.init()
	WIDTH, HEIGHT = 1600, 900
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("2MB - Menu")

	clock = pygame.time.Clock()
	font = pygame.font.SysFont(None, 48)
	title_font = pygame.font.SysFont(None, 72)

	# Resource loading is handled by the Application class below.
class MenuScene:
	def __init__(self, app):
		self.app = app
		self.screen = app.screen
		self.font = app.font
		self.title_font = app.title_font
		self.res_mgr = app.res_mgr

		# button layout
		btn_w, btn_h = 260, 96
		center_x = app.WIDTH // 2
		center_y = app.HEIGHT // 2

		self.start_rect = pygame.Rect(center_x - btn_w - 20, center_y, btn_w, btn_h)
		self.quit_rect = pygame.Rect(center_x + 20, center_y, btn_w, btn_h)

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

		self.start_button = Button(self.start_rect, text="Start", font=self.font,
								   base_color=START_BASE, hover_color=START_HOVER, image=start_img)
		self.quit_button = Button(self.quit_rect, text="Quit", font=self.font,
								  base_color=QUIT_BASE, hover_color=QUIT_HOVER, image=quit_img)

		self.started = False

	def handle_event(self, event):
		if self.start_button.handle_event(event):
			# switch to game scene when Start is clicked
			self.app.scene = GameScene(self.app)
		if self.quit_button.handle_event(event):
			self.app.running = False

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

		if self.started:
			status_surf = self.font.render("Started!", True, STATUS)
			status_rect = status_surf.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2 + 140))
			self.screen.blit(status_surf, status_rect)



class GameScene:
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
		txt = self.title_font.render("Game Scene", True, TITLE)
		rect = txt.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
		self.screen.blit(txt, rect)



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

		# resources
		images = {
			"background": os.path.join("assets", "images", "background.png"),
			"btn_start": os.path.join("assets", "images", "button_start.png"),
			"btn_quit": os.path.join("assets", "images", "button_quit.png"),
		}
		self.res_mgr = ResourceManager(images=images, image_base_dir=None, audio_path=None)

		self.running = True
		self.scene = None

	def load_resources(self):
		print("[startup] load_resources() begin")
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
		print("[startup] load_resources() end")

	def run(self):
		print("[app] run() starting")
		# load resources first
		self.load_resources()
		print("[app] load_resources() returned")

		# create initial scene
		self.scene = MenuScene(self)

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

		print("[app] quitting")
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

