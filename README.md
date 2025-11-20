# 2D Character Animation System

Pygame-based 2D skeletal animation system with real-time pixel art effects and dynamic pose switching.

## Features

- ✅ **Skeletal Animation**: Hierarchical parent-child body part system with smooth transitions
- ✅ **Real-time Pixel Art**: Post-process pixelate effect with adjustable parameters
- ✅ **Multiple Poses**: T-pose, Ready, Block, Punch, Kick, Jump, Hurt (with damage flash)
- ✅ **Action System**: Auto-return actions with configurable durations
- ✅ **Hot-Reload**: Press F6 to reload poses without restarting (F5 for custom poses)
- ✅ **Development Tools**: Pose editor, proportion adjuster, style configurator

## Quick Start

```bash
# Install dependencies
pip install pygame

# Run main animation player
python main.py
```

## Controls

### Pose Switching
- **1** or **B** - Block pose (auto-return)
- **2** - Ready pose (battle stance)
- **3** or **P** - Punch action (auto-return)
- **4** or **K** - Kick action (auto-return)
- **Space** or **J** - Jump action (auto-return)
- **5** or **H** - Hurt action (damage flash, auto-return)
- **F5** or **L** - Load custom pose
- **F6** - Hot-reload all poses

### Pixel Art Controls
- **F7** - Toggle pixelate effect on/off
- **[** / **]** - Decrease/Increase pixel size (2-16)
- **-** / **+** - Decrease/Increase color palette (4-32)

### General
- **ESC** - Quit

## 🎨 Pixel Art System

Real-time post-processing pixelate effect with:
- **Adjustable Pixel Size**: Downscale factor from 2x to 16x
- **Color Palette Reduction**: Limit colors from 4 to 32 for authentic retro look
- **Dominant Color Extraction**: Automatic palette generation from rendered frame
- **No Pre-processing Required**: Works on any character image dynamically

## Project Structure

```
motion test_3/
├── main.py                    # Main animation player with integrated pixel art
├── animation.py               # Animation controller and pose definitions
├── skeleton.py                # Skeletal system with transforms
├── body_parts.py              # Body part slicing and rendering
├── body_parts_config.json     # Body part proportion settings
├── poses_all.json             # Unified pose storage (all 8 poses)
├── update_animation.py        # Helper for pose tool
├── main_backup.py             # Backup before pixel art integration
├── assets/
│   └── photo/
│       └── tpose.png          # Character T-pose image
├── sample/                    # Reference images and test files
├── tools/                     # Development and adjustment tools
│   ├── README.md              # Tool documentation
│   ├── pose_tool.py           # Interactive pose editor
│   ├── adjust_tool.py         # Body proportion adjuster
│   ├── style_config.py        # Pixel art style configurator
│   ├── auto_watch.py          # File change watcher
│   └── compare_images.py     # Visual comparison tool
└── README.md                  # This file
```

## Development Tools

All development tools are located in the `tools/` directory. See `tools/README.md` for detailed documentation.

### Pose Editor
```bash
python tools/pose_tool.py
```
Interactive visual editor for creating and modifying character poses. Changes are saved to `poses_all.json` and can be hot-reloaded with F6.

### Proportion Adjuster
```bash
python tools/adjust_tool.py
```
Adjust body part lengths and proportions in real-time. Saves to `body_parts_config.json`.

## 如何替换角色

### 方法1：修改默认图片
直接替换 `sample/tpose.png` 文件，保持相同的文件名。

## Technical Details

### Skeletal Hierarchy
```
Torso (root)
├── Head
├── Left Upper Arm
│   └── Left Forearm
├── Right Upper Arm
│   └── Right Forearm
├── Left Thigh
│   └── Left Calf
└── Right Thigh
    └── Right Calf
```

### Coordinate System
- Parent-child hierarchical transforms
- Each part has local and world coordinates
- Rotation based on customizable pivot points

### Animation System
- Linear interpolation (LERP) for smooth transitions
- Ease-out function for natural movement
- Configurable transition speed

### Pixel Art Implementation
- **Method B (Post-Processing)**: Entire rendered frame is pixelated
- **Dominant Color Extraction**: k-means clustering on rendered pixels
- **Nearest Color Mapping**: Color quantization to extracted palette
- **Downscale → Quantize → Upscale**: Three-step process for authentic look

## Troubleshooting

### Character not displaying correctly
- Check image path in `body_parts.py`
- Verify slice coordinates match your image dimensions
- Use `tools/adjust_tool.py` to adjust proportions

### Actions feel unnatural
- Adjust pose rotations in `poses_all.json`
- Use `tools/pose_tool.py` for visual editing
- Modify `transition_speed` in `animation.py`

### Pixel art looks wrong
- Press F7 to toggle effect on/off
- Adjust pixel size with [] keys (try 8 for classic look)
- Adjust color count with -+ keys (try 16 for retro feel)

## License

MIT License

## Credits

- Animation System: Skeletal animation with Pygame
- Pixel Art System: Post-process pixelate effect
- GitHub: https://github.com/Bismarck-KL/2MB
