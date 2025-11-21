"""
啟動器 - 選擇不同的視窗模式
Launcher - Choose different window modes
"""

import sys

# 檢查命令列參數
if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    print("=== 2D Character Animation System ===")
    print("\n請選擇視窗模式 Choose Window Mode:")
    print("1. Auto (自動偵測)")
    print("2. 2MB Game (1600x900)")
    print("3. 1080p (1920x1080)")
    print("4. 720p (1280x720)")
    print("5. Classic (1024x768)")
    print("6. Fullscreen (全螢幕)")
    print("\n輸入數字或按Enter使用自動模式: ", end="")

    choice = input().strip()

    mode_map = {
        '1': 'auto',
        '2': '2mb',
        '3': '1080p',
        '4': '720p',
        '5': 'classic',
        '6': 'fullscreen',
        '': 'auto'
    }

    mode = mode_map.get(choice, 'auto')

# 導入並啟動遊戲
from main import CharacterAnimator

if mode == 'fullscreen':
    game = CharacterAnimator(window_mode='auto', fullscreen=True)
else:
    game = CharacterAnimator(window_mode=mode, fullscreen=False)

game.run()
