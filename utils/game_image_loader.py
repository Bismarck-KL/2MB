"""Image loading utilities for game assets.

Provides a GameImageLoader class that can load multiple images with progress
reporting. Designed to work with the existing loading UI (report(progress)).

By default the loader uses `pygame.image.load(path).convert_alpha()` to
produce surfaces. If you need to ensure all Pygame surface operations run on
the main thread, set `create_surfaces_on_main_thread=True` and call
`finalize_surfaces()` on the main thread after `load()` completes; in that
mode the loader will only read raw bytes in the worker thread and keep them
in memory until finalization.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Callable

import pygame


class GameImageLoader:
    """Load multiple images with progress reporting.

    Parameters
    - images: mapping of key->relative path (strings) or list of (key, path)
    - base_dir: optional base directory to join with each path
    - create_surfaces_on_main_thread: if True, loader will read raw bytes only
      and postpone Surface creation to `finalize_surfaces()` which must be
      called on the main thread.
    """

    def __init__(
        self,
        images,
        base_dir: Optional[str] = None,
        create_surfaces_on_main_thread: bool = False,
    ) -> None:
        # normalize images to list of (key, path)
        if isinstance(images, dict):
            self._items = list(images.items())
        else:
            self._items = list(images)

        self.base_dir = base_dir or ""
        self.create_surfaces_on_main_thread = bool(create_surfaces_on_main_thread)

        # results
        self.images: Dict[str, pygame.Surface] = {}
        # if postponing surface creation we keep raw bytes here
        self._raw_bytes: Dict[str, bytes] = {}

    def _full_path(self, path: str) -> str:
        return path if os.path.isabs(path) or not self.base_dir else os.path.join(self.base_dir, path)

    def load(self, report: Optional[Callable[[float], None]] = None, stop_event=None) -> None:
        """Load all images. Call from worker thread via run_loading_with_callback.

        The loader will call `report(progress)` with a percentage value.
        """
        total = len(self._items)
        if total == 0:
            if report:
                report(100)
            return

        for idx, (key, path) in enumerate(self._items, start=1):
            if stop_event is not None and getattr(stop_event, "is_set", lambda: False)():
                break

            full = self._full_path(path)
            try:
                if self.create_surfaces_on_main_thread:
                    # read raw bytes
                    with open(full, "rb") as f:
                        data = f.read()
                    self._raw_bytes[key] = data
                else:
                    surf = pygame.image.load(full)
                    # convert_alpha keeps transparency if present
                    try:
                        surf = surf.convert_alpha()
                    except Exception:
                        surf = surf.convert()
                    self.images[key] = surf
            except Exception:
                # on error skip but continue; caller can check missing keys
                self.images[key] = None  # type: ignore

            if report:
                pct = int((idx / total) * 100)
                report(pct)

        if report:
            report(100)

    def finalize_surfaces(self) -> None:
        """Create pygame.Surface objects from raw bytes.

        Must be called on the main thread (the one with the display) if
        `create_surfaces_on_main_thread=True` was used.
        """
        for key, data in self._raw_bytes.items():
            try:
                import io

                buf = io.BytesIO(data)
                surf = pygame.image.load(buf)
                try:
                    surf = surf.convert_alpha()
                except Exception:
                    surf = surf.convert()
                self.images[key] = surf
            except Exception:
                self.images[key] = None  # type: ignore

        # clear raw bytes to free memory
        self._raw_bytes.clear()

    def get(self, key: str) -> Optional[pygame.Surface]:
        return self.images.get(key)

    def keys(self):
        return [k for k, _ in self._items]


__all__ = ["GameImageLoader"]


if __name__ == "__main__":
    # small demo when run directly
    pygame.init()
    demo_images = {"bg": os.path.join("assets", "images", "background.png")}
    loader = GameImageLoader(demo_images, create_surfaces_on_main_thread=False)
    try:
        loader.load(report=print)
        print("Loaded keys:", loader.keys())
    finally:
        pygame.quit()
