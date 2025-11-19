"""
Advanced Pixel Art Converter
Creates 8-bit style pixel art with outline and optimized palette
"""
import pygame
import sys
from pathlib import Path
from collections import Counter


def get_dominant_colors(surface, num_colors=16):
    """Extract dominant colors from image"""
    width, height = surface.get_size()
    colors = []
    
    # Sample pixels
    for x in range(0, width, max(1, width // 100)):
        for y in range(0, height, max(1, height // 100)):
            color = surface.get_at((x, y))
            if color.a > 128:  # Skip transparent
                colors.append((color.r, color.g, color.b))
    
    # Count and get most common
    color_counter = Counter(colors)
    return [c for c, _ in color_counter.most_common(num_colors)]


def find_nearest_color(color, palette):
    """Find closest color in palette"""
    r, g, b = color[:3]
    min_dist = float('inf')
    nearest = palette[0]
    
    for pr, pg, pb in palette:
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest = (pr, pg, pb)
    
    return nearest


def add_outline(surface, outline_color=(0, 0, 0), thickness=1):
    """Add black outline around non-transparent pixels"""
    width, height = surface.get_size()
    outlined = surface.copy()
    
    # Check each pixel
    for x in range(width):
        for y in range(height):
            pixel = surface.get_at((x, y))
            
            # If pixel is transparent, check if it should be outline
            if pixel.a < 128:
                # Check neighbors
                should_outline = False
                for dx in range(-thickness, thickness + 1):
                    for dy in range(-thickness, thickness + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor = surface.get_at((nx, ny))
                            if neighbor.a >= 128:  # Non-transparent neighbor
                                should_outline = True
                                break
                    if should_outline:
                        break
                
                if should_outline:
                    outlined.set_at((x, y), (*outline_color, 255))
    
    return outlined


def pixelate_advanced(input_path, output_path, pixel_size=8, num_colors=16, 
                     add_outline_effect=True, dither=False):
    """
    Advanced pixelation with palette optimization
    
    Args:
        input_path: Path to input image
        output_path: Path to save result
        pixel_size: Pixel block size
        num_colors: Number of colors in palette
        add_outline_effect: Add black outline
        dither: Apply dithering for smoother gradients
    """
    print(f"Loading image: {input_path}")
    image = pygame.image.load(input_path)
    width, height = image.get_size()
    
    # Calculate new dimensions
    new_width = (width // pixel_size) * pixel_size
    new_height = (height // pixel_size) * pixel_size
    
    if new_width != width or new_height != height:
        image = pygame.transform.scale(image, (new_width, new_height))
        print(f"Resized to: {new_width}x{new_height}")
    
    # Downscale
    small_width = new_width // pixel_size
    small_height = new_height // pixel_size
    small_image = pygame.transform.scale(image, (small_width, small_height))
    
    print(f"Extracting color palette ({num_colors} colors)...")
    # Get dominant colors for palette
    palette = get_dominant_colors(small_image, num_colors)
    
    # Apply palette to small image
    print("Applying palette...")
    small_surface = small_image.copy()
    for x in range(small_width):
        for y in range(small_height):
            color = small_surface.get_at((x, y))
            if color.a > 128:  # Only process non-transparent
                nearest = find_nearest_color(color, palette)
                small_surface.set_at((x, y), (*nearest, color.a))
    
    # Optional dithering (simple ordered dithering)
    if dither:
        print("Applying dithering...")
        dither_matrix = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]
        
        for x in range(small_width):
            for y in range(small_height):
                color = small_surface.get_at((x, y))
                if color.a > 128:
                    threshold = dither_matrix[y % 4][x % 4] * 16
                    r = min(255, color.r + (threshold - 128) // 4)
                    g = min(255, color.g + (threshold - 128) // 4)
                    b = min(255, color.b + (threshold - 128) // 4)
                    nearest = find_nearest_color((r, g, b), palette)
                    small_surface.set_at((x, y), (*nearest, color.a))
    
    # Scale back up
    print("Scaling up...")
    pixelated = pygame.transform.scale(small_surface, (new_width, new_height))
    
    # Add outline
    if add_outline_effect:
        print("Adding outline...")
        pixelated = add_outline(pixelated)
    
    # Save
    pygame.image.save(pixelated, output_path)
    print(f"✓ Saved to: {output_path}")
    print(f"  Pixel size: {pixel_size}x{pixel_size}")
    print(f"  Colors: {len(palette)}")
    print(f"  Outline: {'Yes' if add_outline_effect else 'No'}")
    print(f"  Dithering: {'Yes' if dither else 'No'}")
    
    # Show palette
    print("\nColor Palette:")
    for i, (r, g, b) in enumerate(palette[:8]):
        print(f"  Color {i+1}: RGB({r:3d}, {g:3d}, {b:3d})")
    if len(palette) > 8:
        print(f"  ... and {len(palette) - 8} more colors")
    
    return pixelated


def interactive_mode():
    """Interactive configuration mode"""
    pygame.init()
    
    print("=" * 70)
    print("ADVANCED 8-BIT PIXEL ART CONVERTER")
    print("=" * 70)
    
    # Get input
    input_path = input("\nImage path (default: sample/tpose.png): ").strip()
    if not input_path:
        input_path = "sample/tpose.png"
    
    if not Path(input_path).exists():
        print(f"✗ File not found: {input_path}")
        return
    
    print("\n--- STYLE OPTIONS ---")
    print("1. Classic 8-bit (pixel:8, colors:16, outline)")
    print("2. Retro 16-bit (pixel:4, colors:32, outline)")
    print("3. Chunky pixel (pixel:16, colors:12, outline)")
    print("4. Custom settings")
    
    choice = input("\nSelect style (1-4): ").strip()
    
    if choice == "1":
        pixel_size, num_colors, outline = 8, 16, True
        style_name = "8bit"
    elif choice == "2":
        pixel_size, num_colors, outline = 4, 32, True
        style_name = "16bit"
    elif choice == "3":
        pixel_size, num_colors, outline = 16, 12, True
        style_name = "chunky"
    else:
        pixel_size = int(input("Pixel size (4-32): ") or "8")
        num_colors = int(input("Number of colors (4-64): ") or "16")
        outline = input("Add outline? (Y/n): ").lower() != 'n'
        style_name = "custom"
    
    dither = input("Apply dithering? (y/N): ").lower() == 'y'
    
    # Generate output path
    input_file = Path(input_path)
    output_path = input_file.parent / f"{input_file.stem}_{style_name}.png"
    
    print(f"\n{'='*70}")
    print("PROCESSING...")
    print(f"{'='*70}\n")
    
    pixelated = pixelate_advanced(
        input_path, 
        str(output_path),
        pixel_size=pixel_size,
        num_colors=num_colors,
        add_outline_effect=outline,
        dither=dither
    )
    
    print(f"\n{'='*70}")
    print("✓ CONVERSION COMPLETE!")
    print(f"{'='*70}")
    print(f"\nOutput file: {output_path}")
    print(f"\nYou can now use this in your animation system by:")
    print(f"  1. Copy to sample/ folder")
    print(f"  2. Edit main.py to use this image")
    print(f"  3. Or let main.py auto-detect pixel versions")


if __name__ == "__main__":
    interactive_mode()
