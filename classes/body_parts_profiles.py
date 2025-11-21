"""Profiles / presets for body parts sizes and offsets
This module provides mappings for different body part presets used by
the character builder and editor tools.

It also includes a lightweight compatibility shim (BodyPartsConfig)
used by the AnimatedCharacter class to obtain crop rectangles for a
given T-pose surface. When explicit metadata is missing the shim will
heuristically slice the image so the game remains runnable.
"""

DEFAULT_PROFILE = {
    'torso': {'length': 90, 'position': [0, 0]},
    'head': {'length': 24, 'position': [0, -70]},

    'left_upper_arm': {'length': 42, 'position': [-76, -68]},
    'left_forearm': {'length': 36, 'position': [-36, 31]},

    'right_upper_arm': {'length': 42, 'position': [76, -68]},
    'right_forearm': {'length': 36, 'position': [36, 31]},

    'left_thigh': {'length': 50, 'position': [-44, 88]},
    'left_shin': {'length': 50, 'position': [-11, 72]},

    'right_thigh': {'length': 50, 'position': [44, 88]},
    'right_shin': {'length': 50, 'position': [11, 72]},
}

PROFILES = {
    'default': DEFAULT_PROFILE,
}


class BodyPartsConfig:
    """Compatibility shim for tools and AnimatedCharacter.

    The original project stored crop rectangles for each body part. To
    remain robust, this class exposes from_surface and from_image_path
    factory methods and a get_all_parts() accessor; it will attempt to
    infer reasonable crop rects from the given surface when explicit
    metadata is not available.
    """

    def __init__(self, parts_map=None):
        # parts_map: dict(part_name -> (x, y, w, h))
        self.parts_map = parts_map or {}

    @staticmethod
    def from_surface(surface, image_path=None):
        """Create a BodyPartsConfig by heuristically slicing the surface.

        This is a best-effort fallback so the code remains importable and
        runnable even if there isn't exact metadata. It returns a map with
        rectangles covering areas of the surface.
        """
        try:
            w, h = surface.get_size()
        except Exception:
            # Fallback: single full-image torso
            return BodyPartsConfig({'torso': (0, 0, 64, 64)})

        # Heuristic divisions: center for torso, top for head, left/right for limbs
        parts = {}

        # Torso: center big box
        torso_w = int(w * 0.45)
        torso_h = int(h * 0.35)
        torso_x = int((w - torso_w) / 2)
        torso_y = int((h - torso_h) / 2)
        parts['torso'] = (torso_x, torso_y, torso_w, torso_h)

        # Head: top center
        head_w = int(w * 0.25)
        head_h = int(h * 0.18)
        head_x = int((w - head_w) / 2)
        head_y = int(max(0, torso_y - head_h - 8))
        parts['head'] = (head_x, head_y, head_w, head_h)

        # Arms: left / right vertical strips beside torso
        arm_w = int(w * 0.18)
        arm_h = int(h * 0.28)
        left_arm_x = max(0, torso_x - arm_w - 8)
        right_arm_x = min(w - arm_w, torso_x + torso_w + 8)
        arm_y = torso_y - 10
        parts['left_upper_arm'] = (left_arm_x, arm_y, arm_w, arm_h)
        parts['left_forearm'] = (left_arm_x, arm_y + int(arm_h / 2), arm_w, int(arm_h / 2))
        parts['right_upper_arm'] = (right_arm_x, arm_y, arm_w, arm_h)
        parts['right_forearm'] = (right_arm_x, arm_y + int(arm_h / 2), arm_w, int(arm_h / 2))

        # Legs: bottom area
        leg_w = int(w * 0.18)
        leg_h = int(h * 0.30)
        left_leg_x = torso_x + 4
        right_leg_x = torso_x + torso_w - leg_w - 4
        leg_y = torso_y + torso_h - 8
        parts['left_thigh'] = (left_leg_x, leg_y, leg_w, leg_h)
        parts['left_shin'] = (left_leg_x, leg_y + int(leg_h / 2), leg_w, int(leg_h / 2))
        parts['right_thigh'] = (right_leg_x, leg_y, leg_w, leg_h)
        parts['right_shin'] = (right_leg_x, leg_y + int(leg_h / 2), leg_w, int(leg_h / 2))

        return BodyPartsConfig(parts)

    @staticmethod
    def from_image_path(path):
        """Load a surface via pygame and call from_surface."""
        try:
            import pygame
            surf = pygame.image.load(path).convert_alpha()
            return BodyPartsConfig.from_surface(surf, path)
        except Exception:
            # Fallback: empty config
            return BodyPartsConfig({'torso': (0, 0, 64, 64)})

    def get_all_parts(self):
        return self.parts_map

def get_profile(name='default'):
    return PROFILES.get(name, DEFAULT_PROFILE)
