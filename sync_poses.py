"""
从pose_custom.json同步姿势到animation.py
使用方法：
1. 在pose_tool中按F2/F3/F4切换到ready/punch/kick
2. 调整好姿势
3. 按P键保存（会保存到pose_custom.json）
4. 运行此脚本：python sync_poses.py
"""
import json

print("\n=== 姿势同步工具 ===")
print("请选择要同步的姿势：")
print("1 - Ready (准备)")
print("2 - Punch (出拳)")
print("3 - Kick (踢腿)")
print("4 - 全部同步")

choice = input("\n请输入选项 (1-4): ").strip()

# 读取pose_custom.json
try:
    with open('pose_custom.json', 'r', encoding='utf-8') as f:
        custom = json.load(f)
    print("✓ 已读取 pose_custom.json")
except:
    print("✗ 找不到 pose_custom.json")
    exit(1)

# 读取animation.py
with open('animation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()


def format_pose_data(pose_data):
    """格式化姿势数据为Python代码"""
    code = "        return {\n"

    # 躯干和头部
    for part in ['torso', 'head']:
        if part in pose_data:
            p = pose_data[part]
            code += f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},\n"

    code += "\n            # 左臂\n"
    for part in ['left_upper_arm', 'left_forearm']:
        if part in pose_data:
            p = pose_data[part]
            code += f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},\n"

    code += "\n            # 右臂\n"
    for part in ['right_upper_arm', 'right_forearm']:
        if part in pose_data:
            p = pose_data[part]
            code += f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},\n"

    code += "\n            # 左腿\n"
    for part in ['left_thigh', 'left_shin']:
        if part in pose_data:
            p = pose_data[part]
            code += f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},\n"

    code += "\n            # 右腿\n"
    for part in ['right_thigh', 'right_shin']:
        if part in pose_data:
            p = pose_data[part]
            if part == 'right_shin':
                code += f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}}\n"
            else:
                code += f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},\n"

    code += "        }\n"
    return code


def replace_function(lines, func_name, new_body):
    """替换函数内容"""
    new_lines = []
    in_function = False
    skip_until_return = False
    indent_level = 0

    for i, line in enumerate(lines):
        if f'def {func_name}(' in line:
            in_function = True
            new_lines.append(line)
            # 找到docstring结束
            j = i + 1
            while j < len(lines):
                new_lines.append(lines[j])
                if '"""' in lines[j] and j > i + 1:
                    break
                j += 1
            # 添加新内容
            new_lines.append(new_body)
            skip_until_return = True
            continue

        if skip_until_return:
            # 跳过旧的return内容，直到找到下一个函数或类
            if line.strip().startswith('def ') or line.strip().startswith('class ') or (line.strip().startswith('@') and 'staticmethod' in line):
                skip_until_return = False
                in_function = False
                new_lines.append(line)
            continue

        new_lines.append(line)

    return new_lines


# 根据选择同步
if choice in ['1', '4']:
    print("\n同步 Ready 姿势...")
    new_body = format_pose_data(custom)
    lines = replace_function(lines, 'get_ready', new_body)
    print("✓ Ready 已同步")

if choice in ['2', '4']:
    print("\n同步 Punch 姿势...")
    new_body = format_pose_data(custom)
    lines = replace_function(lines, 'get_punch', new_body)
    print("✓ Punch 已同步")

if choice in ['3', '4']:
    print("\n同步 Kick 姿势...")
    new_body = format_pose_data(custom)
    lines = replace_function(lines, 'get_kick', new_body)
    print("✓ Kick 已同步")

# 保存
with open('animation.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✓ 已更新 animation.py")
print("请在main.py中按F6重新加载姿势！\n")
