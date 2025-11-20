"""
身體部位座標調整工具 - 增強版
支援載入/儲存不同角色的配置檔案
"""

from body_parts_profiles import BodyPartsConfig, PROFILES
import pygame
import sys
import os

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BodyPartAdjustTool:
    """身體部位座標調整工具"""

    def __init__(self, image_path, profile_name='default'):
        """
        初始化調整工具

        Args:
            image_path: 角色圖片路徑
            profile_name: 配置名稱 ('default', 'player1', 'player2')
        """
        pygame.init()

        self.image_path = image_path
        self.profile_name = profile_name

        # 載入圖片
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image_width, self.image_height = self.original_image.get_size()

        # 創建視窗（稍微大一點以顯示UI）
        self.screen = pygame.display.set_mode(
            (self.image_width + 300, self.image_height + 100))
        pygame.display.set_caption(f"Body Parts Adjust Tool - {profile_name}")

        # 載入配置
        if profile_name in PROFILES:
            self.config = BodyPartsConfig(profile_name)
        else:
            self.config = BodyPartsConfig('default')
            self.config.name = profile_name

        # 部位列表
        self.part_names = [
            'head', 'torso',
            'left_upper_arm', 'left_forearm',
            'right_upper_arm', 'right_forearm',
            'left_thigh', 'left_shin',
            'right_thigh', 'right_shin'
        ]

        # 當前選擇的部位
        self.current_part_index = 0

        # 調整模式：'position' 或 'size'
        self.adjust_mode = 'position'

        # 字體
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # 顏色
        self.colors = {
            'head': (255, 0, 0),
            'torso': (0, 255, 0),
            'left_upper_arm': (0, 0, 255),
            'left_forearm': (255, 255, 0),
            'right_upper_arm': (255, 0, 255),
            'right_forearm': (0, 255, 255),
            'left_thigh': (255, 128, 0),
            'left_shin': (128, 255, 0),
            'right_thigh': (128, 0, 255),
            'right_shin': (255, 128, 128),
        }

        self.running = True
        self.clock = pygame.time.Clock()

    def get_current_part_rect(self):
        """獲取當前部位的座標"""
        part_name = self.part_names[self.current_part_index]
        return list(getattr(self.config, part_name))

    def set_current_part_rect(self, rect):
        """設置當前部位的座標"""
        part_name = self.part_names[self.current_part_index]
        setattr(self.config, part_name, tuple(rect))

    def handle_events(self):
        """處理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # 切換部位：Tab / Shift+Tab
                if event.key == pygame.K_TAB:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.current_part_index = (
                            self.current_part_index - 1) % len(self.part_names)
                    else:
                        self.current_part_index = (
                            self.current_part_index + 1) % len(self.part_names)

                # 切換模式：M
                elif event.key == pygame.K_m:
                    self.adjust_mode = 'size' if self.adjust_mode == 'position' else 'position'

                # 儲存：S
                elif event.key == pygame.K_s:
                    self.save_config()

                # 調整座標
                else:
                    self.adjust_rect(event.key)

    def adjust_rect(self, key):
        """調整當前部位的座標"""
        rect = self.get_current_part_rect()
        step = 5 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1

        if self.adjust_mode == 'position':
            # 調整位置 (x, y)
            if key == pygame.K_LEFT:
                rect[0] -= step
            elif key == pygame.K_RIGHT:
                rect[0] += step
            elif key == pygame.K_UP:
                rect[1] -= step
            elif key == pygame.K_DOWN:
                rect[1] += step

        else:  # size mode
            # 調整大小 (w, h)
            if key == pygame.K_LEFT:
                rect[2] -= step
            elif key == pygame.K_RIGHT:
                rect[2] += step
            elif key == pygame.K_UP:
                rect[3] -= step
            elif key == pygame.K_DOWN:
                rect[3] += step

        self.set_current_part_rect(rect)

    def draw(self):
        """繪製畫面"""
        self.screen.fill((40, 40, 40))

        # 繪製原始圖片
        self.screen.blit(self.original_image, (20, 50))

        # 繪製所有部位的框
        for i, part_name in enumerate(self.part_names):
            x, y, w, h = getattr(self.config, part_name)
            color = self.colors[part_name]

            # 當前選擇的部位用粗框
            thickness = 3 if i == self.current_part_index else 1

            pygame.draw.rect(self.screen, color,
                             (x + 20, y + 50, w, h), thickness)

            # 標籤
            if i == self.current_part_index:
                label = self.small_font.render(part_name, True, color)
                self.screen.blit(label, (x + 20, y + 50 - 20))

        # 繪製UI面板
        panel_x = self.image_width + 40
        y_offset = 20

        # 標題
        title = self.font.render(
            f"配置: {self.profile_name}", True, (255, 255, 255))
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40

        # 當前部位
        current_part = self.part_names[self.current_part_index]
        part_text = self.font.render(
            f"部位: {current_part}", True, self.colors[current_part])
        self.screen.blit(part_text, (panel_x, y_offset))
        y_offset += 30

        # 座標資訊
        rect = self.get_current_part_rect()
        coord_text = self.small_font.render(
            f"X: {rect[0]}", True, (200, 200, 200))
        self.screen.blit(coord_text, (panel_x, y_offset))
        y_offset += 20
        coord_text = self.small_font.render(
            f"Y: {rect[1]}", True, (200, 200, 200))
        self.screen.blit(coord_text, (panel_x, y_offset))
        y_offset += 20
        coord_text = self.small_font.render(
            f"W: {rect[2]}", True, (200, 200, 200))
        self.screen.blit(coord_text, (panel_x, y_offset))
        y_offset += 20
        coord_text = self.small_font.render(
            f"H: {rect[3]}", True, (200, 200, 200))
        self.screen.blit(coord_text, (panel_x, y_offset))
        y_offset += 30

        # 模式
        mode_color = (255, 255, 0) if self.adjust_mode == 'position' else (
            0, 255, 255)
        mode_text = self.small_font.render(
            f"模式: {self.adjust_mode}", True, mode_color)
        self.screen.blit(mode_text, (panel_x, y_offset))
        y_offset += 40

        # 說明
        help_texts = [
            "操作說明:",
            "Tab - 下一個部位",
            "Shift+Tab - 上一個",
            "M - 切換位置/大小",
            "方向鍵 - 調整",
            "Shift+方向鍵 - 快速",
            "S - 儲存配置",
            "ESC - 退出"
        ]

        for text in help_texts:
            help_surface = self.small_font.render(text, True, (150, 150, 150))
            self.screen.blit(help_surface, (panel_x, y_offset))
            y_offset += 20

        pygame.display.flip()

    def save_config(self):
        """儲存配置"""
        filename = f"body_parts_{self.profile_name}.json"
        self.config.save_to_file(filename)
        print(f"\n✓ 配置已儲存到: {filename}")
        print(
            f"  請將以下內容複製到 body_parts_profiles.py 中的 {self.profile_name.upper()}_PROFILE:")
        print("\n    'parts': {")
        for part_name in self.part_names:
            coords = getattr(self.config, part_name)
            print(f"        '{part_name}': {coords},")
        print("    }")
        print()

    def run(self):
        """執行主循環"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python adjust_tool_v2.py <圖片路徑> [配置名稱]")
        print("\n範例:")
        print("  python adjust_tool_v2.py assets/photo/player1/tpose.png player1")
        print("  python adjust_tool_v2.py assets/photo/player2/tpose.png player2")
        print("  python adjust_tool_v2.py sample/tpose.png default")
        sys.exit(1)

    image_path = sys.argv[1]
    profile_name = sys.argv[2] if len(sys.argv) > 2 else 'default'

    if not os.path.exists(image_path):
        print(f"錯誤: 找不到圖片 {image_path}")
        sys.exit(1)

    print(f"載入圖片: {image_path}")
    print(f"配置名稱: {profile_name}")
    print("\n開始調整工具...")

    tool = BodyPartAdjustTool(image_path, profile_name)
    tool.run()


if __name__ == "__main__":
    main()
