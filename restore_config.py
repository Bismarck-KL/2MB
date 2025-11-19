"""
从body_parts_config.json恢复配置到body_parts.py
"""
import json

# 读取配置
with open('body_parts_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 生成Python代码
code = '"""\n'
code += '身体部位分割模块\n'
code += '根据提供的切片样本图片定义身体各部位的边界框\n'
code += '"""\n\n\n'
code += "class BodyParts:\n"
code += '    """定义身体各部位的分割区域（基于slice_sample.png的彩色框）"""\n\n'
code += "    def __init__(self):\n"

for name, data in config.items():
    code += f"        self.{name} = ({data['x']}, {data['y']}, {data['width']}, {data['height']})\n"

code += "\n    def get_all_parts(self):\n"
code += '        """返回所有身体部位的字典"""\n'
code += "        return {\n"

for name in config.keys():
    code += f"            '{name}': self.{name},\n"

code += "        }\n"

# 保存
with open('body_parts.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ 已从 body_parts_config.json 恢复配置到 body_parts.py")
print("\n请重新运行 main.py")
