"""
Body part slicing module
Defines bounding boxes for body parts based on provided slice sample image
"""


class BodyParts:
    """Defines slice regions for body parts (based on colored boxes in slice_sample.png)"""

    def __init__(self):
        self.head = (462, 65, 104, 104)
        self.torso = (447, 172, 133, 160)
        self.left_upper_arm = (380, 161, 65, 74)
        self.left_forearm = (218, 161, 160, 75)
        self.right_upper_arm = (583, 161, 65, 74)
        self.right_forearm = (650, 161, 160, 75)
        self.left_thigh = (433, 363, 79, 113)
        self.left_shin = (431, 485, 72, 169)
        self.right_thigh = (516, 363, 79, 113)
        self.right_shin = (525, 485, 72, 169)

    def get_all_parts(self):
        """Return dictionary of all body parts"""
        return {
            'head': self.head,
            'torso': self.torso,
            'left_upper_arm': self.left_upper_arm,
            'left_forearm': self.left_forearm,
            'right_upper_arm': self.right_upper_arm,
            'right_forearm': self.right_forearm,
            'left_thigh': self.left_thigh,
            'left_shin': self.left_shin,
            'right_thigh': self.right_thigh,
            'right_shin': self.right_shin,
        }
