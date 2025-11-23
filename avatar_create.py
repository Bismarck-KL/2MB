import pygame
import cv2
import numpy as np
import math
import os
import shutil

from utils.color import (
    BG,
    TITLE,
    QUIT_BASE,
    QUIT_HOVER,
    NEXT_BASE,
    NEXT_HOVER,
    CAPTURE_BASE,
    CAPTURE_HOVER,
)
from utils.ui import Button


# TO-DO(FAMA): implement actual avatar creation flow and UI
class AvatarCreateScene:
    """A simple placeholder game scene to demonstrate scene switching.

    Adds a small 'Back' button to return to the main menu.
    """

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
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

        # next button (top-right) - navigate to GameScene
        next_w, next_h = 140, 48
        next_x = self.app.WIDTH - 20 - next_w
        next_y = 20
        self.next_rect = pygame.Rect(next_x, next_y, next_w, next_h)
        self.next_button = Button(
            self.next_rect,
            text="Next",
            font=self.font,
            base_color=NEXT_BASE,
            hover_color=NEXT_HOVER,
        )

        # which player are we capturing (1 or 2)
        self.current_player = 1

        # capture photo button (center)
        capture_w, capture_h = 180, 56
        capture_x = (self.app.WIDTH - capture_w) // 2
        capture_y = self.app.HEIGHT // 2 + 80
        self.capture_rect = pygame.Rect(capture_x, capture_y, capture_w, capture_h)
        self.capture_button = Button(
            self.capture_rect,
            text=f"拍照成為Player{self.current_player}",
            font=self.font,
            base_color=CAPTURE_BASE,
            hover_color=CAPTURE_HOVER,
        )

        # internal capture state
        self.capturing = False
        self.cap = None
        self.last_frame = None
        self.camera_scale = 0.6  # how big the camera preview is relative to screen
        # zoom factor applied only during capture preview (1.2 => 20% zoom)
        self.capture_zoom = 1.2
        # desired capture resolution (attempt to set camera to this)
        self.capture_width = 1280
        self.capture_height = 720
        # optional guide overlay (silhouette) for reference while capturing
        self.guide_surf = None
        # base alpha (0-255) and a multiplicative factor to make the guide more transparent
        self.guide_alpha = 220
        self.guide_alpha_factor = 0.7  # reduce opacity by 30%
        self.guide_outline_surf = None
        # auto-capture countdown (seconds). None when not counting down.
        self.capture_countdown = None
        # after capturing player1, show generated preview and wait for Next
        self.show_preview = False
        self.preview_surf = None
        self.preview_path = None

        # NOTE: guide loader is implemented as a class method below.

        # initial attempt to load (may be refreshed later when capture starts)
        try:
            self.guide_surf, self.guide_outline_surf = self._load_guide_from_disk(self.current_player)
        except Exception:
            self.guide_surf = None
            self.guide_outline_surf = None

    def on_enter(self):
        # play menu/background music for this scene
        try:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                try:
                    pygame.mixer.init()
                except Exception:
                    pass

            music_path = os.path.join('assets', 'sounds', 'game_bgm.mp3')
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(0.5)
                    # fade in over 500ms
                    pygame.mixer.music.play(-1, 0.0, 500)
                except Exception as e:
                    print(f"AvatarCreateScene: failed to play music '{music_path}':", e)
            else:
                print(f"AvatarCreateScene: music file not found: {music_path}")
        except Exception:
            pass

    def on_exit(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.fadeout(500)
        except Exception:
            pass

    def _load_guide_from_disk(self, player=1):
        try:
            base_dir = os.path.join("assets", "photo", f"player{player}")
            preferred = os.path.join(base_dir, "guide.png")

            guide_path = None
            if os.path.exists(preferred):
                guide_path = preferred
            else:
                # fallback: find first matching image file in folder (accept guide.png.png etc.)
                if os.path.isdir(base_dir):
                    for name in os.listdir(base_dir):
                        low = name.lower()
                        if low.endswith(('.png', '.jpg', '.jpeg', '.webp')) and 'guide' in low:
                            guide_path = os.path.join(base_dir, name)
                            break
                    # if still not found, pick any image
                    if guide_path is None:
                        for name in os.listdir(base_dir):
                            low = name.lower()
                            if low.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                guide_path = os.path.join(base_dir, name)
                                break

            if not guide_path or not os.path.exists(guide_path):
                return None, None

            # Simply load the image (prefer ResourceManager-provided surface
            # when available, then pygame, then OpenCV fallback)
            guide = None
            loader_used = None
            try:
                if getattr(self, 'res_mgr', None):
                    try:
                        guide = self.res_mgr.get_image_by_path(os.path.abspath(guide_path))
                        if guide:
                            loader_used = 'res_mgr'
                    except Exception:
                        guide = None
            except Exception:
                guide = None

            if guide is None:
                try:
                    guide = pygame.image.load(os.path.abspath(guide_path)).convert_alpha()
                    loader_used = 'pygame.convert_alpha'
                except Exception:
                    try:
                        guide = pygame.image.load(os.path.abspath(guide_path)).convert()
                        loader_used = 'pygame.convert'
                    except Exception:
                        guide = None

            # if pygame failed, try OpenCV -> numpy -> pygame surface fallback
            if guide is None:
                try:
                    img = cv2.imread(guide_path, cv2.IMREAD_UNCHANGED)
                    if img is not None:
                        # if image has alpha channel, keep it; else convert to RGBA
                        if img.ndim == 3 and img.shape[2] == 4:
                            img_rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
                        else:
                            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            alpha = np.full((img_rgb.shape[0], img_rgb.shape[1], 1), 255, dtype=np.uint8)
                            img_rgba = np.concatenate([img_rgb, alpha], axis=2)
                        h, w = img_rgba.shape[:2]
                        try:
                            guide = pygame.image.frombuffer(img_rgba.tobytes(), (w, h), 'RGBA')
                            loader_used = 'cv2_frombuffer'
                        except Exception:
                            guide = None
                except Exception:
                    pass

            # Also generate a high-contrast outline surface using OpenCV Canny
            guide_outline = None
            try:
                img_cv = cv2.imread(guide_path, cv2.IMREAD_GRAYSCALE)
                if img_cv is not None:
                    # blur slightly then Canny
                    blurred = cv2.GaussianBlur(img_cv, (5, 5), 0)
                    edges = cv2.Canny(blurred, 50, 150)
                    # dilate edges to make lines thicker and more visible
                    try:
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        edges = cv2.dilate(edges, kernel, iterations=1)
                    except Exception:
                        pass
                    h, w = edges.shape[:2]
                    # create RGBA array for outline: white lines, transparent elsewhere
                    outline = np.zeros((h, w, 4), dtype=np.uint8)
                    outline[edges > 0] = [255, 255, 255, 255]
                    try:
                        guide_outline = pygame.image.frombuffer(outline.tobytes(), (w, h), 'RGBA')
                    except Exception:
                        guide_outline = None
            except Exception:
                guide_outline = None
            return guide, guide_outline
        except Exception:
            return None, None

    def handle_event(self, event):
        # keyboard: Esc returns to menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_scene("MenuScene")

        # back button click
        if self.back_button.handle_event(event):
            self.app.change_scene("MenuScene")

        # next button click -> go to GameScene
        if self.next_button.handle_event(event):
            # if we're showing the Player1 preview, Next should start Player2 capture
            try:
                if self.show_preview and self.current_player == 1:
                    # prepare to capture player 2
                    self.show_preview = False
                    self.preview_surf = None
                    self.preview_path = None
                    self.current_player = 2
                    # update capture button label
                    try:
                        self.capture_button.text = f"拍照成為Player{self.current_player}"
                    except Exception:
                        pass
                    # reload guide for player2
                    try:
                        self.guide_surf, self.guide_outline_surf = self._load_guide_from_disk(self.current_player)
                    except Exception:
                        self.guide_surf = None
                        self.guide_outline_surf = None
                    # start camera for player2
                    try:
                        self.capturing = True
                        self.cap = cv2.VideoCapture(0)
                        if not self.cap.isOpened():
                            print("Unable to open camera for Player2")
                            self.capturing = False
                            self.cap = None
                        else:
                            try:
                                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.capture_width))
                                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.capture_height))
                            except Exception:
                                pass
                            self.capture_countdown = 20.0
                            print("Starting capture for Player2 (auto-capture in 20s)")
                    except Exception as e:
                        print("Failed to start camera for Player2:", e)
                else:
                    self.app.change_scene("GameScene")
            except Exception:
                try:
                    self.app.change_scene("GameScene")
                except Exception:
                    pass

        # capture photo button click
        if self.capture_button.handle_event(event):
            # start in-game capture mode
            self.capturing = True
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    print("Unable to open camera")
                    self.capturing = False
                    self.cap = None
                else:
                    # try to set a higher capture resolution for better clarity
                    try:
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.capture_width))
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.capture_height))
                    except Exception:
                        pass
            except Exception as e:
                print("Camera open error:", e)
                self.capturing = False
                self.cap = None
            # reload guide for the current player (may be updated between captures)
            try:
                self.guide_surf, self.guide_outline_surf = self._load_guide_from_disk(self.current_player)
            except Exception:
                self.guide_surf = None
                self.guide_outline_surf = None
            # start auto-capture countdown (seconds)
            self.capture_countdown = 20.0
            print(f"Auto-capture started: {self.capture_countdown} seconds")

            # do not print guide/load related status to console (silenced)

        # when in capture mode, use keys to control capture
        if self.capturing and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # cancel capture
                self._stop_capture()
            elif event.key == pygame.K_SPACE:
                # manual immediate capture
                if self.last_frame is not None:
                    self._do_capture()

    def update(self, dt):
        # grab a frame from camera if capturing
        if self.capturing and self.cap is not None:
            try:
                ret, frame = self.cap.read()
                if ret:
                    self.last_frame = frame.copy()
                else:
                    # failed to read; stop capture
                    self._stop_capture()
            except Exception:
                self._stop_capture()

        # handle auto-capture countdown
        if self.capturing and self.capture_countdown is not None:
            try:
                self.capture_countdown -= dt
                if self.capture_countdown <= 0:
                    # time to auto-capture
                    if self.last_frame is not None:
                        self._do_capture()
            except Exception:
                pass

    def render(self):

        # draw background image or color
        try:
            bg_image = self.res_mgr.get_image("avatar_create_background")
            if bg_image:
                # protect against invalid surfaces
                scaled = pygame.transform.smoothscale(
                    bg_image, (self.app.WIDTH, self.app.HEIGHT)
                )
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.fill(BG)
        except Exception:
            # fallback: plain background color
            self.screen.fill(BG)

        # simple visual
        txt = self.title_font.render("Avatar Create Scene", True, TITLE)
        rect = txt.get_rect(center=(self.app.WIDTH // 2, self.app.HEIGHT // 2))
        self.screen.blit(txt, rect)

        # draw back button
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)
        # draw next button
        self.next_button.draw(self.screen, mouse_pos)

        # draw capture photo button
        self.capture_button.draw(self.screen, mouse_pos)

        # if in capture mode, draw camera preview UI
        if self.capturing and self.last_frame is not None:
            try:
                frame = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
                h, w = frame.shape[:2]
                # scale preview and apply capture zoom
                target_w = int(self.app.WIDTH * self.camera_scale * self.capture_zoom)
                target_h = int(target_w * (h / w))
                frame_rgb = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                surf = pygame.image.frombuffer(frame_rgb.tobytes(), (target_w, target_h), 'RGB')
                preview_x = (self.app.WIDTH - target_w) // 2
                # center the preview image exactly in the window
                preview_y = (self.app.HEIGHT - target_h) // 2
                # smaller padding around image to avoid vertical bias and clipping
                pad = 8
                box_top = preview_y - pad
                box_h = target_h + pad * 2
                # dark background box (slightly larger than image)
                box_rect = pygame.Rect(preview_x - pad, box_top, target_w + pad * 2, box_h)
                pygame.draw.rect(self.screen, (10,10,10), box_rect)
                self.screen.blit(surf, (preview_x, preview_y))

                # overlay panel for readable header + note (semi-transparent)
                try:
                    overlay_h = 64
                    overlay_w = target_w + pad * 2
                    overlay_surf = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
                    overlay_surf.fill((0, 0, 0, 180))
                    overlay_x = preview_x - pad
                    overlay_y = box_top + 6
                    # rounded rect fallback: draw rect on temp surface
                    try:
                        pygame.draw.rect(overlay_surf, (0,0,0,180), pygame.Rect(0,0,overlay_w,overlay_h), border_radius=8)
                    except Exception:
                        overlay_surf.fill((0,0,0,180))

                    # header text (larger) with subtle shadow for contrast
                    header_text = f"拍攝中：Player {self.current_player}"
                    header_surf = self.title_font.render(header_text, True, (255, 255, 255))
                    shadow = self.title_font.render(header_text, True, (0,0,0))
                    h_x = 12
                    h_y = 6
                    overlay_surf.blit(shadow, (h_x+2, h_y+2))
                    overlay_surf.blit(header_surf, (h_x, h_y))

                    # explanatory note (smaller)
                    if self.current_player == 1:
                        note = "完成後會自動切換到 Player 2，請準備好下一位。"
                    else:
                        note = "已拍攝 Player 2，完成後會回到建立畫面。"
                    note_surf = self.font.render(note, True, (230, 230, 230))
                    note_shadow = self.font.render(note, True, (0,0,0))
                    n_x = 12
                    n_y = h_y + header_surf.get_height() + 6
                    overlay_surf.blit(note_shadow, (n_x+1, n_y+1))
                    overlay_surf.blit(note_surf, (n_x, n_y))

                    # blit overlay on main screen above preview
                    self.screen.blit(overlay_surf, (overlay_x, overlay_y))
                except Exception:
                    pass
                # if showing preview (Player1), draw it centered above preview
                if self.show_preview and self.preview_surf:
                    try:
                        pw, ph = self.preview_surf.get_size()
                        # scale preview to fit half the screen width if too large
                        max_w = int(self.app.WIDTH * 0.5)
                        if pw > max_w:
                            scale = max_w / pw
                            new_w = int(pw * scale)
                            new_h = int(ph * scale)
                            pv = pygame.transform.smoothscale(self.preview_surf, (new_w, new_h))
                        else:
                            pv = self.preview_surf
                        pv_x = (self.app.WIDTH - pv.get_width()) // 2
                        pv_y = box_top - pv.get_height() - 16
                        # draw background for preview
                        bg = pygame.Surface((pv.get_width()+8, pv.get_height()+8))
                        bg.fill((20,20,20))
                        self.screen.blit(bg, (pv_x-4, pv_y-4))
                        self.screen.blit(pv, (pv_x, pv_y))
                        # hint text
                        hint = self.font.render('確認角色後按 Next 前往 Player2 拍照', True, (230,230,230))
                        self.screen.blit(hint, ((self.app.WIDTH - hint.get_width())//2, pv_y + pv.get_height() + 8))
                    except Exception:
                        pass
                # draw optional semi-transparent guide overlay if available
                if self.guide_surf:
                    try:
                        guide = pygame.transform.smoothscale(self.guide_surf, (target_w, target_h))
                        # apply configured alpha multiplied by factor (reduce opacity)
                        try:
                            alpha_val = int(self.guide_alpha * getattr(self, 'guide_alpha_factor', 1.0))
                            guide.set_alpha(alpha_val)
                        except Exception:
                            pass

                        # blit guide onto preview
                        self.screen.blit(guide, (preview_x, preview_y))
                    except Exception as e:
                        # don't let overlay errors break preview
                        print('Overlay error:', e)

                # draw high-contrast outline on top for visibility
                if getattr(self, 'guide_outline_surf', None):
                    try:
                        out_s = pygame.transform.smoothscale(self.guide_outline_surf, (target_w, target_h))
                        try:
                            temp = out_s.copy()
                            temp.fill((255, 50, 50, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            self.screen.blit(temp, (preview_x, preview_y))
                        except Exception:
                            self.screen.blit(out_s, (preview_x, preview_y))
                    except Exception as e:
                        print('Outline overlay error:', e)

                # instructions (clamped to remain on-screen)
                instr = self.font.render('Press SPACE to capture, ESC to cancel', True, (230,230,230))
                instr_y = min(preview_y + target_h + 20, self.app.HEIGHT - 28)
                irect = instr.get_rect(center=(self.app.WIDTH//2, instr_y))
                self.screen.blit(instr, irect)

                # countdown display (auto-capture)
                try:
                    if getattr(self, 'capture_countdown', None) is not None:
                        secs = max(0, int(math.ceil(self.capture_countdown)))
                        cd_txt = self.title_font.render(f"Auto capture in: {secs}s", True, (255, 255, 255))
                        # place countdown near the top of the preview box for visibility
                        cd_rect = cd_txt.get_rect(center=(self.app.WIDTH//2, box_top + 18))
                        self.screen.blit(cd_txt, cd_rect)
                except Exception:
                    pass

                # status text intentionally omitted
            except Exception as e:
                print('Preview render error:', e)

        # If not actively capturing but we have a saved preview (Player1), draw it
        if not self.capturing and getattr(self, 'show_preview', False) and getattr(self, 'preview_surf', None):
            try:
                pv = self.preview_surf
                pw, ph = pv.get_size()
                max_w = int(self.app.WIDTH * 0.5)
                if pw > max_w:
                    scale = max_w / pw
                    new_w = int(pw * scale)
                    new_h = int(ph * scale)
                    pv = pygame.transform.smoothscale(pv, (new_w, new_h))
                pv_x = (self.app.WIDTH - pv.get_width()) // 2
                # place preview above center area
                pv_y = max(40, (self.app.HEIGHT // 2) - pv.get_height() - 60)
                bg = pygame.Surface((pv.get_width()+8, pv.get_height()+8))
                bg.fill((20,20,20))
                self.screen.blit(bg, (pv_x-4, pv_y-4))
                self.screen.blit(pv, (pv_x, pv_y))
                hint = self.font.render('確認角色後按 Next 前往 Player2 拍照', True, (230,230,230))
                self.screen.blit(hint, ((self.app.WIDTH - hint.get_width())//2, pv_y + pv.get_height() + 8))
            except Exception:
                pass

    def _stop_capture(self):
        # helper to safely stop capture and release resources
        self.capturing = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        self.cap = None
        self.last_frame = None

    def _do_capture(self):
        """Perform capture save and update resources, then stop capture."""
        try:
            # save into the folder for current player (player1 or player2)
            save_dir = os.path.join("assets", "photo", f"player{self.current_player}")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"player{self.current_player}_photo.jpg")
            # last_frame is BGR (from OpenCV). Save a sharpened, high-res version if possible.
            try:
                img = self.last_frame
                if img is not None:
                    # resize to desired capture resolution (use cubic for quality)
                    try:
                        img_resized = cv2.resize(img, (int(self.capture_width), int(self.capture_height)), interpolation=cv2.INTER_CUBIC)
                    except Exception:
                        img_resized = img

                    # apply simple unsharp mask to increase perceived sharpness
                    try:
                        blurred = cv2.GaussianBlur(img_resized, (0, 0), 3)
                        sharpened = cv2.addWeighted(img_resized, 1.5, blurred, -0.5, 0)
                        cv2.imwrite(save_path, sharpened)
                    except Exception:
                        cv2.imwrite(save_path, img_resized)
                else:
                    cv2.imwrite(save_path, self.last_frame)
            except Exception:
                # fallback to raw write
                cv2.imwrite(save_path, self.last_frame)
            print(f"Photo saved to {save_path}")

            # create a tpose image (RGBA when possible) at the target size
            tpose_path = os.path.join(save_dir, "tpose.png")
            target_w, target_h = 1028, 720
            used_guide_cutout = False
            try:
                if getattr(self, 'guide_surf', None):
                    try:
                        # scale guide surface to target size and extract RGBA bytes
                        guide_scaled = pygame.transform.smoothscale(self.guide_surf, (target_w, target_h))
                        guide_bytes = pygame.image.tostring(guide_scaled, 'RGBA')
                        guide_arr = np.frombuffer(guide_bytes, dtype=np.uint8).reshape((target_h, target_w, 4))
                        alpha_ch = guide_arr[:, :, 3]
                        # If the guide has no meaningful alpha, derive mask from luminance
                        if np.mean(alpha_ch) < 10:
                            lum = (np.dot(guide_arr[:, :, :3], [0.2989, 0.5870, 0.1140])).astype(np.uint8)
                            mask = (lum > 10).astype(np.uint8) * 255
                        else:
                            mask = (alpha_ch > 10).astype(np.uint8) * 255
                        # Apply configured guide_alpha as a multiplier to the mask
                        try:
                            factor = float(getattr(self, 'guide_alpha', 255)) / 255.0
                            # apply guide_alpha_factor to further reduce opacity in mask computation
                            factor = factor * float(getattr(self, 'guide_alpha_factor', 1.0))
                            mask = (np.clip((mask.astype(np.float32) * factor), 0, 255)).astype(np.uint8)
                            mask = (mask > 10).astype(np.uint8) * 255
                        except Exception:
                            pass

                        # resize captured frame and write RGBA using mask as alpha
                        resized_bgr = cv2.resize(self.last_frame, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
                        b, g, r = cv2.split(resized_bgr)
                        alpha = mask.astype(np.uint8)
                        rgba = cv2.merge([b, g, r, alpha])
                        cv2.imwrite(tpose_path, rgba)
                        used_guide_cutout = True
                    except Exception as e_gc:
                        print("Mask-based cutout failed:", e_gc)

                if not used_guide_cutout:
                    # fallback: simple resize without alpha
                    try:
                        img = cv2.imread(save_path, cv2.IMREAD_UNCHANGED)
                        if img is not None:
                            resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
                            cv2.imwrite(tpose_path, resized)
                        else:
                            shutil.copyfile(save_path, tpose_path)
                    except Exception:
                        try:
                            shutil.copyfile(save_path, tpose_path)
                        except Exception:
                            pass
            except Exception as e:
                print("Saving tpose failed:", e)

            print(f"Saved tpose image to {tpose_path} (resized to 1028x720)")

            # Stored tpose.png on disk but DO NOT update UI or in-game players automatically.
            # (This avoids displaying the generated image immediately.)
            try:
                print(f"Saved tpose (not applied to UI) at {tpose_path}")
            except Exception:
                pass

        except Exception as e:
            print("Capture failed:", e)
        finally:
            # clear countdown
            try:
                self.capture_countdown = None
            except Exception:
                pass
            # After capture: if we just captured Player1, DO NOT show a preview.
            # Immediately proceed to Player2 capture (start camera) so flow continues.
            try:
                if self.current_player == 1:
                    # stop current capture
                    try:
                        self._stop_capture()
                    except Exception:
                        pass

                    # switch to player2 and start capture immediately
                    try:
                        self.current_player = 2
                        try:
                            self.capture_button.text = f"拍照成為Player{self.current_player}"
                        except Exception:
                            pass
                        # reload guide for player2
                        try:
                            self.guide_surf, self.guide_outline_surf = self._load_guide_from_disk(self.current_player)
                        except Exception:
                            self.guide_surf = None
                            self.guide_outline_surf = None
                        # start camera for player2
                        try:
                            self.capturing = True
                            self.cap = cv2.VideoCapture(0)
                            if not self.cap.isOpened():
                                print("Unable to open camera for Player2")
                                self.capturing = False
                                self.cap = None
                            else:
                                try:
                                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.capture_width))
                                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.capture_height))
                                except Exception:
                                    pass
                                self.capture_countdown = 20.0
                                print("Starting capture for Player2 (auto-capture in 20s)")
                        except Exception as e:
                            print("Failed to start camera for Player2:", e)
                    except Exception:
                        # if switching fails, ensure capture is stopped
                        try:
                            self._stop_capture()
                        except Exception:
                            pass
                else:
                    # final stop after player2
                    self._stop_capture()
            except Exception:
                # ensure capture is stopped on unexpected errors
                self._stop_capture()

    def _remove_background(self, src_path: str, dst_path: str, target_w: int = 1028, target_h: int = 720) -> bool:
        """Remove background from `src_path` and write RGBA PNG to `dst_path`.

        Returns True if removal+save succeeded, False otherwise.
        Uses OpenCV GrabCut with a full-rect initialization and falls back to a simple threshold alpha if GrabCut fails.
        """
        try:
            img = cv2.imread(src_path, cv2.IMREAD_COLOR)
            if img is None:
                return False

            h, w = img.shape[:2]
            # initialize mask, bgd/fgd models
            mask = np.zeros((h, w), np.uint8)
            rect = (max(1, int(w*0.05)), max(1, int(h*0.05)), max(1, int(w*0.9)), max(1, int(h*0.9)))
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)

            try:
                cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                mask2 = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1).astype('uint8')
                # apply mask
                img_fg = img * mask2[:, :, np.newaxis]

                # create alpha channel from mask2
                alpha = (mask2 * 255).astype(np.uint8)
                b, g, r = cv2.split(img_fg)
                rgba = cv2.merge([b, g, r, alpha])

                # resize to target and save
                rgba_resized = cv2.resize(rgba, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                cv2.imwrite(dst_path, rgba_resized)
                return True
            except Exception:
                # fallback: use simple background mask via adaptive threshold on grayscale
                try:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, th = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
                    alpha = th.astype(np.uint8)
                    b, g, r = cv2.split(img)
                    rgba = cv2.merge([b, g, r, alpha])
                    rgba_resized = cv2.resize(rgba, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                    cv2.imwrite(dst_path, rgba_resized)
                    return True
                except Exception:
                    return False
        except Exception:
            return False
