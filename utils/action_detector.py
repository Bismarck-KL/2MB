"""Simple real-time action detector using MediaPipe Pose.

This module provides ActionDetector which runs a background thread
capturing camera frames and uses heuristics on pose landmarks to detect
three actions: 'punch', 'kick', 'jump', and 'block'. When an action is
detected it invokes a provided callback with (player_id, action_name).

It supports a low-cost multi-person approach by running the single-person
MediaPipe Pose on left/right crops. If the project's
`utils/mediapipe_capture` singleton exists, ActionDetector will prefer to
read landmarks from it instead of opening the camera directly.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional, Tuple
import cv2
import math

try:
    import mediapipe as mp
except Exception:
    mp = None

try:
    import utils.mediapipe_capture as mc
except Exception:
    mc = None


class ActionDetector:
    def __init__(self, callback: Callable[[int, str], None], camera_index: int = 0):
        """Create an ActionDetector.

        callback: function(player_id: int, action_name: str)
        camera_index: index passed to cv2.VideoCapture when not using mediapipe_capture
        """
        self.callback = callback
        self.camera_index = camera_index
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._use_mc = False

        # per-player state
        self._last_wrist_x = {0: None, 1: None}
        self._last_time = {0: None, 1: None}
        self._cooldown_until = {0: 0.0, 1: 0.0}
        self._hip_baseline = {0: None, 1: None}

        # thresholds (tweak as needed)
        self.punch_vel_threshold = 0.15
        self.punch_disp_threshold = 0.08
        self.kick_height_threshold = 0.10
        self.jump_height_threshold = 0.12
        self.cooldown_seconds = 0.6
        self.block_wrist_dist_threshold = 0.08
        self.block_chest_y_thresh = 0.16
        self.elbow_extension_cos_threshold = -0.8

        # processing throttling (frames per second to actually run the Pose model)
        # Lowering this reduces CPU usage. Set to None or 0 to process every frame.
        self.process_fps = 10
        # optional downscale factor applied to each crop before feeding to Pose.
        # Values in (0,1] — smaller reduces CPU but may reduce accuracy.
        self.crop_scale = 0.7
        # internal tracker
        self._last_process_time = 0.0

    def start(self):
        if self._running:
            return
        if mp is None:
            print("ActionDetector: mediapipe not available")
            return
        try:
            if mc and hasattr(mc, 'get_latest_landmarks'):
                self._use_mc = True
        except Exception:
            self._use_mc = False

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self):
        mp_pose = mp.solutions.pose

        def _get_point(lm_list, idx: int) -> Optional[Tuple[float, float]]:
            try:
                v = lm_list[idx]
                return (v[0], v[1])
            except Exception:
                return None

        def _run_detection_for_landmarks(lm_list: list, assumed_player: Optional[int] = None):
            # lm_list is a sequence of (x,y) normalized to full-frame coordinates
            nose = _get_point(lm_list, mp_pose.PoseLandmark.NOSE.value)
            left_shoulder = _get_point(lm_list, mp_pose.PoseLandmark.LEFT_SHOULDER.value)
            right_shoulder = _get_point(lm_list, mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
            left_wrist = _get_point(lm_list, mp_pose.PoseLandmark.LEFT_WRIST.value)
            right_wrist = _get_point(lm_list, mp_pose.PoseLandmark.RIGHT_WRIST.value)
            left_elbow = _get_point(lm_list, mp_pose.PoseLandmark.LEFT_ELBOW.value)
            right_elbow = _get_point(lm_list, mp_pose.PoseLandmark.RIGHT_ELBOW.value)
            left_hip = _get_point(lm_list, mp_pose.PoseLandmark.LEFT_HIP.value)
            right_hip = _get_point(lm_list, mp_pose.PoseLandmark.RIGHT_HIP.value)
            left_ankle = _get_point(lm_list, mp_pose.PoseLandmark.LEFT_ANKLE.value)
            right_ankle = _get_point(lm_list, mp_pose.PoseLandmark.RIGHT_ANKLE.value)

            now = time.time()

            # decide player id
            if assumed_player is not None:
                player_id = assumed_player
            else:
                if nose is None:
                    return
                player_id = 0 if nose[0] < 0.5 else 1

            if player_id == 0:
                shoulder = left_shoulder
                wrist = left_wrist
                hip = left_hip
                ankle = left_ankle
                left_el = left_elbow
                right_el = right_elbow
                facing_dir = 1.0
            else:
                shoulder = right_shoulder
                wrist = right_wrist
                hip = right_hip
                ankle = right_ankle
                left_el = left_elbow
                right_el = right_elbow
                facing_dir = -1.0

            # init baseline
            if hip and self._hip_baseline[player_id] is None:
                self._hip_baseline[player_id] = hip[1]

            prev_x = self._last_wrist_x[player_id]
            prev_t = self._last_time[player_id]
            self._last_time[player_id] = now
            if wrist:
                self._last_wrist_x[player_id] = wrist[0]

            vel_x = 0.0
            if prev_x is not None and prev_t is not None and wrist:
                dt = max(1e-3, now - prev_t)
                vel_x = (wrist[0] - prev_x) / dt

            if now < self._cooldown_until[player_id]:
                return

            # BLOCK detection
            try:
                lw = left_wrist
                rw = right_wrist
                ls = left_shoulder
                rs = right_shoulder
                if lw and rw and ls and rs:
                    dist = math.hypot(lw[0] - rw[0], lw[1] - rw[1])
                    shoulder_y = 0.5 * (ls[1] + rs[1])
                    wrist_y_avg = 0.5 * (lw[1] + rw[1])
                    if dist < self.block_wrist_dist_threshold and abs(wrist_y_avg - shoulder_y) < self.block_chest_y_thresh:
                        self._cooldown_until[player_id] = now + self.cooldown_seconds
                        try:
                            self.callback(player_id, 'block')
                            if mc and hasattr(mc, 'set_latest_action'):
                                try:
                                    mc.set_latest_action(player_id, 'BLOCK')
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        return
            except Exception:
                pass

            # PUNCH detection
            punch_disp = None
            if wrist and shoulder:
                punch_disp = (wrist[0] - shoulder[0]) * facing_dir

            if punch_disp is not None and punch_disp > self.punch_disp_threshold and vel_x * facing_dir > self.punch_vel_threshold:
                try:
                    elbow = left_el if player_id == 0 else right_el
                    shoulder_pt = left_shoulder if player_id == 0 else right_shoulder
                    wrist_pt = left_wrist if player_id == 0 else right_wrist
                    extended_ok = True
                    # print("[Develop Log] Punch detected, checking elbow extension")
                    if elbow and shoulder_pt and wrist_pt:
                        # print("[Develop Log] Calculating elbow angle for extension check")  
                        ax = shoulder_pt[0] - elbow[0]
                        ay = shoulder_pt[1] - elbow[1]
                        bx = wrist_pt[0] - elbow[0]
                        by = wrist_pt[1] - elbow[1]
                        na = math.hypot(ax, ay)
                        nb = math.hypot(bx, by)
                        if na > 1e-6 and nb > 1e-6:
                            dot = (ax * bx + ay * by) / (na * nb)
                            extended_ok = (dot < self.elbow_extension_cos_threshold)
                    if not extended_ok:
                        return

                    self._cooldown_until[player_id] = now + self.cooldown_seconds
                    try:
                        self.callback(player_id, 'punch')
                        if mc and hasattr(mc, 'set_latest_action'):
                            try:
                                mc.set_latest_action(player_id, 'PUNCH')
                            except Exception:
                                pass
                    except Exception:
                        pass
                    return
                except Exception:
                    try:
                        self._cooldown_until[player_id] = now + self.cooldown_seconds
                        self.callback(player_id, 'punch')
                    except Exception:
                        pass
                    return

            # KICK detection
            if ankle and hip:
                if (hip[1] - ankle[1]) > self.kick_height_threshold:
                    self._cooldown_until[player_id] = now + self.cooldown_seconds
                    try:
                        self.callback(player_id, 'kick')
                    except Exception:
                        pass
                    return

            # JUMP detection
            baseline = self._hip_baseline[player_id]
            if hip and baseline is not None:
                if (baseline - hip[1]) > self.jump_height_threshold:
                    self._cooldown_until[player_id] = now + self.cooldown_seconds
                    try:
                        self.callback(player_id, 'jump')
                    except Exception:
                        pass
                    return

            # No action detected for this set of landmarks -> mark READY
            try:
                if mc and hasattr(mc, 'set_latest_action'):
                    try:
                        mc.set_latest_action(player_id, 'READY')
                    except Exception:
                        pass
            except Exception:
                pass

        # If a mediapipe_capture singleton exists, poll it for landmarks
        if self._use_mc:
            while self._running:
                try:
                    latest = None
                    try:
                        latest = mc.get_latest_landmarks() if mc else None
                    except Exception:
                        latest = None

                    if not latest or not latest.get('landmarks'):
                        time.sleep(0.01)
                        continue

                    lm_list = latest['landmarks']
                    try:
                        _run_detection_for_landmarks(lm_list)
                    except Exception:
                        pass

                    time.sleep(0.005)
                except Exception:
                    time.sleep(0.02)
            return

        # Otherwise open the camera and run Pose on left/right crops
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("ActionDetector: unable to open camera")
            self._running = False
            return

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self._running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                h, w = frame.shape[:2]
                half_w = max(1, w // 2)

                left_crop = frame[:, :half_w]
                right_crop = frame[:, half_w:]

                # Throttle processing to target FPS to reduce CPU usage.
                now = time.time()
                if self.process_fps and self.process_fps > 0:
                    min_dt = 1.0 / float(self.process_fps)
                    if (now - self._last_process_time) < min_dt:
                        # small sleep to avoid busy-looping
                        time.sleep(0.003)
                        continue
                self._last_process_time = now

                # optionally downscale crops before running Pose to reduce cost
                try:
                    if self.crop_scale and 0.0 < self.crop_scale < 1.0:
                        left_proc = cv2.resize(left_crop, (0, 0), fx=self.crop_scale, fy=self.crop_scale, interpolation=cv2.INTER_AREA)
                        right_proc = cv2.resize(right_crop, (0, 0), fx=self.crop_scale, fy=self.crop_scale, interpolation=cv2.INTER_AREA)
                    else:
                        left_proc = left_crop
                        right_proc = right_crop

                    left_rgb = cv2.cvtColor(left_proc, cv2.COLOR_BGR2RGB)
                    results_l = pose.process(left_rgb)
                except Exception:
                    results_l = None

                try:
                    right_rgb = cv2.cvtColor(right_proc, cv2.COLOR_BGR2RGB)
                    results_r = pose.process(right_rgb)
                except Exception:
                    results_r = None

                if results_l and results_l.pose_landmarks:
                    try:
                        lm_l = results_l.pose_landmarks.landmark
                        lm_list = [(v.x * 0.5, v.y) for v in lm_l]
                        _run_detection_for_landmarks(lm_list, assumed_player=0)
                    except Exception:
                        pass

                if results_r and results_r.pose_landmarks:
                    try:
                        lm_r = results_r.pose_landmarks.landmark
                        lm_list = [(v.x * 0.5 + 0.5, v.y) for v in lm_r]
                        _run_detection_for_landmarks(lm_list, assumed_player=1)
                    except Exception:
                        pass

                # small sleep to yield
                time.sleep(0.001)

        cap.release()
        # end of multi-crop detection loop


__all__ = ["ActionDetector"]
