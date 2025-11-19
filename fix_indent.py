"""修复animation.py的缩进问题"""
import re

with open('animation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 读取修复前的原始内容以备份
with open('animation_backup.py', 'w', encoding='utf-8') as f:
    f.write(content)

# 按行分割
lines = content.split('\n')
fixed_lines = []
in_class = False
in_method = False
method_indent = 0

for i, line in enumerate(lines):
    # 检测类定义
    if line.strip().startswith('class '):
        in_class = True
        fixed_lines.append(line)
        continue

    # 检测方法定义
    if in_class and re.match(r'^\s+def\s+', line):
        # 确保方法使用4个空格缩进
        method_name = line.strip()
        fixed_lines.append('    ' + method_name)
        in_method = True
        method_indent = 8  # 方法内容使用8个空格
        continue

    # 如果是空行，保持原样
    if not line.strip():
        fixed_lines.append(line)
        continue

    # 如果在方法内，确保正确的缩进层级
    if in_method:
        stripped = line.lstrip()
        # 计算当前实际的缩进层级
        leading_spaces = len(line) - len(stripped)

        # 如果遇到新的方法或类，退出当前方法
        if stripped.startswith('def ') or stripped.startswith('class ') or stripped.startswith('@'):
            in_method = False
            if stripped.startswith('@') or stripped.startswith('def '):
                fixed_lines.append('    ' + stripped)
            else:
                fixed_lines.append(stripped)
            continue

        # 修复缩进...此方法太复杂，让我换个思路
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

print("分析完成，但修复逻辑过于复杂。")
print("建议：让我逐个函数手动修复")
