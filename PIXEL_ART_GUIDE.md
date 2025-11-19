# 🎨 Pixel Art Conversion Guide

## Overview

Transform any character image into retro 8-bit pixel art style with automatic color palette optimization, outlines, and dithering support.

## Quick Start

### Option 1: Interactive Mode (Recommended)
```bash
python pixelate_advanced.py
```
Follow the prompts to select style and options.

### Option 2: Simple Pixelation
```bash
python pixelate_image.py
```
Basic pixelation without advanced features.

### Option 3: Quick Demo
```bash
python demo.py
```
Automatically creates pixel art and launches the animation system.

## Style Presets

### 1. Classic 8-bit (Recommended) 🌟
- **Pixel Size:** 8x8
- **Colors:** 16 per channel
- **Outline:** Yes
- **Best For:** Mario, Zelda, retro NES style
- **Output:** `tpose_8bit.png`

**Example:**
```bash
python pixelate_advanced.py
# Enter: sample/tpose.png
# Select: 1 (Classic 8-bit)
# Dithering: n (no)
```

### 2. Retro 16-bit
- **Pixel Size:** 4x4
- **Colors:** 32 per channel
- **Outline:** Yes
- **Best For:** SNES, Mega Drive style
- **Output:** `tpose_16bit.png`

### 3. Chunky Pixel
- **Pixel Size:** 16x16
- **Colors:** 12 per channel
- **Outline:** Yes
- **Best For:** Bold, high-contrast art
- **Output:** `tpose_chunky.png`

### 4. Custom Settings
Configure your own pixel size, color count, and effects.

## Advanced Features

### Color Palette Optimization
The tool automatically extracts dominant colors from your image and reduces the palette intelligently:

```python
# Extracts top 16 most common colors
# Maps each pixel to nearest palette color
# Preserves alpha channel for transparency
```

### Outline Generation
Adds black borders around character edges for clarity:
- **Thickness:** 1 pixel (configurable)
- **Color:** Black (default, can be changed in code)
- **Detection:** Automatically finds edges

### Dithering
Optional ordered dithering for smoother color transitions:
- **Type:** 4x4 Bayer matrix
- **Effect:** Reduces color banding
- **Use Case:** Complex gradients

**Enable dithering:**
```bash
python pixelate_advanced.py
# ... (follow prompts)
# Dithering: y (yes)
```

## Comparison Tool

View before/after side-by-side:
```bash
python compare_images.py
```

Shows:
- Original image (left)
- Pixelated version (right)
- Size information
- Zoom levels

**Controls:**
- ESC - Close viewer

## Integration with Animation System

### Automatic Detection
The main animation system automatically detects and uses pixelated versions:

```bash
python main.py
# Output: "✓ Using pixelated image: sample/tpose_8bit.png"
```

Detection priority (uses first found):
1. `tpose_8bit.png`
2. `tpose_16bit.png`
3. `tpose_chunky.png`
4. `tpose_custom.png`
5. `tpose_pixel8.png` (from simple tool)
6. Falls back to `tpose.png`

### Manual Selection
Edit `main.py` to use specific image:
```python
game = CharacterAnimator("sample/tpose_8bit.png")
```

## File Outputs

### Naming Convention
- Original: `tpose.png`
- 8-bit style: `tpose_8bit.png`
- 16-bit style: `tpose_16bit.png`
- Chunky: `tpose_chunky.png`
- Custom: `tpose_custom.png`

### Location
All outputs saved to `sample/` directory by default.

## Tips & Tricks

### Getting Best Results

1. **Input Image Quality**
   - Use high-resolution source (at least 512x512)
   - Clear, well-lit character
   - Simple background or transparent PNG

2. **Pixel Size Selection**
   - Small character → Use 4-6 pixel size
   - Medium character → Use 8-12 pixel size
   - Large character → Use 16+ pixel size

3. **Color Count**
   - Fewer colors (8-16) → More retro
   - More colors (24-32) → More detailed
   - Too few (<8) → May lose detail

4. **Outline**
   - Always recommended for clarity
   - Helps distinguish character from background
   - Makes animations more readable

5. **Dithering**
   - Use for complex color gradients
   - Skip for flat-color characters
   - May add noise to simple designs

### Common Issues

**Problem:** Output looks blurry
- **Solution:** Ensure pixel size divides image dimensions evenly
- **Fix:** Image is auto-resized, but manual preprocessing may help

**Problem:** Too many colors, not pixelated enough
- **Solution:** Reduce color count (try 8-12 colors)
- **Fix:** Increase pixel size (try 12-16)

**Problem:** Lost detail
- **Solution:** Decrease pixel size or increase color count
- **Balance:** Find sweet spot between retro look and detail

**Problem:** Outline too thick/thin
- **Solution:** Edit `add_outline()` function in `pixelate_advanced.py`
- **Parameter:** Change `thickness=1` to desired value

## Code Customization

### Change Outline Color
Edit `pixelate_advanced.py`:
```python
def add_outline(surface, outline_color=(255, 0, 0), thickness=1):
    # Red outline instead of black
```

### Adjust Dither Strength
Edit dither matrix values:
```python
# Weaker dithering (divide by 8 instead of 4)
threshold = dither_matrix[y % 4][x % 4] * 16
r = min(255, color.r + (threshold - 128) // 8)
```

### Create New Preset
Add to `interactive_mode()` in `pixelate_advanced.py`:
```python
elif choice == "5":
    pixel_size, num_colors, outline = 6, 20, True
    style_name = "mypreset"
```

## Batch Processing

Process multiple images:
```python
# Create batch_pixelate.py
import os
from pixelate_advanced import pixelate_advanced

images = ["char1.png", "char2.png", "char3.png"]
for img in images:
    pixelate_advanced(
        f"sample/{img}",
        f"sample/{img.replace('.png', '_8bit.png')}",
        pixel_size=8,
        num_colors=16,
        add_outline_effect=True
    )
```

## Performance Notes

- **Processing Time:** ~1-3 seconds for typical 1024x720 image
- **Memory Usage:** ~50-100 MB during processing
- **Output Size:** Usually smaller than input (optimized palette)

## Examples Gallery

### Before → After

**Original Character (1024x720)**
- Full color, smooth gradients
- 24-bit color depth
- ~500 KB file size

**8-bit Pixelated (1024x720)**
- 8x8 pixel blocks
- 16 color palette
- Black outline
- ~200 KB file size
- Retro aesthetic

## Workflow Integration

### Complete Pipeline

```bash
# 1. Create/prepare character image
# (Use any image editor, save as PNG)

# 2. Convert to pixel art
python pixelate_advanced.py
# Select: sample/mychar.png
# Choose: Style 1 (8-bit)

# 3. Update body part definitions
# Edit body_parts.py if needed

# 4. Test with animation system
python main.py

# 5. Fine-tune poses
python pose_tool.py

# 6. Compare results
python compare_images.py
```

## Resources

- **Pixel Art Tutorials:** [Lospec](https://lospec.com/pixel-art-tutorials)
- **Color Palettes:** [Lospec Palette List](https://lospec.com/palette-list)
- **Sprite References:** [OpenGameArt](https://opengameart.org)

## Support

If you encounter issues:
1. Check image file exists and is valid PNG
2. Verify Python 3.7+ and pygame installed
3. Try different pixel size/color combinations
4. Review error messages in console

---

**Created for 2D Character Animation System**
*Transform your characters into retro pixel art masterpieces! 🎮*
