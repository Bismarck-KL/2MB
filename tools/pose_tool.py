"""
Intuitive character pose adjustment tool
Displays complete character, allowing direct visualization of adjustments
"""
import glob
import pygame
import sys
import json
import os

# Add parent directory to path for imports (MUST be before other imports)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Change working directory to parent (so relative paths work)
os.chdir(parent_dir)

from animation import Poses
from body_parts import BodyParts
from skeleton import Skeleton, BodyPart


pygame.init()

# Window settings
width = 1600
height = 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Character Pose Adjustment Tool")

# Load and slice image - search in subdirectories
photo_files = glob.glob("assets/photo/**/*.*", recursive=True)
image_files = [f for f in photo_files if f.lower().endswith(
    ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'))]

if not image_files:
    print("Error: No image found in assets/photo/")
    print("Please place your character image in assets/photo/player1/ or assets/photo/player2/")
    sys.exit(1)

# Prefer tpose.png files
tpose_files = [f for f in image_files if 'tpose' in f.lower()]
image_path = tpose_files[0] if tpose_files else image_files[0]
print(f"Loading image: {image_path}")
original_image = pygame.image.load(image_path).convert_alpha()
body_parts_def = BodyParts()
parts_dict = body_parts_def.get_all_parts()

# Slice image
part_images = {}
for part_name, (x, y, w, h) in parts_dict.items():
    part_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    part_surface.blit(original_image, (0, 0), (x, y, w, h))
    part_images[part_name] = part_surface

# Create skeleton
skeleton = Skeleton()

torso = BodyPart('torso', part_images['torso'],
                 pivot_offset=(part_images['torso'].get_width() / 2,
                               part_images['torso'].get_height() / 2))
skeleton.set_root(torso)

head = BodyPart('head', part_images['head'],
                pivot_offset=(part_images['head'].get_width() / 2,
                              part_images['head'].get_height() - 5),
                parent=torso)
skeleton.add_part(head)

left_upper_arm = BodyPart('left_upper_arm', part_images['left_upper_arm'],
                          pivot_offset=(
                              part_images['left_upper_arm'].get_width() * 0.75, 15),
                          parent=torso)
skeleton.add_part(left_upper_arm)

left_forearm = BodyPart('left_forearm', part_images['left_forearm'],
                        pivot_offset=(part_images['left_forearm'].get_width() * 0.85,
                                      part_images['left_forearm'].get_height() / 2),
                        parent=left_upper_arm)
skeleton.add_part(left_forearm)

right_upper_arm = BodyPart('right_upper_arm', part_images['right_upper_arm'],
                           pivot_offset=(
                               part_images['right_upper_arm'].get_width() * 0.25, 15),
                           parent=torso)
skeleton.add_part(right_upper_arm)

right_forearm = BodyPart('right_forearm', part_images['right_forearm'],
                         pivot_offset=(part_images['right_forearm'].get_width() * 0.15,
                                       part_images['right_forearm'].get_height() / 2),
                         parent=right_upper_arm)
skeleton.add_part(right_forearm)

left_thigh = BodyPart('left_thigh', part_images['left_thigh'],
                      pivot_offset=(
                          part_images['left_thigh'].get_width() / 2, 15),
                      parent=torso)
skeleton.add_part(left_thigh)

left_shin = BodyPart('left_shin', part_images['left_shin'],
                     pivot_offset=(
                         part_images['left_shin'].get_width() / 2, 15),
                     parent=left_thigh)
skeleton.add_part(left_shin)

right_thigh = BodyPart('right_thigh', part_images['right_thigh'],
                       pivot_offset=(
                           part_images['right_thigh'].get_width() / 2, 15),
                       parent=torso)
skeleton.add_part(right_thigh)

right_shin = BodyPart('right_shin', part_images['right_shin'],
                      pivot_offset=(
                          part_images['right_shin'].get_width() / 2, 15),
                      parent=right_thigh)
skeleton.add_part(right_shin)

skeleton.set_position(400, height / 2)

# Apply Ready initial pose
skeleton.apply_pose(Poses.get_ready())

# Currently selected part
part_names = ['torso', 'head', 'left_upper_arm', 'left_forearm',
              'right_upper_arm', 'right_forearm', 'left_thigh', 'left_shin',
              'right_thigh', 'right_shin']

# Chinese name mapping for display
part_names_cn = {
    'torso': '躯干',
    'head': '头部',
    'left_upper_arm': '左上臂',
    'left_forearm': '左前臂',
    'right_upper_arm': '右上臂',
    'right_forearm': '右前臂',
    'left_thigh': '左大腿',
    'left_shin': '左小腿',
    'right_thigh': '右大腿',
    'right_shin': '右小腿'
}

selected_index = 0
selected_part = part_names[selected_index]

# Current pose name
current_pose_name = "ready"

# Save notification
save_message = ""
save_message_timer = 0

# Highlight mode
highlight_selected = True

# Use system Chinese font (smaller size) for Chinese text display
try:
    title_font = pygame.font.SysFont('microsoftyahei', 32, bold=True)
    font = pygame.font.SysFont('microsoftyahei', 20)
    small_font = pygame.font.SysFont('microsoftyahei', 16)
    big_font = pygame.font.SysFont('microsoftyahei', 28)
except:
    try:
        title_font = pygame.font.SysFont('simhei', 32, bold=True)
        font = pygame.font.SysFont('simhei', 20)
        small_font = pygame.font.SysFont('simhei', 16)
        big_font = pygame.font.SysFont('simhei', 28)
    except:
        title_font = pygame.font.Font(None, 32)
        font = pygame.font.Font(None, 20)
        small_font = pygame.font.Font(None, 16)
        big_font = pygame.font.Font(None, 28)

clock = pygame.time.Clock()


def get_current_pose():
    """Get current pose data"""
    pose = {}
    for name, part in skeleton.parts.items():
        pose[name] = {
            'rotation': round(part.local_rotation, 1),
            'position': [round(part.local_position[0], 1), round(part.local_position[1], 1)]
        }
    return pose


def save_and_update_animation(pose_name):
    """Save pose to poses_all.json

    Args:
        pose_name: 'ready', 'punch', 'kick', 'jump', 'block', 'hurt', 'tpose', 'custom'

    Returns:
        True if successful
    """
    try:
        # Get current pose
        pose = get_current_pose()

        # Get parent directory
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        poses_file = os.path.join(parent_dir, 'poses_all.json')

        # Load existing poses
        if os.path.exists(poses_file):
            with open(poses_file, 'r', encoding='utf-8') as f:
                all_poses = json.load(f)
        else:
            all_poses = {}

        # Update the specific pose
        all_poses[pose_name] = pose

        # Save back to poses_all.json
        with open(poses_file, 'w', encoding='utf-8') as f:
            json.dump(all_poses, f, indent=4, ensure_ascii=False)

        print(f"\n✓ Saved {pose_name} pose to poses_all.json")
        print(f"   File: {poses_file}")
        print("   Press F6 in game to reload poses")
        return True
        
    except Exception as e:
        print(f"\n✗ Save failed: {e}")
        return False


def mirror_left_to_right():
    """Mirror left limbs to right side"""
    # Mirror arms
    left_upper = skeleton.parts['left_upper_arm']
    right_upper = skeleton.parts['right_upper_arm']
    right_upper.local_position[0] = -left_upper.local_position[0]
    right_upper.local_position[1] = left_upper.local_position[1]
    right_upper.local_rotation = -left_upper.local_rotation

    left_fore = skeleton.parts['left_forearm']
    right_fore = skeleton.parts['right_forearm']
    right_fore.local_position[0] = -left_fore.local_position[0]
    right_fore.local_position[1] = left_fore.local_position[1]
    right_fore.local_rotation = -left_fore.local_rotation

    # Mirror legs
    left_thigh = skeleton.parts['left_thigh']
    right_thigh = skeleton.parts['right_thigh']
    right_thigh.local_position[0] = -left_thigh.local_position[0]
    right_thigh.local_position[1] = left_thigh.local_position[1]
    right_thigh.local_rotation = -left_thigh.local_rotation

    left_shin = skeleton.parts['left_shin']
    right_shin = skeleton.parts['right_shin']
    right_shin.local_position[0] = -left_shin.local_position[0]
    right_shin.local_position[1] = left_shin.local_position[1]
    right_shin.local_rotation = -left_shin.local_rotation

    print("✓ Mirrored left to right")
    return True


def load_pose(pose_name):
    """Load pose from poses_all.json"""
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    poses_file = os.path.join(parent_dir, 'poses_all.json')
    
    # Try to load from poses_all.json first
    if os.path.exists(poses_file):
        try:
            with open(poses_file, 'r', encoding='utf-8') as f:
                all_poses = json.load(f)
                if pose_name in all_poses:
                    skeleton.apply_pose(all_poses[pose_name])
                    print(f"[OK] Loaded pose from poses_all.json: {pose_name}")
                    return True
                else:
                    print(f"[WARN] Pose '{pose_name}' not found in poses_all.json")
        except Exception as e:
            print(f"[ERROR] Failed to load poses_all.json: {e}")
    
    # Fallback: try old format pose_{name}.json
    json_file = f'pose_{pose_name}.json'
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            pose = json.load(f)
            skeleton.apply_pose(pose)
            print(f"[OK] Loaded pose from {json_file}")
            return True
    
    # Last resort: use hardcoded poses
    print(f"[WARN] Loading hardcoded pose for {pose_name}")
    hardcoded_poses = {
        'block': Poses.get_block(),
        'ready': Poses.get_ready(),
        'punch': Poses.get_punch(),
        'kick': Poses.get_kick(),
        'jump': Poses.get_jump(),
        'hurt': Poses.get_hurt()
    }
    if pose_name in hardcoded_poses:
        skeleton.apply_pose(hardcoded_poses[pose_name])
        return True
    
    print(f"[ERROR] Could not load pose: {pose_name}")
    return False


def save_pose():
    """Save current pose (deprecated - use save_and_update_animation instead)

    This function is kept for backward compatibility but does nothing now.
    Use P key (save_and_update_animation) to properly save poses.
    """
    # Do nothing - this prevents accidental file generation
    # Users should use P key to save poses properly
    return True


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # 切换选中部位
            elif event.key == pygame.K_TAB:
                selected_index = (selected_index + 1) % len(part_names)
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_1:
                selected_index = 0
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_2:
                selected_index = 1
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_3:
                selected_index = 2
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_4:
                selected_index = 3
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_5:
                selected_index = 4
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_6:
                selected_index = 5
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_7:
                selected_index = 6
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_8:
                selected_index = 7
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_9:
                selected_index = 8
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_0:
                selected_index = 9
                selected_part = part_names[selected_index]

            # Adjust position
            elif event.key == pygame.K_UP:
                skeleton.parts[selected_part].local_position[1] -= 1
            elif event.key == pygame.K_DOWN:
                skeleton.parts[selected_part].local_position[1] += 1
            elif event.key == pygame.K_LEFT:
                skeleton.parts[selected_part].local_position[0] -= 1
            elif event.key == pygame.K_RIGHT:
                skeleton.parts[selected_part].local_position[0] += 1

            # Adjust rotation (Q/E)
            elif event.key == pygame.K_q:
                skeleton.parts[selected_part].local_rotation -= 1
            elif event.key == pygame.K_e:
                skeleton.parts[selected_part].local_rotation += 1

            # Fast adjustment
            elif event.key == pygame.K_w:
                skeleton.parts[selected_part].local_position[1] -= 5
            elif event.key == pygame.K_s:
                skeleton.parts[selected_part].local_position[1] += 5
            elif event.key == pygame.K_a:
                skeleton.parts[selected_part].local_position[0] -= 5
            elif event.key == pygame.K_d:
                skeleton.parts[selected_part].local_position[0] += 5

            # Fast rotation
            elif event.key == pygame.K_z:
                skeleton.parts[selected_part].local_rotation -= 5
            elif event.key == pygame.K_c:
                skeleton.parts[selected_part].local_rotation += 5

            # Reset current part
            elif event.key == pygame.K_r:
                skeleton.parts[selected_part].local_rotation = 0

            # P key: save pose to poses_all.json
            elif event.key == pygame.K_p:
                if save_and_update_animation(current_pose_name):
                    save_message = f"✓ Saved {current_pose_name} to poses_all.json! Press F6 in game to reload"
                    save_message_timer = 240
                else:
                    save_message = f"✗ Save failed for {current_pose_name}"
                    save_message_timer = 240

            # Mirror function
            elif event.key == pygame.K_m:
                if mirror_left_to_right():
                    save_message = "✓ Mirrored: left → right"
                    save_message_timer = 120

            # Load saved pose
            elif event.key == pygame.K_l:
                if load_pose(current_pose_name):
                    save_message = f"✓ Loaded: {current_pose_name}"
                    save_message_timer = 120
                else:
                    save_message = f"✗ Load failed: {current_pose_name}"
                    save_message_timer = 120

            # Switch to preset pose (load from poses_all.json)
            elif event.key == pygame.K_F1:
                current_pose_name = "block"
                if load_pose(current_pose_name):
                    save_message = "[OK] Switched to: Block"
                    save_message_timer = 120
            elif event.key == pygame.K_F2:
                current_pose_name = "ready"
                if load_pose(current_pose_name):
                    save_message = "[OK] Switched to: Ready"
                    save_message_timer = 120
            elif event.key == pygame.K_F3:
                current_pose_name = "punch"
                if load_pose(current_pose_name):
                    save_message = "[OK] Switched to: Punch"
                    save_message_timer = 120
            elif event.key == pygame.K_F4:
                current_pose_name = "kick"
                if load_pose(current_pose_name):
                    save_message = "[OK] Switched to: Kick"
                    save_message_timer = 120
            elif event.key == pygame.K_F5:
                current_pose_name = "jump"
                if load_pose(current_pose_name):
                    save_message = "[OK] Switched to: Jump"
                    save_message_timer = 120
            elif event.key == pygame.K_F7:
                current_pose_name = "hurt"
                if load_pose(current_pose_name):
                    save_message = "[OK] Switched to: Hurt"
                    save_message_timer = 120

    # Update
    skeleton.update()

    # Draw
    screen.fill((45, 52, 65))

    # Draw left character area background
    pygame.draw.rect(screen, (35, 40, 50), (0, 0, 800, height))

    # Draw reference lines
    center_x = 400
    pygame.draw.line(screen, (60, 70, 80), (center_x, 0),
                     (center_x, height), 1)
    pygame.draw.line(screen, (60, 70, 80), (0, height/2), (800, height/2), 1)

    # Draw ground line (at foot position)
    ground_y = height/2 + 180  # Approximate foot position
    pygame.draw.line(screen, (100, 150, 100),
                     (0, ground_y), (800, ground_y), 3)
    ground_label = small_font.render("Foot Line", True, (100, 200, 100))
    screen.blit(ground_label, (10, ground_y - 20))

    # Draw lower ground line (100 pixels below feet)
    ground_y_lower = ground_y + 100
    pygame.draw.line(screen, (80, 120, 80),
                     (0, ground_y_lower), (800, ground_y_lower), 3)
    ground_label_lower = small_font.render("Ground", True, (80, 120, 80))
    screen.blit(ground_label_lower, (10, ground_y_lower + 5))

    # Draw complete character
    skeleton.draw(screen)

    # Highlight selected part
    selected = skeleton.parts[selected_part]

    # Draw bounding box for selected part
    if highlight_selected:
        # Get world position and image size of part
        img = selected.image
        angle_rad = -selected.world_rotation * 3.14159 / 180

        # Draw large circle marking selected part
        pygame.draw.circle(screen, (255, 255, 0),
                           (int(selected.world_position[0]), int(
                               selected.world_position[1])),
                           40, 3)

        # Draw pivot point
        pygame.draw.circle(screen, (0, 255, 255),
                           (int(selected.world_position[0]), int(selected.world_position[1])), 6)

    # Separator line
    pygame.draw.line(screen, (100, 110, 120), (800, 0), (800, height), 2)

    # Right control panel
    panel_x = 850
    y_offset = 20

    # Title
    title = title_font.render("Pose Adjustment Tool", True, (255, 255, 255))
    screen.blit(title, (panel_x, y_offset))
    y_offset += 40

    # Display current pose name
    pose_name_text = font.render(
        f"Current Pose: {current_pose_name}", True, (100, 255, 150))
    screen.blit(pose_name_text, (panel_x, y_offset))
    y_offset += 35

    # Current selection info
    part = skeleton.parts[selected_part]
    info_box = pygame.Surface((700, 100))
    info_box.fill((60, 70, 85))
    screen.blit(info_box, (panel_x, y_offset))

    y_info = y_offset + 10
    texts = [
        f"Current Part: {part_names_cn[selected_part]} ({selected_part})",
        f"Position X: {part.local_position[0]:.1f}  Y: {part.local_position[1]:.1f}",
        f"Rotation: {part.local_rotation:.1f}°",
    ]

    for text in texts:
        surface = font.render(text, True, (255, 255, 100))
        screen.blit(surface, (panel_x + 15, y_info))
        y_info += 28

    y_offset += 115    # Control instructions
    control_texts = [
        "[Select Part]",
        "TAB to cycle | 1-0 number keys",
        "[Adjust Position]",
        "Arrow keys fine ±1px | WASD fast ±5px",
        "[Adjust Rotation]",
        "Q/E rotate ±1° | Z/C fast ±5° | R reset",
        "[Pose Management]",
        "F1-Block | F2-Ready | F3-Punch",
        "F4-Kick | F5-Jump | F7-Hurt",
        "P-Save & update to animation.py",
        "M-Mirror L→R | ESC-Quit",
        "After save, press F6 in main.py to reload"
    ]

    for text in control_texts:
        if text.startswith("["):
            color = (100, 200, 255)
            surface = font.render(text, True, color)
            y_add = 25
        else:
            color = (200, 200, 200)
            surface = small_font.render(text, True, color)
            y_add = 20
        screen.blit(surface, (panel_x, y_offset))
        y_offset += y_add

    # Part list
    y_offset += 15
    list_title = font.render("[Part List]", True, (100, 200, 255))
    screen.blit(list_title, (panel_x, y_offset))
    y_offset += 30

    for i, name in enumerate(part_names):
        part_obj = skeleton.parts[name]
        is_selected = (name == selected_part)

        # Background
        if is_selected:
            bg = pygame.Surface((700, 22))
            bg.fill((80, 90, 110))
            screen.blit(bg, (panel_x, y_offset - 3))

        color = (255, 255, 100) if is_selected else (180, 180, 180)
        prefix = f"{i+1 if i < 9 else 0}. "
        cn_name = part_names_cn[name]
        text = f"{prefix}{cn_name:6s} ({part_obj.local_position[0]:4.0f},{part_obj.local_position[1]:4.0f}) {part_obj.local_rotation:4.0f}°"
        surface = small_font.render(text, True, color)
        screen.blit(surface, (panel_x, y_offset))
        y_offset += 24    # Display save notification
    if save_message_timer > 0:
        save_message_timer -= 1
        alpha_val = min(255, save_message_timer * 2)
        bg_surface = pygame.Surface((500, 50))
        bg_surface.set_alpha(min(220, alpha_val))
        bg_surface.fill((20, 150, 20))
        screen.blit(bg_surface, (width // 2 - 250, 20))
        text_surface = big_font.render(save_message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width // 2, 45))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
