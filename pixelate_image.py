"""
Pixelate Image Tool
Converts any image into 8-bit pixel art style
"""
import pygame
import sys
from pathlib import Path


def pixelate_image(input_path, output_path, pixel_size=8, palette_size=16):
    """
    Convert an image to pixel art style

    Args:
        input_path: Path to input image
        output_path: Path to save pixelated image
        pixel_size: Size of each pixel block (default: 8)
        palette_size: Number of colors to reduce to (default: 16)
    """
    # Load image
    image = pygame.image.load(input_path)
    width, height = image.get_size()

    # Calculate new dimensions (must be divisible by pixel_size)
    new_width = (width // pixel_size) * pixel_size
    new_height = (height // pixel_size) * pixel_size

    # Resize if needed
    if new_width != width or new_height != height:
        image = pygame.transform.scale(image, (new_width, new_height))

    # Create smaller version
    small_width = new_width // pixel_size
    small_height = new_height // pixel_size
    small_image = pygame.transform.scale(image, (small_width, small_height))

    # Reduce colors (posterize effect)
    small_surface = small_image.copy()
    for x in range(small_width):
        for y in range(small_height):
            color = small_surface.get_at((x, y))
            # Reduce each color channel
            r = (color.r // (256 // palette_size)) * (256 // palette_size)
            g = (color.g // (256 // palette_size)) * (256 // palette_size)
            b = (color.b // (256 // palette_size)) * (256 // palette_size)
            small_surface.set_at((x, y), (r, g, b, color.a))

    # Scale back up (nearest neighbor for sharp pixels)
    pixelated = pygame.transform.scale(small_surface, (new_width, new_height))

    # Save result
    pygame.image.save(pixelated, output_path)
    print(f"✓ Pixelated image saved to: {output_path}")
    print(f"  Original size: {width}x{height}")
    print(f"  Pixel size: {pixel_size}x{pixel_size}")
    print(f"  Color palette: {palette_size} colors per channel")

    return pixelated


def show_preview(pixelated_image, original_path):
    """Show before/after comparison"""
    screen = pygame.display.set_mode((1200, 600))
    pygame.display.set_caption("Pixelation Preview - ESC to close")

    original = pygame.image.load(original_path)

    # Scale images to fit
    orig_scaled = pygame.transform.scale(original, (500, 500))
    pixel_scaled = pygame.transform.scale(pixelated_image, (500, 500))

    font = pygame.font.Font(None, 32)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((30, 30, 40))

        # Draw original
        screen.blit(orig_scaled, (50, 80))
        text = font.render("Original", True, (255, 255, 255))
        screen.blit(text, (50, 30))

        # Draw pixelated
        screen.blit(pixel_scaled, (650, 80))
        text = font.render("Pixelated", True, (255, 255, 100))
        screen.blit(text, (650, 30))

        pygame.display.flip()

    pygame.quit()


def main():
    pygame.init()

    print("=" * 60)
    print("8-BIT PIXEL ART CONVERTER")
    print("=" * 60)

    # Get input file
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input(
            "Enter image path (or press Enter for 'sample/tpose.png'): ").strip()
        if not input_path:
            input_path = "sample/tpose.png"

    if not Path(input_path).exists():
        print(f"✗ Error: File not found: {input_path}")
        return

    # Get pixel size
    pixel_input = input("Enter pixel size (4-32, default 8): ").strip()
    pixel_size = int(pixel_input) if pixel_input.isdigit() else 8
    pixel_size = max(4, min(32, pixel_size))

    # Get color palette size
    palette_input = input(
        "Enter color palette size (4-32, default 16): ").strip()
    palette_size = int(palette_input) if palette_input.isdigit() else 16
    palette_size = max(4, min(32, palette_size))

    # Generate output path
    input_file = Path(input_path)
    output_path = input_file.parent / \
        f"{input_file.stem}_pixel{pixel_size}.png"

    print(f"\nProcessing...")
    pixelated = pixelate_image(input_path, str(
        output_path), pixel_size, palette_size)

    # Ask to show preview
    show = input("\nShow preview? (Y/n): ").strip().lower()
    if show != 'n':
        show_preview(pixelated, input_path)

    print(
        f"\n✓ Done! You can now use '{output_path}' in your animation system.")


if __name__ == "__main__":
    main()
