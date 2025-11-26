import os
from typing import List, Optional

import pygame


class GifPlayer:
    """Simple GIF player using OpenCV to extract frames.

    Notes:
    - Requires `opencv-python` (cv2) to be installed. The project already
      includes opencv in requirements.txt.
    - Loads all frames into memory on init. For short tutorial GIFs this
      is acceptable; for long GIFs consider streaming frames instead.
    - Frame timing uses the capture's FPS if available, otherwise falls
      back to 10 FPS.

    API:
    - update(dt): advance internal timer by seconds (float)
    - get_surface(): return current pygame.Surface (or None if no frames)
    - play(), pause(), reset()
    """

    def __init__(self, path: str, loop: bool = True, default_fps: float = 10.0):
        self.path = path
        self.loop = loop
        self.frames: List[pygame.Surface] = []
        self.frame_count = 0
        self.fps = default_fps
        self.frame_duration = 1.0 / self.fps
        # per-frame durations in seconds (may be variable when using PIL)
        self.durations: List[float] = []
        self._time_acc = 0.0
        self._idx = 0
        self._playing = True

        if not path or not os.path.exists(path):
            return

        # Use OpenCV (cv2) to load GIF frames. OpenCV is the chosen backend for
        # this project — if cv2 is not available, we fall back to a single-frame
        # pygame.image.load so the scene still shows something.
        try:
            import cv2

            cap = cv2.VideoCapture(path)
            # try to read fps from the capture; some GIFs may not provide it
            try:
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps and fps > 0:
                    self.fps = float(fps)
            except Exception:
                pass

            # fallback if still invalid
            if not self.fps or self.fps <= 0:
                self.fps = float(default_fps)

            # For OpenCV path we assume a fixed fps for all frames
            self.frame_duration = 1.0 / self.fps

            frames = []
            while True:
                ok, img = cap.read()
                if not ok:
                    break
                # cv2 provides BGR; convert to RGB
                try:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                except Exception:
                    pass

                h, w = img.shape[:2]
                surf = pygame.image.frombuffer(img.tobytes(), (w, h), "RGB")
                frames.append(surf.copy())

            cap.release()

            self.frames = frames
            self.frame_count = len(frames)
            # uniform durations
            self.durations = [self.frame_duration] * self.frame_count
            return
        except Exception as e:
            # OpenCV not available or failed to load — inform the user and fall
            # back to a single-frame pygame load so the UI remains usable.
            print(f"GifPlayer: OpenCV (cv2) unavailable or failed to load '{path}': {e}")

        # Final fallback: try pygame.image.load (likely single-frame)
        try:
            surf = pygame.image.load(path)
            try:
                surf = surf.convert_alpha()
            except Exception:
                surf = surf.convert()
            self.frames = [surf]
            self.frame_count = 1
            self.durations = [1.0 / default_fps]
            return
        except Exception as e:
            print(f"GifPlayer: failed to load '{path}': {e}")

    def is_valid(self) -> bool:
        return bool(self.frames)

    def update(self, dt: float) -> None:
        if not self._playing or self.frame_count == 0:
            return
        self._time_acc += dt
        # use per-frame duration if available, otherwise fall back to uniform frame_duration
        while self.frame_count > 0:
            cur_dur = self.durations[self._idx] if (self.durations and len(self.durations) > self._idx) else self.frame_duration
            if self._time_acc < cur_dur:
                break
            self._time_acc -= cur_dur
            self._idx += 1
            if self._idx >= self.frame_count:
                if self.loop:
                    self._idx = 0
                else:
                    self._idx = self.frame_count - 1
                    self._playing = False
                    break

    def get_surface(self) -> Optional[pygame.Surface]:
        if self.frame_count == 0:
            return None
        return self.frames[self._idx]

    def play(self) -> None:
        self._playing = True

    def pause(self) -> None:
        self._playing = False

    def reset(self) -> None:
        self._idx = 0
        self._time_acc = 0.0
        self._playing = True


__all__ = ["GifPlayer"]
