import json
import os

SETTINGS_FILE = 'settings.json'

DEFAULTS = {
    'pixel_size': 4,
    'num_colors': 16
}


def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
                # merge with defaults
                out = DEFAULTS.copy()
                out.update({k: v for k, v in data.items() if v is not None})
                return out
    except Exception:
        pass
    return DEFAULTS.copy()


def save_settings(d: dict):
    try:
        cur = load_settings()
        cur.update(d or {})
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
