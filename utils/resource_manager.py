"""Resource manager that coordinates image and audio loading.

Provides a single `ResourceManager` class which uses `GameImageLoader` and
`BackgroundMusicLoader` to load images and music with progress reporting.

Design notes:
- The manager exposes `load_all(report, stop_event)` which reports a single
  0..100 progress value combining image and audio progress.
- Uses simple weighting (images vs audio) to merge progress; this keeps UI
  feedback smooth without changing underlying loaders.
"""
from __future__ import annotations

from typing import Dict, Optional, Callable

from .game_image_loader import GameImageLoader
from .game_sound_loader import BackgroundMusicLoader
import os


class ResourceManager:
    """Load images and audio resources and provide accessors.

    images: dict key->path
    audio_path: optional path for BackgroundMusicLoader (if None uses default)
    """

    def __init__(self, images: Dict[str, str], image_base_dir: Optional[str] = None,
                 audio_path: Optional[str] = None, audio_files: Optional[Dict[str, str]] = None):
        self.images_map = images
        self.image_base_dir = image_base_dir

        # create loaders
        self.image_loader = GameImageLoader(
            images, base_dir=image_base_dir, create_surfaces_on_main_thread=False)

        # audio: support either a single audio_path (backwards compat) or a
        # dict of named audio files. We create BackgroundMusicLoader instances
        # for each provided path; actual `finalize()` (which touches the mixer)
        # is done on demand by `finalize_and_play` / `play_music`.
        self.audio_loader = BackgroundMusicLoader(path=audio_path) if audio_path else None
        self.audio_loaders: Optional[Dict[str, BackgroundMusicLoader]] = None
        if audio_files:
            self.audio_loaders = {k: BackgroundMusicLoader(path=v) for k, v in (audio_files.items())}

    def load_all(self, report: Optional[Callable[[float], None]] = None, stop_event=None) -> None:
        """Load images and audio, reporting combined progress (0..100).

        Strategy: load images first then audio. Weighting: images 70%, audio 30%.
        Calls `report(combined_percent)` where combined_percent is 0..100.
        """
        # weights
        img_weight = 0.7
        audio_weight = 0.3

        # helper to convert subprogress to combined
        def report_images(pct: float):
            if report:
                report(int(pct * img_weight))

        def report_audio(pct: float):
            if report:
                # offset by image weight
                combined = int(img_weight * 100 + pct * audio_weight)
                report(min(100, combined))

        # load images
        self.image_loader.load(report=report_images, stop_event=stop_event)

        # load audio: either a single loader or multiple named loaders
        if self.audio_loader:
            self.audio_loader.load(report=report_audio, stop_event=stop_event)
        elif self.audio_loaders:
            # split the audio weight between each named loader for smooth progress
            keys = list(self.audio_loaders.keys())
            n = len(keys)

            def per_loader_report(idx, pct):
                # compute combined percent: image_weight*100 + audio_weight*(idx/n + pct/n)
                if report:
                    base = int(img_weight * 100)
                    frac = (idx + pct / 100.0) / n
                    combined = int(base + frac * audio_weight * 100)
                    report(min(100, combined))

            for i, k in enumerate(keys):
                loader = self.audio_loaders[k]
                # wrapper to convert 0..100->0..100 for per_loader_report
                def make_report(i):
                    return lambda p: per_loader_report(i, p)

                loader.load(report=make_report(i), stop_event=stop_event)
        else:
            if report:
                # nothing to load for audio
                report(100)

    # Accessors
    def get_image(self, key: str):
        return self.image_loader.get(key)

    def get_image_by_path(self, path: str):
        """Return a loaded pygame.Surface for a filesystem path if that path
        appears in the manager's image map. This helps callers that only know
        the path (not the resource key) to reuse already-loaded surfaces.

        Path matching is done by normalizing paths and joining with the
        configured image_base_dir when the stored path is relative.
        """
        if not path:
            return None

        # normalize requested path
        try:
            req = os.path.normpath(path)
        except Exception:
            req = path

        for key, rel in self.images_map.items():
            try:
                full = rel if os.path.isabs(rel) or not self.image_base_dir else os.path.join(self.image_base_dir, rel)
                if os.path.normpath(full) == req:
                    return self.image_loader.get(key)
            except Exception:
                continue

        return None

    # Simple sound cache for short sound effects (pygame.mixer.Sound)
    # This is intentionally minimal: it synchronously loads the sound the
    # first time it is requested and caches the resulting Sound object.
    # Use `get_sound(path)` with a filesystem path (or a key you choose).
    def get_sound(self, path: str):
        if not hasattr(self, '_sfx_cache'):
            self._sfx_cache = {}

        if path in self._sfx_cache:
            return self._sfx_cache[path]

        try:
            snd = __import__('pygame').mixer.Sound(path)
            self._sfx_cache[path] = snd
            return snd
        except Exception:
            return None

    def play_music(self):
        print("ResourceManager: play_music called")
        # Backwards-compatible play: play the single loader if present, else
        # play the 'game' key if available, else the first named loader.
        if self.audio_loader:
            self.audio_loader.play()
            return
        if self.audio_loaders:
            # prefer 'game' key if present
            key = 'game' if 'game' in self.audio_loaders else next(iter(self.audio_loaders))
            try:
                self.audio_loaders[key].finalize()
                self.audio_loaders[key].play()
            except Exception:
                pass

    def finalize_and_play(self, key: Optional[str] = None):
        print("ResourceManager: finalize_and_play called")
        """Finalize (on main thread) and play a named music track.

        If multiple audio files were provided, `key` selects which one to
        finalize and play. If `key` is None the method will prefer 'game'
        if present, otherwise the first available loader. If only a single
        `audio_loader` was configured (backwards compat), it will be used.
        """
        if self.audio_loader and not self.audio_loaders:
            try:
                print("ResourceManager: finalizing single audio_loader")    
                self.audio_loader.finalize()
            except Exception:
                print("ResourceManager: failed to finalize single audio_loader")
                return
            print("ResourceManager: playing single audio_loader")
            self.audio_loader.play()
            return
        
        print(f"ResourceManager: finalizing and playing audio_loader with key '{key}'")

        if not self.audio_loaders:
            print("ResourceManager: no audio_loaders available")
            return

        # choose key
        if key is None:
            print("ResourceManager: no key provided, defaulting to 'game' or first available")
            key = 'game' if 'game' in self.audio_loaders else next(iter(self.audio_loaders))

        print(f"ResourceManager: finalizing audio_loader with key '{key}'")
        loader = self.audio_loaders.get(key)
        if not loader:
            print(f"ResourceManager: no audio_loader found with key '{key}'")
            return
        try:
            print(f"ResourceManager: finalizing loader for key '{key}'")
            loader.finalize()
            print(f"ResourceManager: playing loader for key '{key}'")
            loader.play()
        except Exception:
            return

    def stop_music(self):
        # stopping is global for pygame.mixer.music
        try:
            if self.audio_loader or self.audio_loaders:
                __import__('pygame').mixer.music.stop()
        except Exception:
            pass


__all__ = ["ResourceManager"]
