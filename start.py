
import sys
import pygame
import time
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
from utils.game_sound_loader import BackgroundMusicLoader


def main():
	pygame.init()
	WIDTH, HEIGHT = 1600, 900
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("2MB - Menu")

	clock = pygame.time.Clock()
	font = pygame.font.SysFont(None, 48)
	title_font = pygame.font.SysFont(None, 72)

	# Start loading background music immediately (before showing menu)
	bg_loader = BackgroundMusicLoader()

	# Run loader with UI. This blocks here until loading finishes, but keeps UI responsive.
	run_loading_with_callback(
		surface=pygame.display.get_surface(),
		loader=bg_loader.load,
		on_complete=bg_loader.play,
		title="Loading Music",
		subtitle="Loading background music...",
	)

	# Button sizes and positions
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

		draw_button(screen, start_rect, "Start", font, base_color, hover_color, mouse_pos)
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

