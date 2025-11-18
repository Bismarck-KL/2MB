## 2MB — Pygame menu & simple scene framework

This small project is a Pygame-based menu and scene scaffold used for the SD5913 group assignment. It includes:

- A 1600×900 Pygame window and main loop (`start.py`).
- A modular scene system (Menu, Game, Avatar Create) separated into individual files under the project root.
- Resource loading utilities (images and background music) with a non-blocking loading screen (`utils/*`).
- Small UI helpers (`utils/ui.py`) and color constants (`utils/color.py`).

## Quick start (Windows / PowerShell)

1. Create a virtual environment and install requirements (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:

```powershell
python .\start.py
```

The app should open a window and show a Main Menu with Start and Quit buttons. Close the window or press Esc to exit.

## Project layout (important files)

- `start.py` — Application entrypoint. Creates `Application`, loads resources, and runs the main loop. It also holds the scene registry and `change_scene()` helper.
- `menu_scene.py` — Main menu scene with Start/Quit buttons. Requests scene changes via `app.change_scene("...")`.
- `game_scene.py` — Placeholder game scene (press Esc to go back).
- `avatar_create.py` — Avatar creation scene with a top-left Back button (returns to menu).
- `utils/resource_manager.py` — Orchestrates image and audio loading (uses `GameImageLoader` and `BackgroundMusicLoader`).
- `utils/game_image_loader.py` — Image loader (progress reporting). See note below about main-thread surface creation.
- `utils/game_sound_loader.py` — Background music loader (reads file bytes in worker thread; `finalize()` runs on main thread to initialize mixer and load bytes).
- `utils/loading.py` — Loading screen UI and `run_loading_with_callback()` runner.
- `utils/ui.py` — Small `Button` component and draw helpers.
- `assets/` — expected location for images and audio (not all assets are included).

## Where the Start button image is loaded

The path for the Start button image is defined in `start.py` when the `ResourceManager` is created. Open `start.py` and look for the `images` mapping, for example:

```python
images = {
	"background": os.path.join("assets", "images", "background.png"),
	"btn_start": os.path.join("assets", "images", "button_start.png"),
	"btn_quit": os.path.join("assets", "images", "button_quit.png"),
}
```

The image is loaded during startup by `GameImageLoader` and accessed in the menu via `self.res_mgr.get_image("btn_start")`.

If the image is missing the code will fall back to drawing a colored button.

## Notes for developers

- If you experience image/mixer issues on your platform, you can set `create_surfaces_on_main_thread=True` when creating `GameImageLoader` in `ResourceManager` and call `finalize_surfaces()` on the main thread after loading completes — this defers all Pygame surface creation to the main thread.
- Scene registration is centralized in `Application` (the `scene_registry` dict). To add a new scene:
  1. Create `my_scene.py` with `class MyScene:` that accepts `app` in the constructor.
  2. Import it in `start.py` and add it to `self.scene_registry`.
  3. Switch to it using `self.app.change_scene("MyScene")`.
- To change the Start button image path, update the `btn_start` entry in the `images` dict in `start.py`.

## Development tips

- Keep images under `assets/images/` and audio under `assets/sounds/`.
- Use `app.change_scene("SceneName")` from scenes to switch scenes; avoid importing scene modules across each other to prevent circular imports.
- For small debug traces use the Python `logging` module instead of prints; it can be toggled or directed to a file.

## License & credits

This repository contains course project code. Review your institution or instructor guidance about sharing or publishing before distributing.

---

If you want, I can also add a short `CONTRIBUTING.md` or a `Makefile`/PowerShell script to automate the run/setup steps.

