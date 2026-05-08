"""Quản lý cài đặt ứng dụng - JSON."""
import os
import json

SETTINGS_PATH = os.path.join(os.path.expanduser('~'), '.holilihu_reclip', 'settings.json')

DEFAULTS = {
    'output_path': os.path.join(os.path.expanduser('~'), 'Downloads', 'HoLiLiHu_ReClip'),
    'quality': 'best',
    'audio_quality': '192',
    'use_aac': False,
    'create_subfolders': True,
    'max_concurrent_downloads': 3,
    'fragment_concurrency': 4,
}


def load_settings():
    """Đọc cài đặt từ file JSON."""
    try:
        if os.path.isfile(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            # Merge với defaults để đảm bảo đủ key
            result = {**DEFAULTS, **saved}
            return result
    except Exception:
        pass
    return dict(DEFAULTS)


def save_settings(data):
    """Lưu cài đặt ra file JSON."""
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
