"""Skeleton data structure for assembling body parts and applying poses"""

from .body_parts import BodyPart, BodyParts


class Skeleton:
    def __init__(self):
        self.parts = {}

    def add_part(self, part: BodyPart):
        self.parts[part.name] = part

    def apply_pose(self, pose_data: dict):
        """Apply pose data to parts (pose_data maps part_name -> {'rotation', 'position'})"""
        for part_name, data in pose_data.items():
            if part_name in self.parts:
                part = self.parts[part_name]
                part.local_rotation = data.get('rotation', part.local_rotation)
                pos = data.get('position')
                if pos:
                    part.local_position[0] = pos[0]
                    part.local_position[1] = pos[1]


class BodyPartInstance(BodyPart):
    pass
