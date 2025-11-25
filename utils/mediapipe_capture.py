import threading
import time
import cv2
import mediapipe as mp


class _MediapipeCapture:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self._running = False
        self._thread = None
        # store latest landmarks and a lock for thread-safe access
        self._latest_lock = threading.Lock()
        self._latest = None

    def start(self):
        if self._running:
            return
        try:
            print(f"MediapipeCapture: starting camera thread (index={self.camera_index})")
        except Exception:
            pass
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            print("MediapipeCapture: stop requested")
        except Exception:
            pass
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
            # create a named, resizable window and start the window thread to
            # improve the likelihood the preview appears reliably on Windows
            try:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                try:
                    cv2.startWindowThread()
                except Exception:
                    # startWindowThread is a best-effort helper; ignore failures
                    pass
            except Exception:
                # ignore if namedWindow is unsupported on this platform
                pass

            while self._running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("MediapipeCapture: frame read failed (ret=False), stopping capture")
                    break

                # Convert BGR to RGB for mediapipe
                try:
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    print("MediapipeCapture: cvtColor failed:", e)
                    # show the raw frame if possible and continue
                    try:
                        cv2.imshow(window_name, frame)
                    except Exception:
                        pass
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self._running = False
                        break
                    continue

                try:
                    results = pose.process(img_rgb)
                except Exception as e:
                    # log and keep running; some mediapipe model issues show as warnings
                    print("MediapipeCapture: pose.process() raised:", repr(e))
                    results = None

                # Draw landmarks on the original BGR frame and store them
                try:
                    if results and getattr(results, 'pose_landmarks', None):
                        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                        try:
                            lm = []
                            for l in results.pose_landmarks.landmark:
                                lm.append((l.x, l.y))
                            with self._latest_lock:
                                self._latest = {
                                    'landmarks': lm,
                                    'width': frame.shape[1],
                                    'height': frame.shape[0],
                                    'ts': time.time(),
                                }
                        except Exception:
                            pass
                except Exception as e:
                    print("MediapipeCapture: drawing landmarks failed:", e)

                try:
                    # draw a vertical divider and labels for left/right halves
                    try:
                        h, w = frame.shape[0], frame.shape[1]
                        cv2.line(frame, (w // 2, 0), (w // 2, h), (100, 100, 100), 2)
                        cv2.putText(frame, 'P1', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                        cv2.putText(frame, 'P2', (w - 70, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                    except Exception:
                        pass

                    cv2.imshow(window_name, frame)
                except Exception as e:
                    # ignore imshow errors but log them for diagnosis
                    print("MediapipeCapture: imshow failed:", e)

                # allow quick manual quit from this window
                try:
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self._running = False
                        break
                except Exception:
                    # if waitKey fails, break to avoid tight loop
                    self._running = False
                    break

            cap.release()
            try:
                cv2.destroyWindow(window_name)
            except Exception:
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
            try:
                print("MediapipeCapture: capture loop exited")
            except Exception:
                pass

    def get_latest_landmarks(self):
        """Return a copy of the latest landmarks dict or None.

        The structure is: {'landmarks': [(x,y),...], 'width':int, 'height':int, 'ts': float}
        Coordinates are normalized (0..1)."""
        try:
            with self._latest_lock:
                if self._latest is None:
                    return None
                # shallow copy is sufficient (list of tuples)
                return {
                    'landmarks': list(self._latest['landmarks']),
                    'width': self._latest['width'],
                    'height': self._latest['height'],
                    'ts': self._latest['ts'],
                }
        except Exception:
            return None

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
