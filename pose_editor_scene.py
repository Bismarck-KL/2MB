import pygame
import os
import json

from utils.color import BG, TITLE
from utils.ui import Button
from classes.animated_character import AnimatedCharacter
from utils.settings import load_settings, save_settings


class PoseEditorScene:
    """A simple in-game pose editor for tweaking part rotations/positions.

    Controls:
      - UP/DOWN: select previous/next body part
      - LEFT/RIGHT: rotate selected part (-/+ degrees)
      - A/D: move selected part X (-/+)
      - W/S: move selected part Y (-/+)
      - Q/E: decrease/increase step size (degrees/pixels)
      - Z: apply current live pose as a named pose (save)
      - R: reload poses
      - ESC / Back: return to Menu
    """

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.title_font = app.title_font
        self.res_mgr = app.res_mgr

        # UI buttons
        self.back_button = Button(pygame.Rect(20, 20, 140, 48), text="Back", font=self.font)
        self.save_button = Button(pygame.Rect(self.app.WIDTH - 160, 20, 140, 48), text="Save Pose", font=self.font)
        # Apply global settings (persist and reload scene)
        self.apply_button = Button(pygame.Rect(self.app.WIDTH - 320, 20, 140, 48), text="Apply Global", font=self.font)

        # create an AnimatedCharacter for live preview
        # try to use generated tpose if available
        tpose_path = os.path.join("assets", "photo", "player1", "tpose.png")
        if not os.path.exists(tpose_path):
            # fallback to packaged image key if exists
            tpose_path = os.path.join("assets", "photo", "tpose.png")

        try:
            self.char = AnimatedCharacter(image_path=tpose_path, scale=0.9)
        except Exception:
            # if loading fails, create with default path that may exist later
            self.char = AnimatedCharacter(image_path=tpose_path, scale=0.9)

        # part list
        self.parts = list(self.char.skeleton.parts.keys())
        if not self.parts:
            self.parts = ['torso']
        self.selected_index = 0
        self.selected_part = self.parts[self.selected_index]

        # adjustment step
        self.step = 5  # degrees/pixels per keypress

        # available poses (loaded from controller) + discovered files
        try:
            ctrl_poses = list(self.char.animation_controller.poses.keys())
        except Exception:
            ctrl_poses = ['ready']

        # discover pose_*.json files and map names -> filenames
        self.pose_file_map = {}
        try:
            for fname in os.listdir('.'):
                if fname.startswith('pose_') and fname.lower().endswith('.json'):
                    try:
                        name = fname[len('pose_'):-5]
                        self.pose_file_map[name] = fname
                    except Exception:
                        pass
        except Exception:
            pass

        # merge lists (controller poses first)
        names = []
        for n in ctrl_poses:
            if n not in names:
                names.append(n)
        for n in self.pose_file_map.keys():
            if n not in names:
                names.append(n)

        self.available_poses = names
        if not self.available_poses:
            self.available_poses = ['ready']
        self.selected_pose_index = 0
        self.selected_pose_name = self.available_poses[self.selected_pose_index]
        # editor state to preserve/restore controller options
        self._editor_prev_auto_return = None

        # text-input for saving name
        self.input_mode = False
        self.input_text = ''
        self.message = ''

        # Pixelation UI sliders
        # pixel size: integer range [2, 32]
        self.pixel_min = 2
        self.pixel_max = 32
        self.pixel_size = int(getattr(self.char, 'pixel_size', 4))
        # color palette size: integer range [2, 32]
        self.color_min = 2
        self.color_max = 32
        self.num_colors = int(getattr(self.char, 'num_colors', 16))

        # slider UI geometry (relative positions)
        self.slider_x = 300
        self.slider_y = 220
        self.slider_w = 300
        self.slider_h = 18
        self.pixel_slider_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_w, self.slider_h)
        self.color_slider_rect = pygame.Rect(self.slider_x, self.slider_y + 48, self.slider_w, self.slider_h)

        # dragging state
        self._drag_pixel = False
        self._drag_color = False

    def on_enter(self):
        # ensure poses are loaded
        try:
            self.char.animation_controller.reload_poses()
        except Exception:
            pass

        # when entering editor, ensure controller won't auto-return while editing
        try:
            ctrl = self.char.animation_controller
            # remember previous auto_return so we can restore on exit
            self._editor_prev_auto_return = getattr(ctrl, 'auto_return', None)
            ctrl.auto_return = False
            # keep pose stable
            ctrl.transition_progress = 1.0
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.input_mode:
                if event.key == pygame.K_RETURN:
                    # save current pose under input_text
                    name = self.input_text.strip()
                    if name:
                        self._save_pose(name)
                        self.message = f"Saved pose '{name}'"
                    self.input_mode = False
                    self.input_text = ''
                elif event.key == pygame.K_ESCAPE:
                    self.input_mode = False
                    self.input_text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    # append char
                    try:
                        ch = event.unicode
                        if ch:
                            self.input_text += ch
                    except Exception:
                        pass
                return

            # global keys
            if event.key == pygame.K_ESCAPE:
                self.app.change_scene("MenuScene")
                return

            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.parts)
                self.selected_part = self.parts[self.selected_index]
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.parts)
                self.selected_part = self.parts[self.selected_index]
            elif event.key == pygame.K_LEFT:
                self._adjust_rotation(-self.step)
            elif event.key == pygame.K_RIGHT:
                self._adjust_rotation(self.step)
            elif event.key == pygame.K_a:
                self._adjust_position(-self.step, 0)
            elif event.key == pygame.K_d:
                self._adjust_position(self.step, 0)
            elif event.key == pygame.K_w:
                self._adjust_position(0, -self.step)
            elif event.key == pygame.K_s:
                self._adjust_position(0, self.step)
            elif event.key == pygame.K_q:
                # smaller step
                self.step = max(1, int(self.step / 2))
            elif event.key == pygame.K_e:
                # larger step
                self.step = int(max(1, self.step * 2))
            elif event.key == pygame.K_z:
                # enter save name mode
                self.input_mode = True
                self.input_text = ''
            elif event.key == pygame.K_LEFTBRACKET:
                # previous available pose
                if self.available_poses:
                    self.selected_pose_index = (self.selected_pose_index - 1) % len(self.available_poses)
                    self.selected_pose_name = self.available_poses[self.selected_pose_index]
                    self.message = f"Selected pose: {self.selected_pose_name}"
            elif event.key == pygame.K_RIGHTBRACKET:
                # next available pose
                if self.available_poses:
                    self.selected_pose_index = (self.selected_pose_index + 1) % len(self.available_poses)
                    self.selected_pose_name = self.available_poses[self.selected_pose_index]
                    self.message = f"Selected pose: {self.selected_pose_name}"
            elif event.key == pygame.K_l:
                # load selected pose into skeleton for editing
                try:
                    self._load_pose(self.selected_pose_name)
                    self.message = f"Loaded pose: {self.selected_pose_name}"
                except Exception as e:
                    self.message = f"Load failed: {e}"
            elif event.key == pygame.K_o:
                # overwrite selected pose with current skeleton (save to original file if exists)
                try:
                    name = self.selected_pose_name or 'custom'
                    # choose filename: use discovered file if present, else default
                    fname = self.pose_file_map.get(name, f"pose_{name}.json")
                    self._save_pose(name, fname)
                    # update mapping and reload
                    self.pose_file_map[name] = fname
                    try:
                        self.char.animation_controller.reload_poses()
                    except Exception:
                        pass
                    # rebuild available_poses combining controller and files
                    try:
                        ctrl_poses = list(self.char.animation_controller.poses.keys())
                    except Exception:
                        ctrl_poses = []
                    names = []
                    for n in ctrl_poses:
                        if n not in names:
                            names.append(n)
                    for n in self.pose_file_map.keys():
                        if n not in names:
                            names.append(n)
                    self.available_poses = names
                    self.message = f"Overwrote pose: {name} -> {fname}"
                except Exception as e:
                    self.message = f"Save failed: {e}"
            elif event.key == pygame.K_r:
                try:
                    self.char.animation_controller.reload_poses()
                    self.message = 'Reloaded poses'
                except Exception as e:
                    self.message = f'Reload failed: {e}'

        # handle UI buttons
        try:
            if self.back_button.handle_event(event):
                # restore controller settings and leave
                try:
                    ctrl = self.char.animation_controller
                    if self._editor_prev_auto_return is not None:
                        ctrl.auto_return = self._editor_prev_auto_return
                except Exception:
                    pass
                self.app.change_scene("MenuScene")

            if self.save_button.handle_event(event):
                # open save name input mode
                self.input_mode = True
                self.input_text = ''
            if self.apply_button.handle_event(event):
                # persist both settings and reload current scene so others pick up
                try:
                    save_settings({"pixel_size": self.pixel_size, "num_colors": self.num_colors})
                except Exception:
                    pass
                self.message = "Saved global settings"
                self._message_timer = 1.8
                # broadcast to existing AnimatedCharacter instances (no reload)
                try:
                    # prefer global registry-based broadcast if available
                    try:
                        from classes.animated_character import apply_global_pixel_settings
                        applied = apply_global_pixel_settings(self.pixel_size, self.num_colors)
                        self.message = f"Applied to {applied} characters"
                        self._message_timer = 1.8
                    except Exception:
                        # fallback to scene-local broadcast
                        self._broadcast_settings()
                except Exception:
                    pass
            # mouse slider events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pixel_slider_rect.collidepoint(event.pos):
                    self._drag_pixel = True
                    # update value immediately
                    self._set_pixel_from_pos(event.pos[0])
                elif self.color_slider_rect.collidepoint(event.pos):
                    self._drag_color = True
                    self._set_color_from_pos(event.pos[0])

            if event.type == pygame.MOUSEMOTION:
                if self._drag_pixel:
                    self._set_pixel_from_pos(event.pos[0])
                if self._drag_color:
                    self._set_color_from_pos(event.pos[0])

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self._drag_pixel:
                    self._drag_pixel = False
                if self._drag_color:
                    self._drag_color = False
        except Exception:
            # fallback: ensure character updates so UI stays responsive
            try:
                self.char.update(1.0/60.0)
            except Exception:
                pass

    def render(self):
        try:
            bg_image = self.res_mgr.get_image("background")
            if bg_image:
                scaled = pygame.transform.smoothscale(bg_image, (self.app.WIDTH, self.app.HEIGHT))
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.fill(BG)
        except Exception:
            self.screen.fill(BG)

        title = self.title_font.render("Pose Editor", True, TITLE)
        self.screen.blit(title, (self.app.WIDTH//2 - title.get_width()//2, 40))

        # draw preview character centered left side
        try:
            self.char.set_position(self.app.WIDTH//2, self.app.HEIGHT//2 + 40)
            self.char.render(self.screen)
        except Exception:
            pass

        # draw UI
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(self.screen, mouse_pos)
        self.save_button.draw(self.screen, mouse_pos)
        try:
            self.apply_button.draw(self.screen, mouse_pos)
        except Exception:
            pass

        # parts list and selected
        x = 40
        y = 140
        line_h = 28
        for i, part in enumerate(self.parts):
            col = (255, 255, 255) if i == self.selected_index else (180, 180, 180)
            txt = self.font.render(f"{part}", True, col)
            self.screen.blit(txt, (x, y + i * line_h))

        # show selected part values
        try:
            part_obj = self.char.skeleton.parts[self.selected_part]
            rot = getattr(part_obj, 'local_rotation', 0)
            pos = getattr(part_obj, 'local_position', [0, 0])
        except Exception:
            rot = 0
            pos = [0, 0]

        info_x = 40
        info_y = self.app.HEIGHT - 160
        self.screen.blit(self.font.render(f"Selected: {self.selected_part}", True, (220,220,220)), (info_x, info_y))
        self.screen.blit(self.font.render(f"Rotation: {rot:.1f} deg", True, (220,220,220)), (info_x, info_y+30))
        self.screen.blit(self.font.render(f"Position: {pos[0]:.1f}, {pos[1]:.1f}", True, (220,220,220)), (info_x, info_y+60))
        self.screen.blit(self.font.render(f"Step: {self.step}", True, (200,200,200)), (info_x, info_y+90))
        # show selected pose and available poses
        try:
            self.screen.blit(self.font.render(f"Pose: {self.selected_pose_name}", True, (220,220,220)), (info_x+300, info_y))
            poses_preview = ', '.join(self.available_poses[:8])
            self.screen.blit(self.font.render(f"Available: {poses_preview}", True, (180,180,180)), (info_x+300, info_y+30))
        except Exception:
            pass

        # message / input
        if self.input_mode:
            prompt = self.font.render("Save as name: " + self.input_text + " (Enter to save)", True, (255,255,200))
            self.screen.blit(prompt, (info_x, info_y+130))
        else:
            hint = self.font.render("Keys: Arrows rotate/move, Q/E step, Z save, R reload", True, (180,180,180))
            self.screen.blit(hint, (info_x, info_y+130))

        if self.message:
            m = self.font.render(self.message, True, (255,200,120))
            self.screen.blit(m, (info_x, info_y+160))

        # draw pixelation sliders
        try:
            mx, my = pygame.mouse.get_pos()
            # track
            pygame.draw.rect(self.screen, (80, 80, 80), self.pixel_slider_rect, border_radius=6)
            pygame.draw.rect(self.screen, (60, 60, 60), self.color_slider_rect, border_radius=6)

            # knob positions
            def knob_x_for(value, vmin, vmax):
                t = (value - vmin) / max(1, (vmax - vmin))
                return int(self.pixel_slider_rect.x + t * self.pixel_slider_rect.width)

            px = knob_x_for(self.pixel_size, self.pixel_min, self.pixel_max)
            cx = knob_x_for(self.num_colors, self.color_min, self.color_max)

            pygame.draw.circle(self.screen, (220, 220, 220), (px, self.pixel_slider_rect.centery), 8)
            pygame.draw.circle(self.screen, (220, 220, 220), (cx, self.color_slider_rect.centery), 8)

            # labels
            self.screen.blit(self.font.render(f"Pixel size: {self.pixel_size}", True, (220,220,220)), (self.slider_x, self.slider_y - 22))
            self.screen.blit(self.font.render(f"Colors: {self.num_colors}", True, (220,220,220)), (self.slider_x, self.slider_y + 26))
        except Exception:
            pass

    def update(self, dt: float):
        """Update loop called from Application; keep character and timers in sync."""
        # update animated character (passes dt to controller)
        try:
            # AnimatedCharacter.update accepts dt
            self.char.update(dt)
        except Exception:
            try:
                # fallback: call without dt
                self.char.update()
            except Exception:
                pass

        # message timeout: clear message after ~3 seconds
        try:
            if hasattr(self, '_message_timer'):
                self._message_timer -= dt
                if self._message_timer <= 0:
                    self.message = ''
                    self._message_timer = 0
            else:
                # initialize when a message is set
                if self.message:
                    self._message_timer = 3.0
        except Exception:
            pass

    def _adjust_rotation(self, delta):
        try:
            part = self.char.skeleton.parts[self.selected_part]
            part.local_rotation = getattr(part, 'local_rotation', 0) + delta
        except Exception:
            pass

    def _adjust_position(self, dx, dy):
        try:
            part = self.char.skeleton.parts[self.selected_part]
            pos = getattr(part, 'local_position', [0,0])
            part.local_position = [pos[0] + dx, pos[1] + dy]
        except Exception:
            pass

    def _set_pixel_from_pos(self, x_coord: int):
        """Set pixel_size from mouse x coordinate on slider."""
        try:
            rel = (x_coord - self.pixel_slider_rect.x) / max(1, self.pixel_slider_rect.width)
            rel = max(0.0, min(1.0, rel))
            val = int(round(self.pixel_min + rel * (self.pixel_max - self.pixel_min)))
            self.pixel_size = val
            try:
                self.char.set_pixel_size(self.pixel_size)
            except Exception:
                self.char.pixel_size = self.pixel_size
            # show message briefly
            self.message = f"Pixel size: {self.pixel_size}"
            self._message_timer = 1.8
            # persist globally
            try:
                save_settings({"pixel_size": self.pixel_size})
            except Exception:
                pass
            # persist globally
            try:
                from utils.settings import save_settings
                save_settings({'pixel_size': self.pixel_size})
            except Exception:
                pass
        except Exception:
            pass

    def _set_color_from_pos(self, x_coord: int):
        """Set num_colors from mouse x coordinate on slider."""
        try:
            rel = (x_coord - self.color_slider_rect.x) / max(1, self.color_slider_rect.width)
            rel = max(0.0, min(1.0, rel))
            val = int(round(self.color_min + rel * (self.color_max - self.color_min)))
            self.num_colors = val
            try:
                self.char.set_color_palette(self.num_colors)
            except Exception:
                self.char.num_colors = self.num_colors
            # show message briefly
            self.message = f"Colors: {self.num_colors}"
            self._message_timer = 1.8
            # persist globally
            try:
                save_settings({"num_colors": self.num_colors})
            except Exception:
                pass
            # persist globally
            try:
                from utils.settings import save_settings
                save_settings({'num_colors': self.num_colors})
            except Exception:
                pass
        except Exception:
            pass

    def _load_pose(self, name: str):
        """Apply a named pose (from animation controller) to the current skeleton for editing."""
        # Prefer using the animation controller to set the pose so controller
        # state matches the skeleton. Set it immediate and disable auto-return
        # temporarily so the idle logic doesn't overwrite torso rotation.
        try:
            ctrl = self.char.animation_controller
            if name not in getattr(ctrl, 'poses', {}):
                raise ValueError(f"Pose '{name}' not found")
            # remember previous auto_return and apply stable pose
            try:
                self._editor_prev_auto_return = getattr(ctrl, 'auto_return', None)
            except Exception:
                self._editor_prev_auto_return = None
            try:
                ctrl.auto_return = False
            except Exception:
                pass
            # set pose immediately (no transition)
            try:
                ctrl.set_pose(name, immediate=True)
            except Exception:
                # fallback: directly apply pose data
                pose = ctrl.poses.get(name, {})
                for part_name, data in pose.items():
                    if part_name in self.char.skeleton.parts:
                        part = self.char.skeleton.parts[part_name]
                        try:
                            part.local_rotation = float(data.get('rotation', getattr(part, 'local_rotation', 0)))
                        except Exception:
                            pass
                        try:
                            part.local_position = list(data.get('position', getattr(part, 'local_position', [0,0])))
                        except Exception:
                            pass
                try:
                    self.char.skeleton.update()
                except Exception:
                    pass
            # ensure controller state indicates pose is active
            try:
                ctrl.current_pose = name
                ctrl.target_pose = name
                ctrl.transition_progress = 1.0
            except Exception:
                pass
        except Exception as e:
            raise

    def _save_pose(self, name: str, filename: str = None):
        # build pose dict from current skeleton
        pose = {}
        try:
            for part_name, part in self.char.skeleton.parts.items():
                pose[part_name] = {
                    'rotation': getattr(part, 'local_rotation', 0),
                    'position': list(getattr(part, 'local_position', [0,0]))
                }
            if filename:
                fname = filename
            else:
                fname = f"pose_{name}.json"
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(pose, f, ensure_ascii=False, indent=2)
            # reload poses
            try:
                self.char.animation_controller.reload_poses()
            except Exception:
                pass
        except Exception as e:
            self.message = f"Save failed: {e}"

    def _broadcast_settings(self):
        """Find AnimatedCharacter instances in the current scene and apply settings live.

        Strategy: inspect top-level attributes of the scene and common containers (player_1/player_2,
        attributes named 'animated_char', or attributes which are AnimatedCharacter themselves).
        """
        try:
            scene = self.app.scene
            applied = 0

            def apply_to_obj(obj):
                nonlocal applied
                try:
                    # if obj is AnimatedCharacter
                    if isinstance(obj, AnimatedCharacter):
                        try:
                            obj.set_pixel_size(self.pixel_size)
                        except Exception:
                            obj.pixel_size = self.pixel_size
                        try:
                            obj.set_color_palette(self.num_colors)
                        except Exception:
                            obj.num_colors = self.num_colors
                        applied += 1
                        return True
                except Exception:
                    pass
                return False

            # check common attributes on scene
            for name, val in list(vars(scene).items()):
                if apply_to_obj(val):
                    continue
                # if object has attribute 'animated_char'
                try:
                    if hasattr(val, 'animated_char') and val.animated_char is not None:
                        apply_to_obj(val.animated_char)
                except Exception:
                    pass

            # also check nested attributes (one level deep)
            for name, val in list(vars(scene).items()):
                try:
                    for sub_name in dir(val):
                        if sub_name.startswith('_'):
                            continue
                        try:
                            sub = getattr(val, sub_name)
                            apply_to_obj(sub)
                        except Exception:
                            pass
                except Exception:
                    pass

            # always apply to editor preview char as well
            try:
                apply_to_obj(self.char)
            except Exception:
                pass

            self.message = f"Applied to {applied} characters"
            self._message_timer = 1.8
        except Exception:
            self.message = "Apply failed"
            self._message_timer = 1.8
