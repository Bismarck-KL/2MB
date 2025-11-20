"""
方案 A 演示：部件級像素化
每個身體部位獨立套用像素化效果
"""
import pygame
import sys
from body_parts import BodyParts
from skeleton import Skeleton, BodyPart
from animation import AnimationController, Poses
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


def pixelate_surface(surface, pixel_size=8, num_colors=16):
    """
    方案 A：對單個 surface 套用像素化
    每個身體部位獨立處理
    """
    width, height = surface.get_size()
    
    # 確保尺寸可被 pixel_size 整除
    new_width = max(pixel_size, (width // pixel_size) * pixel_size)
    new_height = max(pixel_size, (height // pixel_size) * pixel_size)
    
    if new_width != width or new_height != height:
        surface = pygame.transform.scale(surface, (new_width, new_height))
    
    # 縮小
    small_width = max(1, new_width // pixel_size)
    small_height = max(1, new_height // pixel_size)
    small_surface = pygame.transform.scale(surface, (small_width, small_height))
    
    # 獲取調色板
    palette = get_dominant_colors(small_surface, num_colors)
    
    # 套用調色板
    for x in range(small_width):
        for y in range(small_height):
            color = small_surface.get_at((x, y))
            if color.a > 128:
                nearest = find_nearest_color(color, palette)
                small_surface.set_at((x, y), (*nearest, color.a))
    
    # 放大回原尺寸
    pixelated = pygame.transform.scale(small_surface, (new_width, new_height))
    
    return pixelated


class DemoMethodA:
    """方案 A 演示"""
    
    def __init__(self):
        pygame.init()
        
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("方案 A：部件級像素化 (按 P 切換效果)")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # 字體
        try:
            self.font = pygame.font.SysFont('microsoftyahei', 32)
            self.small_font = pygame.font.SysFont('microsoftyahei', 20)
        except:
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
        
        # 載入角色
        self.load_character()
        
        # 動畫控制器
        self.anim_controller = AnimationController(self.skeleton)
        self.anim_controller.set_pose('ready', immediate=True)
        
        # 像素化設定
        self.pixelate_enabled = True
        self.pixel_size = 8
        self.num_colors = 16
        
        self.running = True
    
    def load_character(self):
        """載入角色並建立骨架"""
        # 尋找圖片
        import os
        image_path = None
        for folder in ["assets/photo", "assets/pixelated", "sample"]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if 'tpose' in file.lower() and file.endswith('.png'):
                        image_path = os.path.join(folder, file)
                        break
            if image_path:
                break
        
        if not image_path:
            image_path = "sample/tpose.png"
        
        print(f"載入圖片: {image_path}")
        original_image = pygame.image.load(image_path).convert_alpha()
        
        # 切片
        body_parts_def = BodyParts()
        parts_dict = body_parts_def.get_all_parts()
        
        # 儲存原始和像素化版本
        self.original_parts = {}
        self.pixelated_parts = {}
        
        for part_name, (x, y, w, h) in parts_dict.items():
            part_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            part_surface.blit(original_image, (0, 0), (x, y, w, h))
            
            self.original_parts[part_name] = part_surface
            # 方案 A：每個部件獨立像素化
            self.pixelated_parts[part_name] = pixelate_surface(
                part_surface, self.pixel_size, self.num_colors
            )
        
        # 建立骨架（使用像素化版本）
        self.build_skeleton(self.pixelated_parts)
    
    def build_skeleton(self, part_images):
        """建立骨架系統"""
        self.skeleton = Skeleton()
        
        torso = BodyPart('torso', part_images['torso'],
                        pivot_offset=(part_images['torso'].get_width() / 2,
                                     part_images['torso'].get_height() / 2))
        self.skeleton.set_root(torso)
        
        head = BodyPart('head', part_images['head'],
                       pivot_offset=(part_images['head'].get_width() / 2,
                                    part_images['head'].get_height() - 5),
                       parent=torso)
        self.skeleton.add_part(head)
        
        # 左臂
        left_upper_arm = BodyPart('left_upper_arm', part_images['left_upper_arm'],
                                 pivot_offset=(part_images['left_upper_arm'].get_width() * 0.75, 15),
                                 parent=torso)
        self.skeleton.add_part(left_upper_arm)
        
        left_forearm = BodyPart('left_forearm', part_images['left_forearm'],
                               pivot_offset=(part_images['left_forearm'].get_width() * 0.85,
                                           part_images['left_forearm'].get_height() / 2),
                               parent=left_upper_arm)
        self.skeleton.add_part(left_forearm)
        
        # 右臂
        right_upper_arm = BodyPart('right_upper_arm', part_images['right_upper_arm'],
                                  pivot_offset=(part_images['right_upper_arm'].get_width() * 0.25, 15),
                                  parent=torso)
        self.skeleton.add_part(right_upper_arm)
        
        right_forearm = BodyPart('right_forearm', part_images['right_forearm'],
                                pivot_offset=(part_images['right_forearm'].get_width() * 0.15,
                                            part_images['right_forearm'].get_height() / 2),
                                parent=right_upper_arm)
        self.skeleton.add_part(right_forearm)
        
        # 左腿
        left_thigh = BodyPart('left_thigh', part_images['left_thigh'],
                             pivot_offset=(part_images['left_thigh'].get_width() / 2, 15),
                             parent=torso)
        self.skeleton.add_part(left_thigh)
        
        left_shin = BodyPart('left_shin', part_images['left_shin'],
                            pivot_offset=(part_images['left_shin'].get_width() / 2, 15),
                            parent=left_thigh)
        self.skeleton.add_part(left_shin)
        
        # 右腿
        right_thigh = BodyPart('right_thigh', part_images['right_thigh'],
                              pivot_offset=(part_images['right_thigh'].get_width() / 2, 15),
                              parent=torso)
        self.skeleton.add_part(right_thigh)
        
        right_shin = BodyPart('right_shin', part_images['right_shin'],
                             pivot_offset=(part_images['right_shin'].get_width() / 2, 15),
                             parent=right_thigh)
        self.skeleton.add_part(right_shin)
        
        self.skeleton.set_position(self.width // 2, self.height // 2)
        
        # 套用初始姿勢（重要！）
        self.skeleton.apply_pose(Poses.get_ready())
        self.skeleton.update()  # 更新變換！
    
    def toggle_pixelate(self):
        """切換像素化效果"""
        self.pixelate_enabled = not self.pixelate_enabled
        
        # 重建骨架
        if self.pixelate_enabled:
            self.build_skeleton(self.pixelated_parts)
            print("✓ 啟用像素化（方案 A：部件級處理）")
        else:
            self.build_skeleton(self.original_parts)
            print("✓ 關閉像素化")
        
        # 恢復動畫控制器
        self.anim_controller = AnimationController(self.skeleton)
        self.anim_controller.set_pose('ready', immediate=True)
    
    def handle_events(self):
        """處理輸入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # 切換像素化
                elif event.key == pygame.K_p:
                    self.toggle_pixelate()
                
                # 切換姿勢
                elif event.key == pygame.K_1 or event.key == pygame.K_b:
                    self.anim_controller.set_pose('block')
                elif event.key == pygame.K_2:
                    self.anim_controller.set_pose('ready')
                elif event.key == pygame.K_3 or event.key == pygame.K_p:
                    self.anim_controller.set_pose('punch')
                elif event.key == pygame.K_SPACE:
                    self.anim_controller.set_pose('jump')
    
    def draw(self):
        """繪製"""
        self.screen.fill((50, 50, 80))
        
        # 更新骨架變換（重要！）
        self.skeleton.update()
        
        # 繪製角色
        self.skeleton.draw(self.screen)
        
        # UI 資訊
        title = self.font.render("方案 A：部件級像素化", True, (255, 255, 100))
        self.screen.blit(title, (20, 20))
        
        status = "啟用" if self.pixelate_enabled else "關閉"
        status_text = self.small_font.render(
            f"像素化: {status} (按 P 切換)", True, (255, 255, 255)
        )
        self.screen.blit(status_text, (20, 60))
        
        info_text = self.small_font.render(
            "特點：每個部件獨立處理，邊緣可能不連貫", True, (200, 200, 200)
        )
        self.screen.blit(info_text, (20, 90))
        
        controls = [
            "1/B - 防禦  2 - 準備  3 - 出拳  Space - 跳躍",
            "P - 切換像素化  ESC - 退出"
        ]
        
        y_offset = self.height - 80
        for line in controls:
            text = self.small_font.render(line, True, (180, 180, 180))
            self.screen.blit(text, (20, y_offset))
            y_offset += 25
        
        pygame.display.flip()
    
    def run(self):
        """主循環"""
        print("\n" + "="*60)
        print("方案 A 演示啟動")
        print("部件級像素化：每個身體部位獨立處理")
        print("="*60)
        
        while self.running:
            self.clock.tick(self.fps)
            
            self.handle_events()
            self.anim_controller.update()
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    demo = DemoMethodA()
    demo.run()
