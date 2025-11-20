# PixelArt-Animation 整合到 2MB 遊戲 - 完整說明

## ✅ 整合狀態

### 已完成的功能

1. **動畫系統核心**
   - ✅ 骨骼動畫系統 (skeleton.py, body_parts.py, animation.py)
   - ✅ 動畫控制器 (AnimationController)
   - ✅ 姿勢定義 (ready, block, punch, kick, jump, hurt)
   - ✅ 平滑過渡動畫
   - ✅ 像素化效果

2. **2MB 遊戲整合**
   - ✅ AnimatedCharacter 包裝類 (`classes/animated_character.py`)
   - ✅ Player 類擴展支援動畫 (`classes/player.py`)
   - ✅ GameScene 整合雙角色動畫 (`game_scene.py`)
   - ✅ 自動配置系統 (`body_parts_profiles.py`)

3. **配置管理系統**
   - ✅ 多角色配置支援 (default, player1, player2)
   - ✅ 自動路徑偵測
   - ✅ 配置文件載入/儲存

4. **工具**
   - ✅ 調整工具 v2 (`tools/adjust_tool_v2.py`)
   - ✅ 診斷工具 (`diagnose.py`)
   - ✅ 測試工具 (`test_integration.py`)

### 修復的問題

**最新修復 (2025-11-20):**
- ✅ 雙玩家獨立渲染問題：添加 skeleton 位置狀態保存/恢復機制
- ✅ 角色圖片配置：Player 1 和 Player 2 現在使用各自的圖片
  - Player 1: `assets/photo/player1/tpose.png`
  - Player 2: `assets/photo/player2/tpose.png`

**之前的修復：**

1. **骨骼連接問題** ✅
   - 問題：肢體分散在畫面四周
   - 原因：`render()` 中 `set_position()` 後沒調用 `update()`
   - 解決：在 `skeleton.set_position()` 後調用 `skeleton.update()`

2. **像素化效果** ✅
   - 問題：像素化不顯示或效能差
   - 解決：使用優化的 `_pixelate_surface_fast()` 方法

3. **顏色處理** ✅
   - 問題：`_find_nearest_color()` 無法處理 pygame.Color
   - 解決：添加類型檢測

4. **姿勢初始化** ✅
   - 問題：初始化後沒有應用姿勢
   - 解決：在創建 AnimationController 後立即調用 `set_pose('ready', immediate=True)`

## 🎮 使用方法

### 1. 啟動 2MB 遊戲（動畫系統）

```bash
python start.py
```

1. 點擊 **"Start"** 按鈕進入 Game Scene
2. 看到兩個動畫角色（使用 sample/tpose.png）

**Player 1 控制鍵：**
- `1` 或 `B` - Block
- `2` - Ready
- `3` 或 `P` - Punch
- `4` 或 `K` - Kick
- `5` 或 `H` - Hurt
- `J` - Jump

**Player 2 控制鍵：**
- `U` - Block
- `I` - Punch
- `O` - Kick
- `L` - Hurt

### 2. 測試動畫系統

```bash
python test_integration.py
```

- 空白鍵 - 切換姿勢
- 1-4 - 直接選擇姿勢
- ESC - 退出

### 3. 原始動畫編輯器

```bash
python main.py
```

完整的動畫編輯和測試環境。

## 📁 檔案結構

```
PixelArt-Animation/
├── main.py                          # 原始動畫編輯器
├── start.py                         # 2MB 遊戲入口
├── game_scene.py                    # 遊戲場景（已整合動畫）
├── skeleton.py                      # 骨骼系統
├── body_parts.py                    # 身體部位定義（原始）
├── body_parts_profiles.py           # 多角色配置系統（新）
├── animation.py                     # 動畫控制器
├── config.py                        # 視窗配置
├── launcher.py                      # 多解析度啟動器
│
├── classes/
│   ├── animated_character.py        # 動畫角色包裝類（核心）
│   └── player.py                    # 玩家類（支援動畫）
│
├── tools/
│   └── adjust_tool_v2.py            # 座標調整工具
│
├── assets/
│   └── photo/
│       ├── player1/                 # Player 1 圖片
│       │   └── tpose.png
│       └── player2/                 # Player 2 圖片
│           └── tpose.png
│
├── sample/
│   └── tpose.png                    # 範例圖（已調整座標）
│
└── docs/
    ├── BODY_PARTS_CONFIG_GUIDE.md   # 配置系統指南
    └── FIX_SUMMARY.md               # 修復摘要
```

## 🔧 使用自己的角色圖片

### 步驟 1: 準備圖片

將你的 T-pose 角色圖放到：
- `assets/photo/player1/tpose.png`
- `assets/photo/player2/tpose.png`

圖片要求：
- PNG 格式，透明背景
- T-pose 姿勢（雙臂平舉，雙腿分開）
- 建議尺寸：1028x720

### 步驟 2: 調整座標

```bash
# Player 1
python tools/adjust_tool_v2.py assets/photo/player1/tpose.png player1

# Player 2
python tools/adjust_tool_v2.py assets/photo/player2/tpose.png player2
```

**調整工具操作：**
- `Tab` - 切換到下一個部位
- `Shift+Tab` - 切換到上一個部位
- `M` - 切換位置/大小模式
- `方向鍵` - 調整（Shift+方向鍵 = 快速）
- `S` - 儲存配置
- `ESC` - 退出

### 步驟 3: 更新配置

將調整工具輸出的座標複製到 `body_parts_profiles.py` 中對應的配置。

### 步驟 4: 啟用自訂角色

編輯 `game_scene.py`:

```python
self.player_1 = Player(app, 0, image_key="player1",
                       use_animation=True,
                       animation_image="assets/photo/player1/tpose.png")

self.player_2 = Player(app, 1, image_key="player2",
                       use_animation=True,
                       animation_image="assets/photo/player2/tpose.png")
```

## ⚙️ 配置選項

### 像素化效果

在 `classes/animated_character.py` 的 `__init__`:

```python
self.enable_pixelate = True      # 啟用/禁用
self.pixel_size = 4              # 像素大小 (2-16)
self.num_colors = 16             # 顏色數量 (4-32)
```

### 角色縮放

在 `game_scene.py`:

```python
Player(app, 0, image_key="player1",
       use_animation=True,
       animation_image="sample/tpose.png")  # scale 在 AnimatedCharacter 中設為 0.5
```

## 🐛 故障排除

### 問題：只看到軀幹，肢體在角落

**已修復！** 確保 `classes/animated_character.py` 的 `render()` 方法中包含：

```python
self.skeleton.set_position(center_x, center_y)
self.skeleton.update()  # ← 重要！
self.skeleton.draw(self.render_surface)
```

### 問題：角色圖片不正確

確認：
1. 圖片路徑正確
2. 如果是自訂角色，確認座標已調整
3. 檢查終端輸出是否有 "✓ 自動偵測配置"

### 問題：像素化效果不顯示

確認 `enable_pixelate=True` 並且 `pixel_size > 0`

### 問題：動畫不流暢

檢查：
1. FPS 設置（config.py 中 FPS=60）
2. 電腦效能
3. 像素化效果的 `pixel_size` 和 `num_colors` 是否過高

## 📝 開發筆記

### 關鍵修復

1. **骨骼渲染修復** (最重要)
   ```python
   # 在 render() 中必須調用
   self.skeleton.update()
   ```

2. **姿勢初始化**
   ```python
   self.animation_controller.set_pose('ready', immediate=True)
   self.skeleton.update()
   ```

3. **像素化優化**
   ```python
   # 使用快速方法
   _pixelate_surface_fast()
   ```

### 架構設計

- **AnimatedCharacter**: 包裝骨骼系統，提供簡單的接口
- **Player**: 支援動畫和靜態兩種模式
- **BodyPartsConfig**: 多角色配置，自動路徑偵測

### 效能考量

- 離屏渲染到 surface 再縮放和像素化
- 動畫過渡使用 easing function
- 配置自動偵測避免重複計算

## 🎯 下一步

1. ✅ 動畫系統整合完成
2. ✅ 測試工具完成
3. ⏭️ 為 player1/player2 調整座標（可選）
4. ⏭️ 添加更多姿勢動畫（可選）
5. ⏭️ 優化像素化效果（可選）

## 📚 參考文件

- `BODY_PARTS_CONFIG_GUIDE.md` - 配置系統詳細說明
- `FIX_SUMMARY.md` - 修復歷史
- `RESOLUTION_GUIDE.md` - 解析度系統
- `CHARACTER_SETUP.md` - 角色設置
