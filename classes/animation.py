"""
Action pose data module
Defines pose data for various actions
"""
import os
import json
import math

class Poses:
    """Stores pose data for various actions"""

    @staticmethod
    def get_block():
        return {
            'torso': {'rotation': 0, 'position': [0, 7]},
            'head': {'rotation': 0, 'position': [0, -70]},

            # Left arm
            'left_upper_arm': {'rotation': -45, 'position': [-76, -68]},
            'left_forearm': {'rotation': -155, 'position': [-36, 31]},

            # Right arm
            'right_upper_arm': {'rotation': 45, 'position': [76, -68]},
            'right_forearm': {'rotation': 155, 'position': [36, 31]},

            # Left leg
            'left_thigh': {'rotation': 5, 'position': [-44, 88]},
            'left_shin': {'rotation': -10, 'position': [-11, 72]},

            # Right leg
            'right_thigh': {'rotation': -5, 'position': [44, 88]},
            'right_shin': {'rotation': 10, 'position': [11, 72]}
        }

    @staticmethod
    def get_ready():
        """Ready pose (battle ready)
        Uses values saved in pose_custom.json
        """
        return {
            'torso': {'rotation': 0, 'position': [0, 2]},
            'head': {'rotation': 0, 'position': [0, -70]},

            # Left arm
            'left_upper_arm': {'rotation': -50, 'position': [-76, -69]},
            'left_forearm': {'rotation': -45, 'position': [-56, 35]},

            # Right arm
            'right_upper_arm': {'rotation': 50, 'position': [76, -69]},
            'right_forearm': {'rotation': 45, 'position': [56, 35]},

            # Left leg
            'left_thigh': {'rotation': 0, 'position': [-39, 74]},
            'left_shin': {'rotation': 0, 'position': [-7, 90]},

            # Right leg
            'right_thigh': {'rotation': 0, 'position': [39, 74]},
            'right_shin': {'rotation': 0, 'position': [7, 90]}
        }

    @staticmethod
    def get_punch():
        """Punch pose (right straight punch)
        Feet planted, torso lowered to drop center of gravity
        """
        return {
            'torso': {'rotation': 0, 'position': [0, 7]},
            'head': {'rotation': 0, 'position': [0, -72]},

            # Left arm
            'left_upper_arm': {'rotation': -25, 'position': [-76, -68]},
            'left_forearm': {'rotation': -75, 'position': [-58, 27]},

            # Right arm
            'right_upper_arm': {'rotation': -5, 'position': [76, -74]},
            'right_forearm': {'rotation': 5, 'position': [58, 27]},

            # Left leg
            'left_thigh': {'rotation': 17, 'position': [-42, 84]},
            'left_shin': {'rotation': -18, 'position': [-4, 78]},

            # Right leg
            'right_thigh': {'rotation': -17, 'position': [42, 84]},
            'right_shin': {'rotation': 18, 'position': [4, 78]}
        }

    @staticmethod
    def get_kick():
        """Kick pose (right high kick)
        Center of gravity on support leg, torso lowered for balance
        """
        return {
            'torso': {'rotation': -8, 'position': [-15, -5]},
            'head': {'rotation': -5, 'position': [0, -79]},

            # Left arm
            'left_upper_arm': {'rotation': -50, 'position': [-76, -68]},
            'left_forearm': {'rotation': -25, 'position': [-59, 30]},

            # Right arm
            'right_upper_arm': {'rotation': 20, 'position': [76, -68]},
            'right_forearm': {'rotation': 60, 'position': [58, 27]},

            # Left leg
            'left_thigh': {'rotation': 17, 'position': [-40, 87]},
            'left_shin': {'rotation': -8, 'position': [-2, 76]},

            # Right leg
            'right_thigh': {'rotation': -90, 'position': [14, 85]},
            'right_shin': {'rotation': -5, 'position': [6, 80]}
        }

    @staticmethod
    def get_jump():
        """Jump pose
        Legs tucked, arms swinging down, overall body rising
        """
        return {
            'torso': {'rotation': 0, 'position': [0, -98]},
            'head': {'rotation': 0, 'position': [0, -77]},

            # Left arm
            'left_upper_arm': {'rotation': 15, 'position': [-67, -80]},
            'left_forearm': {'rotation': -55, 'position': [-49, 35]},

            # Right arm
            'right_upper_arm': {'rotation': -15, 'position': [67, -80]},
            'right_forearm': {'rotation': 55, 'position': [49, 35]},

            # Left leg
            'left_thigh': {'rotation': 25, 'position': [-44, 63]},
            'left_shin': {'rotation': -45, 'position': [-5, 85]},

            # Right leg
            'right_thigh': {'rotation': -25, 'position': [44, 63]},
            'right_shin': {'rotation': 45, 'position': [5, 85]}
        }

    @staticmethod
    def get_hurt():
        return {
            'torso': {'rotation': -15, 'position': [-31, -5]},
            'head': {'rotation': -10, 'position': [-5, -68]},

            # Left arm
            'left_upper_arm': {'rotation': -40, 'position': [-77, -64]},
            'left_forearm': {'rotation': -90, 'position': [-48, 32]},

            # Right arm
            'right_upper_arm': {'rotation': 30, 'position': [80, -65]},
            'right_forearm': {'rotation': 70, 'position': [43, 34]},

            # Left leg
            'left_thigh': {'rotation': 20, 'position': [-38, 76]},
            'left_shin': {'rotation': -5, 'position': [-8, 88]},

            # Right leg
            'right_thigh': {'rotation': -15, 'position': [42, 76]},
            'right_shin': {'rotation': 30, 'position': [8, 88]}
        }

    @staticmethod
    def load_custom_pose(pose_name):
        """从JSON文件加载自定义姿势

        Args:
            pose_name: 姿势名称，例如 'custom'

        Returns:
            姿势数据字典，如果加载失败返回None
        """

        # Look for custom poses inside assets/poses/ by convention
        json_file = os.path.join("assets", "poses", f'pose_{pose_name}.json')

        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载姿势失败 {pose_name}: {e}")
                return None
        return None

    @staticmethod
    def get_all_poses():
        """返回所有姿勢的字典，優先從 poses_all.json 載入"""

        
        # Attempt to load poses_all.json and merge with any individual pose_*.json
        poses = {}
        
        json_path = os.path.join("assets","poses", "poses_all.json")

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    poses = json.load(f) or {}
                print(f"✓ Loaded {len(poses)} poses from poses_all.json")
            except Exception as e:
                print(f"⚠ Failed to load poses_all.json: {e}")
                print("  Will use hardcoded poses as fallback for missing entries")

        # If poses_all.json didn't provide entries for core poses, ensure defaults exist
        if not poses:
            poses = {
                'block': Poses.get_block(),
                'ready': Poses.get_ready(),
                'punch': Poses.get_punch(),
                'kick': Poses.get_kick(),
                'jump': Poses.get_jump(),
                'hurt': Poses.get_hurt()
            }

        # Try to load custom pose (as independent pose) and merge/override
        custom_pose = Poses.load_custom_pose('custom')
        if custom_pose:
            poses['custom'] = custom_pose
            print("✓ Loaded custom pose from pose_custom.json")

        # Additionally, load any individual pose_*.json files found in the
        # working directory so the PoseEditor can save poses and have them
        # discovered automatically. These will override entries from
        # poses_all.json when name collisions occur.
        # Additionally, load any individual pose_*.json files found in assets/poses
        try:
            assets_dir = os.path.join("assets", "poses")
            if os.path.isdir(assets_dir):
                for fname in os.listdir(assets_dir):
                    if fname.startswith('pose_') and fname.lower().endswith('.json'):
                        try:
                            name = fname[len('pose_'):-5]
                            path = os.path.join(assets_dir, fname)
                            with open(path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if isinstance(data, dict):
                                poses[name] = data
                        except Exception:
                            pass
        except Exception:
            pass

        return poses


class AnimationController:
    """Animation controller - handles smooth transitions between poses"""

    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.current_pose = 'ready'
        self.target_pose = 'ready'
        self.transition_progress = 1.0  # 0.0 to 1.0
        # Transition duration in seconds (how long a transition should take)
        # Smaller = faster. Default lowered to 0.12s for snappier feel.
        self.transition_duration = 0.12
        # per-pose metadata loaded from pose JSONs (key -> meta dict)
        self.pose_meta = {}
        # helper to remember previous controller settings while a pose's meta is applied
        self._meta_prev = None
        self._meta_applied_pose = None

        self.poses = Poses.get_all_poses()
        self.start_pose_data = {}
        self.target_pose_data = {}

        # Automatic action return
        self.auto_return = True  # Whether to auto-return to ready pose
        # Time to wait (seconds) after action completes before returning
        # Previously this was 8 frames; default set to ~8/60 seconds for parity.
        self.return_delay = 8.0 / 60.0
        self.return_timer = 0.0
        self.action_poses = ['punch', 'kick',
                     'jump', 'block', 'hurt', 'custom']  # Poses that auto-return

        # Idle animation (subtle sway in ready pose)
        self.idle_time = 0.0
        # idle_sway_speed scales how fast the idle oscillation advances (radians/sec)
        self.idle_sway_speed = 1.5
        # amplitude in pixels/degrees for sway
        self.idle_sway_amount = 1.5  # Sway amplitude (degrees)

    def reload_poses(self):
        """Reload all poses, including new custom poses"""
        self.poses = Poses.get_all_poses()
        # extract any per-pose __meta__ fields and remove them from pose data
        self.pose_meta = {}
        try:
            for name, data in list(self.poses.items()):
                if isinstance(data, dict) and '__meta__' in data:
                    try:
                        meta = data.get('__meta__') or {}
                        if isinstance(meta, dict):
                            self.pose_meta[name] = meta
                        # strip the meta entry from the stored pose
                        cleaned = {k: v for k, v in data.items() if k != '__meta__'}
                        self.poses[name] = cleaned
                    except Exception:
                        pass
        except Exception:
            pass
        print(
            f"Reloaded poses, currently available: {list(self.poses.keys())}")

    def set_pose(self, pose_name, immediate=False):
        """Set target pose

        Args:
            pose_name: Pose name ('tpose', 'ready', 'punch', 'kick', 'custom')
            immediate: Whether to switch immediately (no transition)
        """
        # If pose doesn't exist, try reloading
        if pose_name not in self.poses:
            self.reload_poses()

        if pose_name not in self.poses:
            print(f"Pose '{pose_name}' does not exist")
            return

        # If already targeting this pose and transitioning, ignore duplicate input (prevent stiffness)
        if pose_name == self.target_pose and self.transition_progress < 1.0:
            return

        # If already completed this pose and not ready, also ignore (prevent re-execution)
        if pose_name == self.current_pose and pose_name != 'ready' and self.transition_progress >= 1.0:
            return

        # Cancel return timer
        self.return_timer = 0

        # Reset idle time
        if pose_name != 'ready':
            self.idle_time = 0

        if immediate:
            self.current_pose = pose_name
            self.target_pose = pose_name
            self.transition_progress = 1.0
            self.skeleton.apply_pose(self.poses[pose_name])
        else:
            if pose_name != self.target_pose:
                # 保存当前状态作为起始姿势
                self.start_pose_data = self._get_current_pose_data()
                self.target_pose = pose_name
                self.target_pose_data = self.poses[pose_name]
                self.transition_progress = 0.0

                # If this pose has per-pose metadata, apply it now (and remember previous controller settings)
                meta = self.pose_meta.get(pose_name)
                if meta:
                    try:
                        self._meta_prev = {
                            'transition_duration': float(self.transition_duration),
                            'auto_return': bool(self.auto_return),
                            'return_delay': float(self.return_delay),
                        }
                    except Exception:
                        self._meta_prev = None

                    # apply meta values if present
                    try:
                        if 'duration' in meta:
                            self.transition_duration = float(meta['duration'])
                    except Exception:
                        pass
                    try:
                        if 'auto_return' in meta:
                            self.auto_return = bool(meta['auto_return'])
                    except Exception:
                        pass
                    try:
                        if 'return_delay' in meta:
                            self.return_delay = float(meta['return_delay'])
                    except Exception:
                        pass
                    # mark applied so we can restore later
                    self._meta_applied_pose = pose_name

    def _get_current_pose_data(self):
        """Get current skeletal pose data"""
        current_data = {}
        for part_name, part in self.skeleton.parts.items():
            current_data[part_name] = {
                'rotation': part.local_rotation,
                'position': part.local_position.copy()
            }
        return current_data

    def _lerp(self, a, b, t):
        """Linear interpolation"""
        return a + (b - a) * t

    def _lerp_angle(self, a, b, t):
        """Angle linear interpolation (handles 360-degree wraparound)"""
        diff = b - a
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        return a + diff * t

    def update(self, dt: float = 1.0 / 60.0):
        """Update animation state.

        Args:
            dt: delta time in seconds since last update.
        """

        if self.transition_progress < 1.0:
            if self.transition_duration <= 0:
                self.transition_progress = 1.0
            else:
                self.transition_progress = min(1.0, self.transition_progress + (dt / float(self.transition_duration)))

            t = self.transition_progress
            if t < 0.5:
                eased_t = 2 * t * t
            else:
                eased_t = 1 - 2 * (1 - t) * (1 - t)

            interpolated_pose = {}
            for part_name in self.target_pose_data:
                if part_name in self.start_pose_data:
                    start_data = self.start_pose_data[part_name]
                    target_data = self.target_pose_data[part_name]

                    interpolated_pose[part_name] = {
                        'rotation': self._lerp_angle(start_data['rotation'], target_data['rotation'], eased_t),
                        'position': [
                            self._lerp(start_data['position'][0], target_data['position'][0], eased_t),
                            self._lerp(start_data['position'][1], target_data['position'][1], eased_t)
                        ]
                    }

            self.skeleton.apply_pose(interpolated_pose)

            if self.transition_progress >= 1.0:
                self.current_pose = self.target_pose
                if self.auto_return and self.current_pose in self.action_poses:
                    self.return_timer = float(self.return_delay)

        else:
            # auto-return based on seconds
            if self.return_timer > 0.0:
                self.return_timer -= dt
                if self.return_timer <= 0.0:
                    self.set_pose('ready')

            elif self.current_pose == 'ready' and self.target_pose == 'ready':
                # advance idle phase scaled by time
                self.idle_time += self.idle_sway_speed * dt
                vertical_sway = math.sin(self.idle_time) * self.idle_sway_amount

                # apply torso vertical sway (defensive try/except)
                if 'torso' in self.skeleton.parts:
                    try:
                        base_pos = self.poses['ready']['torso']['position']
                        self.skeleton.parts['torso'].local_position[0] = base_pos[0]
                        self.skeleton.parts['torso'].local_position[1] = base_pos[1] - vertical_sway
                    except Exception:
                        pass

                    try:
                        base_rotation = self.poses['ready']['torso']['rotation']
                        self.skeleton.parts['torso'].local_rotation = base_rotation
                    except Exception:
                        pass
                # if we had applied per-pose meta earlier, restore controller settings now
                if self._meta_applied_pose is not None and self._meta_prev is not None:
                    try:
                        self.transition_duration = float(self._meta_prev.get('transition_duration', self.transition_duration))
                    except Exception:
                        pass
                    try:
                        self.auto_return = bool(self._meta_prev.get('auto_return', self.auto_return))
                    except Exception:
                        pass
                    try:
                        self.return_delay = float(self._meta_prev.get('return_delay', self.return_delay))
                    except Exception:
                        pass
                    # clear meta state
                    self._meta_prev = None
                    self._meta_applied_pose = None