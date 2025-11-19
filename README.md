# 2D Character Animation System

Pygame-based 2D skeletal animation system with character pose switching and smooth animation transitions.

## Features

- ✅ Image Slicing: Automatic body part segmentation based on predefined regions
- ✅ Skeletal System: Parent-child hierarchical body part management
- ✅ Multiple Poses: Block, Ready, Punch, Kick, Jump, Custom
- ✅ Smooth Transitions: Easing animations between poses
- ✅ Keyboard Controls: Real-time action switching
- ✅ Character Replacement: Support for different character images
- ✅ **Pixel Art Converter: Transform any image into 8-bit pixel art style**
- ✅ Pose Adjustment Tool: Visual pose editor with direct save to code
- ✅ Hot-Reload: Press F6 to reload poses without restarting

## 安装依赖

```bash
pip install pygame
```

## 运行程序

```bash
python main.py
```

## Controls

- **1** or **B** - Block pose (auto-return)
- **2** - Ready pose (battle stance)
- **3** or **P** - Punch action (auto-return)
- **4** or **K** - Kick action (auto-return)
- **Space** or **J** - Jump action (auto-return)
- **F5** or **L** - Load custom pose
- **F6** - Hot-reload all poses
- **ESC** - Quit

## 🎨 NEW: Pixel Art Converter

Transform any character image into retro 8-bit pixel art style!

### Quick Start
```bash
# Simple pixelation
python pixelate_image.py

# Advanced with custom palette
python pixelate_advanced.py
```

### Features
- **Automatic color palette extraction** - Smart color reduction
- **Pixel size control** - From chunky 16x16 to fine 4x4
- **Outline generation** - Add black borders for clarity
- **Dithering support** - Smoother gradients
- **Before/After preview** - See the transformation

### Pixelation Styles

#### Style 1: Classic 8-bit (Recommended)
```bash
python pixelate_advanced.py
# Select option 1
# Pixel size: 8x8, Colors: 16, Outline: Yes
```
Perfect for retro Mario/Zelda style!

#### Style 2: Retro 16-bit
```bash
# Select option 2
# Pixel size: 4x4, Colors: 32, Outline: Yes
```
More detailed, SNES-era graphics

#### Style 3: Chunky Pixel
```bash
# Select option 3
# Pixel size: 16x16, Colors: 12, Outline: Yes
```
Bold, high-contrast pixel art

### Usage Example
```bash
# Convert your character
python pixelate_advanced.py
# Input: sample/tpose.png
# Output: sample/tpose_8bit.png

# The system will auto-detect and use pixelated version!
python main.py
```

## File Structure

```
motion test_3/
├── main.py                 # Main game loop
├── body_parts.py          # Body part slicing definitions
├── skeleton.py            # Skeletal system and transforms
├── animation.py           # Animation controller and pose data
├── pose_tool.py           # Visual pose adjustment tool
├── pixelate_image.py      # Simple pixelation tool
├── pixelate_advanced.py   # Advanced pixel art converter ⭐
├── update_animation.py    # Direct pose-to-code updater
├── sample/
│   ├── tpose.png         # Original T-pose image
│   ├── tpose_8bit.png    # Pixelated version (auto-generated)
│   ├── slice_sample.png  # Slicing reference
│   ├── punch.png         # Punch reference
│   └── kick.png          # Kick reference
├── pose_*.json           # Saved pose configurations
└── README.md             # Documentation
```

## 如何替换角色

### 方法1：修改默认图片
直接替换 `sample/tpose.png` 文件，保持相同的文件名。

### 方法2：代码中指定
修改 `main.py` 中的路径：
```python
game = CharacterAnimator("你的图片路径.png")
```

### 方法3：运行时切换
在代码中调用：
```python
game.reload_character("新图片路径.png")
```

## 自定义分割区域

如果你的角色图片尺寸不同，需要修改 `body_parts.py` 中的坐标：

```python
class BodyParts:
    def __init__(self):
        # 修改这些坐标以匹配你的图片
        self.head = (x, y, width, height)
        self.torso = (x, y, width, height)
        # ... 其他部位
```

## 自定义动作姿势

在 `animation.py` 中添加新姿势：

```python
@staticmethod
def get_custom_pose():
    return {
        'torso': {'rotation': 0, 'position': [0, 0]},
        'head': {'rotation': 0, 'position': [0, -100]},
        # ... 其他部位的旋转和位置
    }
```

然后在 `get_all_poses()` 中注册：
```python
return {
    'tpose': Poses.get_tpose(),
    'ready': Poses.get_ready(),
    'punch': Poses.get_punch(),
    'kick': Poses.get_kick(),
    'custom': Poses.get_custom_pose()  # 新增
}
```

## 技术细节

### 骨骼层级结构
```
躯干 (根节点)
├── 头部
├── 左上臂
│   └── 左前臂
├── 右上臂
│   └── 右前臂
├── 左大腿
│   └── 左小腿
└── 右大腿
    └── 右小腿
```

### 坐标系统
- 使用父子层级变换
- 每个部位有本地坐标和世界坐标
- 旋转基于设定的旋转中心点（pivot）

### 动画系统
- 使用线性插值（LERP）实现平滑过渡
- 应用缓动函数（ease-out）使动画更自然
- 可调节过渡速度

## 故障排除

### 问题：角色显示不正确
- 检查图片路径是否正确
- 确认 `body_parts.py` 中的坐标匹配你的图片

### 问题：动作不自然
- 调整 `animation.py` 中的姿势数据
- 修改 `transition_speed` 改变动画速度

### 问题：pygame初始化失败
- 确保已安装pygame: `pip install pygame`
- 检查Python版本（建议3.7+）

## 许可证

MIT License
