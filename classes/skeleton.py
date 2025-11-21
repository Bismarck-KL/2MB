"""
Skeletal system module
Manages hierarchical relationships and rotations of body parts
"""

import pygame
import math


class BodyPart:
    """Single body part class"""

    def __init__(self, name, image, pivot_offset=(0, 0), parent=None):
        """
        Args:
            name: Part name
            image: pygame Surface object
            pivot_offset: Rotation center offset from top-left corner of image (x, y)
            parent: Parent BodyPart object
        """
        self.name = name
        self.image = image
        self.pivot_offset = pivot_offset  # Rotation center
        self.parent = parent
        self.children = []

        # Position and rotation relative to parent
        self.local_position = [0, 0]  # Position relative to parent
        self.local_rotation = 0  # Rotation angle relative to parent (degrees)

        # World coordinates (calculated)
        self.world_position = [0, 0]
        self.world_rotation = 0

        if parent:
            parent.add_child(self)

    def add_child(self, child):
        """Add child part"""
        self.children.append(child)
        child.parent = self

    def update_transform(self, root_base_position=None):
        """Update world transform (recursively updates all child nodes)

        Args:
            root_base_position: Base world position of root node (set by Skeleton.set_position)
        """
        if self.parent:
            # Calculate world rotation
            self.world_rotation = self.parent.world_rotation + self.local_rotation

            # Calculate world position (considering parent rotation)
            parent_angle_rad = math.radians(self.parent.world_rotation)
            rotated_x = (self.local_position[0] * math.cos(parent_angle_rad) -
                         self.local_position[1] * math.sin(parent_angle_rad))
            rotated_y = (self.local_position[0] * math.sin(parent_angle_rad) +
                         self.local_position[1] * math.cos(parent_angle_rad))

            self.world_position[0] = self.parent.world_position[0] + rotated_x
            self.world_position[1] = self.parent.world_position[1] + rotated_y
        else:
            # Root node: use base position + local_position offset
            self.world_rotation = self.local_rotation
            if root_base_position:
                self.world_position[0] = root_base_position[0] + \
                    self.local_position[0]
                self.world_position[1] = root_base_position[1] + \
                    self.local_position[1]

        # Recursively update all child nodes
        for child in self.children:
            child.update_transform(root_base_position)

    def draw(self, surface):
        """Draw this part and all child parts with layering"""
        # Define draw order
        back_parts = ['left_upper_arm', 'right_upper_arm',
                      'left_thigh', 'right_thigh']
        # Forearms in front of torso
        front_parts = ['left_forearm', 'right_forearm']

        # Layer 1: Draw upper arms and thighs (behind torso) - but NOT their forearm children
        for child in self.children:
            if child.name in back_parts:
                self._draw_self_only(child, surface)
                # Draw leg children (shins) immediately since they stay behind
                if 'thigh' in child.name:
                    for grandchild in child.children:
                        grandchild.draw(surface)

        # Layer 2: Draw this part (torso)
        self._draw_self_only(self, surface)

        # Layer 3: Draw head (behind forearms)
        for child in self.children:
            if child.name == 'head':
                child.draw(surface)

        # Layer 4: Draw forearms (in front of torso and head)
        for child in self.children:
            if child.name in back_parts and 'arm' in child.name:
                for grandchild in child.children:
                    if grandchild.name in front_parts:
                        grandchild.draw(surface)

    def _draw_self_only(self, part, surface):
        """Draw only this part, not its children"""
        # Rotate image (around pivot point)
        rotated_image = pygame.transform.rotate(
            part.image, -part.world_rotation)
        rotated_rect = rotated_image.get_rect()

        # Calculate pivot point position relative to image top-left corner
        pivot_x, pivot_y = part.pivot_offset

        # Calculate new position of pivot point after rotation
        angle_rad = math.radians(part.world_rotation)

        # Pivot offset relative to original image center
        offset_x = pivot_x - part.image.get_width() / 2
        offset_y = pivot_y - part.image.get_height() / 2

        # Offset after rotation
        rot_offset_x = offset_x * \
            math.cos(angle_rad) - offset_y * math.sin(angle_rad)
        rot_offset_y = offset_x * \
            math.sin(angle_rad) + offset_y * math.cos(angle_rad)

        # Final draw position
        draw_x = part.world_position[0] - rotated_rect.width / 2 - rot_offset_x
        draw_y = part.world_position[1] - \
            rotated_rect.height / 2 - rot_offset_y

        surface.blit(rotated_image, (draw_x, draw_y))


class Skeleton:
    """Skeletal system - manages body part hierarchy for entire character"""

    def __init__(self):
        self.root = None  # Root part (usually torso)
        self.parts = {}  # Dictionary of all parts {name: BodyPart}
        self.root_offset = [0, 0]  # Global position offset of root part

    def set_root(self, body_part):
        """Set root part"""
        self.root = body_part
        self.parts[body_part.name] = body_part

    def add_part(self, body_part):
        """Add part to dictionary"""
        self.parts[body_part.name] = body_part

    def get_part(self, name):
        """Get part by name"""
        return self.parts.get(name)

    def set_position(self, x, y):
        """Set world coordinates of root part"""
        self.root_offset = [x, y]
        if self.root:
            # Only modify root part's world_position when setting position, don't affect local_position
            self.root.world_position = [x, y]

    def update(self):
        """Update all transforms"""
        if self.root:
            # Start updating transforms from root part, passing in base position
            self.root.update_transform(root_base_position=self.root_offset)

    def draw(self, surface):
        """Draw entire skeleton"""
        if self.root:
            self.root.draw(surface)

    def apply_pose(self, pose_data):
        """Apply pose data

        Args:
            pose_data: Dictionary, format {part_name: {'rotation': angle, 'position': [x, y]}}
        """
        for part_name, data in pose_data.items():
            part = self.get_part(part_name)
            if part:
                if 'rotation' in data:
                    part.local_rotation = data['rotation']
                if 'position' in data:
                    part.local_position = data['position'].copy()