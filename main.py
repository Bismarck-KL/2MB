"""
Main game file
2D skeletal animation system using Pygame
With real-time pixelate effect (Method B)
"""

import pygame
import sys
from body_parts import BodyParts
from skeleton import Skeleton, BodyPart
from animation import AnimationController
from collections import Counter


def get_dominant_colors(surface, num_colors=16):
    """Extract dominant colors from image"""
    width, height = surface.get_size()
    colors = []

    for x in range(0, width, max(1, width // 10)):
        for y in range(0, height, max(1, height // 10)):
            color = surface.get_at((x, y))
            if color.a > 128:
                colors.append((color.r, color.g, color.b))

    if not colors:
        return [(0, 0, 0)]

    color_counter = Counter(colors)
    return [c for c, _ in color_counter.most_common(num_colors)]


def find_nearest_color(color, palette):
    """Find closest color in palette"""
    r, g, b = color[:3]
    min_dist = float('inf')
    nearest = palette[0]

    for pr, pg, pb in palette:
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest = (pr, pg, pb)

    return nearest


def pixelate_final_render(surface, pixel_size=8, num_colors=16):
    """
    Method B: Apply pixelate effect to final render
    Process entire character together for unified look
    """
    width, height = surface.get_size()

    # Ensure dimensions are divisible by pixel_size
    new_width = (width // pixel_size) * pixel_size
    new_height = (height // pixel_size) * pixel_size

    # Downscale
    small_width = new_width // pixel_size
    small_height = new_height // pixel_size

    # Crop to divisible size
    cropped = surface.subsurface((0, 0, new_width, new_height)).copy()

    # Scale down
    small_surface = pygame.transform.scale(
        cropped, (small_width, small_height))

    # Get color palette
    palette = get_dominant_colors(small_surface, num_colors)

    # Apply palette
    for x in range(small_width):
        for y in range(small_height):
            color = small_surface.get_at((x, y))
            if color.a > 128:
                nearest = find_nearest_color(color, palette)
                small_surface.set_at((x, y), (*nearest, color.a))

    # Scale back up
    pixelated = pygame.transform.scale(small_surface, (new_width, new_height))

    return pixelated


class CharacterAnimator:
    """Character animator - main game class"""

    def __init__(self, image_path="sample/tpose.png"):
        """Initialize game

        Args:
            image_path: Path to T-pose image
        """
        pygame.init()

        # Window settings
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2D Character Animation System")

        # Clock
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Load character
        self.image_path = image_path
        self.load_character(image_path)

        # Create animation controller
        self.anim_controller = AnimationController(self.skeleton)
        self.anim_controller.set_pose('ready', immediate=True)

        # Pixelate effect settings (Method B)
        self.pixelate_enabled = True
        self.pixel_size = 8
        self.num_colors = 16
        self.render_surface = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA)

        # Hurt effect
        self.hurt_effect = False
        self.hurt_timer = 0
        self.hurt_duration = 0.5  # 0.5 seconds

        # Game state
        self.running = True

        # Input debouncing - track last action time
        self.last_action_time = 0
        self.action_cooldown = 0.2  # Action cooldown time (seconds)

        # UI text - use Chinese font for Chinese text
        try:
            self.font = pygame.font.SysFont('microsoftyahei', 36)
            self.small_font = pygame.font.SysFont('microsoftyahei', 24)
        except:
            try:
                self.font = pygame.font.SysFont('simhei', 36)
                self.small_font = pygame.font.SysFont('simhei', 24)
            except:
                self.font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 24)

    def load_character(self, image_path):
        """Load and slice character image, create skeletal system

        Args:
            image_path: Path to character image
        """
        # Load original image
        original_image = pygame.image.load(image_path).convert_alpha()

        # Get body parts definition
        body_parts_def = BodyParts()
        parts_dict = body_parts_def.get_all_parts()

        # Slice image and create body parts
        part_images = {}
        for part_name, (x, y, w, h) in parts_dict.items():
            # Create subsurface
            part_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            part_surface.blit(original_image, (0, 0), (x, y, w, h))
            part_images[part_name] = part_surface

        # Create skeletal system
        self.skeleton = Skeleton()

        # Create torso (root node) - pivot at center
        torso = BodyPart(
            'torso',
            part_images['torso'],
            pivot_offset=(part_images['torso'].get_width() / 2,
                          part_images['torso'].get_height() / 2)
        )
        self.skeleton.set_root(torso)

        # Create head - pivot at bottom center (neck position)
        head = BodyPart(
            'head',
            part_images['head'],
            pivot_offset=(part_images['head'].get_width() / 2,
                          part_images['head'].get_height() - 5),
            parent=torso
        )
        self.skeleton.add_part(head)

        # Left upper arm - pivot at right upper side (shoulder joint)
        left_upper_arm = BodyPart(
            'left_upper_arm',
            part_images['left_upper_arm'],
            pivot_offset=(
                part_images['left_upper_arm'].get_width() * 0.75, 15),
            parent=torso
        )
        self.skeleton.add_part(left_upper_arm)

        # Left forearm - pivot at right center (elbow joint)
        left_forearm = BodyPart(
            'left_forearm',
            part_images['left_forearm'],
            pivot_offset=(part_images['left_forearm'].get_width() * 0.85,
                          part_images['left_forearm'].get_height() / 2),
            parent=left_upper_arm
        )
        self.skeleton.add_part(left_forearm)

        # Right upper arm - pivot at left upper side (shoulder joint)
        right_upper_arm = BodyPart(
            'right_upper_arm',
            part_images['right_upper_arm'],
            pivot_offset=(
                part_images['right_upper_arm'].get_width() * 0.25, 15),
            parent=torso
        )
        self.skeleton.add_part(right_upper_arm)

        # Right forearm - pivot at left center (elbow joint)
        right_forearm = BodyPart(
            'right_forearm',
            part_images['right_forearm'],
            pivot_offset=(part_images['right_forearm'].get_width() * 0.15,
                          part_images['right_forearm'].get_height() / 2),
            parent=right_upper_arm
        )
        self.skeleton.add_part(right_forearm)

        # Left thigh - pivot at upper center (hip joint)
        left_thigh = BodyPart(
            'left_thigh',
            part_images['left_thigh'],
            pivot_offset=(part_images['left_thigh'].get_width() / 2, 15),
            parent=torso
        )
        self.skeleton.add_part(left_thigh)

        # Left shin - pivot at upper center (knee joint)
        left_shin = BodyPart(
            'left_shin',
            part_images['left_shin'],
            pivot_offset=(part_images['left_shin'].get_width() / 2, 15),
            parent=left_thigh
        )
        self.skeleton.add_part(left_shin)

        # Right thigh - pivot at upper center (hip joint)
        right_thigh = BodyPart(
            'right_thigh',
            part_images['right_thigh'],
            pivot_offset=(part_images['right_thigh'].get_width() / 2, 15),
            parent=torso
        )
        self.skeleton.add_part(right_thigh)

        # Right shin - pivot at upper center (knee joint)
        right_shin = BodyPart(
            'right_shin',
            part_images['right_shin'],
            pivot_offset=(part_images['right_shin'].get_width() / 2, 15),
            parent=right_thigh
        )
        self.skeleton.add_part(right_shin)

        # Position character at screen center
        self.skeleton.set_position(self.width / 2, self.height / 2)

    def reload_all_poses(self):
        """Reload all poses (including base poses)"""
        import importlib
        import animation
        importlib.reload(animation)

        # Recreate animation controller
        from animation import AnimationController
        self.anim_controller = AnimationController(self.skeleton)
        print("✓ Reloaded all poses!")

    def load_custom_pose(self, pose_name='custom'):
        """Load custom pose

        Args:
            pose_name: Pose name, default 'custom'
        """
        # Reload pose list (including new custom poses)
        self.anim_controller.reload_poses()

        # Switch to custom pose
        if pose_name in self.anim_controller.poses:
            self.anim_controller.set_pose(pose_name, immediate=False)
            print(f"✓ Loaded pose: {pose_name}")
            return True
        else:
            print(f"✗ Pose not found: {pose_name}")
            return False

    def reload_character(self, new_image_path):
        """Reload character image

        Args:
            new_image_path: Path to new character image
        """
        try:
            self.image_path = new_image_path
            current_pose = self.anim_controller.current_pose
            self.load_character(new_image_path)
            self.anim_controller = AnimationController(self.skeleton)
            self.anim_controller.set_pose(current_pose, immediate=True)
            print(f"Successfully loaded character: {new_image_path}")
        except Exception as e:
            print(f"Failed to load character: {e}")

    def handle_events(self):
        """Handle input events"""
        import time
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Action keys (with cooldown)
                if event.key in [pygame.K_1, pygame.K_b, pygame.K_3, pygame.K_p,
                                 pygame.K_4, pygame.K_k, pygame.K_SPACE, pygame.K_j]:
                    # Check cooldown
                    if current_time - self.last_action_time < self.action_cooldown:
                        continue  # Skip this input
                    self.last_action_time = current_time

                # Pose switching
                if event.key == pygame.K_1 or event.key == pygame.K_b:
                    self.anim_controller.set_pose('block')
                elif event.key == pygame.K_2:
                    self.anim_controller.set_pose('ready')
                elif event.key == pygame.K_3 or event.key == pygame.K_p:
                    self.anim_controller.set_pose('punch')
                elif event.key == pygame.K_4 or event.key == pygame.K_k:
                    self.anim_controller.set_pose('kick')
                elif event.key == pygame.K_SPACE or event.key == pygame.K_j:
                    self.anim_controller.set_pose('jump')

                # Hurt pose
                elif event.key == pygame.K_5 or event.key == pygame.K_h:
                    self.anim_controller.set_pose('hurt')
                    self.hurt_effect = True
                    self.hurt_timer = self.hurt_duration

                # Load custom pose
                elif event.key == pygame.K_F5:
                    self.load_custom_pose('custom')
                elif event.key == pygame.K_l:
                    self.load_custom_pose('custom')

                # Reload all poses
                elif event.key == pygame.K_F6:
                    self.reload_all_poses()

                # Toggle pixelate effect
                elif event.key == pygame.K_F7:
                    self.pixelate_enabled = not self.pixelate_enabled
                    status = "ON" if self.pixelate_enabled else "OFF"
                    print(f"✓ Pixelate effect: {status}")

                # Adjust pixel size
                elif event.key == pygame.K_LEFTBRACKET:  # [
                    self.pixel_size = max(2, self.pixel_size - 2)
                    print(f"✓ Pixel size: {self.pixel_size}")
                elif event.key == pygame.K_RIGHTBRACKET:  # ]
                    self.pixel_size = min(16, self.pixel_size + 2)
                    print(f"✓ Pixel size: {self.pixel_size}")

                # Adjust color count
                elif event.key == pygame.K_MINUS:  # -
                    self.num_colors = max(4, self.num_colors - 4)
                    print(f"✓ Colors: {self.num_colors}")
                elif event.key == pygame.K_EQUALS:  # +
                    self.num_colors = min(32, self.num_colors + 4)
                    print(f"✓ Colors: {self.num_colors}")

                # Quit
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Update game logic"""
        self.anim_controller.update()
        self.skeleton.update()

        # Update hurt effect timer
        if self.hurt_timer > 0:
            dt = self.clock.get_time() / 1000.0
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.hurt_effect = False
                self.hurt_timer = 0

    def draw_ui(self):
        """Draw UI information"""
        # Title
        title = self.font.render(
            "2D Character Animation", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))

        # Control instructions
        y_offset = 60
        controls = [
            "Controls:",
            "1 or B - Block pose (auto-return)",
            "2 - Ready pose",
            "3 or P - Punch (auto-return)",
            "4 or K - Kick (auto-return)",
            "5 or H - Hurt (auto-return)",
            "Space or J - Jump (auto-return)",
            "F5 or L - Load custom pose",
            "F6 - Reload all poses",
            "F7 - Toggle pixelate effect",
            "[ ] - Pixel size  | - + - Colors",
            "ESC - Quit",
            "",
            f"Current pose: {self.anim_controller.current_pose.upper()}",
            f"Target pose: {self.anim_controller.target_pose.upper()}",
            f"Pixelate: {'ON' if self.pixelate_enabled else 'OFF'} | Size: {self.pixel_size} | Colors: {self.num_colors}",
        ]

        # Add status info
        if self.anim_controller.return_timer > 0:
            controls.append(
                f"Return countdown: {self.anim_controller.return_timer}")
        elif self.anim_controller.current_pose == 'ready' and self.anim_controller.target_pose == 'ready':
            controls.append("Status: Idle breathing")

        for i, text in enumerate(controls):
            color = (255, 255, 100) if "Current pose" in text else (
                200, 200, 200)
            surface = self.small_font.render(text, True, color)
            self.screen.blit(surface, (20, y_offset + i * 25))

        # FPS
        fps_text = self.small_font.render(
            f"FPS: {int(self.clock.get_fps())}", True, (200, 200, 200))
        self.screen.blit(fps_text, (self.width - 100, 20))

    def draw(self):
        """Draw all content"""
        # Clear screen
        self.screen.fill((40, 40, 50))

        # Draw ground lines (at character's foot position)
        # Calculate foot position: character center + torso offset + approximate leg length
        character_center_y = self.height / 2
        ground_y = character_center_y + 180  # Approximate foot position

        # Draw upper ground line (foot level)
        pygame.draw.line(self.screen, (100, 150, 100),
                         (0, ground_y), (self.width, ground_y), 2)
        ground_label = self.small_font.render(
            "Foot Line", True, (100, 200, 100))
        self.screen.blit(ground_label, (self.width - 110, ground_y - 20))

        # Draw lower ground line (100 pixels below feet)
        ground_y_lower = ground_y + 100
        pygame.draw.line(self.screen, (80, 120, 80),
                         (0, ground_y_lower), (self.width, ground_y_lower), 2)
        ground_label_lower = self.small_font.render(
            "Ground", True, (80, 120, 80))
        self.screen.blit(ground_label_lower,
                         (self.width - 60, ground_y_lower + 5))

        # Method B: Render character to temporary surface, then apply pixelate
        if self.pixelate_enabled:
            # Render to temporary surface
            self.render_surface.fill((0, 0, 0, 0))  # Transparent background
            self.skeleton.draw(self.render_surface)

            # Apply hurt effect (red overlay 50%) before pixelate
            if self.hurt_effect:
                red_overlay = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA)
                red_overlay.fill((255, 0, 0, 128))  # Red with 50% alpha
                self.render_surface.blit(
                    red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Apply pixelate effect
            pixelated = pixelate_final_render(
                self.render_surface,
                self.pixel_size,
                self.num_colors
            )
            self.screen.blit(pixelated, (0, 0))
        else:
            # Draw normally without pixelate
            self.skeleton.draw(self.screen)

            # Apply hurt effect (red overlay 50%) on character only
            if self.hurt_effect:
                # Create temporary surface for character
                char_surface = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA)
                char_surface.fill((0, 0, 0, 0))
                self.skeleton.draw(char_surface)

                # Apply red tint
                red_overlay = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA)
                red_overlay.fill((255, 0, 0, 128))
                char_surface.blit(red_overlay, (0, 0),
                                  special_flags=pygame.BLEND_RGBA_MULT)

                # Draw tinted character
                self.screen.blit(char_surface, (0, 0))

        # Draw UI
        self.draw_ui()

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()


def main():
    """Main function"""
    import os

    # Priority order: assets/pixelated > assets/photo > sample
    image_path = None

    # 1. Check pixelated folder first (highest priority)
    if os.path.exists("assets/pixelated"):
        for file in os.listdir("assets/pixelated"):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and 'tpose' in file.lower():
                image_path = os.path.join("assets/pixelated", file)
                print(f"✓ Using pixelated image: {image_path}")
                break

    # 2. If no pixelated version, check assets/photo
    if not image_path and os.path.exists("assets/photo"):
        for file in os.listdir("assets/photo"):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and 'tpose' in file.lower():
                image_path = os.path.join("assets/photo", file)
                print(f"Using original image: {image_path}")
                print("💡 Tip: Run 'python auto_watch.py' to auto-generate pixel art!")
                break

    # 3. Fallback to sample folder
    if not image_path:
        if os.path.exists("sample/tpose.png"):
            image_path = "sample/tpose.png"
            print(f"Using sample image: {image_path}")
            print("💡 Tip: Place your tpose image in 'assets/photo' folder!")
        else:
            print("❌ Error: No tpose image found!")
            print("   Please place a tpose image in one of these folders:")
            print("   - assets/photo/ (for auto-conversion)")
            print("   - sample/")
            sys.exit(1)

    # Create game instance
    game = CharacterAnimator(image_path)

    # Run game
    game.run()


if __name__ == "__main__":
    main()
