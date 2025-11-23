import pygame
import os

from utils.color import BG, TITLE, QUIT_BASE, QUIT_HOVER, HEALTH, HEALTH_BG
from utils.ui import Button, draw_health_bar
from classes.player import Player

# mediapipe capture helpers
try:
    from utils.mediapipe_capture import (
        start_mediapipe_capture,
        stop_mediapipe_capture,
        initialize_mediapipe,
    )
    from utils.loading import run_loading_with_callback
except Exception:
    # allow project to run even if opencv/mediapipe not available at import time
    def start_mediapipe_capture():
        print("start_mediapipe_capture: mediapipe capture not available")

    def stop_mediapipe_capture():
        pass

    def initialize_mediapipe(report, stop_event=None):
        # fake progress for the loading UI when mediapipe isn't installed
        import time

        for p in range(0, 101, 10):
            if stop_event is not None and stop_event.is_set():
                break
            try:
                report(float(p))
            except Exception:
                pass
            time.sleep(0.05)

    def run_loading_with_callback(surface, loader, on_complete=None, **kwargs):
        # Minimal fallback: call loader synchronously and then on_complete
        try:
            try:
                loader(lambda p: None, None)
            except TypeError:
                loader(lambda p: None)
        except Exception:
            pass
        if on_complete:
            try:
                on_complete()
            except Exception:
                pass


class GameScene:
    """Fighting game scene with 2-player combat."""

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        # 使用支持中文的字體
        try:
            self.font = pygame.font.SysFont('microsoftyahei', 36)
            self.title_font = pygame.font.SysFont('microsoftyahei', 60)
        except:
            self.font = app.font
            self.title_font = app.title_font
        self.res_mgr = app.res_mgr

        # back button (top-left)
        self.back_rect = pygame.Rect(20, 20, 140, 48)
        self.back_button = Button(
            self.back_rect,
            text="Back",
            font=self.font,
            base_color=QUIT_BASE,
            hover_color=QUIT_HOVER,
        )

        # Player entities with animation system
        # Player 1 使用 player1 的圖片，Player 2 使用 player2 的圖片
        self.player_1 = Player(app, 0, image_key="player1",
                               use_animation=True,
                               animation_image="assets/photo/player1/tpose.png")
        self.player_2 = Player(app, 1, image_key="player2",
                               use_animation=True,
                               animation_image="assets/photo/player2/tpose.png")
        
        # 格鬥遊戲設定
        self.player_1.position = [300, 500]  # 左側起始位置
        self.player_2.position = [1300, 500]  # 右側起始位置
        self.player_1.facing = 'right'
        self.player_2.facing = 'left'
        
        # 遊戲機制
        self.round_time = 99  # 回合時間（秒）
        self.game_over = False
        self.winner = None
        
        # 攻擊設定
        self.attack_range = 150
        self.punch_damage = 10
        self.kick_damage = 15
        self.block_reduction = 0.7  # 防禦減傷70%
        
        # 物理設定
        self.ground_y = 500
        self.gravity = 0.8
        self.jump_force = -15

    def on_enter(self):
        """Called when the scene becomes active. Start mediapipe capture in a new window."""
        try:
            # show the project's loading UI while we initialize mediapipe
            run_loading_with_callback(
                surface=self.screen,
                loader=initialize_mediapipe,
                on_complete=start_mediapipe_capture,
                title="Initializing Camera",
                subtitle="Preparing MediaPipe...",
            )
        except Exception as e:
            print("GameScene: failed to initialize mediapipe capture:", e)

        # Play background music for the game scene (looped)
        try:
            # ensure mixer is initialized
            try:
                if not pygame.mixer.get_init():
                    print("[SFX] Initializing mixer with 16 channels...")
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                    pygame.mixer.set_num_channels(16)
            except Exception:
                # try to initialize with default params
                try:
                    pygame.mixer.init()
                    pygame.mixer.set_num_channels(16)
                except Exception:
                    pass

            music_path = os.path.join('assets', 'sounds', 'fighting scene_bgm.mp3')
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(0.6)
                    # fade in over 500ms
                    pygame.mixer.music.play(-1, 0.0, 500)  # loop indefinitely
                except Exception as e:
                    print(f"GameScene: failed to play music '{music_path}':", e)
            else:
                print(f"GameScene: music file not found: {music_path}")
        except Exception:
            pass

    def on_exit(self):
        """Called when leaving the scene. Stop the mediapipe capture."""
        try:
            stop_mediapipe_capture()
        except Exception:
            pass
        # stop music when leaving the game scene (fade out)
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.fadeout(500)
        except Exception:
            pass

    def handle_event(self, event):
        print(f'[DEBUG] GameScene.handle_event: event={event}, game_over={self.game_over}')
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print('[DEBUG] GameScene.handle_event: ESC pressed, switching to MenuScene')
            self.app.change_scene("MenuScene")

        # back button click
        if self.back_button.handle_event(event):
            print('[DEBUG] GameScene.handle_event: Back button clicked, switching to MenuScene')
            self.app.change_scene("MenuScene")
        
        # 遊戲結束後按空白鍵重新開始
        if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print('[DEBUG] GameScene.handle_event: SPACE pressed, restarting game')
            self.reset_game()

    def update(self, dt):
        if self.game_over:
            # 遊戲結束時只顯示結果，不自動退出
            return
        
        # 更新回合時間
        self.round_time -= dt
        if self.round_time <= 0:
            self.end_game_by_time()
            return
        
        # 處理鍵盤輸入
        keys = pygame.key.get_pressed()
        self.handle_player_input(keys)
        
        # 更新玩家
        self.player_1.update(dt)
        self.player_2.update(dt)
        
        # 更新物理（跳躍）
        self.update_physics()
        
        # 更新面向方向
        self.update_facing()
        
        # 檢查碰撞和攻擊
        self.check_attacks()
        
        # 檢查勝負
        self.check_win_condition()

    def handle_player_input(self, keys):
        """處理雙玩家輸入"""
        # Player 1 控制 (1234)
        if not self.player_1.is_hurt:
            # 1: 跳躍向前
            if keys[pygame.K_1] and not self.player_1.is_jumping:
                self.player_1.trigger_action('jump', 0.5)
                self.player_1.velocity_y = self.jump_force
                # 根據面向跳躍
                jump_dist = 25
                if self.player_1.facing == 'right':
                    self.player_1.position[0] += jump_dist
                else:
                    self.player_1.position[0] -= jump_dist
            
            # 2: 出拳
            if keys[pygame.K_2] and self.player_1.attack_cooldown <= 0:
                self.player_1.trigger_action('punch', 0.3)
                self.player_1.attack_cooldown = 0.3
                self.player_1.current_attack = 'punch'
            
            # 3: 踢腿
            if keys[pygame.K_3] and self.player_1.attack_cooldown <= 0:
                self.player_1.trigger_action('kick', 0.3)
                self.player_1.attack_cooldown = 0.3
                self.player_1.current_attack = 'kick'
            
            # 4: 防禦
            if keys[pygame.K_4]:
                self.player_1.is_blocking = True
                self.player_1.trigger_action('block', 0.5)
            else:
                self.player_1.is_blocking = False
        
        # Player 2 控制 (QWER)
        if not self.player_2.is_hurt:
            # Q: 跳躍向前
            if keys[pygame.K_q] and not self.player_2.is_jumping:
                self.player_2.trigger_action('jump', 0.5)
                self.player_2.velocity_y = self.jump_force
                # 根據面向跳躍
                jump_dist = 25
                if self.player_2.facing == 'right':
                    self.player_2.position[0] += jump_dist
                else:
                    self.player_2.position[0] -= jump_dist
            
            # W: 出拳
            if keys[pygame.K_w] and self.player_2.attack_cooldown <= 0:
                self.player_2.trigger_action('punch', 0.3)
                self.player_2.attack_cooldown = 0.3
                self.player_2.current_attack = 'punch'
            
            # E: 踢腿
            if keys[pygame.K_e] and self.player_2.attack_cooldown <= 0:
                self.player_2.trigger_action('kick', 0.3)
                self.player_2.attack_cooldown = 0.3
                self.player_2.current_attack = 'kick'
            
            # R: 防禦
            if keys[pygame.K_r]:
                self.player_2.is_blocking = True
                self.player_2.trigger_action('block', 0.5)
            else:
                self.player_2.is_blocking = False
    
    def update_physics(self):
        """更新物理（重力和跳躍）"""
        for player in [self.player_1, self.player_2]:
            if player.is_jumping:
                player.velocity_y += self.gravity
                player.position[1] += player.velocity_y
                
                # 落地
                if player.position[1] >= self.ground_y:
                    player.position[1] = self.ground_y
                    player.velocity_y = 0
                    player.is_jumping = False
        
        # 防止角色重疊
        self.prevent_overlap()
    
    def prevent_overlap(self):
        """防止角色重疊"""
        min_distance = 100  # 最小距離（角色寬度）
        distance = self.player_2.position[0] - self.player_1.position[0]
        
        if abs(distance) < min_distance:
            # 推開角色
            overlap = min_distance - abs(distance)
            if distance > 0:  # player2在右邊
                self.player_1.position[0] -= overlap / 2
                self.player_2.position[0] += overlap / 2
            else:  # player2在左邊
                self.player_1.position[0] += overlap / 2
                self.player_2.position[0] -= overlap / 2
    
    def update_facing(self):
        """更新角色面向"""
        if self.player_1.position[0] < self.player_2.position[0]:
            self.player_1.facing = 'right'
            self.player_2.facing = 'left'
        else:
            self.player_1.facing = 'left'
            self.player_2.facing = 'right'
    
    def check_attacks(self):
        """檢查攻擊碰撞"""
        distance = abs(self.player_1.position[0] - self.player_2.position[0])
        
        # Player 1 攻擊 Player 2
        if hasattr(self.player_1, 'current_attack') and self.player_1.current_attack:
            if distance <= self.attack_range and self.player_1.attack_cooldown > 0.2:
                damage = self.punch_damage if self.player_1.current_attack == 'punch' else self.kick_damage
                if self.player_2.is_blocking:
                    damage = int(damage * self.block_reduction)
                self.player_2.take_damage(damage)
                self.player_1.current_attack = None
        
        # Player 2 攻擊 Player 1
        if hasattr(self.player_2, 'current_attack') and self.player_2.current_attack:
            if distance <= self.attack_range and self.player_2.attack_cooldown > 0.2:
                damage = self.punch_damage if self.player_2.current_attack == 'punch' else self.kick_damage
                if self.player_1.is_blocking:
                    damage = int(damage * self.block_reduction)
                self.player_1.take_damage(damage)
                self.player_2.current_attack = None
    
    def check_win_condition(self):
        """檢查勝負條件"""
        if self.player_1.health_points <= 0:
            self.game_over = True
            self.winner = 2
        elif self.player_2.health_points <= 0:
            self.game_over = True
            self.winner = 1

    def _play_win_sound(self):
        try:
            print("[SFX] _play_win_sound called")
            # 確保 mixer 已初始化
            if not pygame.mixer.get_init():
                print("[SFX] Mixer not initialized, initializing...")
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.set_num_channels(16)
            print(f"[SFX] Mixer get_init: {pygame.mixer.get_init()}")
            print(f"[SFX] Mixer music busy: {pygame.mixer.music.get_busy()}")
            print(f"[SFX] Mixer num_channels: {pygame.mixer.get_num_channels()}")
            if not hasattr(self, '_win_sound_played') or not self._win_sound_played:
                win_path = 'assets/sounds/you win.wav'
                print(f"[SFX] Loading win sound: {win_path}")
                if not os.path.exists(win_path):
                    print(f"[SFX] Win sound file not found: {win_path}")
                win_sfx = pygame.mixer.Sound(win_path)
                win_sfx.set_volume(1.0)
                print(f"[SFX] Win sound volume: {win_sfx.get_volume()}")
                # 只播放勝利音效，不處理 BGM
                channel_id = pygame.mixer.find_channel()
                print(f"[SFX] Allocated channel id: {channel_id}")
                if channel_id:
                    channel_id.play(win_sfx)
                else:
                    print("[SFX] No free channel for win sound!")
                self._win_sound_played = True
        except Exception as e:
            print(f"[SFX] Win sound error: {e}")
    
    def end_game_by_time(self):
        """時間到，血量多的獲勝"""
        self.game_over = True
        if self.player_1.health_points > self.player_2.health_points:
            self.winner = 1
        elif self.player_2.health_points > self.player_1.health_points:
            self.winner = 2
        else:
            self.winner = 0  # 平手
    
    def reset_game(self):
        """重置遊戲"""
        self.player_1.health_points = self.player_1.max_health_points
        self.player_2.health_points = self.player_2.max_health_points
        self.player_1.position = [300, 500]
        self.player_2.position = [1300, 500]
        self.player_1.facing = 'right'
        self.player_2.facing = 'left'
        self.player_1.is_jumping = False
        self.player_2.is_jumping = False
        self.player_1.velocity_y = 0
        self.player_2.velocity_y = 0
        self.round_time = 99
        self.game_over = False
        self.winner = None
        self._win_sound_played = False
        if hasattr(self.player_1, 'attack_cooldown'):
            self.player_1.attack_cooldown = 0
        if hasattr(self.player_2, 'attack_cooldown'):
            self.player_2.attack_cooldown = 0

    def render(self):
        # draw background image or color
        try:
            bg_image = self.res_mgr.get_image("game_background")
            if bg_image:
                scaled = pygame.transform.smoothscale(
                    bg_image, (self.app.WIDTH, self.app.HEIGHT))
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.fill(BG)
        except Exception:
            self.screen.fill(BG)

        # draw back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)

        # draw players
        self.player_1.draw(self.screen)
        self.player_2.draw(self.screen)

        # draw HUD
        try:
            w_margin = 16
            h_margin = 100
            bar_w = 360
            bar_h = 20
            
            # Player 1 health bar (left)
            p1_rect = pygame.Rect(w_margin, h_margin, bar_w, bar_h)
            draw_health_bar(
                self.screen, p1_rect, self.player_1.health_points, self.player_1.max_health_points)
            lbl1 = self.font.render("P1", True, TITLE)
            self.screen.blit(lbl1, (p1_rect.right + 8, h_margin - 2))

            # Player 2 health bar (right)
            p2_rect = pygame.Rect(
                self.app.WIDTH - w_margin - bar_w, h_margin, bar_w, bar_h)
            draw_health_bar(
                self.screen, p2_rect, self.player_2.health_points, self.player_2.max_health_points)
            lbl2 = self.font.render("P2", True, TITLE)
            lbl2_rect = lbl2.get_rect()
            self.screen.blit(
                lbl2, (p2_rect.left - lbl2_rect.width - 8, h_margin - 2))
            
            # 回合時間
            time_text = self.title_font.render(f"{int(self.round_time)}", True, TITLE)
            time_rect = time_text.get_rect(center=(self.app.WIDTH // 2, 40))
            self.screen.blit(time_text, time_rect)
            
            # 控制說明
            controls_y = self.app.HEIGHT - 80
            p1_controls = self.font.render("P1: 1-Jump  2-Punch  3-Kick  4-Block", True, (200, 200, 200))
            p2_controls = self.font.render("P2: Q-Jump  W-Punch  E-Kick  R-Block", True, (200, 200, 200))
            self.screen.blit(p1_controls, (50, controls_y))
            p2_x = self.app.WIDTH - p2_controls.get_width() - 50
            self.screen.blit(p2_controls, (p2_x, controls_y))
            
        except Exception:
            pass
        
        # 遊戲結束畫面
        if self.game_over:
            overlay = pygame.Surface((self.app.WIDTH, self.app.HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            if self.winner == 0:
                result_text = "DRAW!"
            else:
                result_text = f"PLAYER {self.winner} WINS!"
            
            result = self.title_font.render(result_text, True, (255, 255, 0))
            result_rect = result.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
            self.screen.blit(result, result_rect)
            
            restart = self.font.render("Press SPACE to Restart", True, (255, 255, 255))
            restart_rect = restart.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2 + 60))
            self.screen.blit(restart, restart_rect)
