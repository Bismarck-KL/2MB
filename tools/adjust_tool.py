"""
身體部位座標調整工具 - 增強版
支援載入/儲存不同角色的配置檔案
"""

import pygame
import sys
import os

# 添加父目錄到路徑（必須在 import 之前）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from body_parts_profiles import BodyPartsConfig, PROFILES


class BodyPartAdjustTool:
    """身體部位座標調整工具"""

    def __init__(self, image_path, profile_name='default'):
        """
        初始化調整工具

        Args:
            image_path: 角色圖片路徑
            profile_name: 配置名稱 ('default', 'player1', 'player2')
        """
        # 設置 SDL 視頻驅動（Windows 兼容性）
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        pygame.init()

        self.image_path = image_path
        self.profile_name = profile_name

        # 先創建視窗
        # 使用臨時大小，稍後根據圖片調整
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(f"Body Parts Adjust Tool - {profile_name}")
        
        # 載入圖片
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image_width, self.image_height = self.original_image.get_size()

        # 根據圖片大小調整視窗
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
        
        # 滑鼠拖動狀態
        self.dragging = False
        self.drag_start = [0, 0]
        self.original_rect = [0, 0, 0, 0]

        # 字體 - 嘗試載入系統中文字體
        font_loaded = False
        chinese_fonts = ['microsoftyahei', 'simsun', 'simhei', 'msgothic', 'msjh']
        
        for font_name in chinese_fonts:
            try:
                self.font = pygame.font.SysFont(font_name, 24)
                self.small_font = pygame.font.SysFont(font_name, 20)
                font_loaded = True
                print(f"✓ 使用字體: {font_name}")
                break
            except:
                continue
        
        if not font_loaded:
            # 使用預設字體
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
            print("⚠ 未找到中文字體，使用預設字體")

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
        mouse_pos = pygame.mouse.get_pos()
        
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
                
                # 鏡像左右：R
                elif event.key == pygame.K_r:
                    self.mirror_left_to_right()

                # 調整座標
                else:
                    self.adjust_rect(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左鍵
                    rect = self.get_current_part_rect()
                    mx, my = mouse_pos
                    # 檢查是否點擊在當前部位上（考慮偏移）
                    if (20 + rect[0] <= mx <= 20 + rect[0] + rect[2] and
                        50 + rect[1] <= my <= 50 + rect[1] + rect[3]):
                        self.dragging = True
                        self.drag_start = [mx, my]
                        self.original_rect = rect.copy()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mx, my = mouse_pos
                    dx = mx - self.drag_start[0]
                    dy = my - self.drag_start[1]
                    rect = self.get_current_part_rect()
                    rect[0] = self.original_rect[0] + dx
                    rect[1] = self.original_rect[1] + dy
                    self.set_current_part_rect(rect)

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
    
    def mirror_left_to_right(self):
        """將左側部位鏡像到右側"""
        center_x = self.image_width / 2
        
        mirror_pairs = [
            ('left_upper_arm', 'right_upper_arm'),
            ('left_forearm', 'right_forearm'),
            ('left_thigh', 'right_thigh'),
            ('left_shin', 'right_shin')
        ]
        
        for left_name, right_name in mirror_pairs:
            left_rect = list(getattr(self.config, left_name))
            
            # 計算鏡像後的x座標
            left_right_edge = left_rect[0] + left_rect[2]
            distance_to_center = center_x - left_right_edge
            new_x = int(center_x + distance_to_center)
            
            # 更新右側部位
            right_rect = [new_x, left_rect[1], left_rect[2], left_rect[3]]
            setattr(self.config, right_name, tuple(right_rect))
        
        print("✓ 已將左側部位鏡像到右側")

    def draw(self):
        """繪製畫面"""
        self.screen.fill((40, 40, 40))

        # 繪製原始圖片
        self.screen.blit(self.original_image, (20, 50))
        
        # 繪製中心線（用於鏡像參考）
        center_x = int(self.image_width / 2 + 20)
        pygame.draw.line(self.screen, (100, 255, 100),
                        (center_x, 50),
                        (center_x, 50 + self.image_height), 1)

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
            f"Profile: {self.profile_name}", True, (255, 255, 255))
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40

        # 當前部位
        current_part = self.part_names[self.current_part_index]
        part_text = self.font.render(
            f"Part: {current_part}", True, self.colors[current_part])
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
            f"Mode: {self.adjust_mode}", True, mode_color)
        self.screen.blit(mode_text, (panel_x, y_offset))
        y_offset += 40

        # 說明
        help_texts = [
            "Controls:",
            "Tab - Next part",
            "Shift+Tab - Previous",
            "M - Toggle pos/size",
            "Arrow keys - Adjust",
            "Shift+Arrow - Fast",
            "Mouse drag - Move",
            "R - Mirror left->right",
            "S - Save config",
            "ESC - Quit"
        ]

        for text in help_texts:
            help_surface = self.small_font.render(text, True, (150, 150, 150))
            self.screen.blit(help_surface, (panel_x, y_offset))
            y_offset += 20

        pygame.display.flip()

    def save_config(self):
        """儲存配置並自動更新 body_parts_profiles.py"""
        # 1. 儲存 JSON 備份
        filename = f"body_parts_{self.profile_name}.json"
        self.config.save_to_file(filename)
        print(f"\n✓ 配置已儲存到 JSON: {filename}")
        
        # 2. 自動更新 body_parts_profiles.py
        try:
            self.update_profiles_file()
            print(f"✓ 已自動更新 body_parts_profiles.py 中的 {self.profile_name.upper()}_PROFILE")
            print("✓ 你的分割座標已永久保存！")
        except Exception as e:
            print(f"⚠️  自動更新失敗: {e}")
            print(f"  請手動將以下內容複製到 body_parts_profiles.py 中的 {self.profile_name.upper()}_PROFILE:")
            print("\n    'parts': {")
            for part_name in self.part_names:
                coords = getattr(self.config, part_name)
                print(f"        '{part_name}': {coords},")
            print("    }")
        print()
    
    def update_profiles_file(self):
        """自動更新 body_parts_profiles.py 檔案"""
        profiles_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'body_parts_profiles.py'
        )
        
        # 讀取檔案
        with open(profiles_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 建立新的 parts 字典字串
        parts_lines = ["    'parts': {"]
        for part_name in self.part_names:
            coords = getattr(self.config, part_name)
            parts_lines.append(f"        '{part_name}': {coords},")
        parts_lines.append("    }")
        new_parts_str = '\n'.join(parts_lines)
        
        # 找到對應的 PROFILE 並替換
        profile_var = f"{self.profile_name.upper()}_PROFILE"
        
        # 使用正則表達式找到並替換 parts 區塊
        import re
        pattern = rf"({profile_var}\s*=\s*{{\s*'name':\s*'{self.profile_name}',\s*'image_size':\s*\([^)]+\),)\s*'parts':\s*{{[^}}]*}}"
        
        def replace_parts(match):
            return match.group(1) + '\n' + new_parts_str
        
        new_content, count = re.subn(pattern, replace_parts, content, flags=re.DOTALL)
        
        if count == 0:
            raise ValueError(f"找不到 {profile_var} 配置")
        
        # 寫回檔案
        with open(profiles_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    def run(self):
        """執行主循環"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def main():
    """主函數"""
    # 如果沒有命令行參數，使用預設值（方便直接按 Run）
    if len(sys.argv) < 2:
        print("未提供參數，使用預設配置...")
        print("\n使用方法:")
        print("  python adjust_tool.py <圖片路徑> [配置名稱]")
        print("\n範例:")
        print("  python adjust_tool.py assets/photo/player1/tpose.png player1")
        print("  python adjust_tool.py assets/photo/player2/tpose.png player2")
        print("  python adjust_tool.py sample/tpose.png default")
        print("\n" + "="*50)
        
        # 自動尋找可用的圖片
        default_paths = [
            "assets/photo/player1/tpose.png",
            "assets/photo/player2/tpose.png", 
            "sample/tpose.png"
        ]
        
        image_path = None
        for path in default_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        if not image_path:
            print("❌ 錯誤: 找不到任何 tpose.png 圖片")
            print("請確保以下路徑之一存在:")
            for path in default_paths:
                print(f"  - {path}")
            sys.exit(1)
        
        # 根據路徑自動判斷 profile
        if "player1" in image_path:
            profile_name = "player1"
        elif "player2" in image_path:
            profile_name = "player2"
        else:
            profile_name = "default"
        
        print(f"✓ 自動選擇: {image_path} ({profile_name})")
        print("="*50 + "\n")
    else:
        image_path = sys.argv[1]
        profile_name = sys.argv[2] if len(sys.argv) > 2 else 'default'

        if not os.path.exists(image_path):
            print(f"❌ 錯誤: 找不到圖片 {image_path}")
            sys.exit(1)

    print(f"載入圖片: {image_path}")
    print(f"配置名稱: {profile_name}")
    print("\n開始調整工具...")

    tool = BodyPartAdjustTool(image_path, profile_name)
    tool.run()


if __name__ == "__main__":
    main()
