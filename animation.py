"""
Action pose data module
Defines pose data for various actions
"""


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
            'torso': {'rotation': 0, 'position': [0, -45]},
            'head': {'rotation': 0, 'position': [0, -77]},

            # Left arm
            'left_upper_arm': {'rotation': 15, 'position': [-76, -80]},
            'left_forearm': {'rotation': 25, 'position': [-59, 15]},

            # Right arm
            'right_upper_arm': {'rotation': -15, 'position': [76, -80]},
            'right_forearm': {'rotation': -25, 'position': [59, 15]},

            # Left leg
            'left_thigh': {'rotation': 25, 'position': [-44, 63]},
            'left_shin': {'rotation': -45, 'position': [-5, 85]},

            # Right leg
            'right_thigh': {'rotation': -25, 'position': [44, 63]},
            'right_shin': {'rotation': 45, 'position': [5, 85]}
        }

    @staticmethod
    def load_custom_pose(pose_name):
        """从JSON文件加载自定义姿势

        Args:
            pose_name: 姿势名称，例如 'custom'

        Returns:
            姿势数据字典，如果加载失败返回None
        """
        import os
        import json

        json_file = f'pose_{pose_name}.json'

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
        """返回所有姿势的字典，包括自定义姿势"""
        poses = {
            'block': Poses.get_block(),
            'ready': Poses.get_ready(),
            'punch': Poses.get_punch(),
            'kick': Poses.get_kick(),
            'jump': Poses.get_jump()
        }

        # 尝试加载自定义姿势（仅作为独立的第5个姿势）
        custom_pose = Poses.load_custom_pose('custom')
        if custom_pose:
            poses['custom'] = custom_pose
            print("✓ 已加载自定义姿势")

        return poses


class AnimationController:
    """Animation controller - handles smooth transitions between poses"""

    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.current_pose = 'ready'
        self.target_pose = 'ready'
        self.transition_progress = 1.0  # 0.0 to 1.0
        self.transition_speed = 0.4  # Transition speed per frame (faster)

        self.poses = Poses.get_all_poses()
        self.start_pose_data = {}
        self.target_pose_data = {}

        # Automatic action return
        self.auto_return = True  # Whether to auto-return to ready pose
        # Frames to wait after action completes before returning (faster recovery)
        self.return_delay = 8
        self.return_timer = 0
        self.action_poses = ['punch', 'kick',
                             'jump', 'block', 'custom']  # Poses that auto-return

        # Idle animation (subtle sway in ready pose)
        self.idle_time = 0
        self.idle_sway_speed = 0.03  # Sway speed
        self.idle_sway_amount = 1.5  # Sway amplitude (degrees)

    def reload_poses(self):
        """Reload all poses, including new custom poses"""
        self.poses = Poses.get_all_poses()
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

    def update(self):
        """Update animation state"""
        if self.transition_progress < 1.0:
            # Transitioning
            self.transition_progress = min(
                1.0, self.transition_progress + self.transition_speed)

            # Use improved easing function (ease-in-out)
            t = self.transition_progress
            # Smoother easing curve
            if t < 0.5:
                eased_t = 2 * t * t
            else:
                eased_t = 1 - 2 * (1 - t) * (1 - t)

            # Interpolate current pose
            interpolated_pose = {}
            for part_name in self.target_pose_data:
                if part_name in self.start_pose_data:
                    start_data = self.start_pose_data[part_name]
                    target_data = self.target_pose_data[part_name]

                    interpolated_pose[part_name] = {
                        'rotation': self._lerp_angle(
                            start_data['rotation'],
                            target_data['rotation'],
                            eased_t
                        ),
                        'position': [
                            self._lerp(
                                start_data['position'][0], target_data['position'][0], eased_t),
                            self._lerp(
                                start_data['position'][1], target_data['position'][1], eased_t)
                        ]
                    }

            # Apply interpolated pose
            self.skeleton.apply_pose(interpolated_pose)

            # Transition complete
            if self.transition_progress >= 1.0:
                self.current_pose = self.target_pose
                # If action pose, start return timer
                if self.auto_return and self.current_pose in self.action_poses:
                    self.return_timer = self.return_delay

        else:
            # Transition complete
            # Handle auto-return
            if self.return_timer > 0:
                self.return_timer -= 1
                if self.return_timer == 0:
                    # Return to ready pose
                    self.set_pose('ready')

            # Idle animation (only in ready pose) - torso breathing effect (feet stay still)
            elif self.current_pose == 'ready' and self.target_pose == 'ready':
                self.idle_time += self.idle_sway_speed

                # Calculate torso vertical movement (breathing effect)
                import math
                # Torso vertical movement amplitude (breathing feel)
                # 2 pixels up and down
                vertical_sway = math.sin(self.idle_time) * 2.0

                # Only adjust torso position (upper body breathing), legs stay still
                if 'torso' in self.skeleton.parts:
                    base_pos = self.poses['ready']['torso']['position']
                    # Torso moves up/down (negative is upward)
                    self.skeleton.parts['torso'].local_position[0] = base_pos[0]
                    self.skeleton.parts['torso'].local_position[1] = base_pos[1] - vertical_sway

                    # Keep torso rotation unchanged
                    base_rotation = self.poses['ready']['torso']['rotation']
                    self.skeleton.parts['torso'].local_rotation = base_rotation
