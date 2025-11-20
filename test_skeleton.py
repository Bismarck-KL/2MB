"""
測試骨架是否正確載入
"""
import pygame
from body_parts import BodyParts
from skeleton import Skeleton, BodyPart
from animation import Poses

pygame.init()
screen = pygame.display.set_mode((100, 100))  # 需要視頻模式

# 載入圖片
image_path = "assets/photo/tpose.png"
original_image = pygame.image.load(image_path).convert_alpha()

# 切片
body_parts_def = BodyParts()
parts_dict = body_parts_def.get_all_parts()

part_images = {}
for part_name, (x, y, w, h) in parts_dict.items():
    part_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    part_surface.blit(original_image, (0, 0), (x, y, w, h))
    part_images[part_name] = part_surface

# 建立骨架
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
                         pivot_offset=(part_images['left_upper_arm'].get_width() * 0.75, 15),
                         parent=torso)
skeleton.add_part(left_upper_arm)

left_forearm = BodyPart('left_forearm', part_images['left_forearm'],
                       pivot_offset=(part_images['left_forearm'].get_width() * 0.85,
                                   part_images['left_forearm'].get_height() / 2),
                       parent=left_upper_arm)
skeleton.add_part(left_forearm)

right_upper_arm = BodyPart('right_upper_arm', part_images['right_upper_arm'],
                          pivot_offset=(part_images['right_upper_arm'].get_width() * 0.25, 15),
                          parent=torso)
skeleton.add_part(right_upper_arm)

right_forearm = BodyPart('right_forearm', part_images['right_forearm'],
                        pivot_offset=(part_images['right_forearm'].get_width() * 0.15,
                                    part_images['right_forearm'].get_height() / 2),
                        parent=right_upper_arm)
skeleton.add_part(right_forearm)

left_thigh = BodyPart('left_thigh', part_images['left_thigh'],
                     pivot_offset=(part_images['left_thigh'].get_width() / 2, 15),
                     parent=torso)
skeleton.add_part(left_thigh)

left_shin = BodyPart('left_shin', part_images['left_shin'],
                    pivot_offset=(part_images['left_shin'].get_width() / 2, 15),
                    parent=left_thigh)
skeleton.add_part(left_shin)

right_thigh = BodyPart('right_thigh', part_images['right_thigh'],
                      pivot_offset=(part_images['right_thigh'].get_width() / 2, 15),
                      parent=torso)
skeleton.add_part(right_thigh)

right_shin = BodyPart('right_shin', part_images['right_shin'],
                     pivot_offset=(part_images['right_shin'].get_width() / 2, 15),
                     parent=right_thigh)
skeleton.add_part(right_shin)

print("建立骨架完成")
print("\n套用姿勢前的位置:")
for name, part in skeleton.parts.items():
    print(f"  {name}: local_position={part.local_position}, local_rotation={part.local_rotation}")

# 設置位置
skeleton.set_position(512, 384)

# 套用姿勢
print("\n套用 Ready 姿勢...")
skeleton.apply_pose(Poses.get_ready())

print("\n套用姿勢後的位置:")
for name, part in skeleton.parts.items():
    print(f"  {name}: local_position={part.local_position}, local_rotation={part.local_rotation}")

pygame.quit()
print("\n測試完成！")
