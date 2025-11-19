"""
Directly update pose functions in animation.py
"""
import json
import re


def format_pose_code(pose_data):
    """Format pose data as Python code"""
    lines = []
    lines.append("        return {")

    # Torso and head
    for part in ['torso', 'head']:
        if part in pose_data:
            p = pose_data[part]
            lines.append(
                f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},")

    lines.append("")
    lines.append("            # Left arm")
    for part in ['left_upper_arm', 'left_forearm']:
        if part in pose_data:
            p = pose_data[part]
            lines.append(
                f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},")

    lines.append("")
    lines.append("            # Right arm")
    for part in ['right_upper_arm', 'right_forearm']:
        if part in pose_data:
            p = pose_data[part]
            lines.append(
                f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},")

    lines.append("")
    lines.append("            # Left leg")
    for part in ['left_thigh', 'left_shin']:
        if part in pose_data:
            p = pose_data[part]
            lines.append(
                f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},")

    lines.append("")
    lines.append("            # Right leg")
    for part in ['right_thigh', 'right_shin']:
        if part in pose_data:
            p = pose_data[part]
            if part == 'right_shin':
                lines.append(
                    f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}}")
            else:
                lines.append(
                    f"            '{part}': {{'rotation': {p['rotation']}, 'position': {p['position']}}},")

    lines.append("        }")
    return '\n'.join(lines)


def update_pose_in_animation(pose_name, pose_data):
    """Update pose function in animation.py

    Args:
        pose_name: 'ready', 'punch', or 'kick'
        pose_data: Pose data dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read animation.py
        with open('animation.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find function definition line
        func_name = f'def get_{pose_name}('
        start_idx = None
        end_idx = None
        brace_count = 0
        in_return = False

        for i, line in enumerate(lines):
            if func_name in line:
                start_idx = i
                continue

            if start_idx is not None and end_idx is None:
                # Find return {
                if 'return {' in line:
                    in_return = True
                    brace_count = line.count('{') - line.count('}')
                    continue

                # Inside return block, count braces
                if in_return:
                    brace_count += line.count('{') - line.count('}')
                    if brace_count == 0:
                        # Found end of return block
                        end_idx = i + 1
                        break

        if start_idx is None or end_idx is None:
            print(f"⚠ Function get_{pose_name} not found")
            return False

        # Find docstring end position
        docstring_end = start_idx + 1
        for i in range(start_idx + 1, end_idx):
            if '"""' in lines[i] and i > start_idx + 1:
                docstring_end = i + 1
                break

        # Generate new return code
        new_return_code = format_pose_code(pose_data)

        # Build new file
        new_lines = lines[:docstring_end]
        new_lines.append(new_return_code + '\n')
        new_lines.extend(lines[end_idx:])

        # Write back to file
        with open('animation.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"✓ Updated get_{pose_name}() in animation.py")
        return True

    except Exception as e:
        print(f"✗ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Test: read pose_custom.json and update ready
    try:
        with open('pose_custom.json', 'r', encoding='utf-8') as f:
            pose = json.load(f)

        print("Choose pose to update:")
        print("1 - ready")
        print("2 - punch")
        print("3 - kick")
        choice = input("Enter choice (1-3): ").strip()

        pose_map = {'1': 'ready', '2': 'punch', '3': 'kick'}
        if choice in pose_map:
            if update_pose_in_animation(pose_map[choice], pose):
                print("\nSuccess! Now press F6 in main.py to reload poses")
        else:
            print("Invalid choice")

    except FileNotFoundError:
        print("pose_custom.json not found")
