"""
交互式身体部位调整工具
可以手动调整分割区域和连接位置
"""
import glob
import pygame
import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

# 先创建临时窗口
temp_screen = pygame.display.set_mode((100, 100))

# 加载原始图片
photo_files = glob.glob("assets/photo/*.*")
image_files = [f for f in photo_files if f.lower().endswith(
    ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'))]
if not image_files:
    print("Error: No image found in assets/photo/")
    sys.exit(1)
image_path = image_files[0]
print(f"Loading image: {image_path}")
original_image = pygame.image.load(image_path).convert_alpha()
img_width = original_image.get_width()
img_height = original_image.get_height()

# 创建实际窗口
screen_width = img_width + 500
screen_height = img_height + 100
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("身体部位调整工具")

# 初始分割数据
body_parts = {
    'head': {'rect': [444, 58, 137, 127], 'color': (0, 0, 255)},
    'torso': {'rect': [442, 148, 182, 208], 'color': (255, 165, 0)},
    'left_upper_arm': {'rect': [370, 150, 80, 96], 'color': (0, 255, 0)},
    'left_forearm': {'rect': [218, 150, 160, 96], 'color': (0, 200, 0)},
    'right_upper_arm': {'rect': [617, 128, 98, 96], 'color': (0, 255, 0)},
    'right_forearm': {'rect': [655, 125, 173, 96], 'color': (255, 255, 0)},
    'left_thigh': {'rect': [420, 318, 95, 130], 'color': (255, 0, 0)},
    'left_shin': {'rect': [397, 425, 95, 185], 'color': (255, 0, 255)},
    'right_thigh': {'rect': [515, 318, 95, 130], 'color': (255, 0, 0)},
    'right_shin': {'rect': [515, 425, 95, 185], 'color': (255, 0, 255)}
}

# 当前选中的部位
selected_part = 'head'
part_names = list(body_parts.keys())
selected_index = 0

# 拖动状态
dragging = False
drag_mode = None  # 'move', 'resize_x', 'resize_y', 'resize_xy'
drag_start = [0, 0]
original_rect = [0, 0, 0, 0]

# 显示设置
show_all = True
alpha = 100
zoom = 1.0
offset_x = 50
offset_y = 50

# 保存提示
save_message = ""
save_message_timer = 0

# 使用系统中文字体
try:
    font = pygame.font.SysFont('microsoftyahei', 24)
    small_font = pygame.font.SysFont('microsoftyahei', 20)
    big_font = pygame.font.SysFont('microsoftyahei', 36)
except:
    try:
        font = pygame.font.SysFont('simhei', 24)
        small_font = pygame.font.SysFont('simhei', 20)
        big_font = pygame.font.SysFont('simhei', 36)
    except:
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        big_font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()


def load_data():
    """从配置文件加载数据"""
    try:
        config_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'body_parts_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 更新body_parts
        for name, data in config.items():
            if name in body_parts:
                body_parts[name]['rect'] = [
                    data['x'], data['y'], data['width'], data['height']
                ]

        print("✓ 已从 body_parts_config.json 加载配置")
        return True
    except FileNotFoundError:
        print("✗ 找不到 body_parts_config.json")
        return False
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        return False


def save_data():
    """保存当前数据到文件"""
    # 保存到body_parts_config.json
    config = {}
    for name, data in body_parts.items():
        config[name] = {
            'x': data['rect'][0],
            'y': data['rect'][1],
            'width': data['rect'][2],
            'height': data['rect'][3]
        }

    parent_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(parent_dir, 'body_parts_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    # 生成Python代码 - 包含注释
    code = '"""\n'
    code += '身体部位分割模块\n'
    code += '根据提供的切片样本图片定义身体各部位的边界框\n'
    code += '"""\n\n\n'
    code += "class BodyParts:\n"
    code += '    """定义身体各部位的分割区域（基于slice_sample.png的彩色框）"""\n\n'
    code += "    def __init__(self):\n"
    for name, data in body_parts.items():
        x, y, w, h = data['rect']
        code += f"        self.{name} = ({x}, {y}, {w}, {h})\n"

    code += "\n    def get_all_parts(self):\n"
    code += '        """返回所有身体部位的字典"""\n'
    code += "        return {\n"
    for name in body_parts.keys():
        code += f"            '{name}': self.{name},\n"
    code += "        }\n"

    # 同时更新body_parts.py（主文件）
    body_parts_path = os.path.join(parent_dir, 'body_parts.py')
    with open(body_parts_path, 'w', encoding='utf-8') as f:
        f.write(code)

    print("✓ 已保存配置到 body_parts.py 和 body_parts_config.json")
    return True


def get_rect_on_screen(rect):
    """将图片坐标转换为屏幕坐标"""
    x, y, w, h = rect
    return [
        int(x * zoom + offset_x),
        int(y * zoom + offset_y),
        int(w * zoom),
        int(h * zoom)
    ]


def get_rect_on_image(screen_x, screen_y):
    """将屏幕坐标转换为图片坐标"""
    return [
        int((screen_x - offset_x) / zoom),
        int((screen_y - offset_y) / zoom)
    ]


def mirror_left_to_right():
    """将左侧部位镜像到右侧"""
    # 获取图片中心线x坐标
    center_x = img_width / 2

    # 镜像对应关系
    mirror_pairs = [
        ('left_upper_arm', 'right_upper_arm'),
        ('left_forearm', 'right_forearm'),
        ('left_thigh', 'right_thigh'),
        ('left_shin', 'right_shin')
    ]

    for left_name, right_name in mirror_pairs:
        if left_name in body_parts and right_name in body_parts:
            left_rect = body_parts[left_name]['rect']

            # 计算镜像后的x坐标
            # 左侧部位右边缘到中心的距离
            left_right_edge = left_rect[0] + left_rect[2]
            distance_to_center = center_x - left_right_edge

            # 右侧部位的左边缘应该在相同距离的另一侧
            new_x = center_x + distance_to_center

            # 更新右侧部位
            body_parts[right_name]['rect'][0] = int(new_x)
            body_parts[right_name]['rect'][1] = left_rect[1]  # y坐标相同
            body_parts[right_name]['rect'][2] = left_rect[2]  # 宽度相同
            body_parts[right_name]['rect'][3] = left_rect[3]  # 高度相同

    print("已将左侧部位镜像到右侧")


# 启动时自动加载已有配置
print("\n=== 身体部位调整工具 ===")
if load_data():
    print("已自动加载上次保存的配置\n")
else:
    print("使用默认配置\n")

running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_data()
                running = False

            # 切换选中的部位
            elif event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(part_names)
                selected_part = part_names[selected_index]
            elif event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(part_names)
                selected_part = part_names[selected_index]

            # 微调位置
            elif event.key == pygame.K_w:
                body_parts[selected_part]['rect'][1] -= 1
            elif event.key == pygame.K_s:
                body_parts[selected_part]['rect'][1] += 1
            elif event.key == pygame.K_a:
                body_parts[selected_part]['rect'][0] -= 1
            elif event.key == pygame.K_d:
                body_parts[selected_part]['rect'][0] += 1

            # 微调尺寸
            elif event.key == pygame.K_i:  # 增加高度
                body_parts[selected_part]['rect'][3] += 1
            elif event.key == pygame.K_k:  # 减少高度
                body_parts[selected_part]['rect'][3] = max(
                    1, body_parts[selected_part]['rect'][3] - 1)
            elif event.key == pygame.K_j:  # 减少宽度
                body_parts[selected_part]['rect'][2] = max(
                    1, body_parts[selected_part]['rect'][2] - 1)
            elif event.key == pygame.K_l:  # 增加宽度
                body_parts[selected_part]['rect'][2] += 1

            # 切换显示
            elif event.key == pygame.K_SPACE:
                show_all = not show_all

            # 镜像左侧到右侧
            elif event.key == pygame.K_m:
                mirror_left_to_right()
                save_message = "已镜像左侧到右侧"
                save_message_timer = 120

            # 加载
            elif event.key == pygame.K_o:
                if load_data():
                    save_message = "✓ 已加载配置"
                    save_message_timer = 180
                else:
                    save_message = "✗ 加载失败"
                    save_message_timer = 180

            # 保存
            elif event.key == pygame.K_RETURN:
                if save_data():
                    save_message = "✓ 已保存到 body_parts.py"
                    save_message_timer = 180

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 检查是否点击在当前选中的矩形上
                rect = body_parts[selected_part]['rect']
                screen_rect = get_rect_on_screen(rect)
                mx, my = mouse_pos

                if (screen_rect[0] <= mx <= screen_rect[0] + screen_rect[2] and
                        screen_rect[1] <= my <= screen_rect[1] + screen_rect[3]):
                    dragging = True
                    drag_mode = 'move'
                    drag_start = [mx, my]
                    original_rect = rect.copy()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging and drag_mode == 'move':
                mx, my = mouse_pos
                dx = (mx - drag_start[0]) / zoom
                dy = (my - drag_start[1]) / zoom

                body_parts[selected_part]['rect'][0] = int(
                    original_rect[0] + dx)
                body_parts[selected_part]['rect'][1] = int(
                    original_rect[1] + dy)

    # 清屏
    screen.fill((40, 40, 50))

    # 绘制原始图片
    scaled_img = pygame.transform.scale(original_image,
                                        (int(img_width * zoom), int(img_height * zoom)))
    screen.blit(scaled_img, (offset_x, offset_y))

    # 绘制中心线（用于镜像参考）
    center_x_screen = int(img_width / 2 * zoom + offset_x)
    pygame.draw.line(screen, (100, 255, 100),
                     (center_x_screen, offset_y),
                     (center_x_screen, int(offset_y + img_height * zoom)), 2)

    # 绘制所有部位的矩形
    for name, data in body_parts.items():
        rect = data['rect']
        color = data['color']
        screen_rect = get_rect_on_screen(rect)

        if show_all or name == selected_part:
            # 半透明填充
            s = pygame.Surface((screen_rect[2], screen_rect[3]))
            s.set_alpha(alpha if name == selected_part else alpha // 2)
            s.fill(color)
            screen.blit(s, (screen_rect[0], screen_rect[1]))

            # 边框
            thickness = 3 if name == selected_part else 1
            pygame.draw.rect(screen, color, screen_rect, thickness)

            # 标签
            if name == selected_part or show_all:
                label = small_font.render(name, True, color)
                screen.blit(label, (screen_rect[0] + 2, screen_rect[1] + 2))

    # 绘制UI信息
    y_offset = 20
    info_x = img_width + offset_x + 20

    # 当前选中部位信息
    rect = body_parts[selected_part]['rect']
    texts = [
        f"选中: {selected_part}",
        f"位置: ({rect[0]}, {rect[1]})",
        f"尺寸: {rect[2]} x {rect[3]}",
        "",
        "控制说明:",
        "↑↓ - 切换部位",
        "WASD - 移动位置",
        "IJKL - 调整尺寸",
        "  I/K - 高度 ±1",
        "  J/L - 宽度 ±1",
        "鼠标拖动 - 移动",
        "M - 镜像左侧到右侧",
        "O - 加载配置",
        "空格 - 显示全部/单个",
        "回车 - 保存配置",
        "ESC - 保存并退出",
        "",
        "部位列表:"
    ]

    for i, text in enumerate(texts):
        color = (255, 255, 0) if i < 3 else (200, 200, 200)
        surface = small_font.render(text, True, color)
        screen.blit(surface, (info_x, y_offset))
        y_offset += 22

    # 列出所有部位
    for i, name in enumerate(part_names):
        color = body_parts[name]['color'] if name == selected_part else (
            150, 150, 150)
        prefix = "► " if name == selected_part else "  "
        surface = small_font.render(prefix + name, True, color)
        screen.blit(surface, (info_x, y_offset))
        y_offset += 20

    # 显示保存提示
    if save_message_timer > 0:
        save_message_timer -= 1
        # 计算透明度
        alpha_val = min(255, save_message_timer * 2)
        # 绘制半透明背景
        bg_surface = pygame.Surface((500, 60))
        bg_surface.set_alpha(min(200, alpha_val))
        bg_surface.fill((0, 150, 0))
        screen.blit(bg_surface, (screen_width // 2 - 250, 30))
        # 绘制文字
        text_surface = big_font.render(save_message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width // 2, 60))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
