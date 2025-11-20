"""
Pixel Art Comparison Viewer
Shows side-by-side comparison of original and pixelated images
"""
import pygame
import sys
from pathlib import Path


def show_comparison(original_path, pixelated_path):
    """Display side-by-side comparison"""
    pygame.init()

    # Load images
    try:
        original = pygame.image.load(original_path)
        pixelated = pygame.image.load(pixelated_path)
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    # Setup display
    screen_width = 1400
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pixel Art Comparison - ESC to close")

    # Fonts
    title_font = pygame.font.Font(None, 48)
    info_font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 20)

    # Calculate scaling to fit
    max_width = 600
    max_height = 650

    orig_size = original.get_size()
    pixel_size = pixelated.get_size()

    # Scale original
    orig_scale = min(max_width / orig_size[0], max_height / orig_size[1])
    orig_display = pygame.transform.scale(
        original,
        (int(orig_size[0] * orig_scale), int(orig_size[1] * orig_scale))
    )

    # Scale pixelated (use nearest neighbor to preserve pixels)
    pixel_scale = min(max_width / pixel_size[0], max_height / pixel_size[1])
    pixel_display = pygame.transform.scale(
        pixelated,
        (int(pixel_size[0] * pixel_scale), int(pixel_size[1] * pixel_scale))
    )

    # Positions
    orig_x = 50
    pixel_x = screen_width // 2 + 50
    y_pos = 120

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen
        screen.fill((25, 30, 40))

        # Title
        title = title_font.render(
            "Pixel Art Comparison", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen_width // 2, 40))
        screen.blit(title, title_rect)

        # Draw borders
        pygame.draw.rect(screen, (60, 70, 80),
                         (orig_x - 5, y_pos - 5,
                         orig_display.get_width() + 10,
                         orig_display.get_height() + 10), 2)
        pygame.draw.rect(screen, (60, 70, 80),
                         (pixel_x - 5, y_pos - 5,
                         pixel_display.get_width() + 10,
                         pixel_display.get_height() + 10), 2)

        # Draw images
        screen.blit(orig_display, (orig_x, y_pos))
        screen.blit(pixel_display, (pixel_x, y_pos))

        # Labels
        orig_label = info_font.render("ORIGINAL", True, (200, 200, 200))
        pixel_label = info_font.render("PIXELATED", True, (255, 220, 100))

        screen.blit(orig_label, (orig_x, y_pos - 35))
        screen.blit(pixel_label, (pixel_x, y_pos - 35))

        # Info text
        info_y = y_pos + max(orig_display.get_height(),
                             pixel_display.get_height()) + 20

        # Original info
        orig_info = [
            f"Size: {orig_size[0]}x{orig_size[1]}",
            f"File: {Path(original_path).name}"
        ]
        for i, text in enumerate(orig_info):
            surface = small_font.render(text, True, (180, 180, 180))
            screen.blit(surface, (orig_x, info_y + i * 22))

        # Pixelated info
        pixel_info = [
            f"Size: {pixel_size[0]}x{pixel_size[1]}",
            f"File: {Path(pixelated_path).name}",
            f"Style: 8-bit pixel art"
        ]
        for i, text in enumerate(pixel_info):
            surface = small_font.render(text, True, (180, 180, 180))
            screen.blit(surface, (pixel_x, info_y + i * 22))

        # Instructions
        inst = small_font.render("Press ESC to close", True, (150, 150, 150))
        inst_rect = inst.get_rect(
            center=(screen_width // 2, screen_height - 30))
        screen.blit(inst, inst_rect)

        # Zoom indicator
        zoom_text = f"Zoom: {orig_scale:.2f}x / {pixel_scale:.2f}x"
        zoom_surf = small_font.render(zoom_text, True, (120, 120, 120))
        screen.blit(zoom_surf, (10, screen_height - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main():
    print("=" * 70)
    print("PIXEL ART COMPARISON VIEWER")
    print("=" * 70)

    # Default paths
    original = "sample/tpose.png"
    pixelated = "sample/tpose_8bit.png"

    # Check if files exist
    if not Path(original).exists():
        print(f"✗ Original image not found: {original}")
        return

    if not Path(pixelated).exists():
        print(f"✗ Pixelated image not found: {pixelated}")
        print("\nRun 'python pixelate_advanced.py' first to create pixelated version!")
        return

    print(f"\nOriginal:  {original}")
    print(f"Pixelated: {pixelated}")
    print("\nLaunching comparison viewer...")

    show_comparison(original, pixelated)

    print("\n✓ Viewer closed.")


if __name__ == "__main__":
    main()
