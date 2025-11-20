"""
Automatic File Watcher - Monitors tpose images and auto-converts to pixel art
Watches assets\photo folder for changes to tpose.png or tpose.jpg
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog module not found!")
    print("Installing watchdog...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

# Import our pixelation tool
from pixelate_advanced import pixelate_advanced


class ImageWatcher(FileSystemEventHandler):
    """Monitors image file changes and triggers pixel art conversion"""

    def __init__(self, watch_folder="assets\\photo", output_folder="assets\\pixelated"):
        self.watch_folder = watch_folder
        self.output_folder = output_folder
        self.target_extensions = [".png", ".jpg", ".jpeg"]
        self.processing = False
        self.last_processed = {}
        self.cooldown = 2  # seconds between processing same file

        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ Created output folder: {self.output_folder}")

        print(f"🔍 Watching folder: {os.path.abspath(watch_folder)}")
        print(f"📤 Output folder: {os.path.abspath(output_folder)}")
        print(f"📁 Watching all images: *{', *'.join(self.target_extensions)}")
        print("=" * 60)

    def on_modified(self, event):
        """Called when a file is modified"""
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        file_ext = os.path.splitext(filename)[1].lower()

        # Check if it's an image file
        if file_ext not in self.target_extensions:
            return

        # Skip output files (already pixelated) - check if filename has common suffixes
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        # If the last part looks like a style suffix (all lowercase letters, short), skip
        if len(parts) > 1 and parts[-1].isalpha() and len(parts[-1]) < 10:
            return

        # Cooldown check to avoid multiple triggers
        now = time.time()
        if filename in self.last_processed:
            if now - self.last_processed[filename] < self.cooldown:
                return

        self.last_processed[filename] = now

        # Avoid recursive processing
        if self.processing:
            return

        self.process_image(event.src_path)

    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext not in self.target_extensions:
            return

        # No need to filter - all files in watch folder are source files

        # Small delay to ensure file is fully written
        time.sleep(0.5)
        self.process_image(event.src_path)

    def process_image(self, image_path):
        """Convert image to pixel art"""
        self.processing = True

        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"\n[{timestamp}] 🎨 偵測到變更: {os.path.basename(image_path)}")

            # Check if file exists and is accessible
            if not os.path.exists(image_path):
                print(f"   ⚠️  找不到檔案，跳過...")
                return

            file_size = os.path.getsize(image_path)
            if file_size == 0:
                print(f"   ⚠️  檔案為空，等待中...")
                time.sleep(1)
                return

            print(f"   📊 檔案大小: {file_size:,} bytes")
            print(f"   🔄 轉換成像素風格中...")

            # Generate output path - same filename, different folder
            filename = os.path.basename(image_path)
            base_name = Path(image_path).stem
            output_path = os.path.join(
                self.output_folder, f"{base_name}.png")

            # Run pixelation with current style
            pixelate_advanced(
                input_path=image_path,
                output_path=output_path,
                pixel_size=16,
                num_colors=32,
                add_outline_effect=False,
                dither=False,
                outline_thickness=1
            )

            output_size = os.path.getsize(output_path)
            print(f"   ✅ 轉換完成！")
            print(
                f"   💾 輸出檔案: {os.path.basename(output_path)} ({output_size:,} bytes)")
            print(f"   📍 位置: {output_path}")
            print("=" * 60)

        except Exception as e:
            print(f"   ❌ 轉換時發生錯誤: {e}")
            print("=" * 60)

        finally:
            self.processing = False


def main():
    """Main function to start the file watcher"""
    watch_folder = "assets\\photo"

    # Create assets\photo folder if it doesn't exist
    if not os.path.exists(watch_folder):
        os.makedirs(watch_folder)
        print(f"✓ Created folder: {watch_folder}")

    print("\n" + "=" * 60)
    print("🎮 2D 動畫系統 - 自動像素風格轉換器")
    print("=" * 60)
    print("\n📝 使用說明：")
    print("   1. 將原始圖片放在 assets\\photo 資料夾")
    print("   2. 工具會自動轉換並輸出到 assets\\pixelated 資料夾")
    print("   3. 輸出檔案會保持原檔名（例如: tpose.png）")
    print("   4. 執行 main.py 自動使用像素化角色！")
    print("\n💡 調整風格：")
    print("   • 執行 python style_config.py 選擇預設風格或自訂設定")
    print("   • pixel_size: 像素大小 (4=細緻, 8=經典, 16=大塊)")
    print("   • num_colors: 顏色數量 (16=復古, 32=豐富)")
    print("   • add_outline_effect: 是否加輪廓 (True/False)")
    print("   • dither: 是否使用抖動效果 (True/False)")
    print("\n⌨️  控制方式：")
    print("   • 按 'q' + Enter 鍵停止監視")
    print("   • 或按 Ctrl+C 強制退出")
    print("\n")

    # Create event handler and observer
    event_handler = ImageWatcher(watch_folder)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)

    # Start watching
    observer.start()
    print("✅ 監視已啟動！等待檔案變更中...")
    print("💡 提示：輸入 'q' 然後按 Enter 可停止監視\n")

    try:
        # Use input() to allow graceful exit
        while observer.is_alive():
            # Check for user input without blocking (Windows compatible)
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                if key == 'q':
                    print("\n⏹️  收到停止指令，正在關閉監視...")
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n⏹️  收到中斷訊號，正在停止監視...")
    finally:
        observer.stop()
        observer.join()
        print("👋 監視已停止。再見！")


if __name__ == "__main__":
    main()
