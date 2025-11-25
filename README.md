# 2D Character Animation System

Step in! and the game fights as you!
•	Snap one full body photo—instantly become your own pixel fighter.
•	Your body is the controller
•	Fixed tempo moves for solid feel
•	Drain their health bar to win. The cleaner your moves, the better the detection.
•	After calibration, take your left/right spot—countdown… fight!

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
# 2MB — 2D Character Animation (Pygame)

This repository contains a lightweight 2D skeletal animation system built on Pygame, with a runtime pixel-art post-processing effect, pose management, and several developer tools. The project has recently been reorganized — core modules were moved into a `classes/` package and some legacy files were archived under `archive/unused/` for safety.

This README reflects the current layout and how to run the project from the repo root.

## Quick overview
- Entry point for the active project is `start.py` (menu + scenes).
- The core animation/skeleton code now lives under the `classes/` package.
- Utility modules (loading, resource manager, ui, color, mediapipe capture) are in `utils/`.
- Development tools and older entry scripts were moved to `archive/unused/`.

## Requirements
Install dependencies (recommended in a virtualenv):

```powershell
python -m pip install -r requirements.txt
```

requirements.txt currently lists:
- pygame
- mediapipe
- opencv-python

(If you only want to run the UI/animation without Mediapipe/Opencv features, installing `pygame` alone is sufficient for the basic demo.)

## Run (recommended)
From the repository root (important so package imports resolve correctly):

```powershell
python start.py
```

`start.py` shows a menu and launches the game scene or avatar creation scene. It uses `utils.resource_manager` to load images from `assets/`.

## Alternate: archived `main.py` (legacy)
There is an archived legacy player at `archive/unused/main.py`. It was updated to import from the `classes` package and includes a small `sys.path` shim so you can run it directly:

```powershell
python .\archive\unused\main.py
```

Note: running archived scripts directly may require running from the repo root or accepting the shim that adds the repo root to `sys.path`.

## Controls (game scene)
- 1 / B — Block (auto-return)
- 2 — Ready
- 3 / P — Punch (auto-return)
- 4 / K — Kick (auto-return)
- Space / J — Jump (auto-return)
- 5 / H — Hurt (auto-return + red flash)
- F5 / L — Load custom pose
- F6 — Hot-reload poses
- F7 — Toggle pixelate effect
- [ / ] — Pixel size
- - / + — Palette color count
- ESC — Quit

## Project layout (relevant parts)

```
.
├─ assets/                # images and media
├─ classes/               # core animation modules (animation, skeleton, body_parts, profiles)
├─ utils/                 # helpers: resource_manager, loading, ui, color, mediapipe_capture
├─ tools/                 # (some tools may have been archived) dev helpers and editors
├─ archive/unused/        # archived legacy scripts (safe to inspect/restore)
├─ start.py               # application + scene registry (recommended entrypoint)
├─ menu_scene.py
├─ game_scene.py
├─ avatar_create.py
├─ requirements.txt
└─ README.md
```

## Recent refactor notes
- The core modules `animation.py`, `skeleton.py`, `body_parts.py`, and `body_parts_profiles.py` were moved into `classes/` and imports across the project were updated to use `classes.*`.
- A compatibility shim (`BodyPartsConfig`) was added to `classes/body_parts_profiles.py` so the AnimatedCharacter can still slice T-pose surfaces even when explicit metadata is missing.
- Some older files (e.g., the original `main.py`, `launcher.py`, and some tools) were moved to `archive/unused/` rather than deleted so you can restore them if needed.


## Developer notes
- The repository keeps archived copies under `archive/unused/` when files are removed from the active runtime — this is a safety-first choice.
- If you plan to restructure further, prefer absolute package imports (e.g., `from classes.skeleton import Skeleton`) and run from repo root to avoid import-time surprises.

## Running tests / quick checks
- Quick import check (no UI):

```powershell
python -c "import sys; sys.path.insert(0, r'..\2MB'); import start; print('start imported')"
```

## License
MIT

## Contact / Repo
https://github.com/Bismarck-KL/2MB
