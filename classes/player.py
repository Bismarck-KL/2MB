import pygame
from typing import Optional, Tuple
import random
import os
import threading
import time

from classes.animated_character import AnimatedCharacter

class Player:
    """Simple player entity used by GameScene.

    Controls: arrow keys or WASD to move. Draws an image if available via
    app.res_mgr.get_image(image_key) otherwise a colored rectangle.

    Supports animated character if use_animation=True.
    """

    def __init__(
        self,
        app,
        player_id: int,
        image_key: str = "player",
        use_animation: bool = False,
        animation_image: str = None,
    ) -> None:
        self.app = app
        self.screen = app.screen
        # Increase default player size by 50%
        w, h = (300, 300)

        # player 0, bottom left; player 1, bottom right
        start_x = (50 + w) if player_id == 0 else app.WIDTH - 50 - w
        start_y = app.HEIGHT - 50 - h

        self.pos = pygame.Vector2(float(start_x), float(start_y))
        self.size = (w, h)
        self.speed = float(300.0)
        # random color if no image
        self.color = (random.randint(100, 255), random.randint(
            100, 255), random.randint(100, 255))

        # Animation support
        self.use_animation = use_animation
        self.animated_char = None

        if use_animation:
            try:
                # from classes.animated_character import AnimatedCharacter
                # 使用指定的圖片或默認的tpose.png
                anim_path = animation_image or "assets/photo/tpose.png"
                if os.path.exists(anim_path):
                    # Player 1 面向右邊，Player 2 面向左邊（翻轉）
                    flip = (player_id == 1)
                    # increase animation scale by 50% (0.5 -> 0.75)
                    self.animated_char = AnimatedCharacter(
                        image_path=anim_path,
                        scale=0.75,
                        enable_pixelate=True,
                        flip_horizontal=flip
                    )
                    # provide shared ResourceManager from app so images/sfx can be reused
                    try:
                        if hasattr(app, 'res_mgr') and app.res_mgr:
                            self.animated_char.set_resource_manager(app.res_mgr)
                    except Exception:
                        pass
                    self.animated_char.set_position(
                        int(self.pos.x), int(self.pos.y))
                    # 設置初始姿勢為ready
                    self.animated_char.set_pose('ready')
                else:
                    print(f"警告: 找不到動畫圖片 {anim_path}，使用靜態模式")
                    self.use_animation = False
            except Exception as e:
                print(f"無法載入動畫系統: {e}")
                self.use_animation = False

        # load image from resource manager if available (for static mode)
        self.image: Optional[pygame.Surface] = None
        if not self.use_animation:
            try:
                if hasattr(app, "res_mgr"):
                    surf = app.res_mgr.get_image(image_key)
                    if surf:
                        # scale once to desired size
                        try:
                            self.image = pygame.transform.smoothscale(
                                surf, (w, h))
                        except Exception:
                            self.image = pygame.transform.scale(surf, (w, h))
            except Exception:
                self.image = None

        # gamedata
        self.player_id = player_id
        self.health_points = 100
        self.max_health_points = 100

        # collision / draw rect
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # 格鬥遊戲屬性
        self.position = [float(self.pos.x), float(self.pos.y)]  # [x, y] 用於格鬥遊戲
        self.facing = 'right'  # 'left' or 'right'
        self.is_jumping = False
        self.velocity_y = 0
        self.is_blocking = False
        self.is_hurt = False
        self.attack_cooldown = 0
        self.current_attack = None

    def update(self, dt: float) -> None:
        # 同步 position 和 pos
        self.pos.x = self.position[0]
        self.pos.y = self.position[1]
        
        # clamp to screen
        half_w, half_h = self.size[0] / 2, self.size[1] / 2
        self.pos.x = max(half_w, min(self.app.WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(self.app.HEIGHT - half_h, self.pos.y))
        
        # 更新 position
        self.position[0] = self.pos.x
        self.position[1] = self.pos.y

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # 更新攻擊冷卻
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                self.current_attack = None

        # 更新動畫角色位置和狀態
        if self.use_animation and self.animated_char:
            self.animated_char.set_position(int(self.pos.x), int(self.pos.y))
            self.animated_char.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.use_animation and self.animated_char:
            # 使用動畫渲染
            self.animated_char.render(surface)
        elif self.image:
            # 使用靜態圖片
            img_rect = self.image.get_rect(
                center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(self.image, img_rect)
        else:
            # 使用彩色方塊
            pygame.draw.rect(surface, self.color, self.rect, border_radius=8)

    def set_pose(self, pose_name: str) -> None:
        """切換姿勢（僅動畫模式）"""
        if self.use_animation and self.animated_char:
            self.animated_char.set_pose(pose_name)

    def trigger_action(self, action_name: str, duration: float = 0.5) -> None:
        """觸發動作（僅動畫模式）"""
        if self.use_animation and self.animated_char:
            self.animated_char.trigger_action(action_name, duration)
    
    def take_damage(self, damage: int) -> None:
        """受到傷害"""
        self.health_points = max(0, self.health_points - damage)
        self.is_hurt = True
        self.trigger_action('hurt', 0.5)
        # 0.5秒後恢復

        def reset_hurt():
            time.sleep(0.5)
            self.is_hurt = False
        threading.Thread(target=reset_hurt, daemon=True).start()

    def set_animation_image(self, image_path: str) -> bool:
        """Replace or set the animated character image at runtime.

        Returns True on success, False otherwise.
        """
        try:
            if not image_path or not os.path.exists(image_path):
                print(f"set_animation_image: image not found: {image_path}")
                return False
            # create a new AnimatedCharacter using the same options as __init__
            flip = (self.player_id == 1)
            self.animated_char = AnimatedCharacter(
                image_path=image_path,
                scale=0.5,
                enable_pixelate=True,
                flip_horizontal=flip,
            )
            self.animated_char.set_position(int(self.pos.x), int(self.pos.y))
            self.animated_char.set_pose('ready')
            self.use_animation = True
            return True
        except Exception as e:
            print(f"Failed to set animation image: {e}")
            return False


__all__ = ["Player"]