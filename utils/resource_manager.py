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


class ResourceManager:
    """Load images and audio resources and provide accessors.

    images: dict key->path
    audio_path: optional path for BackgroundMusicLoader (if None uses default)
    """

    def __init__(self, images: Dict[str, str], image_base_dir: Optional[str] = None, audio_path: Optional[str] = None):
        self.images_map = images
        self.image_base_dir = image_base_dir
        self.audio_path = audio_path

        # create loaders
        self.image_loader = GameImageLoader(images, base_dir=image_base_dir, create_surfaces_on_main_thread=False)
        # pass the audio path into the music loader if provided
        self.audio_loader = BackgroundMusicLoader(path=audio_path) if audio_path else BackgroundMusicLoader()

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

        # load audio
        self.audio_loader.load(report=report_audio, stop_event=stop_event)

    # Accessors
    def get_image(self, key: str):
        return self.image_loader.get(key)

    def play_music(self):
        self.audio_loader.play()

    def stop_music(self):
        self.audio_loader.stop()


__all__ = ["ResourceManager"]
