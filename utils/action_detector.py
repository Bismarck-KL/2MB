"""Simple real-time action detector using MediaPipe Pose.

This module provides ActionDetector which runs a background thread
capturing camera frames and uses heuristics on pose landmarks to detect
three actions: 'punch', 'kick', and 'jump'. When an action is detected it
invokes a provided callback with (player_id, action_name).

Heuristics are intentionally simple and tuned for two players standing
side-by-side: which player produced the action is decided by the
x-coordinate of the nose landmark (left half -> player 0, right half ->
player 1). Use cooldowns to avoid repeated triggers.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional, Tuple
import cv2
try:
    import mediapipe as mp
except Exception:
    mp = None

# attempt to reuse the mediapipe_capture singleton if available so we don't
# open multiple VideoCapture devices. This avoids camera contention that
# causes `cap.read()` to fail when another process already holds the camera.
try:
    import utils.mediapipe_capture as mc
except Exception:
    mc = None


class ActionDetector:
    def __init__(self, callback: Callable[[int, str], None], camera_index: int = 0):
        """callback(player_id, action_name)"""
        self.callback = callback
        self.camera_index = camera_index
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # if a mediapipe_capture singleton is available we will prefer
        # reading its latest landmarks rather than opening our own camera.
        self._use_mc = False

        # state per player
        self._last_wrist_x = {0: None, 1: None}
        self._last_time = {0: None, 1: None}
        self._cooldown_until = {0: 0.0, 1: 0.0}

        # thresholds (tweak as needed)
        self.punch_vel_threshold = 0.15  # normalized x/sec
        self.punch_disp_threshold = 0.08  # normalized displacement from shoulder
        self.kick_height_threshold = 0.10  # ankle above hip (normalized)
        self.jump_height_threshold = 0.12  # hip y decrease from baseline
        self.cooldown_seconds = 0.6

        # baseline hip y for jump detection (per player)
        self._hip_baseline = {0: None, 1: None}

    def start(self):
        if self._running:
            return
        if mp is None:
            print("ActionDetector: mediapipe not available")
            return
        # prefer using mediapipe_capture's landmarks if present
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

        if self._use_mc:
            # Use mediapipe_capture singleton's landmarks rather than opening
            # a second VideoCapture. This polling approach avoids device lock
            # conflicts on single-camera systems.
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

                    # helper to read landmark safely from lm_list (list of (x,y))
                    def L(idx: int) -> Optional[Tuple[float, float]]:
                        try:
                            v = lm_list[idx]
                            return (v[0], v[1])
                        except Exception:
                            return None

                    # keypoints we use
                    nose = L(mp_pose.PoseLandmark.NOSE.value)
                    left_shoulder = L(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
                    right_shoulder = L(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
                    left_wrist = L(mp_pose.PoseLandmark.LEFT_WRIST.value)
                    right_wrist = L(mp_pose.PoseLandmark.RIGHT_WRIST.value)
                    left_hip = L(mp_pose.PoseLandmark.LEFT_HIP.value)
                    right_hip = L(mp_pose.PoseLandmark.RIGHT_HIP.value)
                    left_ankle = L(mp_pose.PoseLandmark.LEFT_ANKLE.value)
                    right_ankle = L(mp_pose.PoseLandmark.RIGHT_ANKLE.value)

                    now = time.time()

                    # decide which player each landmark belongs to by nose x
                    if nose is None:
                        time.sleep(0.005)
                        continue
                    player_id = 0 if nose[0] < 0.5 else 1

                    # choose side-specific landmarks
                    if player_id == 0:
                        shoulder = left_shoulder
                        wrist = left_wrist
                        hip = left_hip
                        ankle = left_ankle
                        facing_dir = 1.0  # punching to the right
                    else:
                        shoulder = right_shoulder
                        wrist = right_wrist
                        hip = right_hip
                        ankle = right_ankle
                        facing_dir = -1.0  # punching to the left

                    # initialize baseline hip
                    if hip and self._hip_baseline[player_id] is None:
                        self._hip_baseline[player_id] = hip[1]

                    # compute wrist velocity
                    prev_x = self._last_wrist_x[player_id]
                    prev_t = self._last_time[player_id]
                    self._last_time[player_id] = now
                    if wrist:
                        self._last_wrist_x[player_id] = wrist[0]
                    # velocity in normalized units per second
                    vel_x = 0.0
                    if prev_x is not None and prev_t is not None and wrist:
                        dt = max(1e-3, now - prev_t)
                        vel_x = (wrist[0] - prev_x) / dt

                    # check cooldown
                    if now < self._cooldown_until[player_id]:
                        time.sleep(0.005)
                        continue

                    # punch detection: wrist moving quickly outward and displaced past shoulder
                    punch_disp = None
                    if wrist and shoulder:
                        punch_disp = (wrist[0] - shoulder[0]) * facing_dir

                    if punch_disp is not None and punch_disp > self.punch_disp_threshold and vel_x * facing_dir > self.punch_vel_threshold:
                        # detected punch
                        self._cooldown_until[player_id] = now + self.cooldown_seconds
                        try:
                            self.callback(player_id, 'punch')
                            try:
                                if mc and hasattr(mc, 'set_latest_action'):
                                    mc.set_latest_action(player_id, 'PUNCH')
                            except Exception:
                                pass
                        except Exception:
                            pass
                        time.sleep(0.01)
                        continue

                    # kick detection: ankle higher (smaller y) than hip by threshold
                    if ankle and hip:
                        if (hip[1] - ankle[1]) > self.kick_height_threshold:
                            self._cooldown_until[player_id] = now + self.cooldown_seconds
                            try:
                                self.callback(player_id, 'kick')
                                try:
                                    if mc and hasattr(mc, 'set_latest_action'):
                                        mc.set_latest_action(player_id, 'KICK')
                                except Exception:
                                    pass
                            except Exception:
                                pass
                            time.sleep(0.01)
                            continue

                    # jump detection: hip y drops significantly from baseline
                    baseline = self._hip_baseline[player_id]
                    if hip and baseline is not None:
                        if (baseline - hip[1]) > self.jump_height_threshold:
                            self._cooldown_until[player_id] = now + self.cooldown_seconds
                            try:
                                self.callback(player_id, 'jump')
                                try:
                                    if mc and hasattr(mc, 'set_latest_action'):
                                        mc.set_latest_action(player_id, 'JUMP')
                                except Exception:
                                    pass
                            except Exception:
                                pass
                            time.sleep(0.01)
                            continue

                    # small sleep to avoid hogging CPU
                    time.sleep(0.005)
                except Exception:
                    time.sleep(0.02)

        else:
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                print("ActionDetector: unable to open camera")
                self._running = False
                return

            mp_pose = mp.solutions.pose
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while self._running and cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = pose.process(img_rgb)

                    if results and results.pose_landmarks:
                        # landmarks are normalized in [0,1]
                        lm = results.pose_landmarks.landmark

                        # helper to read landmark safely
                        def L(idx: int) -> Optional[Tuple[float, float]]:
                            try:
                                v = lm[idx]
                                return (v.x, v.y)
                            except Exception:
                                return None

                        # keypoints we use
                        nose = L(mp_pose.PoseLandmark.NOSE.value)
                        left_shoulder = L(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
                        right_shoulder = L(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
                        left_wrist = L(mp_pose.PoseLandmark.LEFT_WRIST.value)
                        right_wrist = L(mp_pose.PoseLandmark.RIGHT_WRIST.value)
                        left_hip = L(mp_pose.PoseLandmark.LEFT_HIP.value)
                        right_hip = L(mp_pose.PoseLandmark.RIGHT_HIP.value)
                        left_ankle = L(mp_pose.PoseLandmark.LEFT_ANKLE.value)
                        right_ankle = L(mp_pose.PoseLandmark.RIGHT_ANKLE.value)

                        now = time.time()

                        # decide which player each landmark belongs to by nose x
                        if nose is None:
                            continue
                        player_id = 0 if nose[0] < 0.5 else 1

                        # choose side-specific landmarks
                        if player_id == 0:
                            shoulder = left_shoulder
                            wrist = left_wrist
                            hip = left_hip
                            ankle = left_ankle
                            facing_dir = 1.0  # punching to the right
                        else:
                            shoulder = right_shoulder
                            wrist = right_wrist
                            hip = right_hip
                            ankle = right_ankle
                            facing_dir = -1.0  # punching to the left

                        # initialize baseline hip
                        if hip and self._hip_baseline[player_id] is None:
                            self._hip_baseline[player_id] = hip[1]

                        # compute wrist velocity
                        prev_x = self._last_wrist_x[player_id]
                        prev_t = self._last_time[player_id]
                        self._last_time[player_id] = now
                        if wrist:
                            self._last_wrist_x[player_id] = wrist[0]
                        # velocity in normalized units per second
                        vel_x = 0.0
                        if prev_x is not None and prev_t is not None and wrist:
                            dt = max(1e-3, now - prev_t)
                            vel_x = (wrist[0] - prev_x) / dt

                        # check cooldown
                        if now < self._cooldown_until[player_id]:
                            continue

                        # punch detection: wrist moving quickly outward and displaced past shoulder
                        punch_disp = None
                        if wrist and shoulder:
                            punch_disp = (wrist[0] - shoulder[0]) * facing_dir

                        if punch_disp is not None and punch_disp > self.punch_disp_threshold and vel_x * facing_dir > self.punch_vel_threshold:
                            # detected punch
                            self._cooldown_until[player_id] = now + self.cooldown_seconds
                            try:
                                self.callback(player_id, 'punch')
                            except Exception:
                                pass
                            continue

                        # kick detection: ankle higher (smaller y) than hip by threshold
                        if ankle and hip:
                            if (hip[1] - ankle[1]) > self.kick_height_threshold:
                                self._cooldown_until[player_id] = now + self.cooldown_seconds
                                try:
                                    self.callback(player_id, 'kick')
                                except Exception:
                                    pass
                                continue

                        # jump detection: hip y drops significantly from baseline
                        baseline = self._hip_baseline[player_id]
                        if hip and baseline is not None:
                            if (baseline - hip[1]) > self.jump_height_threshold:
                                self._cooldown_until[player_id] = now + self.cooldown_seconds
                                try:
                                    self.callback(player_id, 'jump')
                                except Exception:
                                    pass
                                continue

                    # small sleep to avoid hogging CPU
                    time.sleep(0.01)

                cap.release()


__all__ = ["ActionDetector"]
