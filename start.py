
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
from utils.ui import draw_button
from utils.resource_manager import ResourceManager


def main():
	pygame.init()
	WIDTH, HEIGHT = 1600, 900
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("2MB - Menu")

	clock = pygame.time.Clock()
	font = pygame.font.SysFont(None, 48)
	title_font = pygame.font.SysFont(None, 72)

	# Start loading background music immediately (before showing menu)
	# Prepare resources to load: background and button images
	# TO-DO(Qianrina): please upload the image assets to the repo
	images = {
		"background": os.path.join("assets", "images", "background.png"),
		"btn_start": os.path.join("assets", "images", "button_start.png"),
		"btn_quit": os.path.join("assets", "images", "button_quit.png"),
	}

	res_mgr = ResourceManager(images=images, image_base_dir=None, audio_path=None)

	# Run combined loader (images + audio) with the loading UI
	run_loading_with_callback(
		surface=pygame.display.get_surface(),
		loader=res_mgr.load_all,
		on_complete=res_mgr.play_music,
		title="Loading Resources",
		subtitle="Images and audio",
	)

	# Button sizes and positions
    # TO-DO(Qianrina): please update the button sizes and positions if needed
	btn_w, btn_h = 260, 96
	center_x = WIDTH // 2
	center_y = HEIGHT // 2

	start_rect = pygame.Rect(center_x - btn_w - 20, center_y, btn_w, btn_h)
	quit_rect = pygame.Rect(center_x + 20, center_y, btn_w, btn_h)

	base_color = START_BASE
	hover_color = START_HOVER

	running = True
	started = False

	while running:
		mouse_pos = pygame.mouse.get_pos()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if start_rect.collidepoint(event.pos):
					started = True
				elif quit_rect.collidepoint(event.pos):
					running = False

		# draw
		screen.fill(BG)

		# title
		title_surf = title_font.render("Main Menu", True, TITLE)
		title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
		screen.blit(title_surf, title_rect)

		# draw using loaded images if available, fallback to drawn buttons
		bg_image = res_mgr.get_image("background")
		if bg_image:
			scaled = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))
			screen.blit(scaled, (0, 0))
		else:
			screen.fill(BG)

		start_img = res_mgr.get_image("btn_start")
		quit_img = res_mgr.get_image("btn_quit")

		if start_img:
			img_rect = start_img.get_rect(center=start_rect.center)
			screen.blit(start_img, img_rect)
		else:
			draw_button(screen, start_rect, "Start", font, base_color, hover_color, mouse_pos)

		if quit_img:
			img_rect = quit_img.get_rect(center=quit_rect.center)
			screen.blit(quit_img, img_rect)
		else:
			draw_button(screen, quit_rect, "Quit", font, QUIT_BASE, QUIT_HOVER, mouse_pos)

		if started:
			status_surf = font.render("Started!", True, STATUS)
			status_rect = status_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))
			screen.blit(status_surf, status_rect)



		pygame.display.flip()
		clock.tick(60)

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()

