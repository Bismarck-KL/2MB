"""Body parts definitions and utilities
This module defines a BodyPart container and helper utilities used by
the skeleton/animated character logic.
"""

class BodyPart:
    def __init__(self, name, length=0, parent=None, position=(0, 0), rotation=0):
        self.name = name
        self.length = length
        self.parent = parent
        self.local_position = list(position)
        self.local_rotation = rotation
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def __repr__(self):
        return f"BodyPart({self.name}, len={self.length}, pos={self.local_position}, rot={self.local_rotation})"


class BodyParts:
    """Holds a dict of named BodyPart instances for easy access"""

    def __init__(self):
        self.parts = {}

    def add(self, part: BodyPart):
        self.parts[part.name] = part

    def get(self, name):
        return self.parts.get(name)

    def __iter__(self):
        return iter(self.parts.items())
