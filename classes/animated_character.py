"""
AnimatedCharacter class - 整合骨骼動畫系統到2MB遊戲中
Integrates the skeletal animation system into the 2MB game
"""

import pygame
import os
from collections import Counter
import weakref

from .body_parts import BodyParts
from .skeleton import Skeleton, BodyPart
from .animation import AnimationController
from .body_parts_profiles import BodyPartsConfig


class AnimatedCharacter:
    """
    包裝骨骼動畫系統的角色類別
    用於在遊戲主循環中渲染和控制動畫角色
    """

    def __init__(self, image_path="assets/photo/tpose.png", scale=1.0, enable_pixelate=True, flip_horizontal=False):
        """
        初始化動畫角色

        Args:
            image_path: T-pose圖片路徑
            scale: 縮放比例
            enable_pixelate: 是否啟用像素化效果
            flip_horizontal: 是否水平翻轉（鏡像）
        """
        # 載入並切割圖片
        self._load_and_setup_skeleton(image_path)

        # 縮放和位置
        self.scale = scale
        self.position = [0, 0]  # 世界位置
        self.flip_horizontal = flip_horizontal

        # 像素化設置 - 強制使用固定值
        self.enable_pixelate = enable_pixelate
        # 硬性設定：PIXEL = 6, COLOR = 32
        self.pixel_size = 6
        self.num_colors = 32

        # 用於渲染的離屏surface
        self.render_surface = None
        self.final_surface = None

        # SFX paths and lazy cache. Prefer using an external ResourceManager
        # when available (passed as `res_mgr`) so sounds are shared and cached.
        self._sfx_paths = {
            'punch': 'assets/sounds/punch sfx.mp3',
            'kick': 'assets/sounds/kick sfx.mp3',
            'jump': 'assets/sounds/jump sfx.mp3',
            'hurt': 'assets/sounds/hurt sfx.mp3',
            'block': 'assets/sounds/block sfx.mp3',
        }
        self._sfx_cache = {}
        # optional ResourceManager instance (set when caller passes it)
        self.res_mgr = None

    def _load_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"[SFX] Failed to load {path}: {e}")
            return None

    def set_resource_manager(self, res_mgr):
        """Optionally provide a ResourceManager instance so this class
        can ask it for shared sounds via `get_sound(path)`.
        """
        try:
            self.res_mgr = res_mgr
        except Exception:
            self.res_mgr = None

    def _get_sfx(self, name):
        """Return a pygame.mixer.Sound for `name` (lazy, cached).

        If a ResourceManager (`self.res_mgr`) is available, use
        `res_mgr.get_sound(path)` so sounds are shared across objects.
        """
        path = self._sfx_paths.get(name)
        if not path:
            return None

        # try resource manager first
        if self.res_mgr:
            try:
                snd = self.res_mgr.get_sound(path)
                if snd:
                    return snd
            except Exception:
                pass

        # fallback to local cache + load
        snd = self._sfx_cache.get(name)
        if snd is not None:
            return snd

        try:
            snd = pygame.mixer.Sound(path)
            self._sfx_cache[name] = snd
            return snd
        except Exception:
            return None

    def _load_and_setup_skeleton(self, image_path):
        """載入圖片並建立骨骼系統"""
        # 載入圖片 - prefer ResourceManager-provided surface when available
        original_image = None
        try:
            if self.res_mgr:
                try:
                    original_image = self.res_mgr.get_image_by_path(image_path)
                except Exception:
                    original_image = None
        except Exception:
            original_image = None

        if original_image is None:
            try:
                original_image = pygame.image.load(image_path)
                try:
                    original_image = original_image.convert_alpha()
                except Exception:
                    original_image = original_image.convert()
            except Exception:
                # loading failed; raise so callers can handle or fallback
                raise

        # 獲取身體部位定義 - 自動根據圖片路徑選擇配置
        body_parts_def = BodyPartsConfig.from_image_path(image_path)
        parts_dict = body_parts_def.get_all_parts()

        # 切割圖片並創建身體部位
        part_images = {}
        for part_name, (x, y, w, h) in parts_dict.items():
            part_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            part_surface.blit(original_image, (0, 0), (x, y, w, h))
            part_images[part_name] = part_surface

        # 創建骨骼系統
        self.skeleton = Skeleton()

        # 創建軀幹（根節點）
        torso = BodyPart(
            'torso',
            part_images['torso'],
            pivot_offset=(part_images['torso'].get_width() / 2,
                          part_images['torso'].get_height() / 2)
        )
        self.skeleton.set_root(torso)

        # 創建頭部
        head = BodyPart(
            'head',
            part_images['head'],
            pivot_offset=(part_images['head'].get_width() / 2,
                          part_images['head'].get_height() - 5),
            parent=torso
        )
        head.local_position = [0, -60]  # 頸部連接點（從軀幹中心向上）
        self.skeleton.add_part(head)

        # 左上臂
        left_upper_arm = BodyPart(
            'left_upper_arm',
            part_images['left_upper_arm'],
            pivot_offset=(
                part_images['left_upper_arm'].get_width() * 0.75, 15),
            parent=torso
        )
        left_upper_arm.local_position = [-50, -45]  # 左肩連接點
        self.skeleton.add_part(left_upper_arm)

        # 左前臂
        left_forearm = BodyPart(
            'left_forearm',
            part_images['left_forearm'],
            pivot_offset=(part_images['left_forearm'].get_width() * 0.85,
                          part_images['left_forearm'].get_height() / 2),
            parent=left_upper_arm
        )
        left_forearm.local_position = [-40, 25]  # 左肘連接點
        self.skeleton.add_part(left_forearm)

        # 右上臂
        right_upper_arm = BodyPart(
            'right_upper_arm',
            part_images['right_upper_arm'],
            pivot_offset=(
                part_images['right_upper_arm'].get_width() * 0.25, 15),
            parent=torso
        )
        right_upper_arm.local_position = [50, -45]  # 右肩連接點
        self.skeleton.add_part(right_upper_arm)

        # 右前臂
        right_forearm = BodyPart(
            'right_forearm',
            part_images['right_forearm'],
            pivot_offset=(part_images['right_forearm'].get_width() * 0.15,
                          part_images['right_forearm'].get_height() / 2),
            parent=right_upper_arm
        )
        right_forearm.local_position = [40, 25]  # 右肘連接點
        self.skeleton.add_part(right_forearm)

        # 左大腿
        left_thigh = BodyPart(
            'left_thigh',
            part_images['left_thigh'],
            pivot_offset=(part_images['left_thigh'].get_width() / 2, 15),
            parent=torso
        )
        left_thigh.local_position = [-25, 60]  # 左髖連接點
        self.skeleton.add_part(left_thigh)

        # 左小腿
        left_shin = BodyPart(
            'left_shin',
            part_images['left_shin'],
            pivot_offset=(part_images['left_shin'].get_width() / 2, 15),
            parent=left_thigh
        )
        left_shin.local_position = [0, 80]  # 左膝連接點
        self.skeleton.add_part(left_shin)

        # 右大腿
        right_thigh = BodyPart(
            'right_thigh',
            part_images['right_thigh'],
            pivot_offset=(part_images['right_thigh'].get_width() / 2, 15),
            parent=torso
        )
        right_thigh.local_position = [25, 60]  # 右髖連接點
        self.skeleton.add_part(right_thigh)

        # 右小腿
        right_shin = BodyPart(
            'right_shin',
            part_images['right_shin'],
            pivot_offset=(part_images['right_shin'].get_width() / 2, 15),
            parent=right_thigh
        )
        right_shin.local_position = [0, 80]  # 右膝連接點
        self.skeleton.add_part(right_shin)

        # 創建動畫控制器
        self.animation_controller = AnimationController(self.skeleton)

        # register instance in global weak registry so tools can broadcast updates
        try:
            GLOBAL_ANIM_CHAR_REGISTRY.add(self)
            try:
                print(f"[AnimatedCharacter] Registered instance: {repr(self)}")
            except Exception:
                print("[AnimatedCharacter] Registered instance")
        except Exception:
            pass

        # NOTE: settings.json is intentionally ignored so pixel settings
        # remain fixed to PIXEL=6, COLOR=32 as requested.

        # 應用初始姿勢並更新骨骼
        self.animation_controller.set_pose('ready', immediate=True)
        self.skeleton.update()

        # Intentionally not applying persisted settings to enforce fixed pixel values.

    def set_position(self, x, y):
        """設置角色在遊戲世界中的位置"""
        self.position = [x, y]

    def set_pose(self, pose_name):
        """
        切換姿勢

        Args:
            pose_name: 姿勢名稱 ('ready', 'block', 'punch', 'kick', 'jump', 'hurt')
        """
        self.animation_controller.set_pose(pose_name)

    def trigger_action(self, action_name, duration=0.5):
        """
        觸發動作（自動返回）
        AnimationController會自動處理返回到ready姿勢

        Args:
            action_name: 動作名稱
            duration: 動作持續時間（秒）- 目前由AnimationController自動控制
        """
        # 播放對應聲效（lazy, 使用 ResourceManager 若可用）
        snd = self._get_sfx(action_name)
        if snd:
            try:
                snd.play()
            except Exception:
                # ignore sound playback errors
                pass
        self.animation_controller.set_pose(action_name)

    def update(self, dt):
        """
        更新動畫狀態

        Args:
            dt: Delta time (秒) - 目前AnimationController不使用dt，未來可能需要
        """
        # pass dt into the animation controller (now time-based)
        try:
            self.animation_controller.update(dt)
        except TypeError:
            # fallback if controller doesn't accept dt for some reason
            self.animation_controller.update()

    def render(self, target_surface, offset=(0, 0)):
        """
        渲染角色到目標surface

        Args:
            target_surface: 目標pygame surface
            offset: 額外偏移量 (x, y)
        """
        # 計算渲染區域大小
        base_size = (600, 800)  # 基礎渲染大小（更大以容納完整角色）

        # 應用縮放後的大小
        render_size = (int(base_size[0] * self.scale),
                       int(base_size[1] * self.scale))

        # 創建或重用離屏surface
        if self.render_surface is None or self.render_surface.get_size() != base_size:
            self.render_surface = pygame.Surface(base_size, pygame.SRCALPHA)

        # 清空並渲染骨骼
        self.render_surface.fill((0, 0, 0, 0))

        # 將骨骼位置設置到渲染surface的中心
        center_x = base_size[0] // 2
        center_y = base_size[1] // 2

        # --- 根據腳距離動態繪製影子 ---
        left_shin = self.skeleton.get_part('left_shin') if hasattr(self.skeleton, 'get_part') else None
        right_shin = self.skeleton.get_part('right_shin') if hasattr(self.skeleton, 'get_part') else None
        if left_shin and right_shin:
            lx, ly = left_shin.world_position
            rx, ry = right_shin.world_position
            foot_dist = abs(rx - lx)
            shadow_width = max(int(foot_dist * 1.2), int(80 * self.scale))
            shadow_height = int(40 * self.scale)
            # 轉換到 render_surface 座標
            root_x, root_y = self.skeleton.root.world_position
            avg_x = (lx + rx) / 2
            avg_y = (ly + ry) / 2
            rel_x = center_x + (avg_x - root_x) - shadow_width // 2
            rel_y = center_y + (avg_y - root_y) - shadow_height // 2
            rel_y -= 15  # 向上偏移 15 pixel
            # fallback: 如果影子超出 render surface，則用預設位置
            if not (0 <= rel_x <= self.render_surface.get_width() - shadow_width and 0 <= rel_y <= self.render_surface.get_height() - shadow_height):
                rel_x = center_x - shadow_width // 2
                rel_y = center_y + 320 - shadow_height // 2
                rel_y -= 15  # 向上偏移 15 pixel
            shadow_x = int(rel_x)
            shadow_y = int(rel_y)
        else:
            shadow_width = int(120 * self.scale)
            shadow_height = int(40 * self.scale)
            shadow_x = center_x - shadow_width // 2
            shadow_y = center_y + 320 - shadow_height // 2
        shadow_color = (0, 0, 0, 80)  # 半透明黑色
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, shadow_color, (0, 0, shadow_width, shadow_height))
        self.render_surface.blit(shadow_surface, (shadow_x, shadow_y))

        # 保存原始位置
        original_offset = self.skeleton.root_offset[:]
        original_world_pos = self.skeleton.root.world_position[:]

        # 臨時設置渲染位置
        self.skeleton.set_position(center_x, center_y)
        self.skeleton.update()

        # 渲染
        self.skeleton.draw(self.render_surface)

        # 恢復原始位置（防止影響其他實例）
        self.skeleton.root_offset = original_offset
        self.skeleton.root.world_position = original_world_pos

        # 先應用縮放
        if self.scale != 1.0:
            scaled = pygame.transform.smoothscale(
                self.render_surface, render_size)
        else:
            scaled = self.render_surface

        # 再應用像素化效果（在縮放後的圖像上）
        if self.enable_pixelate:
            final = self._pixelate_surface_fast(
                scaled, self.pixel_size, self.num_colors)
        else:
            final = scaled

        # 應用水平翻轉（如果需要）
        if self.flip_horizontal:
            final = pygame.transform.flip(final, True, False)

        # 計算最終位置（中心對齊）
        final_rect = final.get_rect()
        final_rect.center = (
            self.position[0] + offset[0], self.position[1] + offset[1])

        # 繪製到目標surface
        target_surface.blit(final, final_rect)

    def _pixelate_surface_fast(self, surface, pixel_size, num_colors):
        """快速像素化效果（使用 main.py 的優化方法）"""
        width, height = surface.get_size()

        # 確保尺寸能被 pixel_size 整除
        new_width = (width // pixel_size) * pixel_size
        new_height = (height // pixel_size) * pixel_size

        if new_width == 0 or new_height == 0:
            return surface

        # 縮小尺寸
        small_width = new_width // pixel_size
        small_height = new_height // pixel_size

        # 裁剪到可整除的尺寸
        cropped = surface.subsurface((0, 0, new_width, new_height)).copy()

        # 縮小
        small_surface = pygame.transform.scale(
            cropped, (small_width, small_height))

        # 獲取調色板
        palette = self._get_dominant_colors_fast(small_surface, num_colors)

        # 應用調色板
        for x in range(small_width):
            for y in range(small_height):
                color = small_surface.get_at((x, y))
                if color.a > 128:  # 只處理不透明像素
                    nearest = self._find_nearest_color(color, palette)
                    small_surface.set_at((x, y), (*nearest, color.a))

        # 放大回原尺寸
        pixelated = pygame.transform.scale(
            small_surface, (new_width, new_height))

        return pixelated

    def _pixelate_surface(self, surface, pixel_size, num_colors):
        """向後兼容的像素化方法"""
        return self._pixelate_surface_fast(surface, pixel_size, num_colors)

    def _get_dominant_colors_fast(self, surface, num_colors):
        """快速提取主色調（使用 main.py 的方法）"""

        width, height = surface.get_size()
        colors = []

        # 採樣所有像素（小圖像所以可以全部採樣）
        for x in range(width):
            for y in range(height):
                color = surface.get_at((x, y))
                if color.a > 128:  # 只考慮不透明的像素
                    colors.append((color.r, color.g, color.b))

        if not colors:
            return [(0, 0, 0)]

        # 返回最常見的顏色
        color_counter = Counter(colors)
        return [c for c, _ in color_counter.most_common(num_colors)]

    def _get_dominant_colors(self, surface, num_colors):
        """向後兼容"""
        return self._get_dominant_colors_fast(surface, num_colors)

    def _apply_palette(self, surface, palette):
        """將surface的顏色映射到調色板"""
        width, height = surface.get_size()
        result = pygame.Surface((width, height), pygame.SRCALPHA)

        for x in range(width):
            for y in range(height):
                color = surface.get_at((x, y))
                if color.a > 0:
                    nearest = self._find_nearest_color(color[:3], palette)
                    result.set_at((x, y), (*nearest, color.a))
                else:
                    result.set_at((x, y), (0, 0, 0, 0))

        return result

    def _find_nearest_color(self, color, palette):
        """在調色板中找到最接近的顏色"""
        # 處理 pygame.Color 對象或元組
        if hasattr(color, 'r'):
            r, g, b = color.r, color.g, color.b
        else:
            r, g, b = color[:3]

        min_dist = float('inf')
        nearest = palette[0] if palette else (0, 0, 0)

        for pal_color in palette:
            pr, pg, pb = pal_color[:3]
            dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist < min_dist:
                min_dist = dist
                nearest = (pr, pg, pb)

        return nearest

    def set_pixelate(self, enabled):
        """啟用/禁用像素化效果"""
        self.enable_pixelate = enabled

    def set_pixel_size(self, size):
        """設置像素大小 (2-16)"""
        # allow up to 32 to match editor slider range
        self.pixel_size = max(2, min(32, size))

    def set_color_palette(self, num_colors):
        """設置調色板大小 (4-32)"""
        self.num_colors = max(4, min(32, num_colors))


__all__ = ['AnimatedCharacter']

# Global weak registry for live AnimatedCharacter instances
try:
    GLOBAL_ANIM_CHAR_REGISTRY = weakref.WeakSet()
except Exception:
    GLOBAL_ANIM_CHAR_REGISTRY = set()


def apply_global_pixel_settings(pixel_size: int = None, num_colors: int = None):
    """Apply pixel settings to all live AnimatedCharacter instances.

    This is a convenience used by editor tools to update existing characters
    without recreating scenes.
    """
    print(f"[apply_global_pixel_settings] called with pixel_size={pixel_size}, num_colors={num_colors}")
    applied = 0
    try:
        regs = list(GLOBAL_ANIM_CHAR_REGISTRY)
        print(f"[apply_global_pixel_settings] registry contains {len(regs)} entries")
        for inst in regs:
            try:
                try:
                    ident = repr(inst)
                except Exception:
                    ident = str(type(inst))
                print(f"[apply_global_pixel_settings] applying to instance: {ident}")
                if pixel_size is not None:
                    try:
                        inst.set_pixel_size(int(pixel_size))
                    except Exception:
                        inst.pixel_size = int(pixel_size)
                if num_colors is not None:
                    try:
                        inst.set_color_palette(int(num_colors))
                    except Exception:
                        inst.num_colors = int(num_colors)
                applied += 1
            except Exception as e:
                print(f"[apply_global_pixel_settings] error applying to instance: {e}")
                pass
    except Exception as e:
        print(f"[apply_global_pixel_settings] error iterating registry: {e}")
        pass
    try:
        print(f"[apply_global_pixel_settings] applied to {applied} instances")
    except Exception:
        pass
    return applied