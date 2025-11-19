# 2D角色动画系统

基于Pygame的2D骨骼动画系统，支持角色姿势切换和平滑动画过渡。

## 功能特性

- ✅ 图片分割：根据预定义区域自动分割身体部位
- ✅ 骨骼系统：父子层级关系的身体部位管理
- ✅ 多种姿势：T-Pose、准备、出拳、踢腿
- ✅ 平滑过渡：姿势之间的缓动动画
- ✅ 键盘控制：实时切换动作
- ✅ 可替换角色：支持更换不同的角色图片

## 安装依赖

```bash
pip install pygame
```

## 运行程序

```bash
python main.py
```

## 控制说明

- **1** - T-Pose姿势（初始姿势）
- **2** - 准备姿势（战斗准备）
- **3** 或 **P** - 出拳动作
- **4** 或 **K** - 踢腿动作
- **ESC** - 退出程序

## 文件结构

```
motion test_3/
├── main.py              # 主程序入口
├── body_parts.py        # 身体部位分割定义
├── skeleton.py          # 骨骼系统和变换
├── animation.py         # 动画控制和姿势数据
├── sample/
│   ├── tpose.png       # T-Pose原始图片
│   ├── slice_sample.png # 分割参考图
│   ├── punch.png       # 出拳参考图
│   └── kick.png        # 踢腿参考图
└── README.md           # 说明文档
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
