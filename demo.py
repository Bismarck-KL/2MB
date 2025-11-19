"""
Quick Demo: Pixelate Character and Show Animation
Creates pixel art version and launches the animation system
"""
import os
import sys
import subprocess


def main():
    print("=" * 70)
    print("PIXEL ART CHARACTER ANIMATION - QUICK DEMO")
    print("=" * 70)
    
    # Check if pixelated version exists
    pixel_file = "sample/tpose_8bit.png"
    
    if not os.path.exists(pixel_file):
        print("\n📦 Creating 8-bit pixel art version...")
        print("   This will take a moment...\n")
        
        # Create pixelated version automatically
        try:
            # Use pixelate_advanced with preset
            result = subprocess.run(
                [sys.executable, "pixelate_advanced.py"],
                input="sample/tpose.png\n1\nn\n",
                text=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                print("\n✓ Pixel art created successfully!")
            else:
                print(f"\n⚠ Warning: {result.stderr}")
        except Exception as e:
            print(f"\n✗ Error creating pixel art: {e}")
            print("   Using original image instead.")
    else:
        print(f"\n✓ Found existing pixel art: {pixel_file}")
    
    # Launch main animation
    print("\n🎮 Launching animation system...")
    print("\nControls:")
    print("  1/B - Block    2 - Ready    3/P - Punch")
    print("  4/K - Kick     Space/J - Jump")
    print("  F6 - Reload    ESC - Quit")
    print("\n" + "=" * 70)
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\n✓ Demo ended.")


if __name__ == "__main__":
    main()
