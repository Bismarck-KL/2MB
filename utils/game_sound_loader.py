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

    def __init__(self, path: Optional[str] = None, volume: float = 0.5, init_mixer: bool = False):
        self.path = path or os.path.join('assets', 'sounds', 'bgm.mp3')
        self.volume = float(volume)
        # init_mixer controls whether finalize() will call pygame.mixer.init();
        # default False so mixer init runs on the main thread via finalize().
        self.init_mixer = bool(init_mixer)
        self._loaded = False
        # raw bytes buffer when loading happens off-main-thread
        self._raw_bytes: Optional[bytes] = None

    def load(self, report: Optional[Callable[[float], None]] = None, stop_event=None) -> None:
        """Perform file I/O to read the music file into memory.

        This method is intended to run in a worker thread. It reads the
        file bytes into memory and reports progress. Actual mixer
        initialization and passing the data to the mixer must be done on
        the main thread by calling `finalize()`.
        """
        if report:
            report(5)

        if stop_event is not None and getattr(stop_event, 'is_set', lambda: False)():
            return

        # read file bytes
        try:
            with open(self.path, 'rb') as f:
                data = f.read()
            self._raw_bytes = data
        except Exception:
            # propagate exception to caller/runner
            raise

        if report:
            report(100)

    def play(self, loop: bool = True) -> None:
        """Start playback. Call on main thread after load completes."""
        if not self._loaded:
            # nothing loaded into mixer
            return

        loops = -1 if loop else 0
        pygame.mixer.music.play(loops=loops)

    def finalize(self) -> None:
        """Finalize loading on the main thread: initialize mixer and load data.

        Must be called on the main thread. Uses the bytes read by `load()` to
        load into pygame.mixer.music via a BytesIO object.
        """
        if self._raw_bytes is None:
            return

        # initialize mixer on main thread if requested or if mixer isn't initialized
        try:
            if self.init_mixer:
                pygame.mixer.init()
            else:
                # ensure mixer is initialized
                try:
                    pygame.mixer.get_init()
                except Exception:
                    pygame.mixer.init()
        except Exception:
            # best-effort: continue and let load raise if unsupported
            pass

        try:
            import io

            buf = io.BytesIO(self._raw_bytes)
            # pygame.mixer.music.load accepts a file-like object in many setups
            pygame.mixer.music.load(buf)
            pygame.mixer.music.set_volume(self.volume)
            self._loaded = True
        finally:
            # free raw bytes
            self._raw_bytes = None

    def stop(self) -> None:
        pygame.mixer.music.stop()


__all__ = ["BackgroundMusicLoader"]