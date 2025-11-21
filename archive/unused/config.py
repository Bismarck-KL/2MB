"""
遊戲配置設定
Game Configuration Settings
"""

# ===== 視窗設定 Window Settings =====

# 預設視窗模式 (可選: 'auto', '2mb', '1080p', '720p', 'classic')
WINDOW_MODE = 'auto'

# 自訂視窗尺寸 (如果WINDOW_MODE='custom')
CUSTOM_WINDOW_SIZE = (1600, 900)

# 全螢幕模式
FULLSCREEN = False

# 預設解析度設定
RESOLUTIONS = {
    '2mb': (1600, 900),      # 2MB遊戲專用
    '1080p': (1920, 1080),   # Full HD
    '720p': (1280, 720),     # HD
    'classic': (1024, 768),  # 原始 4:3
    'custom': CUSTOM_WINDOW_SIZE
}

# ===== 角色設定 Character Settings =====

# 預設角色圖片路徑
DEFAULT_CHARACTER_IMAGE = "sample/tpose.png"

# 角色縮放比例 (相對於視窗大小)
CHARACTER_SCALE = 1.0

# 角色在螢幕上的位置 (0.0-1.0, 0.5 = 中心)
CHARACTER_POS_X = 0.5
CHARACTER_POS_Y = 0.5

# ===== 像素化效果 Pixelate Effect =====

# 預設是否啟用像素化
PIXELATE_ENABLED = True

# 預設像素大小 (2-16)
PIXEL_SIZE = 8

# 預設顏色數量 (4-32)
COLOR_COUNT = 16

# ===== 動畫設定 Animation Settings =====

# 幀率
FPS = 60

# 動畫轉換速度 (0.1-1.0, 越高越快)
TRANSITION_SPEED = 0.4

# 自動返回ready姿勢的延遲幀數
AUTO_RETURN_DELAY = 8

# ===== 控制設定 Control Settings =====

# 動作冷卻時間（秒）
ACTION_COOLDOWN = 0.2

# ===== UI設定 UI Settings =====

# UI字體大小
FONT_SIZE_LARGE = 36
FONT_SIZE_SMALL = 24

# UI文字顏色 (R, G, B)
TEXT_COLOR = (255, 255, 255)
TEXT_COLOR_HIGHLIGHT = (255, 255, 0)

# 背景顏色 (R, G, B)
BACKGROUND_COLOR = (40, 44, 52)

# 地面線條顏色
GROUND_LINE_COLOR = (100, 255, 100)

# ===== 開發模式 Development Mode =====

# 顯示FPS
SHOW_FPS = True

# 顯示控制提示
SHOW_CONTROLS = True

# 顯示姿勢資訊
SHOW_POSE_INFO = True

# 顯示像素化資訊
SHOW_PIXELATE_INFO = True


def get_window_size(mode=None):
    """
    取得視窗尺寸

    Args:
        mode: 視窗模式 ('auto', '2mb', '1080p', '720p', 'classic', 'custom')

    Returns:
        tuple: (width, height)
    """
    if mode is None:
        mode = WINDOW_MODE

    if mode == 'auto':
        import pygame
        if not pygame.get_init():
            pygame.init()

        display_info = pygame.display.Info()
        screen_w, screen_h = display_info.current_w, display_info.current_h

        # 自動選擇最適合的解析度
        if screen_w >= 1920 and screen_h >= 1080:
            return RESOLUTIONS['2mb']
        elif screen_w >= 1600 and screen_h >= 900:
            return RESOLUTIONS['2mb']
        elif screen_w >= 1280 and screen_h >= 720:
            return RESOLUTIONS['720p']
        else:
            return RESOLUTIONS['classic']

    return RESOLUTIONS.get(mode, RESOLUTIONS['2mb'])


def get_character_scale(window_width, window_height):
    """
    根據視窗大小計算角色縮放比例

    Args:
        window_width: 視窗寬度
        window_height: 視窗高度

    Returns:
        float: 縮放比例
    """
    # 基準解析度 (1600x900)
    base_width = 1600
    base_height = 900

    # 計算縮放比例（取寬高縮放比的平均）
    scale_w = window_width / base_width
    scale_h = window_height / base_height
    scale = (scale_w + scale_h) / 2

    return scale * CHARACTER_SCALE


# 預設載入時顯示的訊息
WELCOME_MESSAGE = """
2D Character Animation System
Press number keys or letters to change poses
Press F7 to toggle pixelate effect
Press ESC to quit
"""
