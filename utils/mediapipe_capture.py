import threading
import time
import cv2
import mediapipe as mp


class _MediapipeCapture:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        # give thread a moment to clean up
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("MediapipeCapture: unable to open camera")
            self._running = False
            return

        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            window_name = 'Mediapipe Capture - press q to close'
            while self._running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert BGR to RGB for mediapipe
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(img_rgb)

                # Draw landmarks on the original BGR frame
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                cv2.imshow(window_name, frame)
                # allow quick manual quit from this window
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self._running = False
                    break

            cap.release()
            try:
                cv2.destroyWindow(window_name)
            except Exception:
                pass

    def initialize(self, report, stop_event=None):
        """Synchronous initialization helper suitable as a loader callable.

        The function will open the camera, perform a few warm-up frames with
        MediaPipe to ensure models are loaded and camera is responsive, then
        release the camera. It must accept a `report(progress_float)`
        callable and an optional `stop_event` threading.Event.
        """
        try:
            report(5.0)
        except Exception:
            pass

        # stop early if requested
        if stop_event is not None and stop_event.is_set():
            return

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError("MediapipeCapture: unable to open camera during initialization")

        try:
            mp_pose = mp.solutions.pose
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                # warm up a few frames
                frames = 0
                while frames < 6:
                    if stop_event is not None and stop_event.is_set():
                        break
                    ret, frame = cap.read()
                    if not ret:
                        break
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    _ = pose.process(img_rgb)
                    frames += 1
                    try:
                        report(5.0 + (frames / 6.0) * 90.0)
                    except Exception:
                        pass
        finally:
            cap.release()

        try:
            report(100.0)
        except Exception:
            pass


# module-level singleton for easy use
_instance = _MediapipeCapture()


def start_mediapipe_capture():
    """Start the mediapipe capture in a background thread. Safe to call repeatedly."""
    _instance.start()


def stop_mediapipe_capture():
    """Stop the running mediapipe capture if active."""
    _instance.stop()


def initialize_mediapipe(report, stop_event=None):
    """Module-level loader wrapper that matches the loader signature used
    by utils.loading.run_loading_with_callback.

    It delegates to the singleton instance's `initialize` method.
    """
    return _instance.initialize(report, stop_event)
