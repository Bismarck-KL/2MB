"""
A vs B 比較工具
同時展示兩種方案的差異
"""
import pygame
import sys
import subprocess
import os


class ComparisonMenu:
    """比較選單"""
    
    def __init__(self):
        pygame.init()
        
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("像素化方案比較")
        
        # 字體
        try:
            self.title_font = pygame.font.SysFont('microsoftyahei', 48)
            self.font = pygame.font.SysFont('microsoftyahei', 32)
            self.small_font = pygame.font.SysFont('microsoftyahei', 24)
        except:
            self.title_font = pygame.font.Font(None, 48)
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        
        self.running = True
        self.selected = 0  # 0=A, 1=B, 2=說明
    
    def handle_events(self):
        """處理輸入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % 3
                
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % 3
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.launch_demo()
    
    def launch_demo(self):
        """啟動選擇的演示"""
        if self.selected == 0:
            print("\n啟動方案 A 演示...")
            subprocess.run([sys.executable, "demo_method_a.py"])
        elif self.selected == 1:
            print("\n啟動方案 B 演示...")
            subprocess.run([sys.executable, "demo_method_b.py"])
        elif self.selected == 2:
            self.show_explanation()
    
    def show_explanation(self):
        """顯示說明頁面"""
        explaining = True
        
        while explaining:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    explaining = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        explaining = False
            
            self.screen.fill((30, 30, 50))
            
            title = self.title_font.render("方案差異說明", True, (255, 255, 100))
            title_rect = title.get_rect(center=(self.width // 2, 50))
            self.screen.blit(title, title_rect)
            
            explanations = [
                "",
                "【方案 A：部件級像素化】",
                "• 每個身體部位獨立套用像素化",
                "• 部件之間的邊緣可能不連貫",
                "• 適合：需要個別調整部件效果",
                "• 性能：中等（每個部件處理一次）",
                "",
                "【方案 B：後處理像素化】",
                "• 整個角色渲染後一起處理",
                "• 邊緣連貫，視覺效果統一",
                "• 適合：追求整體一致性",
                "• 性能：較好（只處理最終畫面）",
                "",
                "按任意鍵返回..."
            ]
            
            y_offset = 120
            for line in explanations:
                if line.startswith("【"):
                    color = (100, 255, 255) if "方案 A" in line else (255, 100, 255)
                    text = self.font.render(line, True, color)
                else:
                    color = (220, 220, 220) if line.startswith("•") else (180, 180, 180)
                    text = self.small_font.render(line, True, color)
                
                text_rect = text.get_rect(center=(self.width // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 35 if line.startswith("【") else 28
            
            pygame.display.flip()
    
    def draw(self):
        """繪製選單"""
        self.screen.fill((30, 30, 50))
        
        # 標題
        title = self.title_font.render("像素化方案比較", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)
        
        subtitle = self.small_font.render("選擇要測試的方案", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 選項
        options = [
            ("方案 A：部件級像素化", (100, 255, 255)),
            ("方案 B：後處理像素化", (255, 100, 255)),
            ("查看詳細說明", (100, 255, 100))
        ]
        
        y_offset = 220
        for i, (text, color) in enumerate(options):
            is_selected = (i == self.selected)
            
            # 選中標記
            if is_selected:
                marker = self.font.render("►", True, (255, 255, 100))
                marker_rect = marker.get_rect(center=(150, y_offset))
                self.screen.blit(marker, marker_rect)
            
            # 選項文字
            option_color = color if is_selected else (150, 150, 150)
            option_text = self.font.render(text, True, option_color)
            option_rect = option_text.get_rect(center=(self.width // 2 + 20, y_offset))
            self.screen.blit(option_text, option_rect)
            
            y_offset += 80
        
        # 控制說明
        controls = [
            "↑/↓ - 選擇",
            "Enter/Space - 確認",
            "ESC - 退出"
        ]
        
        y_offset = self.height - 120
        for line in controls:
            text = self.small_font.render(line, True, (180, 180, 180))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        pygame.display.flip()
    
    def run(self):
        """主循環"""
        print("\n" + "="*60)
        print("像素化方案比較工具")
        print("="*60)
        print("\n請選擇要測試的方案：")
        print("1. 方案 A - 部件級像素化（每個部位獨立處理）")
        print("2. 方案 B - 後處理像素化（整體處理）")
        print("3. 查看詳細說明")
        print("\n" + "="*60)
        
        clock = pygame.time.Clock()
        
        while self.running:
            clock.tick(60)
            self.handle_events()
            self.draw()
        
        pygame.quit()
        print("\n感謝使用比較工具！")


if __name__ == "__main__":
    menu = ComparisonMenu()
    menu.run()
