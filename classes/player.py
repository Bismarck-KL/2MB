import pygame
from typing import Optional, Tuple
import random

class Player:
    """Simple player entity used by GameScene.

    Controls: arrow keys or WASD to move. Draws an image if available via
    app.res_mgr.get_image(image_key) otherwise a colored rectangle.
    """

    def __init__(
        self,
        app,
        player_id: int,
        image_key: str = "player",
    ) -> None:
        self.app = app
        self.screen = app.screen
        w, h = (200,200)

        # player 0, bottom left; player 1, bottom right
        start_x = (50 + w) if player_id == 0 else app.WIDTH - 50 - w
        start_y = app.HEIGHT - 50 - h

        self.pos = pygame.Vector2(float(start_x), float(start_y))
        self.size = (w, h)
        self.speed = float(300.0)
        # random color if no image
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        # load image from resource manager if available
        self.image: Optional[pygame.Surface] = None
        try:
            if hasattr(app, "res_mgr"):
                surf = app.res_mgr.get_image(image_key)
                if surf:
                    # scale once to desired size
                    try:
                        self.image = pygame.transform.smoothscale(surf, (w, h))
                    except Exception:
                        self.image = pygame.transform.scale(surf, (w, h))
        except Exception:
            self.image = None

        # gamedata
        self.player_id = player_id
        self.helth = 100


        # collision / draw rect
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        dir_x = 0
        dir_y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dir_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dir_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dir_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dir_x += 1

        vel = pygame.Vector2(dir_x, dir_y)
        if vel.length_squared() > 0:
            vel = vel.normalize() * self.speed * dt
            self.pos += vel

        # clamp to screen
        half_w, half_h = self.size[0] / 2, self.size[1] / 2
        self.pos.x = max(half_w, min(self.app.WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(self.app.HEIGHT - half_h, self.pos.y))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface) -> None:
        if self.image:
            img_rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(self.image, img_rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=8)


__all__ = ["Player"]
