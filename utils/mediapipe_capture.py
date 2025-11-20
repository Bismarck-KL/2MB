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


# module-level singleton for easy use
_instance = _MediapipeCapture()


def start_mediapipe_capture():
    """Start the mediapipe capture in a background thread. Safe to call repeatedly."""
    _instance.start()


def stop_mediapipe_capture():
    """Stop the running mediapipe capture if active."""
    _instance.stop()
