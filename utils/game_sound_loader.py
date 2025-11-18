"""Background music loader implemented as a reusable class.

Refactored for SOLID principles:
- Single Responsibility: this module exposes a BackgroundMusicLoader class that
  handles loading and playback of background music.
- Open/Closed: the loader is configurable (path, volume) and can be extended.
- Dependency Inversion: accepts configuration rather than hard-coding behavior.
"""

import os
import pygame
from typing import Optional, Callable


class BackgroundMusicLoader:
    """Loads and controls background music.

    Usage:
        loader = BackgroundMusicLoader(path='assets/sounds/bgm.mp3', volume=0.5)
        # run in worker thread with report callback
        loader.load(report)
        # on main thread
        loader.play()
    """

    def __init__(self, path: Optional[str] = None, volume: float = 0.5, init_mixer: bool = True):
        self.path = path or os.path.join('assets', 'sounds', 'bgm.mp3')
        self.volume = float(volume)
        self.init_mixer = bool(init_mixer)
        self._loaded = False

    def load(self, report: Optional[Callable[[float], None]] = None, stop_event=None) -> None:
        """Load the background music file.

        report: optional callable(progress_float) to report progress (0..100).
        stop_event: optional threading.Event to support cancellation.
        """
        if report:
            report(5)

        if stop_event is not None and getattr(stop_event, 'is_set', lambda: False)():
            return

        # Initialize mixer if requested. Some platforms prefer init on main thread;
        # caller can set init_mixer=False and initialize earlier on the main thread.
        if self.init_mixer:
            try:
                pygame.mixer.init()
            except Exception:
                # continue and let pygame raise on load if unsupported
                pass

        if report:
            report(30)

        if stop_event is not None and getattr(stop_event, 'is_set', lambda: False)():
            return

        try:
            pygame.mixer.music.load(self.path)
            pygame.mixer.music.set_volume(self.volume)
            self._loaded = True
        except Exception as e:
            # Re-raise to let caller handle errors
            raise

        if report:
            report(100)

    def play(self, loop: bool = True) -> None:
        """Start playback. Call on main thread after load completes."""
        if not self._loaded:
            # attempt to load synchronously if not loaded
            try:
                pygame.mixer.music.load(self.path)
                pygame.mixer.music.set_volume(self.volume)
                self._loaded = True
            except Exception:
                return

        loops = -1 if loop else 0
        pygame.mixer.music.play(loops=loops)

    def stop(self) -> None:
        pygame.mixer.music.stop()


__all__ = ["BackgroundMusicLoader"]