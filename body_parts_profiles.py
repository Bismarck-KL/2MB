"""
身體部位切割配置檔案
支援多個角色配置，每個角色有獨立的切割座標
"""

# 預設配置：原始 sample/tpose.png
DEFAULT_PROFILE = {
    'name': 'default',
    'image_size': (1028, 720),
    'parts': {
        'head': (462, 65, 104, 104),
        'torso': (447, 172, 133, 160),
        'left_upper_arm': (380, 161, 65, 74),
        'left_forearm': (218, 161, 160, 75),
        'right_upper_arm': (583, 161, 65, 74),
        'right_forearm': (650, 161, 160, 75),
        'left_thigh': (433, 363, 79, 113),
        'left_shin': (431, 485, 72, 169),
        'right_thigh': (516, 363, 79, 113),
        'right_shin': (525, 485, 72, 169),
    }
}

# Player 1 配置（需要調整）
PLAYER1_PROFILE = {
    'name': 'player1',
    'image_size': (1028, 720),
    'parts': {
        # TODO: 使用 tools/adjust_tool.py 調整這些座標
        'head': (462, 65, 104, 104),
        'torso': (447, 172, 133, 160),
        'left_upper_arm': (380, 161, 65, 74),
        'left_forearm': (218, 161, 160, 75),
        'right_upper_arm': (583, 161, 65, 74),
        'right_forearm': (650, 161, 160, 75),
        'left_thigh': (433, 363, 79, 113),
        'left_shin': (431, 485, 72, 169),
        'right_thigh': (516, 363, 79, 113),
        'right_shin': (525, 485, 72, 169),
    }
}

# Player 2 配置（需要調整）
PLAYER2_PROFILE = {
    'name': 'player2',
    'image_size': (1028, 720),
    'parts': {
        # TODO: 使用 tools/adjust_tool.py 調整這些座標
        'head': (462, 65, 104, 104),
        'torso': (447, 172, 133, 160),
        'left_upper_arm': (380, 161, 65, 74),
        'left_forearm': (218, 161, 160, 75),
        'right_upper_arm': (583, 161, 65, 74),
        'right_forearm': (650, 161, 160, 75),
        'left_thigh': (433, 363, 79, 113),
        'left_shin': (431, 485, 72, 169),
        'right_thigh': (516, 363, 79, 113),
        'right_shin': (525, 485, 72, 169),
    }
}

# 所有配置的映射
PROFILES = {
    'default': DEFAULT_PROFILE,
    'player1': PLAYER1_PROFILE,
    'player2': PLAYER2_PROFILE,
}

# 圖片路徑到配置的自動映射
PATH_TO_PROFILE = {
    'sample/tpose.png': 'default',
    'assets/photo/tpose.png': 'default',
    'assets/photo/player1/tpose.png': 'player1',
    'assets/photo/player2/tpose.png': 'player2',
}


class BodyPartsConfig:
    """動態身體部位配置類別"""

    def __init__(self, profile_name='default'):
        """
        初始化身體部位配置

        Args:
            profile_name: 配置名稱 ('default', 'player1', 'player2' 或自定義)
        """
        self.profile_name = profile_name
        self.load_profile(profile_name)

    def load_profile(self, profile_name):
        """載入指定配置"""
        if profile_name not in PROFILES:
            print(f"⚠️  配置 '{profile_name}' 不存在，使用預設配置")
            profile_name = 'default'

        profile = PROFILES[profile_name]
        self.name = profile['name']
        self.image_size = profile['image_size']

        # 載入所有部位座標
        parts = profile['parts']
        self.head = parts['head']
        self.torso = parts['torso']
        self.left_upper_arm = parts['left_upper_arm']
        self.left_forearm = parts['left_forearm']
        self.right_upper_arm = parts['right_upper_arm']
        self.right_forearm = parts['right_forearm']
        self.left_thigh = parts['left_thigh']
        self.left_shin = parts['left_shin']
        self.right_thigh = parts['right_thigh']
        self.right_shin = parts['right_shin']

    @staticmethod
    def from_image_path(image_path):
        """根據圖片路徑自動選擇配置"""
        # 標準化路徑分隔符
        norm_path = image_path.replace('\\', '/')

        # 檢查是否有完全匹配
        if norm_path in PATH_TO_PROFILE:
            profile_name = PATH_TO_PROFILE[norm_path]
            print(f"✓ 自動偵測配置: {profile_name} (for {image_path})")
            return BodyPartsConfig(profile_name)

        # 檢查路徑包含關鍵字
        if 'player1' in norm_path.lower():
            print(f"✓ 自動偵測配置: player1 (for {image_path})")
            return BodyPartsConfig('player1')
        elif 'player2' in norm_path.lower():
            print(f"✓ 自動偵測配置: player2 (for {image_path})")
            return BodyPartsConfig('player2')

        # 預設配置
        print(f"✓ 使用預設配置 (for {image_path})")
        return BodyPartsConfig('default')

    def get_all_parts(self):
        """返回所有身體部位的字典"""
        return {
            'head': self.head,
            'torso': self.torso,
            'left_upper_arm': self.left_upper_arm,
            'left_forearm': self.left_forearm,
            'right_upper_arm': self.right_upper_arm,
            'right_forearm': self.right_forearm,
            'left_thigh': self.left_thigh,
            'left_shin': self.left_shin,
            'right_thigh': self.right_thigh,
            'right_shin': self.right_shin,
        }

    def save_to_file(self, filename):
        """將當前配置儲存到檔案"""
        import json
        profile = {
            'name': self.name,
            'image_size': self.image_size,
            'parts': self.get_all_parts()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=4, ensure_ascii=False)
        print(f"✓ 配置已儲存到: {filename}")

    @staticmethod
    def load_from_file(filename):
        """從檔案載入配置"""
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        config = BodyPartsConfig.__new__(BodyPartsConfig)
        config.name = profile['name']
        config.image_size = tuple(profile['image_size'])

        parts = profile['parts']
        for part_name, coords in parts.items():
            setattr(config, part_name, tuple(coords))

        print(f"✓ 配置已載入: {filename}")
        return config


# 向後兼容：保留原始 BodyParts 類別
class BodyParts(BodyPartsConfig):
    """向後兼容的身體部位類別（使用預設配置）"""

    def __init__(self):
        super().__init__('default')
