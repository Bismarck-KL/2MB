"""
像素風格設定工具
Interactive Pixel Art Style Configuration Tool
"""
import os
import sys


def show_current_config():
    """顯示當前設定"""
    print("\n" + "=" * 70)
    print("📊 當前像素風格設定")
    print("=" * 70)

    # 讀取 auto_watch.py 找出當前設定
    try:
        with open('auto_watch.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取當前參數
        import re
        pixel_size = re.search(r'pixel_size=(\d+)', content)
        num_colors = re.search(r'num_colors=(\d+)', content)
        outline = re.search(r'add_outline_effect=(True|False)', content)
        dither = re.search(r'dither=(True|False)', content)
        output_name = re.search(r'f"{base_name}_(\w+)\.png"', content)

        if pixel_size:
            print(f"  🔹 像素大小 (pixel_size): {pixel_size.group(1)}")
        if num_colors:
            print(f"  🎨 顏色數量 (num_colors): {num_colors.group(1)}")
        if outline:
            print(f"  ✏️  輪廓效果 (add_outline_effect): {outline.group(1)}")
        if dither:
            print(f"  🌫️  抖動效果 (dither): {dither.group(1)}")
        if output_name:
            print(f"  💾 輸出檔名後綴: _{output_name.group(1)}.png")

    except Exception as e:
        print(f"  ⚠️  無法讀取設定: {e}")

    print("=" * 70)


def show_presets():
    """顯示預設風格"""
    print("\n📐 預設風格選項：\n")
    print("1. 經典 8-bit 風格 (Classic 8-bit)")
    print("   • 像素大小: 8x8")
    print("   • 顏色數量: 16 色")
    print("   • 輪廓: 是")
    print("   • 特色: 復古 NES/FC 遊戲風格")
    print()
    print("2. 復古 16-bit 風格 (Retro 16-bit) ⭐ 當前使用")
    print("   • 像素大小: 4x4")
    print("   • 顏色數量: 32 色")
    print("   • 輪廓: 是")
    print("   • 特色: SNES/MD 遊戲風格，更細緻")
    print()
    print("3. 大塊像素風格 (Chunky Pixel)")
    print("   • 像素大小: 16x16")
    print("   • 顏色數量: 12 色")
    print("   • 輪廓: 是")
    print("   • 特色: 粗獷、高對比度")
    print()
    print("4. 平滑漸層風格 (Smooth Gradient)")
    print("   • 像素大小: 8x8")
    print("   • 顏色數量: 24 色")
    print("   • 輪廓: 是")
    print("   • 抖動: 是")
    print("   • 特色: 漸層更平滑")
    print()
    print("5. 自訂設定 (Custom)")
    print("   • 自行設定所有參數")
    print()


def apply_preset(preset_num):
    """套用預設風格"""
    presets = {
        1: {
            'pixel_size': 8,
            'num_colors': 16,
            'outline': True,
            'outline_thickness': 1,
            'dither': False,
            'name': '8bit'
        },
        2: {
            'pixel_size': 4,
            'num_colors': 32,
            'outline': True,
            'outline_thickness': 1,
            'dither': False,
            'name': '16bit'
        },
        3: {
            'pixel_size': 16,
            'num_colors': 12,
            'outline': True,
            'outline_thickness': 1,
            'dither': False,
            'name': 'chunky'
        },
        4: {
            'pixel_size': 8,
            'num_colors': 24,
            'outline': True,
            'outline_thickness': 1,
            'dither': True,
            'name': 'smooth'
        }
    }

    if preset_num not in presets:
        return None

    return presets[preset_num]


def get_custom_config():
    """取得自訂設定"""
    print("\n🎨 自訂風格設定\n")

    try:
        pixel_size = int(input("  像素大小 (4-32，建議: 4, 8, 16): "))
        if pixel_size < 4 or pixel_size > 32:
            print("  ⚠️  像素大小建議在 4-32 之間")
            return None

        num_colors = int(input("  顏色數量 (8-32，建議: 12, 16, 24, 32): "))
        if num_colors < 8 or num_colors > 32:
            print("  ⚠️  顏色數量建議在 8-32 之間")
            return None

        outline_input = input("  是否加輪廓？ (y/n，建議: y): ").lower()
        outline = outline_input == 'y'

        outline_thickness = 1
        if outline:
            thickness_input = input("  輪廓粗細 (1=細, 2=粗，建議: 1): ").strip()
            if thickness_input:
                outline_thickness = int(thickness_input)
                if outline_thickness < 1 or outline_thickness > 3:
                    print("  ⚠️  輪廓粗細建議在 1-3 之間")
                    outline_thickness = 1

        dither_input = input("  是否使用抖動效果？ (y/n，建議: n): ").lower()
        dither = dither_input == 'y'

        name = input("  輸出檔名後綴 (例如: custom): ").strip()
        if not name:
            name = 'custom'

        return {
            'pixel_size': pixel_size,
            'num_colors': num_colors,
            'outline': outline,
            'outline_thickness': outline_thickness,
            'dither': dither,
            'name': name
        }

    except ValueError:
        print("  ⚠️  輸入格式錯誤")
        return None


def update_auto_watch(config):
    """更新 auto_watch.py 的設定"""
    try:
        with open('auto_watch.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新參數
        import re
        # 匹配 pixel_size=數字, (注意包含逗號)
        content = re.sub(
            r'pixel_size=\d+,',
            f"pixel_size={config['pixel_size']},",
            content
        )
        # 匹配 num_colors=數字, (注意包含逗號)
        content = re.sub(
            r'num_colors=\d+,',
            f"num_colors={config['num_colors']},",
            content
        )
        # 匹配 add_outline_effect=True或False, (注意包含逗號)
        content = re.sub(
            r'add_outline_effect=(True|False),',
            f"add_outline_effect={config['outline']},",
            content
        )
        # 匹配 dither=True或False, (注意包含逗號)
        content = re.sub(
            r'dither=(True|False),',
            f"dither={config['dither']},",
            content
        )
        # 匹配 outline_thickness=數字 (最後一個參數)
        content = re.sub(
            r'outline_thickness=\d+(?=\s*\))',
            f"outline_thickness={config.get('outline_thickness', 1)}",
            content
        )
        # 匹配輸出檔案名稱格式
        content = re.sub(
            r'f"\{base_name\}_\w+\.png"',
            f'f"{{base_name}}_{config["name"]}.png"',
            content
        )

        # 寫回檔案
        with open('auto_watch.py', 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"  ❌ 更新失敗: {e}")
        return False


def fine_tune_config(config):
    """微調設定"""
    print("\n" + "=" * 70)
    print("🔧 微調設定")
    print("=" * 70)
    print("\n當前設定：")
    print(f"  • 像素大小: {config['pixel_size']}x{config['pixel_size']}")
    print(f"  • 顏色數量: {config['num_colors']} 色")
    print(f"  • 輪廓效果: {'是' if config['outline'] else '否'}", end="")
    if config['outline']:
        print(f" (粗細: {config.get('outline_thickness', 1)})")
    else:
        print()
    print(f"  • 抖動效果: {'是' if config['dither'] else '否'}")
    print(f"  • 輸出檔名: [檔名]_{config['name']}.png")

    print("\n請選擇要調整的項目（直接按 Enter 跳過）：")

    # 像素大小
    pixel_input = input(
        f"  像素大小 (目前: {config['pixel_size']}，範圍: 4-32): ").strip()
    if pixel_input:
        try:
            new_value = int(pixel_input)
            if 4 <= new_value <= 32:
                config['pixel_size'] = new_value
            else:
                print("    ⚠️  超出範圍，保持原值")
        except ValueError:
            print("    ⚠️  無效輸入，保持原值")

    # 顏色數量
    colors_input = input(
        f"  顏色數量 (目前: {config['num_colors']}，範圍: 8-32): ").strip()
    if colors_input:
        try:
            new_value = int(colors_input)
            if 8 <= new_value <= 32:
                config['num_colors'] = new_value
            else:
                print("    ⚠️  超出範圍，保持原值")
        except ValueError:
            print("    ⚠️  無效輸入，保持原值")

    # 輪廓效果
    outline_input = input(
        f"  是否加輪廓？ (目前: {'y' if config['outline'] else 'n'}，y/n): ").strip().lower()
    if outline_input:
        config['outline'] = (outline_input == 'y')

    # 輪廓粗細（如果有輪廓）
    if config['outline']:
        thickness_input = input(
            f"  輪廓粗細 (目前: {config.get('outline_thickness', 1)}，範圍: 1-3): ").strip()
        if thickness_input:
            try:
                new_value = int(thickness_input)
                if 1 <= new_value <= 3:
                    config['outline_thickness'] = new_value
                else:
                    print("    ⚠️  超出範圍，保持原值")
            except ValueError:
                print("    ⚠️  無效輸入，保持原值")

    # 抖動效果
    dither_input = input(
        f"  是否使用抖動？ (目前: {'y' if config['dither'] else 'n'}，y/n): ").strip().lower()
    if dither_input:
        config['dither'] = (dither_input == 'y')

    return config


def main():
    """主程式"""
    print("\n" + "=" * 70)
    print("🎨 像素風格設定工具")
    print("   Pixel Art Style Configuration Tool")
    print("=" * 70)

    while True:
        show_current_config()
        show_presets()

        choice = input("請選擇風格 (1-5) 或按 q 離開: ").strip().lower()

        if choice == 'q':
            print("\n👋 再見！")
            break

        try:
            choice_num = int(choice)
        except ValueError:
            print("\n⚠️  請輸入有效的數字")
            continue

        if choice_num == 5:
            # 自訂設定
            config = get_custom_config()
        elif 1 <= choice_num <= 4:
            # 預設風格
            config = apply_preset(choice_num)
            if config:
                # 詢問是否要微調
                tune = input("\n要微調這些設定嗎？ (y/n，直接 Enter 跳過): ").strip().lower()
                if tune == 'y':
                    config = fine_tune_config(config)
        else:
            print("\n⚠️  請輸入 1-5 之間的數字")
            continue

        if config is None:
            continue

        # 確認套用
        print("\n" + "-" * 70)
        print("📋 即將套用以下設定：")
        print(f"  • 像素大小: {config['pixel_size']}x{config['pixel_size']}")
        print(f"  • 顏色數量: {config['num_colors']} 色")
        print(f"  • 輪廓效果: {'是' if config['outline'] else '否'}")
        print(f"  • 抖動效果: {'是' if config['dither'] else '否'}")
        print(f"  • 輸出檔名: [檔名]_{config['name']}.png")
        print("-" * 70)

        confirm = input("\n確定套用？ (y/n): ").lower()

        if confirm == 'y':
            if update_auto_watch(config):
                print("\n✅ 風格設定已更新！")
                print("\n💡 下一步：")
                print("  1. 重新啟動 auto_watch.py (如果正在運行)")
                print("  2. 或直接執行 python auto_watch.py")
                print("  3. 新圖片會自動套用新風格")

                # 詢問是否立即轉換現有圖片
                convert = input("\n要立即轉換現有圖片嗎？ (y/n): ").lower()
                if convert == 'y':
                    print("\n🔄 正在轉換...")
                    # 檢查是否有圖片
                    photo_dir = "assets/photo"
                    output_dir = "assets/pixelated"

                    # 創建輸出資料夾
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                        print(f"✓ 已創建資料夾: {output_dir}")

                    if os.path.exists(photo_dir):
                        # 轉換所有圖片（現在不需要過濾，因為輸出到不同資料夾）
                        images = []
                        for f in os.listdir(photo_dir):
                            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                                images.append(f)

                        if images:
                            from pixelate_advanced import pixelate_advanced
                            for img in images:
                                input_path = os.path.join(photo_dir, img)
                                base_name = os.path.splitext(img)[0]
                                # 輸出到 pixelated 資料夾，保持原檔名
                                output_path = os.path.join(
                                    output_dir, f"{base_name}.png")

                                print(f"  轉換中: {img}...")
                                try:
                                    pixelate_advanced(
                                        input_path=input_path,
                                        output_path=output_path,
                                        pixel_size=config['pixel_size'],
                                        num_colors=config['num_colors'],
                                        add_outline_effect=config['outline'],
                                        dither=config['dither'],
                                        outline_thickness=config.get(
                                            'outline_thickness', 1)
                                    )
                                    print(
                                        f"  ✓ 完成: {os.path.basename(output_path)}")
                                except Exception as e:
                                    print(f"  ✗ 失敗: {e}")

                            print("\n✅ 所有圖片轉換完成！")
                        else:
                            print(f"  ⚠️  在 {photo_dir} 中找不到圖片")
                    else:
                        print(f"  ⚠️  找不到 {photo_dir} 資料夾")

                break
            else:
                print("\n❌ 更新失敗，請檢查錯誤訊息")
        else:
            print("\n❌ 已取消")


if __name__ == "__main__":
    main()
