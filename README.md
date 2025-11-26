# 2MB — 2D Character Animation

Step in! and the game fights as you!
•	Snap one full body photo—instantly become your own pixel fighter.
•	Your body is the controller
•	Fixed tempo moves for solid feel
•	Drain their health bar to win. The cleaner your moves, the better the detection.
•	After calibration, take your left/right spot—countdown… fight!

## Quick summary

- Languages: Python 3
- Main library: pygame, OpenCV
- Entry point / menu: `start.py` — run this to pick a mode and start the game
- The core animation/skeleton code now lives under the `classes/` package.
- Utility modules (loading, resource manager, ui, color, mediapipe capture) are in `utils/`.
- Development tools and older entry scripts were moved to `archive/unused/`.

## Features

- ✅ Skeletal animation — hierarchical parent/child body-part system with pose interpolation and smooth transitions.
- ✅ Real-time pixel-art post-processing — optional pixelation filter applied to the game view.
- ✅ Multiple animation poses — built-in poses (T-pose, Ready, Punch, Kick, Jump, Block, Hurt) with data-driven pose definitions (JSON).
- ✅ Action system — time-limited actions with auto-return behavior and configurable durations.
- ✅ Tutorial playback — animated tutorial assets supported via OpenCV-based GIF playback (optional; falls back to a static image when OpenCV is not installed).
- ✅ Camera-based action detection (optional) — Mediapipe-based landmark capture with an ActionDetector that maps poses to in-game actions (jump, punch, kick, block).
- ✅ HUD and round system — player health bars, round timer, and on-screen detected-action indicators.
- ✅ Hot-reload (developer) — reload pose/asset changes during development (keybindings depend on the runtime environment).
- ✅ Developer tools — pose editor, proportion adjuster, and style configurator to tweak avatars and animations.

## Requirements / Dependencies

- Python 3.x < 3.10 
- Required libraries:
  - `pygame`
  - `mediapipe`
  - `opencv-python`
  - `numpy`    

## Installation

1. Install Python 3.8+ (3.10 recommended).
2. (Optional) Create and activate a virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Running the game

From the project directory run the menu script (recommended):

```powershell
python start.py
```

## Controls

Below are the controls used by the default `GameScene` implementation (exact mappings are taken from `game_scene.py`).

- General
  - ESC: return to the Menu (pressing Escape while in the game switches to the menu scene).
  - Back (top-left UI button): click with the mouse to return to the Menu.
  - When the round ends / game over: press SPACE to restart the match.

- Player controls (local keyboard)
  - Player 1 (left side):
    - 1 — Jump
    - 2 — Punch
    - 3 — Kick
    - 4 — Block
  - Player 2 (right side):
    - Q — Jump
    - W — Punch
    - E — Kick
    - R — Block

- Camera / action-detection (optional)
  - If the Mediapipe camera / ActionDetector is enabled, detected actions map directly to in-game triggers for the corresponding player: jump, punch, kick, block.
    - punch to close attack
    - kick to long reach
    - jump to move forward
    - cross arms to block
  - Camera-detected actions also honor attack cooldowns and state (e.g., cannot trigger if player is currently 'hurt').

Notes
- The in-game HUD also displays the controls near the bottom of the screen during play.
- Blocking reduces incoming damage (block reduction is applied in the game logic).

## Project Structure
### Core Files
- `start.py` - application bootstrap and scene registry; initializes Pygame, the ResourceManager and drives the main loop.
- `menu_scene.py` - main menu UI that allows navigating to the game, avatar creation.
- `game_scene.py` - the main gameplay scene: handles the game loop, input mapping to actions, health bars and round logic.
- `avatar_create.py` / `avatar_create_scene.py` - avatar capture UI: uses camera (via `utils/mediapipe_capture.py`) to capture a T-pose photo and create a pixel-art avatar.
- `tutorial_scene.py` - shows tutorial images / animated GIFs (uses `utils/gif_player.GifPlayer` to play tutorial GIFs).

### Utils
Small helper modules used across scenes and during loading.
- `utils/resource_manager.py` - coordinates image/audio loading and exposes `get_image`/`finalize_and_play` helpers.
- `utils/game_image_loader.py` - worker-friendly image loader used by the loading screen.
- `utils/game_sound_loader.py` - background music / audio loader helper.
- `utils/loading.py` - loading-screen UI and `run_loading_with_callback` helper.
- `utils/ui.py` - small UI widgets (Button and simple controls) used by scenes.
- `utils/color.py` - color palette constants used across scenes.
- `utils/mediapipe_capture.py` - optional Mediapipe-based capture helper for live avatar calibration (requires `mediapipe`).
- `utils/action_detector.py` - translates pose/keypoint sequences into game actions (jump, punch, kick, block).
- `utils/gif_player.py` - GIF helper that decodes GIF frames (OpenCV backend) and exposes a simple `update(dt)`/`get_surface()` API for animated tutorials.

### Assets
Project media and data used by the demo. Key locations:
- `assets/images/` - background and UI images used by scenes (e.g., `background.jpg`, `game_background.jpg`, `avatar_create_background.jpg`).
  - `assets/images/tutorial/` - tutorial GIFs (jump/punch/kick/block). Place tutorial GIFs here.
- `assets/photo/` - per-player capture folders and the T-pose images used for avatar slicing:
  - `assets/photo/player1/`, `assets/photo/player2/` each contain `guide.png` and `tpose.png`.
- `assets/poses/` - JSON pose definitions used by the animation controller (e.g., `poses_all.json`, `pose_punch.json`, ...).
- `assets/sounds/` - background music and sound effects (BGM, punch/kick SFX, etc.).

## Known issues and notes

Below are common issues, platform notes and quick fixes observed while running this project.

- GIF playback (OpenCV required)
  - Tutorial GIFs are decoded with OpenCV (`opencv-python`). If OpenCV is not installed the tutorial will show a static image instead of animated frames. Install with:

```powershell
pip install opencv-python
```

- Mediapipe / camera features (optional)
  - Camera capture and the ActionDetector depend on `mediapipe` and a functional camera. On systems without Mediapipe the game falls back to keyboard-only controls. Mediapipe installation can be platform-specific; use a virtual environment and consult the Mediapipe installation notes for Windows if you run into issues.

- Audio / mixer issues
  - On some systems Pygame's mixer may fail to initialize or report no available channels. If you see audio errors, try initializing the mixer manually or adjust buffer/channel arguments in `game_scene.py`. As a quick workaround you can comment out BGM/SFX plays while debugging.

- Performance
  - Real-time camera processing and GIF decoding increase CPU usage. Disable camera features or reduce preview resolution to improve framerate on slower machines.

- Assets & paths
  - Run the project from the repository root so package imports and relative asset paths resolve correctly. Missing assets (images/sounds) will be logged; confirm the following layout:
    - `assets/photo/player1/` and `assets/photo/player2/` (guide.png, tpose.png)
    - `assets/images/tutorial/` for tutorial GIFs
    - `assets/sounds/` for BGM and SFX

- Hot-reload and developer keys
  - Hot-reload behavior (F5/F6) is a development convenience and depends on the runtime key handlers. If hot-reload does not trigger, check your environment and keybinding handlers.

- Archive folder
  - Old entry scripts and tools have been moved to `archive/unused/`. They are not used by the active runtime but kept for safety — delete only if you are sure.

- Quick troubleshooting checklist

```powershell
# from project root
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python start.py

# if GIFs appear static:
pip install opencv-python

# to clear stale imports/bytecode
python -c "import shutil, pathlib; shutil.rmtree('__pycache__', ignore_errors=True)"
```

If you hit an error not listed above, open an issue or paste the traceback in a new bug report so it can be triaged.

## Developer notes
- The repository keeps archived copies under `archive/unused/` when files are removed from the active runtime — this is a safety-first choice.
- If you plan to restructure further, prefer absolute package imports (e.g., `from classes.skeleton import Skeleton`) and run from repo root to avoid import-time surprises.

## Running tests / quick checks
- Quick import check (no UI):

```powershell
python -c "import sys; sys.path.insert(0, r'..\2MB'); import start; print('start imported')"
```

## Contributing

Small fixes, bug reports, and PRs are welcome. If you open a PR, please:

- Keep changes focused (one feature / fix per PR).
- Run and verify the game runs locally.
- Add a brief description of the change in the PR message.

## License
MIT

## Contact / Repo
https://github.com/Bismarck-KL/2MB
